
# KPAP Citizen Reports API Contract

## Purpose
Define how the React frontend will submit citizen reports
to the FastAPI backend.

## Proposed endpoint

POST /api/reports/

## Request fields

| Field | Type | Required |
|---|---|---|
| project_name | String | Yes |
| county | String | Yes |
| category | String | Yes |
| description | String | Yes |

## Example request

{
  "project_name": "Community Health Centre",
  "county": "Tharaka Nithi",
  "category": "Healthcare",
  "description": "I would like clarification on the project's progress."
}

## Expected successful response

HTTP 201 Created

The response should confirm that the report was saved
and provide its assigned report ID.

## Backend requirements

- Validate all fields on the server.
- Enforce appropriate field-length limits.
- Store reports in the database.
- Apply appropriate access controls.
- Protect against spam and malicious input.
- Keep reporter identity and public report information
  separate where identity information is collected.
- Do not expose private information in public responses.

## Integration status

PROPOSED - Awaiting agreement with the backend developer.

The endpoint and response format must be confirmed
before frontend integration.
