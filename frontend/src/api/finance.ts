
import { apiRequest } from "./client";

export interface Budget {
  id: number;
  budget_type: "approved" | "revised" | "committed";
  amount: string;
  financial_year: string;
  reporting_period: string | null;
  verification_status: string;
  supersedes_id: number | null;
  is_current: boolean;
  notes: string | null;
  source_document: {
    id: number;
    title: string;
    source_name: string;
    url: string | null;
    document_type: string;
    financial_year: string | null;
    period_label: string | null;
    published_date: string | null;
  };
}

export interface BudgetList {
  has_data: boolean;
  items: Budget[];
}

export interface Expenditure {
  id: number;
  amount: string;
  financial_year: string;
  period_start: string | null;
  period_end: string;
  is_cumulative: boolean;
  verification_status: string;
  notes: string | null;
  source_document: {
    id: number;
    title: string;
    source_name: string;
    url: string | null;
    document_type: string;
    financial_year: string | null;
    period_label: string | null;
    published_date: string | null;
  };
}

export interface ExpenditureList {
  has_data: boolean;
  items: Expenditure[];
}

export async function getProjectBudgets(
  projectId: number,
): Promise<BudgetList> {
  return apiRequest<BudgetList>(`/projects/${projectId}/budgets`);
}

export async function getProjectExpenditures(
  projectId: number,
): Promise<ExpenditureList> {
  return apiRequest<ExpenditureList>(
    `/projects/${projectId}/expenditures`,
  );
}
