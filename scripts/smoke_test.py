#!/usr/bin/env python3
"""
smoke_test.py - quick end-to-end check of the database and the API.

    python scripts/smoke_test.py            # uses backend/jac_predictor.db
    python scripts/smoke_test.py --db path/to/other.db --expect 4046

Starts the backend on a free local port, calls the real endpoints with sample
values taken from the database itself, then shuts it down. Standard library
only (uvicorn/fastapi must be installed, as for normal use).
"""
import argparse
import json
import os
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
TABLES = ["universities", "campuses", "branches", "categories", "quota_types",
          "gender_pools", "home_regions", "rounds", "cutoffs"]

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail and not ok else ""))


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def get(base, path, **params):
    q = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    try:
        with urllib.request.urlopen(f"{base}{path}?{q}", timeout=15) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=BACKEND / "jac_predictor.db")
    ap.add_argument("--expect", type=int, default=None, help="expected number of cutoff rows")
    args = ap.parse_args()

    # ---------- database ----------
    if not args.db.is_file():
        sys.exit(f"Database not found: {args.db}\nBuild it first: python data-pipeline/build_db.py --expect 4046")
    conn = sqlite3.connect(f"{args.db.resolve().as_uri()}?mode=ro", uri=True)
    present = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    check("all 9 tables exist", set(TABLES) <= present, f"missing {sorted(set(TABLES) - present)}")
    n = conn.execute("SELECT COUNT(*) FROM cutoffs").fetchone()[0]
    check(f"cutoffs has rows ({n})", n > 0)
    if args.expect is not None:
        check(f"cutoffs count is {args.expect}", n == args.expect, f"found {n}")
    check("integrity_check ok", conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok")
    check("foreign_key_check clean", conn.execute("PRAGMA foreign_key_check").fetchall() == [])

    sample = conn.execute("""
        SELECT cat.category_code, q.quota_code, r.region_code, ro.round_number, c.closing_rank,
               c.rank_type, c.with_bonus
        FROM cutoffs c
        JOIN categories cat ON c.category_id = cat.category_id
        JOIN quota_types q ON c.quota_id = q.quota_id
        JOIN home_regions r ON c.region_id = r.region_id
        JOIN rounds ro ON c.round_id = ro.round_id
        WHERE c.rank_type = 'JEE_CRL' AND c.with_bonus = 0
        ORDER BY (q.quota_code = 'GENERAL') DESC, ro.year DESC, ro.round_number DESC, c.closing_rank
        LIMIT 1""").fetchone()
    female_only = [r[0] for r in conn.execute(
        "SELECT short_code FROM universities WHERE admits_gender = 'FEMALE_ONLY'")]
    conn.close()
    if not sample:
        sys.exit("No JEE_CRL cutoff rows to build a sample request from.")
    category, quota, region, rnd, closing, _, _ = sample
    region_param = None if region == "NOT_APPLICABLE" else region

    # ---------- API ----------
    port = free_port()
    env = dict(os.environ, DB_PATH=str(args.db.resolve()))
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", str(port), "--log-level", "warning"],
        cwd=BACKEND, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(60):
            if server.poll() is not None:
                sys.exit("Backend failed to start:\n" + (server.stdout.read() or ""))
            try:
                urllib.request.urlopen(base + "/", timeout=1)
                break
            except Exception:
                time.sleep(0.25)
        else:
            sys.exit("Backend did not start within 15 seconds.")

        s, j = get(base, "/api/universities")
        check("GET /api/universities", s == 200 and len(j) > 0)
        s, j = get(base, "/api/branches")
        check("GET /api/branches", s == 200 and len(j) > 0)
        s, j = get(base, "/api/rounds")
        check("GET /api/rounds", s == 200 and len(j) > 0)

        common = dict(category=category, quota=quota, region=region_param, round=rnd)
        s, j = get(base, "/api/predict", rank=closing, applicant_gender="FEMALE", **common)
        ok = s == 200 and j.get("count", 0) > 0 and "disclaimer" in j
        check(f"predict (female, rank {closing}, {category}/{quota}) returns results", ok, f"status {s}")
        if ok:
            first = j["results"][0]
            need = {"university", "branch_code", "branch_name", "years", "conservative_rank",
                    "reliability", "chance", "margin_percent"}
            check("result has every field the frontend reads", need <= set(first), f"missing {need - set(first)}")

        if female_only:
            s, j = get(base, "/api/predict", rank=closing, applicant_gender="MALE", **common)
            check("male applicant never sees women-only universities",
                  s == 200 and not any(r["university"] in female_only for r in j.get("results", [])))

        s, _ = get(base, "/api/predict", rank=closing, category=category, applicant_gender="MALE", quota="GENERAL")
        check("missing region for GENERAL quota -> 400", s == 400, f"status {s}")
        s, _ = get(base, "/api/predict", rank=0, category=category, applicant_gender="MALE", region="DELHI")
        check("rank 0 rejected -> 422", s == 422, f"status {s}")
        s, j = get(base, "/api/predict", rank=1, category=category, applicant_gender="MALE",
                   region="DELHI", quota="GENERAL", round=99)
        check("unknown round -> 200 with empty results", s == 200 and j.get("count") == 0, f"status {s}")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    failed = results.count(False)
    print(f"\n{len(results) - failed}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
