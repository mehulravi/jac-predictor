# Source data

Put the two CSV files here, then build the database (see the root README):

- `cutoffs_unified.csv`  (required, 4,046 rows: DTU, NSUT, IGDTUW, IIIT-D, 2024 and 2025)
- `branches_master.csv`  (optional, only used for branch names)

`data-pipeline/build_db.py` reads them and writes `backend/jac_predictor.db`.
