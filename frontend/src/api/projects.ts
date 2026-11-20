
import { apiRequest } from "./client";

export type ProjectStatus =
  | "planned"
  | "ongoing"
  | "completed"
  | "delayed"
  | "suspended"
  | "stalled"
  | "unknown";

export type VerificationStatus =
  | "official"
  | "verified"
  | "citizen_submitted"
  | "unverified"
  | "disputed";

export interface NamedItem {
  id: number;
  name: string;
}

export interface SourceDocument {
  id: number;
  title: string;
  source_name: string;
  url: string | null;
  document_type: string;
  financial_year: string | null;
  period_label: string | null;
  published_date: string | null;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  county: NamedItem;
  sub_county: string | null;
  location_text: string | null;
  sector: NamedItem | null;
  agency: NamedItem | null;
  contractor: NamedItem | null;
  start_date: string | null;
  expected_completion: string | null;
  actual_completion: string | null;
  status: ProjectStatus;
  verification_status: VerificationStatus;
  source_document: SourceDocument;
}

export interface ProjectList {
  items: Project[];
  total: number;
  page: number;
  page_size: number;
}

export async function getProjects(): Promise<ProjectList> {
  return apiRequest<ProjectList>("/projects");
}

export async function getProjectById(id: number): Promise<Project> {
  return apiRequest<Project>(`/projects/${id}`);
}
