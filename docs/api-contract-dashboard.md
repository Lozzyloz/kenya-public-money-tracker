# API Contract: dashboard (v0.5, draft)

`GET /dashboard` requires a Bearer token of role `auditor_reviewer` or `administrator`.
Other roles get 403, no token gets 401. Read-only.

```json
{
  "generated_at": "2026-11-25T19:00:00Z",
  "projects": {
    "total": 3,
    "by_county": [ { "id": 13, "name": "Tharaka-Nithi", "count": 2 } ],
    "by_sector": [ { "id": 7, "name": "Health", "count": 1 },
                   { "id": null, "name": "Unspecified", "count": 2 } ],
    "by_status": [ { "status": "planned", "count": 0 } ]
  },
  "reports": {
    "total": 2, "awaiting_review": 1, "public": 1,
    "by_status": [ { "status": "submitted", "count": 1 } ]
  },
  "finance": {
    "projects_with_budget_data": 2, "projects_without_budget_data": 1,
    "projects_with_expenditure_data": 1, "projects_without_expenditure_data": 2,
    "current_budget_by_financial_year": [
      { "financial_year": "2025/2026", "total": "15000000.00", "project_count": 2 } ],
    "note": "..."
  },
  "recent_projects": [ { "id": 5, "name": "...", "county": "Tharaka-Nithi", "created_at": "..." } ],
  "recent_activity": null
}
```

Notes:
- `by_status` lists every status even at 0, so charts keep a stable shape. A 0 count is a real count.
- `by_county` lists only counties that have projects. `by_sector` uses `id: null` / "Unspecified" for projects with no sector.
- `awaiting_review` is the number of reports still in `submitted`.
- `recent_activity` is a list for administrators and `null` for reviewers.
  Items: `{ id, user_id, action, table_name, record_id, created_at }`.
- Money totals are decimal strings. They sum each project's current approved or revised
  budget per financial year. Show the `note` text near them.
- There is deliberately no expenditure total. Do not add one in the UI either:
  expenditure figures can be year-to-date and cannot be summed.
- "Projects without data" are not zero-budget projects. Label them "no data".

