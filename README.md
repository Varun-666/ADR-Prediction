# ADR Prediction System

Predicts Hotel Average Daily Rate (ADR) from booking details using a trained
Random Forest Regressor (Test R² = 0.868, MAE = 10.10, RMSE = 18.58).

## Project structure

```
ADR_Prediction/
├── app/
│   ├── main.py           # FastAPI routes (/, /predict, /health)
│   ├── predictor.py       # Feature engineering + model inference
│   ├── schemas.py         # Pydantic request/response models
│   ├── templates/
│   │   └── index.html     # Booking form + prediction UI
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/script.js
│   └── model/
│       └── ADR_Prediction_Model.pkl   # NOT included in this zip — see below
├── requirements.txt
├── render.yaml
└── .gitignore
```

## ⚠️ The model file (461 MB) is not committed to git

`ADR_Prediction_Model.pkl` is too large for a normal GitHub push (100 MB
limit) and would also blow past GitHub's free **Git LFS** quota (1 GB
storage / 1 GB bandwidth per month). So instead, the app downloads the
model at startup from a URL you host it at, and `app/model/*.pkl` is
gitignored.

### 1. Host the model as a GitHub Release asset (free, no quota issues)

GitHub Releases allow files up to 2 GB each and aren't subject to the LFS
storage/bandwidth quota — completely separate system.

1. On GitHub, go to your repo → **Releases** → **Draft a new release**.
2. Give it any tag (e.g. `v1.0-model`), then drag `ADR_Prediction_Model.pkl`
   into the asset upload area.
3. Publish the release. Right-click the uploaded asset link and copy its
   URL — it'll look like:
   ```
   https://github.com/<you>/<repo>/releases/download/v1.0-model/ADR_Prediction_Model.pkl
   ```

### 2. Point the app at it

- **Locally:** either drop the `.pkl` straight into `app/model/` (simplest
  for dev), or set an env var:
  ```bash
  export MODEL_URL="https://github.com/<you>/<repo>/releases/download/v1.0-model/ADR_Prediction_Model.pkl"
  uvicorn app.main:app --reload
  ```
- **On Render:** in the service's dashboard under **Environment**, add
  `MODEL_URL` with that same value (already stubbed in `render.yaml` as
  `sync: false`, meaning Render will prompt you to fill it in).

On startup, `predictor.py` checks for the file locally first; if it's
missing, it downloads it from `MODEL_URL` before the first prediction.

### Alternatives, if you'd rather not use GitHub Releases

- **Hugging Face Hub** — free, purpose-built for hosting ML model files,
  effectively unlimited for public repos.
- **Shrink the model** — a Random Forest this large usually has more trees
  or depth than needed. Reducing `n_estimators`/`max_depth` and re-saving
  with `joblib.dump(model, path, compress=3)` can bring it under 100 MB
  with little accuracy loss, letting you commit it directly to git.

## Local development

```bash
cd ADR_Prediction
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/` for the UI, or `http://127.0.0.1:8000/docs`
for the interactive API docs.

## API

### `POST /predict`

Accepts a JSON body of raw booking fields (see `app/schemas.py` for the
full list and allowed category values) and returns:

```json
{
  "predicted_adr": 166.78,
  "currency_note": "...",
  "season": "Summer",
  "total_guests": 3,
  "total_nights": 5
}
```

Feature engineering (`season`, `total_guests`, `total_nights`, `is_family`,
`customer_history`, `weekend_stay`, `long_stay`) is computed server-side in
`predictor.py` from the raw fields — the client only ever sends raw booking
data.

### `GET /health`

Liveness check used by `render.yaml`'s `healthCheckPath`.

## Deploying to Render

1. Push this repo to GitHub (see the Git LFS note above).
2. In Render, create a new **Web Service** from the repo — `render.yaml`
   will be picked up automatically (Blueprint), or configure manually:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Confirm the model file is present in the deployed filesystem before
   the first request (Render's free tier spins down on idle, so the first
   request after a cold start will take longer while the model loads).

## Notes

- `requirements.txt` pins `scikit-learn==1.7.2` to match the version the
  model was trained/pickled with. Unpickling with a different sklearn
  version works but logs `InconsistentVersionWarning` and carries a small
  risk of subtly different behavior — keep this pin unless you retrain.
- ADR values are in the same currency/unit as the original Hotel Booking
  Demand dataset (EUR).
