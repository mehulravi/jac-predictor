# JAC Predictor

Predicts eligible JAC Delhi colleges and branches (DTU, NSUT, IIIT-Delhi, IGDTUW)
from a JEE rank and category, using the 2024 and 2025 cutoffs.

```
jac-predictor/
├── frontend/       React + Vite app (http://localhost:5173)
├── backend/        FastAPI + SQLite API (http://localhost:8000)
├── data/           source CSVs (cutoffs_unified.csv, branches_master.csv)
├── data-pipeline/  build_db.py (CSV -> SQLite) and the PDF extraction scripts
└── scripts/        smoke_test.py
```

## Run it on macOS (VS Code)

**1. Prerequisites** (skip what you already have)
```bash
brew install node python
node -v && python3 --version
```

**2. Unzip and open**
```bash
cd ~/Downloads
unzip jac-predictor-complete.zip
cd jac-predictor
code .
```

**3. Add the source data**, then build the database
```bash
cp /path/to/cutoffs_unified.csv /path/to/branches_master.csv data/

python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

python data-pipeline/build_db.py --expect 4046
python scripts/smoke_test.py --expect 4046
```
`build_db.py` stops without writing a database if any row is invalid or the
count is not 4,046, and prints what is wrong.

**4. Start the backend** (same terminal, venv active)
```bash
cd backend
uvicorn main:app --reload
```
API docs: http://localhost:8000/docs

**5. Start the frontend** (new terminal)
```bash
cd jac-predictor/frontend
cp .env.example .env
npm install
npm run dev
```
App: http://localhost:5173

In VS Code, pick the `.venv` interpreter (Cmd+Shift+P, "Python: Select Interpreter").

## Notes
- Regenerate the database any time with `python data-pipeline/build_db.py --expect 4046`.
- The Kashmiri Migrant and Sikkim/Goa quotas have no home region in the cutoff data, so
  the form disables Region for them and the API ignores it.
- The PDF extraction scripts in `data-pipeline/` need `jac_merged.pdf` in that folder
  (or `JAC_PDF_PATH`) and `pip install -r data-pipeline/requirements.txt`. They are only
  needed to re-extract from the PDFs; the database is built from the CSVs.
- Cutoffs are historical estimates, not guarantees.
