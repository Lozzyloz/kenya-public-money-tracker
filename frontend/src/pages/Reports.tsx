
import {
  FileText,
  ShieldCheck,
  ClipboardCheck,
  Search,
  Clock,
  CheckCircle,
  Inbox,
  MapPin,
  Layers,
  Filter,
  RotateCcw,
  Eye,
  X,
  Save,
  MessageSquare,
} from "lucide-react";
import { useState } from "react";

type ReportStatus = "Received" | "Under review" | "Resolved";

type Report = {
  id: number;
  title: string;
  county: string;
  category: string;
  status: ReportStatus;
  description: string;
  reviewNotes: string;
};

const initialReports: Report[] = [
  {
    id: 1,
    title: "Request for clarification on a road project",
    county: "Tharaka Nithi",
    category: "Infrastructure",
    status: "Under review",
    description:
      "A citizen is requesting clarification about the progress and implementation of a local road improvement project.",
    reviewNotes: "",
  },
  {
    id: 2,
    title: "Question about a community water project",
    county: "Meru",
    category: "Water",
    status: "Received",
    description:
      "A citizen is asking for an update about a community water supply project.",
    reviewNotes: "",
  },
  {
    id: 3,
    title: "Request for school construction updates",
    county: "Embu",
    category: "Education",
    status: "Under review",
    description:
      "A citizen is requesting information about the progress of a school construction project.",
    reviewNotes: "",
  },
];

export default function Reports() {
  const [reports, setReports] = useState<Report[]>(initialReports);

  const [search, setSearch] = useState("");
  const [selectedCounty, setSelectedCounty] = useState("All");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [selectedStatus, setSelectedStatus] = useState("All");

  const [selectedReportId, setSelectedReportId] = useState<number | null>(null);
  const [draftStatus, setDraftStatus] = useState<ReportStatus>("Received");
  const [draftNotes, setDraftNotes] = useState("");

  const totalReports = reports.length;

  const receivedReports = reports.filter(
    (report) => report.status === "Received",
  ).length;

  const underReviewReports = reports.filter(
    (report) => report.status === "Under review",
  ).length;

  const resolvedReports = reports.filter(
    (report) => report.status === "Resolved",
  ).length;

  const counties = [...new Set(reports.map((report) => report.county))].sort();

  const categories = [
    ...new Set(reports.map((report) => report.category)),
  ].sort();

  const filteredReports = reports.filter((report) => {
    const matchesSearch = `${report.title} ${report.county} ${report.category}`
      .toLowerCase()
      .includes(search.toLowerCase());

    const matchesCounty =
      selectedCounty === "All" || report.county === selectedCounty;

    const matchesCategory =
      selectedCategory === "All" || report.category === selectedCategory;

    const matchesStatus =
      selectedStatus === "All" || report.status === selectedStatus;

    return (
      matchesSearch &&
      matchesCounty &&
      matchesCategory &&
      matchesStatus
    );
  });

  const countyCounts = Object.entries(
    reports.reduce<Record<string, number>>((counts, report) => {
      counts[report.county] = (counts[report.county] || 0) + 1;
      return counts;
    }, {}),
  ).sort((a, b) => b[1] - a[1]);

  const categoryCounts = Object.entries(
    reports.reduce<Record<string, number>>((counts, report) => {
      counts[report.category] = (counts[report.category] || 0) + 1;
      return counts;
    }, {}),
  ).sort((a, b) => b[1] - a[1]);

  const selectedReport = reports.find(
    (report) => report.id === selectedReportId,
  );

  const clearFilters = () => {
    setSearch("");
    setSelectedCounty("All");
    setSelectedCategory("All");
    setSelectedStatus("All");
  };

  const openReportDetails = (report: Report) => {
    setSelectedReportId(report.id);
    setDraftStatus(report.status);
    setDraftNotes(report.reviewNotes);
  };

  const closeReportDetails = () => {
    setSelectedReportId(null);
    setDraftNotes("");
  };

  const saveReviewChanges = () => {
    if (selectedReportId === null) return;

    setReports((currentReports) =>
      currentReports.map((report) =>
        report.id === selectedReportId
          ? {
              ...report,
              status: draftStatus,
              reviewNotes: draftNotes.trim(),
            }
          : report,
      ),
    );

    closeReportDetails();
  };

  return (
    <div className="reports-page">
      <div className="reports-header">
        <div>
          <span className="eyebrow">CITIZEN PARTICIPATION</span>
          <h1>Citizen Reports</h1>
          <p>
            Learn about reporting public project concerns
            and strengthening accountability.
          </p>
        </div>

        <FileText size={45} />
      </div>

      <div className="demo-notice">
        Demonstration only: The reports displayed here are
        fictional examples, not verified complaints.
        Changes made on this page are temporary and will not
        be saved to a database.
      </div>

      {/* REPORT SUMMARY */}
      <div className="report-summary-grid">
        <article className="report-summary-card">
          <div className="report-summary-icon total-reports-icon">
            <FileText size={23} />
          </div>
          <span>Total Reports</span>
          <h2>{totalReports}</h2>
          <p>All demonstration reports</p>
        </article>

        <article className="report-summary-card">
          <div className="report-summary-icon received-reports-icon">
            <Inbox size={23} />
          </div>
          <span>Received</span>
          <h2>{receivedReports}</h2>
          <p>Reports awaiting review</p>
        </article>

        <article className="report-summary-card">
          <div className="report-summary-icon review-reports-icon">
            <Clock size={23} />
          </div>
          <span>Under Review</span>
          <h2>{underReviewReports}</h2>
          <p>Reports being assessed</p>
        </article>

        <article className="report-summary-card">
          <div className="report-summary-icon resolved-reports-icon">
            <CheckCircle size={23} />
          </div>
          <span>Resolved</span>
          <h2>{resolvedReports}</h2>
          <p>Reports marked resolved</p>
        </article>
      </div>

      {/* REPORT ORGANISATION */}
      <div className="report-organisation-grid">
        <section className="report-organisation-card">
          <div className="report-organisation-heading">
            <div className="report-organisation-icon">
              <MapPin size={22} />
            </div>
            <div>
              <h2>Reports by County</h2>
              <p>Distribution of reports across counties.</p>
            </div>
          </div>

          {countyCounts.map(([county, count]) => (
            <div className="report-breakdown-item" key={county}>
              <div className="report-breakdown-label">
                <span>{county}</span>
                <strong>
                  {count} {count === 1 ? "report" : "reports"}
                </strong>
              </div>
              <div className="report-breakdown-track">
                <div
                  className="report-breakdown-fill county-fill"
                  style={{
                    width: `${totalReports ? (count / totalReports) * 100 : 0}%`,
                  }}
                />
              </div>
            </div>
          ))}
        </section>

        <section className="report-organisation-card">
          <div className="report-organisation-heading">
            <div className="report-organisation-icon category-icon">
              <Layers size={22} />
            </div>
            <div>
              <h2>Reports by Category</h2>
              <p>Issues raised by citizens.</p>
            </div>
          </div>

          {categoryCounts.map(([category, count]) => (
            <div className="report-breakdown-item" key={category}>
              <div className="report-breakdown-label">
                <span>{category}</span>
                <strong>
                  {count} {count === 1 ? "report" : "reports"}
                </strong>
              </div>
              <div className="report-breakdown-track">
                <div
                  className="report-breakdown-fill category-fill"
                  style={{
                    width: `${totalReports ? (count / totalReports) * 100 : 0}%`,
                  }}
                />
              </div>
            </div>
          ))}
        </section>
      </div>

      {/* REPORTING GUIDANCE */}
      <div className="report-info-grid">
        <article className="report-info-card">
          <ShieldCheck size={28} />
          <h2>Responsible Reporting</h2>
          <p>
            Provide clear, factual information and distinguish
            personal observations from assumptions.
          </p>
        </article>

        <article className="report-info-card">
          <ClipboardCheck size={28} />
          <h2>Review Process</h2>
          <p>
            Reports should be reviewed before information
            is treated as verified.
          </p>
        </article>
      </div>

      {/* SEARCH AND FILTERS */}
      <div className="reports-list">
        <div className="reports-list-heading">
          <div>
            <h2>Demonstration Reports</h2>
            <p>Search, filter and review submitted reports.</p>
          </div>
        </div>

        <div className="report-search">
          <Search size={19} />
          <input
            type="search"
            placeholder="Search reports..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>

        <div className="report-filter-section">
          <div className="report-filter-title">
            <Filter size={19} />
            <h3>Filter Reports</h3>
          </div>

          <div className="report-filter-grid">
            <label>
              County
              <select
                value={selectedCounty}
                onChange={(event) => setSelectedCounty(event.target.value)}
              >
                <option value="All">All Counties</option>
                {counties.map((county) => (
                  <option key={county} value={county}>
                    {county}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Category
              <select
                value={selectedCategory}
                onChange={(event) => setSelectedCategory(event.target.value)}
              >
                <option value="All">All Categories</option>
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Status
              <select
                value={selectedStatus}
                onChange={(event) => setSelectedStatus(event.target.value)}
              >
                <option value="All">All Statuses</option>
                <option value="Received">Received</option>
                <option value="Under review">Under Review</option>
                <option value="Resolved">Resolved</option>
              </select>
            </label>
          </div>

          <button
            type="button"
            className="report-clear-filters"
            onClick={clearFilters}
          >
            <RotateCcw size={16} />
            Clear Filters
          </button>
        </div>

        <div className="report-results-count">
          Showing <strong>{filteredReports.length}</strong> of{" "}
          <strong>{totalReports}</strong> reports
        </div>

        <div className="report-records">
          {filteredReports.map((report) => (
            <article className="report-record" key={report.id}>
              <div className="report-record-information">
                <h3>{report.title}</h3>
                <p>
                  {report.county} County · {report.category}
                </p>
                <button
                  type="button"
                  className="report-view-details"
                  onClick={() => openReportDetails(report)}
                >
                  <Eye size={16} />
                  View Details
                </button>
              </div>

              <span
                className={`report-review-status ${report.status
                  .toLowerCase()
                  .replaceAll(" ", "-")}`}
              >
                {report.status}
              </span>
            </article>
          ))}

          {filteredReports.length === 0 && (
            <p className="empty-results">
              No matching reports found. Try changing your search or filters.
            </p>
          )}
        </div>
      </div>

      {/* REPORT DETAILS AND REVIEW PANEL */}
      {selectedReport && (
        <div
          className="report-modal-overlay"
          onClick={closeReportDetails}
        >
          <section
            className="report-details-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="report-details-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="report-modal-header">
              <div>
                <span className="eyebrow">REPORT REVIEW</span>
                <h2 id="report-details-title">Report Details</h2>
              </div>

              <button
                type="button"
                className="report-modal-close"
                onClick={closeReportDetails}
                aria-label="Close report details"
              >
                <X size={22} />
              </button>
            </div>

            <div className="report-detail-content">
              <div className="report-detail-field">
                <span>Report title</span>
                <h3>{selectedReport.title}</h3>
              </div>

              <div className="report-detail-two-column">
                <div className="report-detail-field">
                  <span>County</span>
                  <p>{selectedReport.county}</p>
                </div>

                <div className="report-detail-field">
                  <span>Category</span>
                  <p>{selectedReport.category}</p>
                </div>
              </div>

              <div className="report-detail-field">
                <span>Report description</span>
                <p>{selectedReport.description}</p>
              </div>

              <div className="report-review-editor">
                <div className="report-review-editor-heading">
                  <MessageSquare size={19} />
                  <h3>Review Management</h3>
                </div>

                <label htmlFor="report-status">Update report status</label>
                <select
                  id="report-status"
                  value={draftStatus}
                  onChange={(event) =>
                    setDraftStatus(event.target.value as ReportStatus)
                  }
                >
                  <option value="Received">Received</option>
                  <option value="Under review">Under Review</option>
                  <option value="Resolved">Resolved</option>
                </select>

                <label htmlFor="report-review-notes">Review notes</label>
                <textarea
                  id="report-review-notes"
                  rows={4}
                  placeholder="Enter review notes or follow-up information..."
                  value={draftNotes}
                  onChange={(event) => setDraftNotes(event.target.value)}
                />

                <p className="report-review-hint">
                  These notes are demonstration data and are not publicly
                  verified.
                </p>
              </div>
            </div>

            <div className="report-modal-actions">
              <button
                type="button"
                className="report-cancel-button"
                onClick={closeReportDetails}
              >
                Cancel
              </button>

              <button
                type="button"
                className="report-save-button"
                onClick={saveReviewChanges}
              >
                <Save size={17} />
                Save Changes
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
