
import {
  Wallet,
  Building2,
  FileText,
  Users,
  TrendingUp,
  ArrowRight,
} from "lucide-react";

import { Link } from "react-router-dom";

const dashboardStats = [
  {
    title: "Sample Budget Allocation",
    value: "KES 1.9B",
    description: "Illustrative budget figures",
    icon: Wallet,
  },
  {
    title: "Development Projects",
    value: "4",
    description: "Demonstration project records",
    icon: Building2,
  },
  {
    title: "Citizen Reports",
    value: "3",
    description: "Demonstration report records",
    icon: FileText,
  },
  {
    title: "Platform Users",
    value: "0",
    description: "No registered users yet",
    icon: Users,
  },
];

const budgetBreakdown = [
  {
    name: "National Government",
    amount: "KES 1,000M",
    percentage: 52.6,
  },
  {
    name: "Education Development",
    amount: "KES 500M",
    percentage: 26.3,
  },
  {
    name: "Healthcare Services",
    amount: "KES 250M",
    percentage: 13.2,
  },
  {
    name: "Road Infrastructure",
    amount: "KES 150M",
    percentage: 7.9,
  },
];

const projectStatusSummary = [
  {
    name: "Planned",
    count: 1,
    percentage: 25,
  },
  {
    name: "Ongoing",
    count: 2,
    percentage: 50,
  },
  {
    name: "Completed",
    count: 1,
    percentage: 25,
  },
];

export default function Dashboard() {
  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <span className="eyebrow">PLATFORM OVERVIEW</span>
          <h1>KPAP Dashboard</h1>
          <p>
            An overview of public finance information,
            development projects and citizen participation.
          </p>
        </div>
      </div>

      <div className="demo-notice">
        Demonstration dashboard: These figures are sample values,
        not official or verified government statistics.
      </div>

      <div className="dashboard-stats">
        {dashboardStats.map((stat) => {
          const Icon = stat.icon;

          return (
            <article
              className="dashboard-stat-card"
              key={stat.title}
            >
              <div className="dashboard-stat-icon">
                <Icon size={25} />
              </div>

              <p>{stat.title}</p>

              <h2>{stat.value}</h2>

              <span>{stat.description}</span>
            </article>
          );
        })}
      </div>

      <section className="dashboard-section budget-chart-section">
        <div className="dashboard-section-heading">
          <span className="eyebrow">FINANCIAL OVERVIEW</span>
          <h2>Budget Allocation Breakdown</h2>
          <p>
            Distribution of illustrative budget allocations
            across four categories.
          </p>
        </div>

        <div className="budget-chart-card">
          {budgetBreakdown.map((item) => (
            <div className="budget-bar-item" key={item.name}>
              <div className="budget-bar-heading">
                <strong>{item.name}</strong>
                <span>{item.amount}</span>
              </div>

              <div className="budget-bar-track">
                <div
                  className="budget-bar-fill"
                  style={{
                    width: `${item.percentage}%`,
                  }}
                />
              </div>

              <small>
                {item.percentage}% of total allocation
              </small>
            </div>
          ))}
        </div>
      </section>

      <section className="dashboard-section">
  <div className="dashboard-section-heading">
    <span className="eyebrow">PROJECT MONITORING</span>
    <h2>Development Project Status</h2>
    <p>
      Overview of the current status of demonstration
      development projects.
    </p>
  </div>

  <div className="project-status-grid">
    {projectStatusSummary.map((item) => (
      <div className="project-status-card" key={item.name}>
  <h3>{item.name}</h3>

  <strong>{item.count}</strong>

  <p>Demonstration projects</p>

  <div className="project-progress-track">
    <div
      className="project-progress-fill"
      style={{ width: `${item.percentage}%` }}
    />
  </div>

  <small>{item.percentage}% of all projects</small>
</div>
    ))}
  </div>
</section>

      <section className="dashboard-section">
        <div className="dashboard-section-heading">
          <div>
            <span className="eyebrow">QUICK ACCESS</span>
            <h2>Explore KPAP</h2>
            <p>
              Go directly to the platform's main sections.
            </p>
          </div>
        </div>

        <div className="dashboard-links">
          <Link
            to="/budgets"
            className="dashboard-link-card"
          >
            <Wallet size={25} />
            <h3>Public Budgets</h3>
            <p>Explore sample budget allocations.</p>
            <span>
              View budgets <ArrowRight size={16} />
            </span>
          </Link>

          <Link
            to="/projects"
            className="dashboard-link-card"
          >
            <Building2 size={25} />
            <h3>Development Projects</h3>
            <p>
              Review project records and reported progress.
            </p>
            <span>
              View projects <ArrowRight size={16} />
            </span>
          </Link>

          <Link
            to="/reports"
            className="dashboard-link-card"
          >
            <FileText size={25} />
            <h3>Citizen Reports</h3>
            <p>Explore demonstration citizen reports.</p>
            <span>
              View reports <ArrowRight size={16} />
            </span>
          </Link>
        </div>
      </section>

      <section className="dashboard-note">
        <TrendingUp size={25} />

        <div>
          <h3>Building public transparency</h3>
          <p>
            KPAP aims to make public information easier to
            access, understand and review. Information should
            be verified before being presented as fact.
          </p>
        </div>
      </section>
    </div>
  );
}
