# System Architecture

## 1. Purpose

The AI Sales Monitoring, Forecasting & Performance System is a web application for recording sales transactions, monitoring performance against targets, producing forecasts, evaluating forecast accuracy, and generating business alerts.

This project is intentionally designed as a **single-company enterprise-style application** for a resume/portfolio. We will demonstrate strong authentication, role-based authorization, domain separation, data integrity, forecasting, testing, and CI without adding unnecessary multi-tenant SaaS complexity.

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
│ forecasting                  │
│ targets                      │
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
SalesTarget
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

1. Business domains are already separated into Django applications.
2. Forecasting logic is mostly isolated in a service module instead of being embedded directly in API views.
3. Alert rules are separated into reusable service functions.
4. ORM aggregation is used for dashboard calculations.
5. Environment-based database configuration and JWT authentication are already present.
6. Backend and frontend have separate CI workflows.

## 6. Current architectural risks

### P0 — Security and authorization

- Public registration currently performs demo-data initialization when the sales table is empty.
- Transaction writes are available to any authenticated user rather than a clearly defined role model.
- Authorization currently relies heavily on Django `is_staff`/`is_superuser` instead of application roles.
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

The target architecture remains modular and single-company:

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
          Role checks          Validation          API contracts
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
                    ┌───────────────┴──────────────┐
                    ▼                              ▼
               PostgreSQL                    Analytics/ML
```

## 8. Role-based authorization model

The application uses a single-company role model:

```text
Company
  │
  ├── Company Admin
  ├── Sales Manager
  ├── Salesperson
  └── Analyst
```

### Company Admin

- Full access to company data and administration.
- Manage users/roles.
- Manage master data and sales records.
- Manage targets and alert configuration.

### Sales Manager

- View sales and performance data within authorized operational scope.
- Manage appropriate sales records and targets according to business rules.
- Review forecasts and alerts.

### Salesperson

- View their permitted sales activity.
- Create sales activity where permitted.
- Cannot modify unrelated users' data or administrative configuration.

### Analyst

- Read-only access to sales analytics, forecasts, targets, and alerts.
- No destructive business-data operations.

The exact permission matrix is defined in Sprint 1 implementation and tests.

## 9. Authorization principles

Authorization has two independent layers:

1. **Action authorization** — whether a role may perform the operation.
2. **Object/queryset authorization** — which records the role may access.

Filtering parameters such as `region`, `product`, or `salesperson` may narrow an already-authorized queryset, but may never expand access.

The backend is the security source of truth. React route guards exist only for user experience and must not be relied upon for security.

## 10. Target forecasting architecture

Forecasting should evolve from baseline methods into a model evaluation pipeline:

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
Best model for the dataset/scope
   ↓
Forecast
   ↓
Target comparison + alerts
```

No advanced ML model should be introduced until the baseline data alignment and evaluation pipeline are trustworthy.

## 11. Data integrity principles

The following should become invariants:

- Financial/business calculations are server-authoritative.
- Historical business records are not silently deleted by reference-object deletion.
- Database constraints enforce invariants where practical.
- API serializers expose explicit fields.
- Historical transaction prices remain immutable snapshots of the transaction, even when product catalog pricing changes.

## 12. CI/CD direction

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

## 13. Resume-focused engineering goals

The project should clearly demonstrate professional software-engineering capabilities without artificial complexity:

- Django REST API architecture.
- JWT authentication.
- Role-based authorization.
- ORM/query optimization.
- Financial data integrity.
- Service-layer business logic.
- Time-series forecasting.
- Forecast evaluation with measurable metrics.
- Automated business alerts.
- Automated tests.
- GitHub Actions CI.
- Git-based branching and pull-request workflow.
- Production configuration awareness.

## 14. Architectural decision rules

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

## 15. Sprint ownership

Sprint 0 established the architecture baseline. Sprint 1 implements authentication, role-based authorization, secure registration, and permission tests. Later sprints will address data integrity, forecasting quality, alerts, and production readiness.
