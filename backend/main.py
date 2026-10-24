"""
main.py — the predictor API.

Run locally:
    pip install -r requirements.txt
    # put jac_predictor.db in this folder, or: export DB_PATH=/path/to/jac_predictor.db
    uvicorn main:app --reload

Then open http://localhost:8000/docs for interactive API docs (auto-generated
by FastAPI from the type hints below).
"""
import os
from enum import Enum
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.db import fetch_all
from backend import queries

app = FastAPI(
    title="JAC College Predictor API",
    description="Predicts eligible colleges/branches from JEE rank + category, "
                "based on JAC counselling cutoff data (DTU, NSUT, IIIT-D, IGDTUW).",
    version="1.0.0",
)

# Allow the frontend (running on a different port during development) to call this API.
# Tighten this to your actual frontend domain before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------
# Enums — these double as input validation AND as the source of truth
# for what the frontend's dropdowns should offer.
# ---------------------------------------------------------------------
class Category(str, Enum):
    GEN = "GEN"
    EWS = "EWS"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"


class GenderPool(str, Enum):
    GN = "GN"      # gender-neutral
    GIRL = "GIRL"  # girls-only seats


class ApplicantGender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class Quota(str, Enum):
    GENERAL = "GENERAL"
    PWD = "PWD"
    DEFENCE_CW = "DEFENCE_CW"
    KASHMIRI_MIGRANT = "KASHMIRI_MIGRANT"
    SIKKIM_GOA = "SIKKIM_GOA"


class Region(str, Enum):
    DELHI = "DELHI"
    OUTSIDE_DELHI = "OUTSIDE_DELHI"


class RankType(str, Enum):
    JEE_CRL = "JEE_CRL"
    IIITD_RANK = "IIITD_RANK"


# ---------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------
class YearRank(BaseModel):
    year: int
    closing_rank: int
    priority_note: Optional[str]


class PredictionResult(BaseModel):
    university: str
    university_full_name: str
    branch_code: str
    branch_name: str
    campus_name: Optional[str]
    round_number: int
    years: List[YearRank]           # every year with data for this branch
    conservative_rank: int          # the worse (lower) closing rank across years -- used for chance
    reliability: str                # 'single_year' | 'consistent' | 'moderate_swing' | 'volatile'
    chance: str                     # 'Safe' | 'Moderate' | 'Tough', based on conservative_rank
    margin_percent: float


class TrendPoint(BaseModel):
    year: int
    round_number: int
    closing_rank: int


def classify_chance(rank: int, closing_rank: int) -> tuple[str, float]:
    """
    A simple, explainable heuristic: how much headroom does the student's
    rank have below the historical closing rank? Bigger gap = safer bet.
    This is NOT a guarantee -- cutoffs move year to year -- and the API
    response says so explicitly (see 'disclaimer' in the predict response).
    """
    margin = (closing_rank - rank) / closing_rank * 100
    if margin >= 30:
        return "Safe", round(margin, 1)
    elif margin >= 5:
        return "Moderate", round(margin, 1)
    else:
        return "Tough", round(margin, 1)


def classify_reliability(ranks_by_year: dict) -> str:
    """
    With only one year of data (e.g. a branch introduced in 2025), there's
    nothing to cross-check against -- flagged explicitly rather than silently
    treated as equally trustworthy as a 2-year comparison.
    With two+ years, a small year-over-year swing suggests a stable cutoff
    worth trusting; a large swing means last year's number alone would have
    been a poor guide, which is exactly the "don't blindly trust one year"
    problem this endpoint exists to avoid.
    """
    if len(ranks_by_year) < 2:
        return "single_year"
    values = list(ranks_by_year.values())
    lo, hi = min(values), max(values)
    swing = (hi - lo) / hi * 100
    if swing <= 15:
        return "consistent"
    elif swing <= 40:
        return "moderate_swing"
    else:
        return "volatile"


@app.get("/api/predict", response_model=dict)
def predict(
    rank: int = Query(..., gt=0, description="Your JEE rank (CRL)"),
    category: Category = Query(...),
    applicant_gender: ApplicantGender = Query(
        ..., description="Male applicants are ineligible for women-only institutions "
                          "(e.g. IGDTUW) and for girls-reserved seats at co-ed institutions."
    ),
    region: Optional[Region] = Query(None, description="Ignored for Kashmiri Migrant and Sikkim/Goa quotas"),
    quota: Quota = Query(Quota.GENERAL),
    round_number: int = Query(5, alias="round", description="Compared across every year that has this round"),
    rank_type: RankType = Query(RankType.JEE_CRL),
    with_bonus: bool = Query(False, description="IIIT-D 'with bonus' cutoffs only"),
    limit: int = Query(50, le=200),
):
    # These quotas are stored with no home region in the cutoff data.
    regionless = quota in (Quota.KASHMIRI_MIGRANT, Quota.SIKKIM_GOA)
    if not regionless and region is None:
        raise HTTPException(400, "region is required unless quota is KASHMIRI_MIGRANT or SIKKIM_GOA")

    # A female applicant is eligible for BOTH gender-neutral seats and
    # girls-reserved seats; a male applicant is eligible for gender-neutral
    # seats only. Women-only universities (admits_gender='FEMALE_ONLY') are
    # excluded entirely for male applicants at the SQL level (see queries.py).
    eligible_gender_pools = ("GN", "GIRL") if applicant_gender == ApplicantGender.FEMALE else ("GN",)

    params = {
        "category": category.value,
        "pool_1": eligible_gender_pools[0],
        "pool_2": eligible_gender_pools[-1],
        "applicant_gender": applicant_gender.value,
        "region": None if regionless else (region.value if region else None),
        "quota": quota.value,
        "round_number": round_number,
        "rank_type": rank_type.value,
        "with_bonus": with_bonus,
    }

    raw_rows = fetch_all(queries.PREDICT_MULTI_YEAR_SQL, params)

    # group every (year, closing_rank) row under its branch, so each branch
    # is judged on its full multi-year history rather than one snapshot
    branches = {}
    order = []
    for row in raw_rows:
        key = (row["university"], row["branch_code"], row["campus_name"])
        if key not in branches:
            branches[key] = {
                "university": row["university"],
                "university_full_name": row["university_full_name"],
                "branch_code": row["branch_code"],
                "branch_name": row["branch_name"],
                "campus_name": row["campus_name"],
                "years": {},
                "priority_by_year": {},
            }
            order.append(key)
        branches[key]["years"][row["year"]] = row["closing_rank"]
        branches[key]["priority_by_year"][row["year"]] = row["priority_note"]

    results = []
    for key in order:
        b = branches[key]
        conservative_rank = min(b["years"].values())
        if max(b["years"].values()) < rank:
            continue  # not reachable in ANY available year -- skip entirely
        reliability = classify_reliability(b["years"])
        chance, margin = classify_chance(rank, conservative_rank)
        results.append(PredictionResult(
            university=b["university"],
            university_full_name=b["university_full_name"],
            branch_code=b["branch_code"],
            branch_name=b["branch_name"],
            campus_name=b["campus_name"],
            round_number=round_number,
            years=[YearRank(year=y, closing_rank=b["years"][y], priority_note=b["priority_by_year"][y])
                   for y in sorted(b["years"])],
            conservative_rank=conservative_rank,
            reliability=reliability,
            chance=chance,
            margin_percent=margin,
        ))

    results.sort(key=lambda r: r.conservative_rank)
    results = results[:limit]

    return {
        "count": len(results),
        "results": results,
        "disclaimer": "Each branch is judged on every year of cutoff data available for it "
                       "(not just one year), using the more conservative (harder) of the "
                       "available years to classify chance. Historical cutoffs are not a "
                       "guarantee -- actual cutoffs can still move beyond this range.",
    }


@app.get("/api/trend", response_model=List[TrendPoint])
def trend(
    university: str,
    branch_code: str,
    category: Category,
    gender: GenderPool = GenderPool.GN,
    region: Optional[Region] = None,
    quota: Quota = Quota.GENERAL,
    rank_type: RankType = RankType.JEE_CRL,
    with_bonus: bool = False,
):
    params = {
        "university": university,
        "branch_code": branch_code,
        "category": category.value,
        "gender": gender.value,
        "region": region.value if region else None,
        "quota": quota.value,
        "rank_type": rank_type.value,
        "with_bonus": with_bonus,
    }
    rows = fetch_all(queries.TREND_SQL, params)
    return [TrendPoint(**r) for r in rows]


@app.get("/api/universities")
def list_universities():
    return fetch_all(queries.META_UNIVERSITIES_SQL)


@app.get("/api/branches")
def list_branches(university: Optional[str] = None):
    return fetch_all(queries.META_BRANCHES_SQL, {"university": university})


@app.get("/api/rounds")
def list_rounds():
    return fetch_all(queries.META_ROUNDS_SQL)


@app.get("/")
def root():
    return {"message": "JAC College Predictor API — see /docs for interactive documentation"}
