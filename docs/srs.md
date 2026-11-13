# Software Requirements Specification (MVP)

Status: draft. Pilot county undecided (see decisions.md).

## 1. Users
- Public: browses without an account, can submit reports.
- Admin: manages official data and users.
- Reviewer: reviews citizen reports; cannot edit official data.

## 2. Data integrity rules (apply everywhere)
- DI-1: Missing data is never shown as zero. Show "No data available".
- DI-2: Approved budget, revised budget, committed funds and reported
  expenditure are separate figures, each with a source and reporting period.
- DI-3: Every financial and project record stores source name, source
  document or URL, reporting period, date recorded, verification status
  and who recorded it.
- DI-4: Changes to important records are kept as history, not overwritten.
- DI-5: A citizen report is an observation, never displayed as fact.

## 3. Functional requirements

### Projects
- FR-1: Admin can create, edit and archive a project.
- FR-2: Public can list projects with pagination.
- FR-3: Public can filter by county, sector and status, and search by name.
- FR-4: Public can open a project profile showing details, sources,
  budgets, expenditure, milestones and documents.

### Finance
- FR-5: Admin can add budget records (approved or revised) to a project.
- FR-6: Admin can add reported expenditure records to a project.
- FR-7: Each financial record shows its type, amount, financial year,
  reporting period and source.
- FR-8: Revising a budget adds a new record; the original stays visible.

### Milestones and updates
- FR-9: Admin can add milestones with status and optional evidence.
- FR-10: Admin can add dated progress updates with a source.

### Documents
- FR-11: Admin can attach a document or link to a project or record.

### Citizen reports
- FR-12: Anyone can submit a report on a project (description required).
- FR-13: Reporter may attach photos or files and optional contact details.
- FR-14: Contact details are never shown publicly.
- FR-15: New reports start as "Submitted".
- FR-16: Reviewer can set status: under review, awaiting information,
  verified, unverified, disputed, rejected, resolved.
- FR-17: Every status change records the reviewer, time and a note.
- FR-18: Public sees only reports a reviewer has made public, with
  neutral wording and their status.

### Accounts and access
- FR-19: Admin and reviewer log in with email and password.
- FR-20: Role-based access: each endpoint enforces its allowed roles.
- FR-21: Admin can create accounts and assign roles.

### Audit
- FR-22: Admin and reviewer actions that change data are logged with
  user, action, record and time.

### Dashboard
- FR-23: Admin sees counts by county, sector and status, and the
  number of reports awaiting review.

## 4. Non-functional requirements
- NFR-1: Passwords hashed; secrets only in environment variables.
- NFR-2: All input validated; protected against SQL injection and XSS.
- NFR-3: Uploads limited by type and size.
- NFR-4: Rate limiting on report submission and login.
- NFR-5: Money stored as exact decimals, never floats.
- NFR-6: Schema changes only through migrations.
- NFR-7: Core business rules covered by automated tests.
- NFR-8: Personal data handling follows the Kenya Data Protection Act, 2019.

## 5. Out of scope for MVP
Maps, county comparisons, notifications, automated imports, AI features.

## 6. Acceptance example (FR-6 / DI-1)
- Given a project with no expenditure records,
  when the project profile is requested,
  then expenditure is returned as null / "No data available", not 0.
