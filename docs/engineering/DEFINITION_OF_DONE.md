# Definition of Done

## Purpose
This document defines the minimum quality bar for changes to the AI Sales Monitoring, Forecasting & Performance System.

## Code
- The change has a clear requirement and acceptance criteria.
- Code follows the existing project structure and naming conventions.
- Business logic is kept out of presentation code where practical.
- No secrets, credentials, or environment-specific values are committed.
- API contracts are explicit and intentional.

## Security
- Authentication and authorization are enforced at the correct boundary.
- Object/queryset access cannot bypass ownership or role restrictions.
- User-controlled input is validated server-side.
- Production configuration does not rely on insecure development fallbacks.

## Data integrity
- Financial/business calculations are server-authoritative.
- Database constraints are used where they can enforce invariants.
- Delete behavior is intentional for historical business data.
- Migrations are included and reviewed for schema changes.

## Testing
- New business logic has automated tests.
- Bugs fixed by code have regression tests where practical.
- API permission behavior is tested.
- Forecasting changes include time-series edge cases and metric validation.

## CI
- Backend checks and tests pass.
- Frontend lint/build/tests, where configured, pass.
- No known failing checks are ignored without a documented reason.

## Review
- The change is implemented on a feature/fix branch.
- A pull request describes the problem, solution, testing, and risk.
- Review feedback is addressed before merge.
- `main` remains releasable.

## Release readiness
- Documentation is updated when behavior or architecture changes.
- Configuration/environment requirements are documented.
- Observability/logging implications are considered for production changes.
