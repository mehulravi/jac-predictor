# JAC Predictor — Backend API

FastAPI service reading cutoff data from a SQLite database.

## Setup
```
pip install -r requirements.txt
```
The database is generated from the CSVs in `../data`:
```
python ../data-pipeline/build_db.py --expect 4046
```
This writes `backend/jac_predictor.db`. To use a database elsewhere:
```
export DB_PATH=/path/to/jac_predictor.db
```
`DB_PATH` and the default path work from any launch directory.
The file is opened read-only, so the API never modifies your data.

## Run
```
uvicorn main:app --reload
```
Then open http://localhost:8000/docs for the interactive API explorer.

## Endpoints
- `GET /api/predict` — the core predictor. Required: `rank`, `category`,
  `applicant_gender` (MALE | FEMALE). Optional: `region` (required unless
  quota=KASHMIRI_MIGRANT), `quota` (default GENERAL), `round` (default 5),
  `rank_type` (default JEE_CRL), `with_bonus` (default false), `limit` (default 50).
  Every year that has data for the chosen round is compared automatically,
  so there is no `year` parameter.
- `GET /api/trend` — closing rank across rounds for one branch + category.
- `GET /api/universities` — reference list.
- `GET /api/branches?university=DTU` — reference list, optionally filtered.
- `GET /api/rounds` — reference list.

## Example
```
curl "http://localhost:8000/api/predict?rank=15000&category=GEN&applicant_gender=MALE&region=DELHI&round=5"
```

## Expected tables
`universities`, `campuses`, `branches`, `categories`, `quota_types`,
`gender_pools`, `home_regions`, `rounds`, `cutoffs` (column names as used in `queries.py`).
