# StayNearby System Architecture

## 1. High-Level Architecture Overview

StayNearby is architectured as a decoupled, multi-tier web application built for high responsiveness, privacy-first property discovery, and explainable machine learning inference.

```mermaid
graph TD
    subgraph Client["Frontend (React 18 + Vite + Tailwind CSS)"]
        UI_Home["Landing & Discovery Hero"]
        UI_Explore["Explore (List/Map Split View)"]
        UI_Detail["Property Details & Booking"]
        UI_Host["Host Dashboard & Demand Analytics"]
        UI_Admin["MLOps Model Governance"]
    end

    subgraph API["FastAPI Application Gateway (:8000)"]
        AuthRoute["/api/v1/auth (JWT + Bcrypt)"]
        PropRoute["/api/v1/properties (Geocoded Listings)"]
        BookRoute["/api/v1/bookings (Transactional State Machine)"]
        RecRoute["/api/v1/recommendations (4-Stage Ranking Engine)"]
        AnalyticsRoute["/api/v1/analytics (Demand Forecasts)"]
        MLOpsRoute["/api/v1/ml (Registry & Drift Monitor)"]
    end

    subgraph ML_Subsystem["ML & Inference Engine"]
        Stage1["Stage 1: Hard Eligibility Filter"]
        Stage2["Stage 2: Haversine Geo Scorer"]
        Stage3["Stage 3: Weighted Attribution Baseline"]
        Stage4["Stage 4: GradientBoosting Candidate Ranker"]
        DemandModel["HistGradientBoosting Time-Slot Regressor"]
        DriftDetector["PSI Population Stability Engine"]
    end

    subgraph Data_Storage["Persistent Storage"]
        AppDB[("SQLite App Database (staynearby.db)")]
        MLflowDB[("MLflow Tracking SQLite (mlflow.db)")]
        ModelArtifacts["Serialized Models (/artifacts)"]
    end

    Client -->|REST / JSON| API
    API --> ML_Subsystem
    API --> AppDB
    ML_Subsystem --> ModelArtifacts
    ML_Subsystem -.->|Experiments & Metrics| MLflowDB
```

---

## 2. Relational Entity-Relationship Model

```mermaid
erDiagram
    USERS ||--o{ PROPERTIES : "hosts"
    USERS ||--o{ BOOKINGS : "books"
    USERS ||--o{ REVIEWS : "writes"
    USERS ||--o{ FAVOURITES : "saves"
    USERS ||--o{ RECOMMENDATION_FEEDBACK : "provides"
    PROPERTIES ||--o{ BOOKINGS : "receives"
    PROPERTIES ||--o{ REVIEWS : "receives"
    PROPERTIES ||--o{ AVAILABILITY_SLOTS : "defines"
    BOOKINGS ||--o| REVIEWS : "evaluated_by"

    USERS {
        int id PK
        string email UK
        string hashed_password
        string full_name
        string role "renter | host | admin"
        string phone
        datetime created_at
    }

    PROPERTIES {
        int id PK
        int host_id FK
        string title
        string description
        string property_type
        string neighbourhood
        string city
        string address_approx
        string address_exact
        float latitude
        float longitude
        float price_per_hour
        float price_per_half_day
        float price_per_full_day
        float cleaning_fee
        int max_guests
        json amenities
        json supported_durations
        boolean is_active
        float average_rating
        int review_count
    }

    BOOKINGS {
        int id PK
        int renter_id FK
        int property_id FK
        datetime start_datetime
        datetime end_datetime
        string duration_type
        int guest_count
        float base_price
        float cleaning_fee
        float total_price
        string status "pending | confirmed | rejected | cancelled | completed"
        string payment_status
        datetime created_at
    }

    REVIEWS {
        int id PK
        int booking_id FK,UK
        int property_id FK
        int renter_id FK
        int rating
        string comment
        datetime created_at
    }
```

---

## 3. Privacy & Security Architecture

1. **Host Exact Address Shielding:**
   - Public exploration and detail pages (`GET /api/v1/properties`) return strictly `address_approx` (e.g. *"Near Guindy Metro Station, Chennai"*).
   - The private column `address_exact` is excluded from standard responses.
   - Only a renter who possesses a **confirmed** booking (`status == 'confirmed'`) can access the exact physical address via `GET /api/v1/bookings/my-bookings`.

2. **Booking Transaction Concurrency:**
   - To prevent double bookings for the same property across overlapping time periods, booking requests check confirmed booking collisions within a transactional lock.
   - Pricing calculations are strictly enforced server-side via the database entity prices; client-provided prices are ignored.

3. **Authentication & Authorization:**
   - Passwords hashed using bcrypt.
   - JWT tokens signed with HS256 containing user ID, role, and expiration timestamp.
   - Role-based dependencies (`get_current_active_user`, `require_host_role`, `require_admin_role`) guard protected administrative and host modification endpoints.
