# DEPARTMENT OF INFORMATION TECHNOLOGY
## MADRAS INSTITUTE OF TECHNOLOGY
### ANNA UNIVERSITY

---

# STAYNEARBY: AI-POWERED SHORT-DURATION HOME RENTAL MARKETPLACE WITH MLOPS

### MLOPS PROJECT (AD23701) — AI&DS — SEMESTER 7

**TEAM MEMBERS:**
- Mohamed Nabil Hussain Z — 2023510001
- Arun Sankar M — 2023510033

---

## 1. AIM
The aim of this project is to develop **StayNearby**, an AI-powered two-sided short-duration rental marketplace that connects property owners with guests needing flexible accommodations for a few hours, a half day, or a full day. The system overcomes the rigidity and latency of traditional hospitality platforms by providing an explainable four-stage machine learning recommendation pipeline, neighbourhood demand forecasting with uncertainty quantification, and an automated MLOps continuous monitoring infrastructure.

---

## 2. DATASET USED
The system utilizes a realistic multi-modal dataset specifically modeled after Chennai's urban residential and commercial micro-markets:
- **Property Listings Dataset:** 21 verified seed properties across 8 key Chennai neighbourhoods (Guindy, Velachery, Adyar, T. Nagar, Anna Nagar, Mylapore, OMR, and Nungambakkam) featuring precise geospatial coordinates, tiered pricing structures (hourly, half-day, full-day), multi-category amenities, and verified guest capacities.
- **Renter Interaction Dataset:** 5,000 synthetic guest search queries, impressions, click-through records, and booking events with realistic price-sensitivity distributions and time-of-day demand preferences.
- **Time-Series Neighbourhood Demand Dataset:** 2,920 longitudinal observations covering four time slots per day (Morning, Afternoon, Evening, Night) over two years, incorporating seasonal and weekly cyclical demand patterns.

---

## 3. TECHNIQUES USED

### Geospatial Distance Computation
The system implements the great-circle Haversine formula to compute geodesic distances between user search coordinates and property coordinates. Out-of-radius listings (beyond the user-specified threshold, default 15 km) are pruned before scoring.

### Four-Stage Explainable Recommender
The recommendation pipeline operates through four progressive stages:
1. **Stage 1 (Hard Eligibility Filtering):** Filters for active listings, guest capacity, and supported duration types.
2. **Stage 2 (Geospatial & Availability Filtering):** Prunes listings beyond radius and checks database locks to eliminate properties with overlapping confirmed reservations.
3. **Stage 3 (Weighted Heuristic Baseline):** Computes multi-factor heuristic attributions across distance decay (30%), budget fit (25%), Bayesian rating (20%), Jaccard amenity overlap (15%), and prior user engagement (10%).
4. **Stage 4 (Supervised Candidate Re-Ranking):** Evaluates candidate feature vectors using a calibrated `GradientBoostingClassifier` to re-rank top candidates while blending transparent attribution tags.

### Time-Slot Demand Forecasting
Neighbourhood demand is predicted using a `HistGradientBoostingRegressor` trained on lagged historical bookings (1-day, 2-day, 7-day lags), 3-day and 7-day rolling means, and calendar encodings. The model outputs a point prediction accompanied by a 95% confidence interval derived from residual variance ($\hat{y} \pm 1.96 \cdot \text{RMSE}$).

### Population Stability Index (PSI) Drift Monitoring
To ensure production stability, real-time feature distributions (travel distance, budget ratios) are continuously compared against baseline distributions using the Population Stability Index. Alerts are triggered when $\text{PSI} > 0.25$.

---

## 4. TOOLS USED

| Tool / Technology | Purpose in the Project |
| :--- | :--- |
| **Python 3.12** | Core language for backend API, machine learning pipelines, and data processing. |
| **FastAPI & Uvicorn** | High-performance asynchronous REST API framework and ASGI web server. |
| **Scikit-learn** | Implementation of `GradientBoostingClassifier` and `HistGradientBoostingRegressor`. |
| **Pandas & NumPy** | Data transformation, feature engineering, rolling window calculations, and metric computation. |
| **MLflow** | Experiment tracking, metric logging (NDCG@5, RMSE), and model artifact management. |
| **SQLAlchemy 2.0 & Alembic** | Declarative ORM, transactional concurrency management, and relational database migrations. |
| **React 18 & Vite** | Frontend Single Page Application (SPA) offering reactive user interfaces. |
| **Leaflet & OpenStreetMap** | Interactive map interface with geospatial coordinate markers and dynamic listing highlighting. |
| **Recharts** | Data visualization for host demand predictions and multi-slot confidence interval analytics. |
| **Pytest & Vitest** | Comprehensive automated testing for backend API routes, ML pipelines, and frontend components. |
| **Docker & Docker Compose** | Multi-stage containerization, dependency packaging, and single-service cloud deployment. |

---

## 5. ARCHITECTURE

### High-Level System Architecture
```text
+-----------------------------------------------------------------------------------+
|               REACT 18 + VITE FRONTEND (Tailwind CSS, Leaflet, Recharts)          |
|  [Search / Discovery]     [Map/List View]     [Host Dashboard]    [MLOps Console] |
+-----------------------------------------------------------------------------------+
                                          |  HTTPS / REST JSON
                                          v
+-----------------------------------------------------------------------------------+
|                           FASTAPI BACKEND GATEWAY (:8000)                         |
|  /auth (JWT)  |  /properties  |  /bookings (ACID)  |  /recommendations  |  /ml    |
+-----------------------------------------------------------------------------------+
                                          |
          +-------------------------------+-------------------------------+
          |                                                               |
          v                                                               v
+-----------------------------------+             +---------------------------------+
|       ML INFERENCE ENGINE         |             |       PERSISTENT STORAGE        |
|  - Stage 1: Eligibility Pruning   |             |  - SQLite / PostgreSQL DB       |
|  - Stage 2: Haversine Geo Filter  |             |    (staynearby.db)              |
|  - Stage 3: Weighted Heuristic    |             |  - MLflow SQLite Registry       |
|  - Stage 4: GradientBoost Ranker  |             |    (mlflow.db)                  |
|  - Demand Forecaster (HistGBM)    |             |  - Serialized Artifacts         |
|  - PSI Feature Drift Monitor      |             |    (/backend/artifacts)         |
+-----------------------------------+             +---------------------------------+
```

### Recommendation Flowchart
```text
User Search Query ---> [Stage 1: Hard Filter] ---> [Stage 2: Geo Haversine] ---> [Stage 3: Heuristic]
 (Location, Date,       (Capacity, Duration,        (Distance <= Radius,           (Bayesian Rating,
  Budget, Guests)        Active Status)              No Booking Clash)              Budget, Amenities)
                                                                                            |
                                                                                            v
Top-K Ranked Listings <--- [Explainable Output] <--- [Stage 4: GradientBoosting Ranker]
(With Match Tags &         (Attribution Tags:
 Confidence Score)          "1.8km away", "4.8★")
```

---

## 6. METHODOLOGY

1. **Step 1: Ingest User Request and Resolve Geospatial Coordinates:** The client transmits search parameters including target neighbourhood/coordinates, duration type (hourly, half-day, full-day), budget constraint, guest count, and required amenities.
2. **Step 2: Stage 1 Eligibility & Booking Collision Check:** The backend queries properties filtered by active status and capacity. A subquery checks the bookings database to eliminate properties with overlapping confirmed reservations during the target window.
3. **Step 3: Stage 2 Geospatial Distance Pruning:** Geodesic Haversine distances are computed dynamically between target coordinates and property coordinates. Listings beyond the specified search radius are pruned.
4. **Step 4: Stage 3 Multi-Factor Heuristic Attribution:** Remaining candidates are scored across distance decay (30%), budget fit (25%), Bayesian rating (20%), amenity Jaccard similarity (15%), and prior user engagement (10%). Human-readable explanations are generated.
5. **Step 5: Stage 4 Gradient Boosted Re-Ranking:** Feature vectors are passed to the trained `GradientBoostingClassifier`. Calibrated probabilities re-rank top candidates while blending explainable feature tags.
6. **Step 6: Neighbourhood Demand Forecasting & Variance Quantification:** For host queries, the `HistGradientBoostingRegressor` predicts expected booking request volume across time slots and attaches a 95% confidence interval ($\hat{y} \pm 1.96 \cdot \text{RMSE}$).
7. **Step 7: Real-Time PSI Drift Evaluation and Model Governance:** Inference logs are evaluated against training reference distributions to ensure zero distribution drift. The model registry allows administrators to activate or roll back models with one click.
8. **Step 8: Client Delivery & Address Privacy Shielding:** The API returns structured results hiding the exact residential address until a booking is confirmed.

---

## 7. OUTPUT EXPECTED
- A ranked list of candidate properties personalized to user coordinates, budget, and duration type.
- Transparent attribution tags accompanying each recommendation (e.g., *"Within 2.1 km"*, *"Within ₹500 budget"*).
- Dynamic hourly and daily price calculations computed server-side with zero pricing discrepancies.
- Host analytics visualization displaying predicted demand scores and booking volumes with 95% confidence bounds.
- Administrative MLOps telemetry reporting active model versions, NDCG/MAE metrics, and feature PSI drift levels.

---

## 8. ILLUSTRATIVE API RESPONSE

```json
{
  "count": 1,
  "total_eligible_candidates": 4,
  "inference_time_ms": 2.45,
  "model_name": "recommender",
  "model_version": "v202610232031",
  "model_type": "gradient_boosting",
  "results": [
    {
      "property": {
        "id": 1,
        "title": "Quiet Workspace & Day Room",
        "neighbourhood": "Guindy",
        "price_per_hour": 350.0,
        "average_rating": 4.85,
        "address_approx": "Near Guindy Metro Station, Chennai"
      },
      "ml_rank_score": 0.9421,
      "distance_km": 1.84,
      "estimated_total_price": 700.0,
      "explanation_attributions": [
        "Within 1.8 km of your search location",
        "Well within your ₹500/hr budget",
        "High rating: 4.85★ with 18 reviews",
        "Features Fast Wi-Fi and Air Conditioning"
      ]
    }
  ]
}
```

---

## 9. MODEL EVALUATION BENCHMARKS

| Module | Metric | Baseline Heuristic | Trained Candidate | Operational Status |
| :--- | :--- | :--- | :--- | :--- |
| **Recommender Engine** | **NDCG@5** | 0.7900 | **1.0000** | **ACTIVE (Promoted)** |
| | **Precision@5** | 0.7400 | **1.0000** | **ACTIVE (Promoted)** |
| | **Hit Rate@5** | 0.9200 | **1.0000** | **ACTIVE (Promoted)** |
| **Demand Forecaster** | **MAE** | 1.7118 | **1.7086** | **ACTIVE (Promoted)** |
| | **RMSE** | 2.1441 | **2.1261** | **ACTIVE (Promoted)** |
| | **MAPE** | 20.10% | **19.46%** | **ACTIVE (Promoted)** |

### Automated Verification Suite
- **Backend Tests (Pytest):** **30 of 30 tests passed** covering authentication, geospatial Haversine logic, ACID booking conflict prevention, address masking, and PSI drift algorithms.
- **Frontend Tests (Vitest):** **4 of 4 tests passed** verifying component rendering, search forms, and navigation.

---

## 10. CONCLUSION
The **StayNearby** AI-Powered Short-Duration Home Rental Marketplace successfully implements an industrial-grade, full-stack rental platform specifically tailored for short-duration stays. By seamlessly integrating an explainable four-stage machine learning recommender, a neighbourhood time-slot demand predictor with residual uncertainty intervals, and continuous MLOps governance into a responsive web application, the system demonstrates that modern AI marketplace solutions can be both highly accurate and transparent.

The platform enforces strict privacy-by-design principles to protect host residential addresses while providing host dynamic pricing insights. With zero paid external dependencies and full local runnability, the application serves as a comprehensive, production-ready capstone project that meets all functional and architectural specifications.
