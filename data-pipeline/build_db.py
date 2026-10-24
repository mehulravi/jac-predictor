#!/usr/bin/env python3
"""
build_db.py - builds backend/jac_predictor.db (SQLite) from the cutoff CSVs.

    python data-pipeline/build_db.py --expect 4046

Inputs (default locations, relative to the project root):
    data/cutoffs_unified.csv   required - one row per cutoff
    data/branches_master.csv   optional - only used for branch names

Uses only the Python standard library. The database is built in a temporary
file, validated, and only then moved into place, so a failed build never
leaves a half-written database behind.

No row is dropped silently: rows that cannot be loaded are listed and the
build stops (use --allow-skipped to load the valid rows anyway).
"""
import argparse
import csv
import os
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

UNIVERSITIES = {
    "DTU": ("Delhi Technological University", "Delhi", "ALL"),
    "NSUT": ("Netaji Subhas University of Technology", "Delhi", "ALL"),
    "IIITD": ("Indraprastha Institute of Information Technology Delhi", "Delhi", "ALL"),
    "IGDTUW": ("Indira Gandhi Delhi Technical University for Women", "Delhi", "FEMALE_ONLY"),
}
CATEGORIES = {
    "GEN": "General", "EWS": "Economically Weaker Section", "OBC": "Other Backward Classes",
    "SC": "Scheduled Caste", "ST": "Scheduled Tribe",
}
QUOTAS = {
    "GENERAL": "General", "PWD": "Persons with Disabilities", "DEFENCE_CW": "Defence (CW)",
    "KASHMIRI_MIGRANT": "Kashmiri Migrant", "SIKKIM_GOA": "Sikkim / Goa",
}
POOLS = {"GN": "Gender-neutral", "GIRL": "Girls-only seats"}
REGIONS = {"DELHI": "Delhi", "OUTSIDE_DELHI": "Outside Delhi", "NOT_APPLICABLE": "Not applicable"}
RANK_TYPES = {"JEE_CRL", "IIITD_RANK"}

# Accepted column names for each field (first match wins).
ALIASES = {
    "university": ["university", "university_code", "short_code"],
    "branch_code": ["branch_code", "branch"],
    "branch_name": ["branch_name"],
    "campus": ["campus", "campus_name"],
    "year": ["year"],
    "round_number": ["round_number", "round"],
    "category_code": ["category_code", "category"],
    "quota_code": ["quota_code", "quota", "quota_type_code"],
        
            "gender_pool": ["gender_pool", "gender_pool_code", "pool_code"],
    "region_code": ["region_code", "region"],
    "rank_type": ["rank_type"],
    "with_bonus": ["with_bonus"],
    "closing_rank": ["closing_rank"],
    "priority_note": ["priority_note"],
    "source_page_ref": ["source_page_ref"],
}
REQUIRED = ["university", "branch_code", "year", "round_number",
            "category_code", "quota_code", "closing_rank"]
BLANKS = {"", "none", "null", "nan", "na", "n/a"}


def blank(v):
    return v is None or str(v).strip().lower() in BLANKS


def text(v):
    return None if blank(v) else str(v).strip()


def resolve_columns(header, required, label):
    lower = {h.strip().lower(): h for h in header}
    cols = {}
    for field, names in ALIASES.items():
        cols[field] = next((lower[n] for n in names if n in lower), None)
    missing = [f for f in required if cols[f] is None]
    if missing:
        sys.exit(f"ERROR: {label} is missing required column(s): {', '.join(missing)}\n"
                 f"       Columns found: {', '.join(header)}")
    return cols


def parse_bool(v):
    s = "" if v is None else str(v).strip().lower()
    if s in ("1", "true", "t", "yes", "y"):
        return 1
    if s in BLANKS or s in ("0", "false", "f", "no", "n"):
        return 0
    raise ValueError(f"unrecognised with_bonus value {v!r}")


def parse_int(v, what):
    try:
        n = int(float(str(v).strip()))
    except (TypeError, ValueError):
        raise ValueError(f"{what} is not a number: {v!r}")
    return n


def normalise_row(raw, cols):
    """Return a clean dict for one CSV row, or raise ValueError with the reason."""
    def get(field):
        c = cols[field]
        return raw.get(c) if c else None

    uni = (text(get("university")) or "").upper().replace("-", "").replace(" ", "")
    if uni not in UNIVERSITIES:
        raise ValueError(f"unknown university {get('university')!r}")

    category = (text(get("category_code")) or "").upper()
    if category not in CATEGORIES:
        raise ValueError(f"unknown category {get('category_code')!r}")

    quota = (text(get("quota_code")) or "").upper()
    pool = (text(get("gender_pool")) or "").upper()
    # JAC codes encode "girls-only seats" as a quota letter pair (GL); the API models
    # that as quota GENERAL + gender pool GIRL.
    if quota in ("GIRLS", "GIRL", "GL"):
        quota = "GENERAL"
        pool = pool or "GIRL"
    if quota not in QUOTAS:
        raise ValueError(f"unknown quota {get('quota_code')!r}")
    pool = {"GIRLS": "GIRL", "GL": "GIRL"}.get(pool, pool) or "GN"
    if pool not in POOLS:
        raise ValueError(f"unknown gender pool {get('gender_pool')!r}")

    region = (text(get("region_code")) or "NOT_APPLICABLE").upper()
    region = {"OUTSIDE": "OUTSIDE_DELHI"}.get(region, region)
    if region not in REGIONS:
        raise ValueError(f"unknown region {get('region_code')!r}")

    rank_type = (text(get("rank_type")) or "JEE_CRL").upper()
    rank_type = {"JEE": "JEE_CRL", "IIITD": "IIITD_RANK"}.get(rank_type, rank_type)
    if rank_type not in RANK_TYPES:
        raise ValueError(f"unknown rank_type {get('rank_type')!r}")

    branch_code = text(get("branch_code"))
    if not branch_code:
        raise ValueError("blank branch_code")
    closing = parse_int(get("closing_rank"), "closing_rank")
    if closing <= 0:
        raise ValueError(f"closing_rank must be positive, got {closing}")

    return {
        "university": uni, "branch_code": branch_code, "branch_name": text(get("branch_name")),
        "campus": text(get("campus")), "year": parse_int(get("year"), "year"),
        "round_number": parse_int(get("round_number"), "round_number"),
        "category": category, "quota": quota, "pool": pool, "region": region,
        "rank_type": rank_type, "with_bonus": parse_bool(get("with_bonus")),
        "closing_rank": closing, "priority_note": text(get("priority_note")),
        "source_page_ref": text(get("source_page_ref")),
    }


def read_cutoffs(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cols = resolve_columns(reader.fieldnames or [], REQUIRED, path.name)
        rows, bad, total = [], [], 0
        for line_no, raw in enumerate(reader, start=2):
            if not any((v or "").strip() for v in raw.values() if isinstance(v, str)):
                continue  # fully blank line
            total += 1
            try:
                rows.append(normalise_row(raw, cols))
            except ValueError as e:
                bad.append((line_no, str(e)))
    return rows, bad, total


def read_branch_master(path):
    """Optional: {(university, branch_code): branch_name}. Ignored if columns don't fit."""
    if not path.is_file():
        return {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        lower = {h.strip().lower(): h for h in header}
        uc = next((lower[n] for n in ALIASES["university"] if n in lower), None)
        bc = next((lower[n] for n in ALIASES["branch_code"] if n in lower), None)
        nc = next((lower[n] for n in ALIASES["branch_name"] if n in lower), None)
        if not (uc and bc and nc):
            print(f"note: {path.name} has no university/branch_code/branch_name columns "
                  f"({', '.join(header)}); branch names come from the cutoff file instead.")
            return {}
        names = {}
        for raw in reader:
            u = (text(raw.get(uc)) or "").upper().replace("-", "").replace(" ", "")
            b, n = text(raw.get(bc)), text(raw.get(nc))
            if u and b and n:
                names[(u, b)] = n
        return names


def build(cutoff_path, branch_path, out_path, expect, allow_skipped):
    rows, bad, total = read_cutoffs(cutoff_path)
    print(f"Read {total} data rows from {cutoff_path.name}: {len(rows)} valid, {len(bad)} invalid")
    if bad:
        for line_no, reason in bad[:20]:
            print(f"  line {line_no}: {reason}")
        if len(bad) > 20:
            print(f"  ... and {len(bad) - 20} more")
        if not allow_skipped:
            sys.exit("ERROR: invalid rows found, database not built. "
                     "Fix the CSV or re-run with --allow-skipped to load the valid rows.")

    master = read_branch_master(branch_path)

    # branch display names: most common name in the cutoff file, else the master list
    name_votes = defaultdict(Counter)
    for r in rows:
        if r["branch_name"]:
            name_votes[(r["university"], r["branch_code"], r["campus"])][r["branch_name"]] += 1
    branch_keys = sorted({(r["university"], r["branch_code"], r["campus"]) for r in rows},
                         key=lambda k: (k[0], k[1], k[2] or ""))

    tmp_path = out_path.with_name(out_path.name + ".tmp")
    if tmp_path.exists():
        tmp_path.unlink()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(tmp_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript((HERE / "schema.sql").read_text(encoding="utf-8"))

        def seed(table, cols, data):
            conn.executemany(f"INSERT INTO {table} ({cols}) VALUES ({','.join('?' * len(data[0]))})", data)

        seed("universities", "short_code, full_name, location_city, admits_gender",
             [(k, v[0], v[1], v[2]) for k, v in UNIVERSITIES.items()])
        seed("categories", "category_code, category_name", list(CATEGORIES.items()))
        seed("quota_types", "quota_code, quota_name", list(QUOTAS.items()))
        seed("gender_pools", "pool_code, pool_name", list(POOLS.items()))
        seed("home_regions", "region_code, region_name", list(REGIONS.items()))
        campuses = sorted({k[2] for k in branch_keys if k[2]})
        if campuses:
            seed("campuses", "campus_name", [(c,) for c in campuses])
        seed("rounds", "year, round_number", sorted({(r["year"], r["round_number"]) for r in rows}))

        def ids(table, code_col, id_col):
            return {c: i for i, c in conn.execute(f"SELECT {id_col}, {code_col} FROM {table}")}
        uni_id = ids("universities", "short_code", "university_id")
        cat_id = ids("categories", "category_code", "category_id")
        quota_id = ids("quota_types", "quota_code", "quota_id")
        pool_id = ids("gender_pools", "pool_code", "gender_pool_id")
        region_id = ids("home_regions", "region_code", "region_id")
        campus_id = ids("campuses", "campus_name", "campus_id")
        round_id = {(y, n): i for i, y, n in conn.execute("SELECT round_id, year, round_number FROM rounds")}

        branch_id = {}
        for key in branch_keys:
            uni, code, campus = key
            votes = name_votes.get(key)
            name = votes.most_common(1)[0][0] if votes else master.get((uni, code), code)
            if votes and len(votes) > 1:
                print(f"warning: {uni} {code} has several branch names {dict(votes)}; using {name!r}")
            cur = conn.execute(
                "INSERT INTO branches (university_id, campus_id, branch_code, branch_name) VALUES (?,?,?,?)",
                (uni_id[uni], campus_id.get(campus), code, name))
            branch_id[key] = cur.lastrowid

        conn.executemany(
            "INSERT INTO cutoffs (branch_id, category_id, quota_id, gender_pool_id, region_id, round_id, "
            "rank_type, with_bonus, closing_rank, priority_note, source_page_ref) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            [(branch_id[(r["university"], r["branch_code"], r["campus"])], cat_id[r["category"]],
              quota_id[r["quota"]], pool_id[r["pool"]], region_id[r["region"]],
              round_id[(r["year"], r["round_number"])], r["rank_type"], r["with_bonus"],
              r["closing_rank"], r["priority_note"], r["source_page_ref"]) for r in rows])
        conn.commit()

        # ---- validation ----
        problems = []
        if conn.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            problems.append("PRAGMA integrity_check failed")
        fk = conn.execute("PRAGMA foreign_key_check").fetchall()
        if fk:
            problems.append(f"{len(fk)} foreign key violation(s)")
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        need = {"universities", "campuses", "branches", "categories", "quota_types",
                "gender_pools", "home_regions", "rounds", "cutoffs"}
        if need - tables:
            problems.append(f"missing tables: {sorted(need - tables)}")
        n_cut = conn.execute("SELECT COUNT(*) FROM cutoffs").fetchone()[0]
        if n_cut != len(rows):
            problems.append(f"cutoffs table has {n_cut} rows but {len(rows)} valid rows were read")
        if expect is not None and n_cut != expect:
            problems.append(f"expected {expect} cutoff rows but loaded {n_cut}")

        dup = conn.execute(
            "SELECT COUNT(*) FROM (SELECT 1 FROM cutoffs GROUP BY branch_id, category_id, quota_id, "
            "gender_pool_id, region_id, round_id, rank_type, with_bonus HAVING COUNT(*) > 1)").fetchone()[0]
        if dup:
            print(f"warning: {dup} cutoff key(s) appear more than once (same branch/category/quota/"
                  f"pool/region/round/rank type/bonus). All rows were kept, but the API will use only "
                  f"one value per key.")

        if problems:
            raise SystemExit("ERROR: validation failed: " + "; ".join(problems))

        print("\nLoaded:")
        for t in ["universities", "campuses", "branches", "categories", "quota_types",
                  "gender_pools", "home_regions", "rounds", "cutoffs"]:
            print(f"  {t:<14}{conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:>7}")
        print("\nCutoffs by university / year / round:")
        for u, y, n, c in conn.execute(
                "SELECT u.short_code, ro.year, ro.round_number, COUNT(*) FROM cutoffs c "
                "JOIN branches b ON c.branch_id=b.branch_id JOIN universities u ON b.university_id=u.university_id "
                "JOIN rounds ro ON c.round_id=ro.round_id GROUP BY 1,2,3 ORDER BY 1,2,3"):
            print(f"  {u:<8}{y}  round {n}: {c}")
        print("\nChecks passed: integrity_check ok, foreign_key_check clean, all 9 tables present.")
    except BaseException:
        conn.close()
        tmp_path.unlink(missing_ok=True)
        raise
    conn.close()
    os.replace(tmp_path, out_path)
    print(f"Wrote {out_path}")


def main():
    ap = argparse.ArgumentParser(description="Build backend/jac_predictor.db from the cutoff CSVs.")
    ap.add_argument("--cutoffs", type=Path, default=ROOT / "data" / "cutoffs_unified.csv")
    ap.add_argument("--branches", type=Path, default=ROOT / "data" / "branches_master.csv")
    ap.add_argument("--out", type=Path, default=ROOT / "backend" / "jac_predictor.db")
    ap.add_argument("--expect", type=int, default=None, help="fail unless exactly this many cutoff rows load")
    ap.add_argument("--allow-skipped", action="store_true", help="load valid rows even if some rows are invalid")
    args = ap.parse_args()
    if not args.cutoffs.is_file():
        sys.exit(f"ERROR: {args.cutoffs} not found. Copy cutoffs_unified.csv (and branches_master.csv) "
                 f"into the data/ folder, or pass --cutoffs.")
    build(args.cutoffs, args.branches, args.out, args.expect, args.allow_skipped)


if __name__ == "__main__":
    main()
