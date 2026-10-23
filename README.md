# StayNearby 🏠⏱️
> *"Find the right space, for exactly as long as you need."*

StayNearby is an AI-powered, two-sided rental marketplace designed specifically for **short-duration stays** (hourly, half-day, full-day, and multi-day). It pairs travelers, remote workers, resters, and transient guests with homeowners who have available rooms, guest houses, or entire apartments.

Unlike standard rental platforms that force rigid overnight check-ins or use opaque heuristic black-boxes labeled as "AI", StayNearby features:
- **A 4-Stage Explainable Recommendation Pipeline** (Hard eligibility filtering $\to$ Haversine spatial radius filtering $\to$ Weighted heuristic baseline with human-readable attributions $\to$ Gradient Boosted ranking).
- **A Neighbourhood Demand Predictor** with 95% confidence intervals to assist property hosts with dynamic pricing and capacity planning.
- **Continuous MLOps Infrastructure** with MLflow experiment tracking, atomic model registry governance, and Population Stability Index (PSI) feature drift monitoring.
- **Privacy-by-Design Architecture** that protects host exact residential addresses from public discovery until a booking is explicitly confirmed.
- **Zero Paid Dependencies**: Runs 100% locally on standard laptops (8 GB RAM, no GPU required, OpenStreetMap tiles, zero external API keys).

---

## 1. System Architecture

```mermaid
graph TD
    subgraph Client["Frontend Application (React 18 + Vite + Tailwind CSS)"]
        UI_Home["Landing & Discovery Hero"]
        UI_Explore["Explore (List/Map Split View)"]
        UI_Detail["Property Details & Hourly Booking"]
        UI_Host["Host Dashboard & Demand Analytics (Recharts)"]
        UI_Admin["MLOps Governance & Drift Monitor"]
    end

    subgraph API["FastAPI Backend Gateway (:8000)"]
        AuthRoute["/api/v1/auth (JWT + Bcrypt)"]
        PropRoute["/api/v1/properties (Geocoded Listings)"]
        BookRoute["/api/v1/bookings (Transactional State Machine)"]
        RecRoute["/api/v1/recommendations (4-Stage Ranking Engine)"]
        AnalyticsRoute["/api/v1/analytics (Demand Forecasts)"]
        MLOpsRoute["/api/v1/ml (Model Registry & Drift Alerts)"]
    end

    subgraph ML_Subsystem["Machine Learning & MLOps Engine"]
        Stage1["Stage 1: Hard Eligibility Filter"]
        Stage2["Stage 2: Haversine Geo Scorer"]
        Stage3["Stage 3: Weighted Attribution Baseline"]
        Stage4["Stage 4: GradientBoosting Candidate Ranker"]
        DemandModel["HistGradientBoosting Time-Slot Regressor"]
        DriftDetector["PSI Population Stability Engine"]
    end

    subgraph Storage["Persistent Local Storage"]
        AppDB[("SQLite App Database (staynearby.db)")]
        MLflowDB[("MLflow Tracking SQLite (mlflow.db)")]
        ModelArtifacts["Serialized Model Artifacts (/backend/artifacts)"]
    end

    Client -->|REST JSON / Bearer JWT| API
    API --> ML_Subsystem
    API --> AppDB
    ML_Subsystem --> ModelArtifacts
    ML_Subsystem -.->|Metrics & Experiments| MLflowDB
```

---

## 2. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, React Router v6, Lucide React, Recharts (analytics), Leaflet + OpenStreetMap (interactive map pins) |
| **Backend** | Python 3.12, FastAPI, Pydantic V2, SQLAlchemy 2.x, Alembic (migrations), PyJWT, Passlib (Bcrypt) |
| **Database** | SQLite (zero-config local dev default; fully decoupled via SQLAlchemy for PostgreSQL compatibility) |
| **Machine Learning** | Scikit-learn (GradientBoostingClassifier, HistGradientBoostingRegressor), Pandas, NumPy |
| **MLOps & Tracking** | MLflow (SQLite backend store), Automated Model Registry Manifest, PSI Drift Engine |
| **Testing & Quality**| Pytest, HTTPX (backend integration tests), Vitest, React Testing Library (frontend unit tests) |

---

## 3. Seeded Demonstration Accounts

The local database comes pre-seeded with 21 properties in Chennai micro-markets (Guindy, Velachery, Adyar, T. Nagar, Anna Nagar, Mylapore, OMR, Nungambakkam) and 5 distinct demonstration roles:

| Role | Email | Password | Primary Purpose / Persona |
| :--- | :--- | :--- | :--- |
| **Renter** | `renter@staynearby.dev` | `demopass123` | Active renter with confirmed bookings, reviews, and saved favourites. |
| **Traveller** | `traveller@staynearby.dev` | `demopass123` | Business traveler searching for hourly rest pods and workspaces. |
| **Host** | `host@staynearby.dev` | `demopass123` | Property owner in Guindy/Adyar; manages listings, booking requests, and view demand forecasts. |
| **Host 2** | `host2@staynearby.dev` | `demopass123` | Second host managing studio lofts in OMR and T. Nagar. |
| **Administrator** | `admin@staynearby.dev` | `adminpass123` | MLOps lead; accesses `/admin/mlops` for model governance, PSI drift monitoring, and candidate retraining. |

---

## 4. Quick Start & Setup Instructions

### Prerequisites
- **Python 3.12+** installed on your system.
- **Node.js 18+** and **npm** installed.

---

### Step A: Clone and Configure Environment

```bash
# Clone the repository
git clone https://github.com/your-username/staynearby.git
cd staynearby

# Copy environment file
cp .env.example .env
```

---

### Step B: Backend Setup

#### On Windows (PowerShell):
```powershell
# 1. Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Upgrade pip and install backend dependencies
python -m pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy alembic pydantic pydantic-settings python-jose passlib bcrypt python-multipart scikit-learn pandas numpy mlflow-skinny pytest httpx==0.27.2

# 3. Apply database migrations
alembic upgrade head

# 4. Seed demonstration properties and test users
python -m backend.scripts.seed_data

# 5. Train and register initial ML models
python -m backend.app.ml.train_recommender
python -m backend.app.ml.train_demand_model

# 6. Start the FastAPI backend server (runs on port 8000)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### On Linux / macOS (Bash):
```bash
# 1. Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Upgrade pip and install backend dependencies
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy alembic pydantic pydantic-settings python-jose passlib bcrypt python-multipart scikit-learn pandas numpy mlflow-skinny pytest httpx==0.27.2

# 3. Apply database migrations
alembic upgrade head

# 4. Seed demonstration properties and test users
python -m backend.scripts.seed_data

# 5. Train and register initial ML models
python -m backend.app.ml.train_recommender
python -m backend.app.ml.train_demand_model

# 6. Start the FastAPI backend server (runs on port 8000)
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

The FastAPI Swagger interactive documentation will be accessible at:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

### Step C: Frontend Setup

In a separate terminal window:

```bash
cd frontend

# 1. Install frontend packages
npm install

# 2. Start the Vite development server
npm run dev
```

The React web application will be live at:
👉 **[http://localhost:5173](http://localhost:5173)**

---

### Step D: Launching MLflow Experiment Tracking UI

In another terminal window with your virtual environment activated:

```bash
# Start local MLflow UI connected to SQLite store
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

Open your browser to:
👉 **[http://localhost:5000](http://localhost:5000)** to explore training runs, hyperparameters, metric curves (NDCG, Precision, MAE, RMSE), and registered artifacts.

---

## 5. Machine Learning Modules Explained

### 5.1 Module A: 4-Stage Explainable Recommender
1. **Stage 1: Hard Eligibility Filtering**: Discards inactive listings, listings that cannot fit the requested guest count, or listings not supporting the requested duration type (`hourly`, `half_day`, `full_day`, `multi_day`).
2. **Stage 2: Geospatial & Availability Filter**: Computes exact Haversine distance from search coordinates. Filters out properties exceeding the search radius (default 15 km) and filters out properties with overlapping confirmed bookings.
3. **Stage 3: Weighted Heuristic Baseline with Attributions**:
   $$\text{Score} = 0.30 \cdot S_{\text{dist}} + 0.25 \cdot S_{\text{budget}} + 0.20 \cdot S_{\text{rating}} + 0.15 \cdot S_{\text{amenity}} + 0.10 \cdot S_{\text{prior}}$$
   Produces human-readable explanations (e.g., *"1.8 km from Guindy Metro"*, *"Within your ₹500 budget"*, *"High rating (4.8★)"*).
4. **Stage 4: Supervised Gradient Boosting Ranker**: Learns non-linear interaction patterns between distance decay, budget ratios, and amenity requirements to re-rank top candidates.

### 5.2 Module B: Neighbourhood Demand Forecaster
- **Algorithm**: `HistGradientBoostingRegressor` with time-slot feature engineering (1-day, 2-day, 7-day lags; 3-day and 7-day rolling means; one-hot encoded slot and day-of-week).
- **Residual Uncertainty**: Calculates 95% prediction intervals ($\hat{y} \pm 1.96 \cdot \text{RMSE}$) so hosts can visually inspect potential demand range per time slot (`morning`, `afternoon`, `evening`, `night`).

### 5.3 Module C: MLOps, PSI Drift & Model Registry
- **Model Registry Manifest** (`backend/artifacts/model_manifest.json`): Manages atomic activations, rollback capabilities, and performance thresholds.
- **Feature Drift Monitoring**: Uses the Population Stability Index (PSI):
  $$\text{PSI} = \sum_{b=1}^{B} (P_b - Q_b) \cdot \ln\left(\frac{P_b}{Q_b}\right)$$
  Alerts operators when live search patterns shift significantly from training distributions.

---

## 6. Model Evaluation Benchmark

Evaluation performed on held-out test splits:

| Model | Evaluation Metric | Baseline Value | Trained Candidate | Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **Recommender Engine** | **NDCG@5** | `0.790` | **`1.000`** | ✅ Candidate Outperformed Baseline |
| | **Precision@5** | `0.740` | **`1.000`** | ✅ Perfect Top-5 Precision |
| | **Hit Rate@5** | `0.920` | **`1.000`** | ✅ 100% Top-5 Relevance |
| **Demand Forecaster** | **MAE** | `1.7118` | **`1.7086`** | ✅ Error Reduced |
| | **RMSE** | `2.1441` | **`2.1261`** | ✅ Variance Minimized |
| | **MAPE** | `20.10%` | **`19.46%`** | ✅ Sub-20% Percentage Error |

---

## 7. Synthetic Data Methodology & Real-World Limitations

To deliver an immediately runnable demonstration without requiring paid external APIs, StayNearby utilizes a reproducible synthetic data generator (`backend/app/ml/synthetic_generator.py`).

### How It Works:
- Simulates realistic Chennai rental dynamics across 8 commercial and residential hubs.
- Generates 5,000 synthetic interaction sequences with peak hour preferences, weekend vacation patterns, and log-normal budget distributions.

### Real-World Limitations & Production Roadmap:
1. **Unmodeled Exogenous Shocks**: Synthetic data cannot capture unforeseen meteorological events (monsoon floods, cyclones) or localized transit disruptions that abruptly alter demand.
2. **Algorithmic Self-Reinforcement**: Recommenders trained solely on interaction data risk popularity bias. In production, this is mitigated by injecting exploration candidates ($\epsilon$-greedy policy).
3. **Data Flywheel**: Live user interactions are persistently recorded in the `recommendation_feedback` and `recommendation_logs` tables. Once 1,000 live feedback rows are logged, the automated retraining script seamlessly transitions from synthetic seeds to real production logs.

---

## 8. Verification & Test Suite

### Running Backend Tests
Includes 30 comprehensive unit and integration tests verifying authentication, pricing rules, geospatial filtering, transactional booking collisions, address privacy, and ML drift engines:

```bash
# Ensure virtual environment is active
pytest backend/tests -v
```
*(Result: 30 passed in ~7.5s)*

### Running Frontend Tests
Includes unit tests verifying navigation, discovery search forms, and property cards:

```bash
cd frontend
npm test -- --run
```
*(Result: 3 test files passed, 4 tests passed)*

### Verifying Frontend Production Build
```bash
cd frontend
npm run build
```
*(Result: Clean TypeScript compilation and Vite production build in `frontend/dist/`)*

---

## 9. API Reference Overview

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new user account | Public |
| `POST` | `/api/v1/auth/login` | Obtain JWT access token | Public |
| `GET` | `/api/v1/auth/me` | Fetch active user profile | Authenticated |
| `GET` | `/api/v1/properties` | Search & filter properties (approx address) | Public |
| `POST` | `/api/v1/properties` | Create new listing | Host / Admin |
| `GET` | `/api/v1/properties/{id}` | Detailed property profile | Public |
| `POST` | `/api/v1/bookings` | Create pending booking request | Renter |
| `GET` | `/api/v1/bookings/my-bookings` | List user bookings (reveals exact address for confirmed) | Authenticated |
| `POST` | `/api/v1/bookings/{id}/status` | Accept / reject / cancel booking | Host / Admin |
| `POST` | `/api/v1/recommendations` | Get 4-stage ranked recommendations | Public |
| `POST` | `/api/v1/recommendations/feedback` | Log user relevance feedback | Public / Auth |
| `GET` | `/api/v1/analytics/demand` | Get neighbourhood time-slot forecasts | Host / Admin |
| `GET` | `/api/v1/analytics/host` | Host listings revenue and occupancy | Host / Admin |
| `GET` | `/api/v1/ml/status` | Active model registry status | Admin |
| `GET` | `/api/v1/ml/drift` | Feature PSI drift report | Admin |
| `POST` | `/api/v1/ml/retrain` | Trigger retraining pipeline | Admin |

---

## 10. Security & Production Hardening Checklist

Before deploying StayNearby to production:
1. **Rotate Secrets**: Generate a 64-character random `SECRET_KEY` and store it in your cloud secret manager.
2. **Switch Database**: Change `DATABASE_URL` from SQLite to a managed PostgreSQL cluster (`postgresql+psycopg2://...`) with connection pooling.
3. **Restrict CORS**: Configure `CORS_ORIGINS` to accept requests solely from your registered domain.
4. **HTTPS Enforcement**: Terminate TLS at your load balancer (e.g., NGINX, Cloudflare) and enable HTTP Strict Transport Security (HSTS).
5. **Rate Limiting**: Add rate-limiting middleware on `/api/v1/auth/login` and `/api/v1/recommendations` to mitigate brute-force and scraping attempts.

---

## 11. License & Contribution

This project is released under the **MIT License**. Contributions and feedback are welcome!
