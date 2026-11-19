
# KPAP Backend Role and Permission Requirements

## 1. Purpose

The backend must enforce user permissions independently of the React frontend.

Frontend navigation and ProtectedRoute are for user experience only. They are not security controls.

## 2. User Roles

The platform has five roles:

- citizen
- journalist_researcher
- government_officer
- auditor_reviewer
- administrator

## 3. Permission Matrix

| Permission | Citizen | Journalist | Officer | Auditor | Admin |
|---|---|---|---|---|---|
| View public information | Yes | Yes | Yes | Yes | Yes |
| Submit reports | Yes | No | No | No | Yes |
| View own reports | Yes | No | No | No | Yes |
| Research public data | No | Yes | No | No | Yes |
| Manage assigned projects | No | No | Yes | No | Yes |
| Upload official documents | No | No | Yes | No | Yes |
| Review citizen reports | No | No | No | Yes | Yes |
| Verify submissions | No | No | No | Yes | Yes |
| Manage users | No | No | No | No | Yes |
| Manage projects | No | No | No | No | Yes |
| Manage budgets | No | No | No | No | Yes |
| Manage platform settings | No | No | No | No | Yes |
| View audit logs | No | No | No | Yes | Yes |

## 4. Backend Security Requirements

The backend developer should:

1. Verify user identity using secure authentication.
2. Retrieve the user's role from trusted server-side account data.
3. Check permissions on every protected API request.
4. Return HTTP 401 for unauthenticated requests.
5. Return HTTP 403 when a user lacks permission.
6. Never trust a role supplied by the frontend.
7. Restrict government officers to projects assigned to them.
8. Restrict citizens to their own private report information.
9. Record sensitive administrative actions in audit logs.
10. Validate all incoming data on the server.

## 5. Important API Access Rules

- Public budget and project information should be readable without privileged access.
- Report submission should be available to authenticated citizens.
- Report review and verification should require the appropriate reviewer permissions.
- User management and platform settings should require administrator permissions.
- Every protected endpoint must enforce permissions on the backend.

## 6. Development Status

This document defines the proposed access requirements.

The frontend role selector is temporary demonstration functionality. Real authentication and backend permission enforcement must be implemented before production deployment.
