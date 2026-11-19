
export type UserRole =
  | "citizen"
  | "journalist_researcher"
  | "government_officer"
  | "auditor_reviewer"
  | "administrator";

export type Permission =
  | "view_public_information"
  | "submit_reports"
  | "view_own_reports"
  | "research_public_data"
  | "manage_assigned_projects"
  | "upload_official_documents"
  | "review_citizen_reports"
  | "verify_submissions"
  | "manage_users"
  | "manage_projects"
  | "manage_budgets"
  | "manage_platform_settings"
  | "view_audit_logs";

export const rolePermissions: Record<UserRole, Permission[]> = {
  citizen: [
    "view_public_information",
    "submit_reports",
    "view_own_reports",
  ],

  journalist_researcher: [
    "view_public_information",
    "research_public_data",
  ],

  government_officer: [
    "view_public_information",
    "manage_assigned_projects",
    "upload_official_documents",
  ],

  auditor_reviewer: [
    "view_public_information",
    "review_citizen_reports",
    "verify_submissions",
    "view_audit_logs",
  ],

  administrator: [
    "view_public_information",
    "submit_reports",
    "view_own_reports",
    "research_public_data",
    "manage_assigned_projects",
    "upload_official_documents",
    "review_citizen_reports",
    "verify_submissions",
    "manage_users",
    "manage_projects",
    "manage_budgets",
    "manage_platform_settings",
    "view_audit_logs",
  ],
};

export function hasPermission(
  role: UserRole,
  permission: Permission,
): boolean {
  return rolePermissions[role].includes(permission);
}
