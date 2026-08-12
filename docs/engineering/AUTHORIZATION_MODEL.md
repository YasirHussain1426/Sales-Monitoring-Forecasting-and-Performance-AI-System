# Authorization Model

## Status
Sprint 1 design baseline. No application behavior is changed by this document.

## 1. Goal

Replace the current binary `admin vs authenticated user` model with explicit business roles and company-level data ownership.

The backend is the source of truth for authorization. Frontend route guards are user-experience controls only and must never be relied upon for security.

## 2. Initial role model

The first production-oriented role set is:

| Role | Purpose |
| --- | --- |
| `company_admin` | Full administration of company users, master data, sales data, targets, alerts, and configuration. |
| `sales_manager` | Manage and analyze sales data within the manager's authorized scope; manage targets for authorized scope where permitted. |
| `salesperson` | Work with sales activity within the salesperson's authorized scope; no unrestricted access to other users' data. |
| `analyst` | Read-only access to authorized sales, targets, forecasting, dashboards, and alerts. |
| `viewer` | Read-only access to authorized dashboard/business information with the narrowest business permissions. |

The exact UI capabilities can evolve, but the backend permissions must be explicit.

## 3. Company / tenant boundary

Every business record that contains company-owned data must ultimately be reachable through a company/tenant ownership boundary.

Conceptually:

```text
Company
  |
  +-- Users / Memberships
  |      +-- role
  |
  +-- Regions
  +-- Products
  +-- Customers
  +-- Salespeople
  +-- Transactions
  +-- Targets
  +-- Alerts
```

A request authenticated as a member of Company A must never be able to read or mutate Company B data.

## 4. Authorization rules

Authorization has two independent layers:

### Action authorization

Can this role perform the operation?

Examples:

```text
Viewer       -> GET only
Analyst      -> GET only
Salesperson  -> limited sales create/read for own scope
Manager      -> team/region management
Admin        -> company-wide administration
```

### Object/queryset authorization

Even if a role can perform an operation, can it operate on this specific record?

Examples:

```text
Salesperson A cannot PATCH Salesperson B's transaction.
Manager for Region X cannot read Region Y's private operational data.
Company A user cannot filter API requests to expose Company B records.
```

Query parameters such as `?region=`, `?salesperson=`, or `?product=` may narrow an authorized queryset, but must never expand it.

## 5. Backend enforcement

The backend will enforce access using:

1. Explicit user/company membership and role state.
2. DRF permission classes for action-level permissions.
3. Queryset/service filtering for object/data-scope restrictions.
4. Serializer validation for user-controlled relationships.
5. Database foreign keys and constraints for integrity.

Frontend route guards are not an authorization mechanism.

## 6. Frontend behavior

The frontend should consume the authenticated user's authorization context from the backend.

The current `AdminRoute` checks `is_staff`/`is_superuser`. This should eventually be replaced by role/capability checks returned from `/api/v1/auth/me/` or an equivalent endpoint.

UI restrictions are for usability only. A hidden button must not be considered a security control.

## 7. Registration policy

Public registration must not create or seed shared company business data.

Company-admin/user onboarding must be an explicit workflow.

Demo-data creation must be an explicit development/test/admin operation, never a side effect of public registration.

## 8. Sprint 1 implementation sequence

1. Define company and membership domain model.
2. Define role representation and role constraints.
3. Define authenticated-user response contract.
4. Remove registration → demo-data coupling.
5. Implement backend permission classes.
6. Scope sales and master-data querysets by company and role.
7. Add API permission/ownership tests.
8. Update frontend route/feature guards to consume backend authorization state.
9. Run CI and open a pull request.

## 9. Non-goals for this sprint

- SSO/social authentication.
- Multi-factor authentication.
- Fine-grained policy engines such as OPA.
- External identity providers.
- Advanced audit/compliance tooling.

Those can be evaluated later after the core ownership and role model is correct.
