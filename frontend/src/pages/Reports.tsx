
import {
  FileText,
  ShieldCheck,
  ClipboardCheck,
  Search,
} from "lucide-react";
import { useState } from "react";

type Report = {
  id: number;
  title: string;
  county: string;
  category: string;
  status: string;
};

const sampleReports: Report[] = [
  {
    id: 1,
    title: "Request for clarification on a road project",
    county: "Tharaka Nithi",
    category: "Infrastructure",
    status: "Under review",
  },
  {
    id: 2,
    title: "Question about a community water project",
    county: "Meru",
    category: "Water",
    status: "Received",
  },
  {
    id: 3,
    title: "Request for school construction updates",
    county: "Embu",
    category: "Education",
    status: "Under review",
  },
];

export default function Reports() {
  const [search, setSearch] = useState("");

  const filteredReports = sampleReports.filter((report) =>
    `${report.title} ${report.county} ${report.category}`
      .toLowerCase()
      .includes(search.toLowerCase()),
  );

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
      </div>

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

      <div className="reports-list">
        <div className="reports-list-heading">
          <div>
            <h2>Demonstration Reports</h2>
            <p>Example reports and their review statuses.</p>
          </div>
        </div>

        <div className="report-search">
          <Search size={19} />
          <input
            type="search"
            placeholder="Search reports or counties..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>

        <div className="report-records">
          {filteredReports.map((report) => (
            <article className="report-record" key={report.id}>
              <div>
                <h3>{report.title}</h3>
                <p>
                  {report.county} County · {report.category}
                </p>
              </div>

              <span className="report-review-status">
                {report.status}
              </span>
            </article>
          ))}

          {filteredReports.length === 0 && (
            <p className="empty-results">
              No matching reports found.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
