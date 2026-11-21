# API Contract: admin write endpoints (v0.2, draft)

All endpoints below need `Authorization: Bearer <token>` of an
**administrator**. Other roles get 403, no token gets 401.
`recorded_by` is set by the server from the token and must NOT be sent
(unknown fields are rejected with 422).

## Reference data
- `GET /documents?q=&limit=` (public) returns `SourceDocument[]`
- `POST /documents`
  `{ title, source_name, document_type, url?, financial_year?, period_label?, published_date? }`
  `url` must be http(s). Returns `SourceDocument` (201).
- `GET /contractors`, `GET /agencies` (public) return `NamedItem[]`
- `POST /contractors` `{ name, registration_no? }`
- `POST /agencies` `{ name, county_id? }`

## Projects
- `POST /projects` (201, returns `Project`)
  Required: `name`, `county_id`, `source_document_id`.
  Optional: description, sub_county, location_text, latitude, longitude,
  sector_id, agency_id, contractor_id, start_date, expected_completion,
  actual_completion, `status` (default `unknown`),
  `verification_status` (default `official`).
- `PATCH /projects/{id}` sends only the fields to change. Empty body gives 422.
  `name`, `county_id`, `status`, `verification_status`, `source_document_id`
  and `is_archived` cannot be set to null; the other fields can be cleared with null.
- Archive: `PATCH` with `{ "is_archived": true }`. Archived projects disappear from reads (404).
- Admins may set verification_status to official, verified, unverified or disputed.
  `citizen_submitted` is reserved for citizen reports.

## Budgets and expenditures
- `POST /projects/{id}/budgets` (201, returns `Budget`)
  `{ budget_type, amount, financial_year, source_document_id,
     reporting_period?, verification_status?, supersedes_id?, notes? }`
  - `amount`: decimal string or number, >= 0, at most 2 decimal places.
  - `financial_year`: `"2025/2026"` (consecutive years).
  - A `revised` budget MUST include `supersedes_id` (a budget of the same project
    and financial year, not already superseded, not `committed`).
  - Only `revised` budgets may set `supersedes_id`.
  - 409 if the budget was already superseded.
- `POST /projects/{id}/expenditures` (201, returns `Expenditure`)
  `{ amount, financial_year, period_end, is_cumulative, source_document_id,
     period_start?, verification_status?, notes? }`
  `is_cumulative` is required: true for year-to-date totals, false for a single period.
- There is no edit or delete for budgets or expenditures. Corrections for
  budgets are new `revised` records.

## Audit log (administrator only)
`GET /audit-logs?table_name=&record_id=&user_id=&page=&page_size=`
```json
{ "items": [ { "id": 1, "user_id": 1, "action": "create",
    "table_name": "projects", "record_id": 5,
    "before": null, "after": { "...": "..." },
    "created_at": "2026-11-21T09:30:00" } ],
  "total": 1, "page": 1, "page_size": 50 }
```
`action` is create, update or archive.

## Errors
- 401 no or expired token, 403 wrong role
- 404 unknown or archived project
- 409 budget already superseded
- 422 validation failure; for unknown ids the detail says which field, e.g. `"county_id 9999 does not exist"`
