ADMINISTRATOR = "administrator"
AUDITOR_REVIEWER = "auditor_reviewer"
CITIZEN = "citizen"
JOURNALIST_RESEARCHER = "journalist_researcher"
GOVERNMENT_OFFICER = "government_officer"

ALL_ROLES = (
    ADMINISTRATOR,
    AUDITOR_REVIEWER,
    CITIZEN,
    JOURNALIST_RESEARCHER,
    GOVERNMENT_OFFICER,
)

# Permission groups. Endpoints check these, not raw role names.
# journalist_researcher and government_officer have citizen-level access
# only for the MVP, so they appear in no staff group.
STAFF_ADMIN = (ADMINISTRATOR,)
REVIEWERS = (ADMINISTRATOR, AUDITOR_REVIEWER)
