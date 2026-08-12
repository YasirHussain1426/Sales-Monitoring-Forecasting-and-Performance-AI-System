# System Architecture

## 1. Purpose

The AI Sales Monitoring, Forecasting & Performance System is a web application for recording sales transactions, monitoring performance against targets, producing forecasts, evaluating forecast accuracy, and generating business alerts.

This document describes the **current architecture observed in the repository** and the **target architectural direction** for subsequent sprints.

## 2. Current technology stack

### Frontend
- React
- Vite
- Tailwind CSS
- Axios
- React Router
- Recharts

### Backend
- Django
- Django REST Framework
- Simple JWT
- PostgreSQL
- WhiteNoise
- Gunicorn

### Domain applications
- `core` — authentication, current-user API, permissions, shared validation
- `sales` — regions, products, customers, salespeople, sales transactions, dashboard APIs
- `targets` — sales target definitions and target validation
- `forecasting` — historical aggregation, moving-average forecasts, weighted moving-average forecasts, forecast-vs-actual and forecast-vs-target calculations
- `alerts` — alert persistence and rules based on forecast/target and forecast-error conditions

### Delivery / CI
- GitHub Actions backend workflow
- GitHub Actions frontend workflow

## 3. Current logical architecture

```text
┌──────────────────────────────┐
│          React UI            │
│ Dashboard / Auth / Data UI   │
└──────────────┬───────────────┘
               │ HTTP + JWT
               ▼
┌──────────────────────────────┐
│     Django REST API          │
├──────────────────────────────┤
│ core                         │
│ sales                        │
│ targets                      │
│ forecasting                  │
│ alerts                       │
└──────────────┬───────────────┘
               │ ORM
               ▼
┌──────────────────────────────┐
│         PostgreSQL           │
│ sales / target / alert data  │
└──────────────────────────────┘
```

## 4. Request and domain flow

### Authentication

```text
Registration/Login
      ↓
JWT access + refresh tokens
      ↓
Authenticated API requests
```

### Sales

```text
Sales UI
   ↓
Sales API
   ↓
SalesTransaction
   ├── Customer
   ├── Product
   └── SalesPerson → Region
```

### Performance dashboard

```text
SalesTransaction
       ↓
Django ORM aggregations
       ↓
Revenue / transactions / quantity / AOV
       ↓
Trend / region / top-product APIs
       ↓
React charts and KPI cards
```

### Forecasting

```text
SalesTransaction
       ↓
Daily sales history
       ↓
Forecasting service
       ├── Moving Average
       └── Weighted Moving Average
       ↓
Forecast series
       ├── Forecast vs Actual
       └── Forecast vs Target
```

### Alerts

```text
Active SalesTarget
       ↓
Forecasting service
       ↓
Alert rules
       ├── Forecast target shortfall
       └── High forecast error / WAPE
       ↓
Alert persistence
```

## 5. Current strengths

1. Business domains have already been separated into Django applications.
2. Forecasting logic is mostly isolated in a service module instead of being embedded directly in API views.
3. Alert rules are separated into reusable service functions.
4. ORM aggregation is used for dashboard calculations.
5. Environment-based database configuration and JWT authentication are already present.
6. Backend and frontend have separate CI workflows.

## 6. Current architectural risks

### P0 — Security and authorization

- Public registration currently performs demo-data initialization when the sales table is empty.
- Transaction writes are available to any authenticated user rather than a clearly defined role model.
- The reviewed domain model has no explicit company/tenant ownership boundary.
- Query-string filters must never be treated as authorization boundaries.

### P1 — Data integrity

- Transaction financial totals should be derived server-side.
- Target overlap/conflict rules are not enforced at the database level.
- Target foreign keys currently use cascading deletion.
- API serializers expose `fields = "__all__"`, creating an overly implicit API contract.

### P1 — Forecasting correctness

- Daily history is based on transaction dates only, so dates with zero sales disappear.
- Forecasting currently represents baseline statistical methods rather than a validated multi-model forecasting engine.
- Current-day and future-day forecast semantics need to be explicitly defined.

### P1/P2 — Engineering quality

- Backend CI currently performs Django checks but does not execute the test suite.
- Frontend CI builds the app but does not run the existing lint script.
- Production configuration contains development fallbacks such as an insecure default secret key.

## 7. Target architecture

The target architecture should remain modular while adding explicit security and domain boundaries:

```text
                         ┌──────────────────────┐
                         │     React Frontend   │
                         └──────────┬───────────┘
                                    │ HTTPS + JWT
                                    ▼
                         ┌──────────────────────┐
                         │   API / Auth Layer   │
                         └──────────┬───────────┘
                                    │
               ┌────────────────────┼────────────────────┐
               │                    │                    │
               ▼                    ▼                    ▼
        Authorization          Validation          API contracts
               │                    │                    │
               └────────────────────┼────────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │    Domain Services   │
                         ├──────────────────────┤
                         │ Sales                │
                         │ Targets              │
                         │ Forecasting          │
                         │ Alerts               │
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  ▼                 ▼                 ▼
             PostgreSQL       Analytics/ML       Background jobs
                                  layer             (when required)
```

## 8. Target security model

The application should move toward an explicit authorization model:

```text
Company / Tenant
      │
      ├── Admin
      ├── Manager
      ├── Salesperson
      └── Viewer / Analyst
```

Access should be enforced at two levels:

1. **Permission level** — whether the role may perform the action.
2. **Queryset/service level** — which company/team/region/records the user may access.

Filtering parameters such as `region`, `product`, or `salesperson` must only narrow an already-authorized queryset.

## 9. Target forecasting architecture

Forecasting should evolve from a single-baseline implementation into a model evaluation pipeline:

```text
Sales Data
   ↓
Calendar-aligned time series
   ↓
Feature / decomposition layer
   ↓
Candidate models
   ├── Naive baseline
   ├── Moving Average
   ├── Weighted Moving Average
   ├── Exponential Smoothing
   └── ML model(s) when justified
   ↓
Backtesting / evaluation
   ├── WAPE
   ├── MAE
   ├── RMSE
   └── Bias
   ↓
Best model for scope / dataset
   ↓
Forecast
   ↓
Target comparison + alerts
```

No advanced ML model should be introduced until the baseline data alignment and evaluation pipeline are trustworthy.

## 10. Data ownership principles

The following should become invariants:

- Financial/business calculations are server-authoritative.
- Historical business records are not silently deleted by reference-object deletion.
- Database constraints enforce invariants where practical.
- API serializers expose explicit fields.
- Historical transaction prices remain immutable snapshots of the transaction, even when product catalog pricing changes.

## 11. CI/CD direction

### Backend pipeline

```text
Install
  ↓
Django checks
  ↓
Migrations/checks
  ↓
Unit + API + domain tests
  ↓
Coverage / quality gates
```

### Frontend pipeline

```text
Install
  ↓
Lint
  ↓
Tests
  ↓
Production build
```

## 12. Architectural decision rules for future work

1. Fix P0 security issues before adding new business features.
2. Do not add advanced AI before the data/forecasting baseline is correct.
3. Prefer domain services over large API views.
4. Prefer explicit API contracts over `fields = "__all__"`.
5. Enforce critical invariants in the database as well as application validation.
6. Every bug fix should include a regression test when practical.
7. Every schema change must include a reviewed migration.
8. Production behavior must never depend on development-only fallbacks.
9. Changes should be developed on branches and merged through pull requests.
10. `main` should remain releasable.

## 13. Sprint ownership

Sprint 0 establishes this document as the baseline. Sprint 1 will address authentication, authorization, registration behavior, and the data-ownership model before further feature expansion.
