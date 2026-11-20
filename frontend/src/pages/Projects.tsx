
import {
  Building2,
  MapPin,
  CalendarDays,
  Search,
  Filter,
  RefreshCw,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import { getProjects } from "../api/projects";
import type { Project as ApiProject } from "../api/projects";
import { getCounties } from "../api/counties";
import type { County } from "../api/counties";
import { getSectors } from "../api/sectors";
import type { Sector } from "../api/sectors";
import {
  getProjectBudgets,
  getProjectExpenditures,
} from "../api/finance";
import type {
  BudgetList,
  ExpenditureList,
} from "../api/finance";

interface ProjectFinance {
  budgets: BudgetList | null;
  expenditures: ExpenditureList | null;
  error: string | null;
}

// CORRECTED CURRENCY FORMATTER
const formatCurrency = (amount: string | number): string => {
  const normalized = String(amount).replace(/,/g, "").trim();

  const match = normalized.match(/^(-?)(\d+)(?:\.(\d{1,2}))?$/);

  if (!match) {
    return `KES ${String(amount)}`;
  }

  const [, sign, wholePart, decimalPart = ""] = match;

  const whole = BigInt(wholePart);
  const formattedWhole = new Intl.NumberFormat("en-KE").format(whole);

  const decimals = decimalPart.padEnd(2, "0");

  return `KES ${sign}${formattedWhole}${
    decimals !== "00" ? `.${decimals}` : ""
  }`;
};

const formatDate = (date: string | null): string => {
  if (!date) return "Not provided";

  return new Date(`${date}T00:00:00`).toLocaleDateString("en-KE", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
};

const formatStatus = (status: string): string => {
  return status
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

const formatVerification = (status: string): string => {
  return formatStatus(status);
};

const isSampleProject = (name: string): boolean => {
  return name.toUpperCase().startsWith("SAMPLE");
};

const getTimelineStatus = (project: ApiProject): string => {
  if (project.status === "completed") return "Completed";

  if (!project.start_date && !project.expected_completion) {
    return "Dates unavailable";
  }

  const today = new Date().toISOString().split("T")[0];

  if (project.start_date && today < project.start_date) {
    return "Not Started";
  }

  if (project.expected_completion && today > project.expected_completion) {
    return "Past Expected Date";
  }

  return "In Progress";
};

const getCurrentBudgets = (finance: ProjectFinance | undefined) => {
  if (!finance?.budgets?.has_data) return [];

  return finance.budgets.items.filter((budget) => budget.is_current);
};

const getTotalCurrentBudget = (
  projects: ApiProject[],
  finances: Record<number, ProjectFinance>,
): string | null => {
  let totalCents = 0n;
  let hasBudget = false;

  for (const project of projects) {
    const budgets = getCurrentBudgets(finances[project.id]);

    for (const budget of budgets) {
      const [whole, decimal = "00"] = budget.amount.split(".");

      totalCents +=
        BigInt(whole || "0") * 100n +
        BigInt(decimal.padEnd(2, "0").slice(0, 2));

      hasBudget = true;
    }
  }

  if (!hasBudget) return null;

  const whole = totalCents / 100n;
  const decimal = (totalCents % 100n).toString().padStart(2, "0");

  return `${new Intl.NumberFormat("en-KE").format(whole)}${
    decimal !== "00" ? `.${decimal}` : ""
  }`;
};

export default function Projects() {
  const [projects, setProjects] = useState<ApiProject[]>([]);
  const [counties, setCounties] = useState<County[]>([]);
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [finances, setFinances] = useState<
    Record<number, ProjectFinance>
  >({});

  const [search, setSearch] = useState("");
  const [selectedCounty, setSelectedCounty] = useState("All");
  const [selectedSector, setSelectedSector] = useState("All");
  const [selectedStatus, setSelectedStatus] = useState("All");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      setLoading(true);
      setError("");

      try {
        const [projectResponse, countyResponse, sectorResponse] =
          await Promise.all([
            getProjects(),
            getCounties(),
            getSectors(),
          ]);

        if (cancelled) return;

        setProjects(projectResponse.items);
        setCounties(countyResponse);
        setSectors(sectorResponse);

        const financeResults = await Promise.all(
          projectResponse.items.map(async (project) => {
            try {
              const [budgets, expenditures] = await Promise.all([
                getProjectBudgets(project.id),
                getProjectExpenditures(project.id),
              ]);

              return {
                id: project.id,
                data: {
                  budgets,
                  expenditures,
                  error: null,
                } satisfies ProjectFinance,
              };
            } catch {
              return {
                id: project.id,
                data: {
                  budgets: null,
                  expenditures: null,
                  error: "Financial information could not be loaded.",
                } satisfies ProjectFinance,
              };
            }
          }),
        );

        if (cancelled) return;

        const financeMap: Record<number, ProjectFinance> = {};

        financeResults.forEach((result) => {
          financeMap[result.id] = result.data;
        });

        setFinances(financeMap);
      } catch (err) {
        if (cancelled) return;

        setError(
          err instanceof Error
            ? err.message
            : "Could not connect to the KPAP backend.",
        );
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadData();

    return () => {
      cancelled = true;
    };
  }, []);

  const totalProjects = projects.length;

  const plannedProjects = projects.filter(
    (project) => project.status === "planned",
  ).length;

  const ongoingProjects = projects.filter(
    (project) => project.status === "ongoing",
  ).length;

  const completedProjects = projects.filter(
    (project) => project.status === "completed",
  ).length;

  const totalBudget = getTotalCurrentBudget(projects, finances);

  const filteredProjects = useMemo(() => {
    return projects.filter((project) => {
      const matchesSearch =
        project.name.toLowerCase().includes(search.toLowerCase()) ||
        project.county.name.toLowerCase().includes(search.toLowerCase()) ||
        (project.sector?.name ?? "")
          .toLowerCase()
          .includes(search.toLowerCase());

      const matchesCounty =
        selectedCounty === "All" ||
        project.county.name === selectedCounty;

      const matchesSector =
        selectedSector === "All" ||
        project.sector?.name === selectedSector;

      const matchesStatus =
        selectedStatus === "All" ||
        project.status === selectedStatus;

      return (
        matchesSearch &&
        matchesCounty &&
        matchesSector &&
        matchesStatus
      );
    });
  }, [
    projects,
    search,
    selectedCounty,
    selectedSector,
    selectedStatus,
  ]);

  const clearFilters = () => {
    setSearch("");
    setSelectedCounty("All");
    setSelectedSector("All");
    setSelectedStatus("All");
  };

  const refreshProjects = () => {
    window.location.reload();
  };

  return (
    <div className="projects-page">
      <div className="page-header">
        <div>
          <h1>Public Projects</h1>
          <p>Track public development projects across Kenya.</p>
        </div>
      </div>

      <div className="demo-notice">
        <strong>Sample data notice:</strong> Records marked SAMPLE are
        fictional demonstration records supplied by the backend. They are
        not real public projects or verified financial information.
      </div>

      {/* LOADING STATE */}
      {loading && (
        <div className="no-projects-message">
          <RefreshCw size={24} />
          <h3>Loading project records...</h3>
          <p>Connecting to the KPAP backend.</p>
        </div>
      )}

      {/* ERROR STATE */}
      {!loading && error && (
        <div className="no-projects-message">
          <h3>Could not load project records</h3>
          <p>{error}</p>
          <button
            type="button"
            className="add-project-button"
            onClick={refreshProjects}
          >
            <RefreshCw size={16} />
            Refresh Page
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          {/* PROJECT SUMMARY */}
          <div className="project-summary-grid">
            <div className="project-summary-card">
              <span>Total Projects</span>
              <h2>{totalProjects}</h2>
              <p>Projects returned by the backend</p>
            </div>

            <div className="project-summary-card">
              <span>Total Current Budgets</span>
              <h2>
                {totalBudget !== null
                  ? formatCurrency(totalBudget)
                  : "No data available"}
              </h2>
              <p>Current budget records only</p>
            </div>

            <div className="project-summary-card">
              <span>Ongoing Projects</span>
              <h2>{ongoingProjects}</h2>
              <p>Projects marked ongoing</p>
            </div>

            <div className="project-summary-card">
              <span>Completed Projects</span>
              <h2>{completedProjects}</h2>
              <p>Projects marked completed</p>
            </div>
          </div>

          {/* PROJECT STATUS BREAKDOWN */}
          <div className="project-status-breakdown">
            <span>Project Status Breakdown:</span>
            <strong>Planned: {plannedProjects}</strong>
            <strong>Ongoing: {ongoingProjects}</strong>
            <strong>Completed: {completedProjects}</strong>
          </div>

          {/* REGISTRATION NOTICE */}
          <div className="demo-notice">
            <strong>Project registration:</strong> Project creation is not
            yet available through the backend API. This page currently
            displays records retrieved from the backend.
          </div>

          {/* SEARCH AND FILTERS */}
          <div className="project-filter-section">
            <div className="project-filter-heading">
              <Filter size={19} />
              <h2>Find Projects</h2>
            </div>

            <div className="project-filter-grid">
              <div className="project-search">
                <Search size={18} />
                <input
                  type="text"
                  placeholder="Search project, county or sector..."
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                />
              </div>

              <select
                aria-label="Filter by county"
                value={selectedCounty}
                onChange={(event) =>
                  setSelectedCounty(event.target.value)
                }
              >
                <option value="All">All Counties</option>
                {counties.map((county) => (
                  <option key={county.id} value={county.name}>
                    {county.name}
                  </option>
                ))}
              </select>

              <select
                aria-label="Filter by sector"
                value={selectedSector}
                onChange={(event) =>
                  setSelectedSector(event.target.value)
                }
              >
                <option value="All">All Sectors</option>
                {sectors.map((sector) => (
                  <option key={sector.id} value={sector.name}>
                    {sector.name}
                  </option>
                ))}
              </select>

              <select
                aria-label="Filter by project status"
                value={selectedStatus}
                onChange={(event) =>
                  setSelectedStatus(event.target.value)
                }
              >
                <option value="All">All Statuses</option>
                <option value="planned">Planned</option>
                <option value="ongoing">Ongoing</option>
                <option value="completed">Completed</option>
                <option value="delayed">Delayed</option>
                <option value="suspended">Suspended</option>
                <option value="stalled">Stalled</option>
                <option value="unknown">Unknown</option>
              </select>

              <button
                type="button"
                className="clear-project-filters"
                onClick={clearFilters}
              >
                Clear Filters
              </button>
            </div>
          </div>

          {/* PROJECT RESULTS */}
          <div className="projects-results-heading">
            <h2>Project Records</h2>
            <span>
              Showing {filteredProjects.length} of {projects.length} projects
            </span>
          </div>

          <div className="project-grid">
            {filteredProjects.length === 0 ? (
              <div className="no-projects-message">
                <Search size={30} />
                <h3>No projects found</h3>
                <p>
                  Try changing your search or filters to find other projects.
                </p>
                <button
                  type="button"
                  className="clear-project-filters"
                  onClick={clearFilters}
                >
                  Clear Filters
                </button>
              </div>
            ) : (
              filteredProjects.map((project) => {
                const finance = finances[project.id];
                const currentBudgets = getCurrentBudgets(finance);

                const historicalBudgets =
                  finance?.budgets?.items.filter(
                    (budget) => !budget.is_current,
                  ) ?? [];

                const expenditures =
                  finance?.expenditures?.has_data
                    ? finance.expenditures.items
                    : [];

                return (
                  <div className="project-card" key={project.id}>
                    <div className="project-card-top">
                      <div className="project-card-icon">
                        <Building2 size={22} />
                      </div>

                      <span
                        className={`project-status status-${project.status}`}
                      >
                        {formatStatus(project.status)}
                      </span>
                    </div>

                    <h3>{project.name}</h3>

                    {isSampleProject(project.name) && (
                      <div className="demo-notice">
                        Fictional sample project – not real data.
                      </div>
                    )}

                    <div className="project-location">
                      <MapPin size={16} />
                      <span>{project.county.name} County</span>
                    </div>

                    <p className="project-description">
                      {project.description || "No description available."}
                    </p>

                    <div className="project-information">
                      <div>
                        <span>Sector</span>
                        <strong>
                          {project.sector?.name || "Not provided"}
                        </strong>
                      </div>

                      <div>
                        <span>Agency</span>
                        <strong>
                          {project.agency?.name || "Not provided"}
                        </strong>
                      </div>

                      <div>
                        <span>Contractor</span>
                        <strong>
                          {project.contractor?.name || "Not provided"}
                        </strong>
                      </div>
                    </div>

                    {/* BUDGET INFORMATION */}
                    <div className="project-timeline">
                      <strong>Budget Information</strong>

                      {finance?.error ? (
                        <p>{finance.error}</p>
                      ) : !finance?.budgets ? (
                        <p>Loading budget information...</p>
                      ) : !finance.budgets.has_data ? (
                        <p>No budget data available.</p>
                      ) : currentBudgets.length === 0 ? (
                        <p>No current budget available.</p>
                      ) : (
                        currentBudgets.map((budget) => (
                          <div key={budget.id}>
                            <span>
                              {formatStatus(budget.budget_type)} Budget:
                            </span>
                            <strong>
                              {formatCurrency(budget.amount)}
                            </strong>
                            <span>
                              Financial year: {budget.financial_year}
                            </span>
                            <span>
                              Verification:{" "}
                              {formatVerification(
                                budget.verification_status,
                              )}
                            </span>
                            <span>
                              Source: {budget.source_document.source_name}
                            </span>

                            {budget.source_document.url && (
                              <a
                                href={budget.source_document.url}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                View source document
                              </a>
                            )}
                          </div>
                        ))
                      )}

                      {historicalBudgets.length > 0 && (
                        <div>
                          <strong>Budget History</strong>
                          {historicalBudgets.map((budget) => (
                            <p key={budget.id}>
                              {formatStatus(budget.budget_type)}:{" "}
                              {formatCurrency(budget.amount)} (
                              {budget.financial_year}) – Historical
                            </p>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* EXPENDITURE INFORMATION */}
                    <div className="project-timeline">
                      <strong>Expenditure Information</strong>

                      {finance?.error ? (
                        <p>{finance.error}</p>
                      ) : !finance?.expenditures ? (
                        <p>Loading expenditure information...</p>
                      ) : !finance.expenditures.has_data ? (
                        <p>No expenditure data available.</p>
                      ) : (
                        expenditures.map((expenditure) => (
                          <div key={expenditure.id}>
                            <strong>
                              {formatCurrency(expenditure.amount)}
                            </strong>
                            <span>
                              {expenditure.is_cumulative
                                ? "Cumulative expenditure"
                                : "Period expenditure"}
                            </span>
                            <span>
                              Period:{" "}
                              {formatDate(expenditure.period_start)} to{" "}
                              {formatDate(expenditure.period_end)}
                            </span>
                            <span>
                              Financial year: {expenditure.financial_year}
                            </span>
                            <span>
                              Verification:{" "}
                              {formatVerification(
                                expenditure.verification_status,
                              )}
                            </span>
                            <span>
                              Source:{" "}
                              {expenditure.source_document.source_name}
                            </span>

                            {expenditure.source_document.url && (
                              <a
                                href={expenditure.source_document.url}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                View source document
                              </a>
                            )}
                          </div>
                        ))
                      )}
                    </div>

                    {/* TIMELINE STATUS */}
                    <div className="project-timeline-status">
                      <span>Timeline Status</span>
                      <strong
                        className={`timeline-${getTimelineStatus(project)
                          .toLowerCase()
                          .replaceAll(" ", "-")}`}
                      >
                        {getTimelineStatus(project)}
                      </strong>
                    </div>

                    <div className="project-timeline">
                      <div>
                        <CalendarDays size={16} />
                        <span>
                          Start Date: {formatDate(project.start_date)}
                        </span>
                      </div>

                      <div>
                        <CalendarDays size={16} />
                        <span>
                          Expected Completion:{" "}
                          {formatDate(project.expected_completion)}
                        </span>
                      </div>

                      {project.actual_completion && (
                        <div>
                          <CalendarDays size={16} />
                          <span>
                            Actual Completion:{" "}
                            {formatDate(project.actual_completion)}
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="project-timeline">
                      <span>
                        Project verification:{" "}
                        {formatVerification(project.verification_status)}
                      </span>

                      <span>
                        Source: {project.source_document.source_name}
                      </span>

                      {project.source_document.url && (
                        <a
                          href={project.source_document.url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          View project source document
                        </a>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </>
      )}
    </div>
  );
}
