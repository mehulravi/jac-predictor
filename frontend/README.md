# JAC Predictor — Frontend

## Setup
```
npm install
cp .env.example .env   # edit if your backend runs somewhere other than localhost:8000
npm run dev
```

Opens at http://localhost:5173. Requires the backend (see ../backend) to be
running for the form to return results.

## Build for production
```
npm run build
```
Outputs static files to `dist/`.

## Structure
- `src/App.jsx` — layout, header, top-level state (idle/loading/success/error)
- `src/PredictorForm.jsx` — rank/category/gender/region/quota/round inputs
- `src/ResultsList.jsx` — renders eligible branches with Safe/Moderate/Tough stamps
- `src/api.js` — fetch wrapper around the FastAPI backend
- `src/index.css` — design tokens (color/type) and global resets
- `src/App.css` — component styles
