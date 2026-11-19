# API Contract (v0.1, draft)

Base URL: `{HOST}/api/v1`
Interactive docs: `{HOST}/docs`. Machine-readable spec: `{HOST}/openapi.json`.

## Conventions
- JSON everywhere, except login (form-encoded).
- Dates are ISO strings: `"2026-07-01"`.
- Money is a **decimal string**: `"10000000.00"`. Never parse it as a float.
- `null` means "no data". Never display it as 0.
- Errors: `{"detail": "message"}`. Validation errors (422):
  `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}`.
- Protected endpoints need `Authorization: Bearer <token>`.
  Missing/invalid token: 401. Wrong role: 403.

## Public endpoints (no token)
health, counties, projects, budgets, expenditures.

## Auth

### POST /auth/login
Request: `application/x-www-form-urlencoded` with `username` (the email) and `password`.
Response 200:
```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```
Response 401: `{"detail": "Incorrect email or password"}`. Tokens last 60 minutes.

### GET /auth/me  (any logged-in user)
```json
{ "id": 1, "email": "a@b.com", "full_name": "A B", "role": "admin", "is_active": true }
```
`role` is `"admin" | "reviewer" | "citizen"` (under review, see roles section).

### GET /users, POST /users  (admin only)
POST body:
```json
{ "email": "x@y.com", "password": "min 12 chars", "full_name": "X Y", "role": "reviewer" }
```
Returns the same shape as /auth/me (201). Duplicate email: 409.

## Counties

### GET /counties
```json
[ { "id": 13, "code": 13, "name": "Tharaka-Nithi" } ]
```
Ordered by `code` (1 to 47).

## Projects

### GET /projects
Query params (all optional):
`county_id` int, `sector_id` int, `status` (see below),
`q` text search on name (2-100 chars), `page` (default 1), `page_size` (1-100, default 20).
Response:
```json
{ "items": [ Project ], "total": 42, "page": 1, "page_size": 20 }
```

### GET /projects/{id}  -> Project (404 if unknown or archived)
Project:
```json
{
  "id": 1,
  "name": "Kathwana Water Project",
  "description": null,
  "county": { "id": 13, "name": "Tharaka-Nithi" },
  "sub_county": null,
  "location_text": null,
  "sector": { "id": 3, "name": "Water and Sanitation" },
  "agency": null,
  "contractor": null,
  "start_date": null,
  "expected_completion": null,
  "actual_completion": null,
  "status": "ongoing",
  "verification_status": "official",
  "source_document": {
    "id": 1,
    "title": "Q2 FY2025/26 Budget Implementation Review",
    "source_name": "County Government of Tharaka-Nithi",
    "url": null,
    "document_type": "implementation_report",
    "financial_year": null,
    "period_label": null,
    "published_date": null
  }
}
```
Nullable: description, sub_county, location_text, sector, agency, contractor,
the three dates, and all source_document fields except id, title, source_name, document_type.

Enums:
- `status`: planned, ongoing, completed, delayed, suspended, stalled, unknown
- `verification_status`: official, verified, citizen_submitted, unverified, disputed
- `document_type`: budget, implementation_report, audit, tender_notice, award, other

## Budgets

### GET /projects/{id}/budgets
```json
{
  "has_data": true,
  "items": [
    {
      "id": 2,
      "budget_type": "revised",
      "amount": "12000000.00",
      "financial_year": "2025/2026",
      "reporting_period": null,
      "verification_status": "official",
      "supersedes_id": 1,
      "is_current": true,
      "notes": null,
      "source_document": { "...same as in Project..." }
    }
  ]
}
```
- `budget_type`: approved, revised, committed.
- `has_data: false` with `items: []` means no figures published. Show "No budget data available", not 0.
- A revision keeps the original; the replaced row has `is_current: false`. Show history, highlight the current one.

## Expenditures

### GET /projects/{id}/expenditures
```json
{
  "has_data": true,
  "items": [
    {
      "id": 1,
      "amount": "4000000.00",
      "financial_year": "2025/2026",
      "period_start": "2025-07-01",
      "period_end": "2025-12-31",
      "is_cumulative": true,
      "verification_status": "official",
      "notes": null,
      "source_document": { "...same as in Project..." }
    }
  ]
}
```
- `is_cumulative: true` means a year-to-date total. **Never add cumulative figures together.**
- `has_data: false`: show "No expenditure data available", not 0.
- Do not subtract expenditure from budget in the UI for now; periods may differ.

## Not built yet
- `GET /sectors` (needed for the sector filter)
- POST/PUT for projects, budgets, expenditures, documents (admin)
- Milestones, progress updates, citizen reports, audit log
- Rate limiting on login
