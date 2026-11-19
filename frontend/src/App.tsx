
import {
  Menu,
  ArrowRight,
  ShieldCheck,
  Wallet,
  Building2,
  FileText,
  Eye,
} from "lucide-react";

import { Link, Routes, Route } from "react-router-dom";

import Budgets from "./pages/Budgets";
import Projects from "./pages/Projects";
import Reports from "./pages/Reports";
import { useState } from "react";
import { hasPermission } from "./auth/roles";
import type { UserRole } from "./auth/roles";
import ProtectedRoute from "./auth/ProtectedRoute";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import SubmitReport from "./pages/SubmitReport";
import Register from "./pages/Register";

import "./App.css";

function HomePage() {
  return (
    <main>
      {/* HERO SECTION */}
      <section className="hero-section">
        <div className="hero-content">
          <span className="eyebrow">
            TRANSPARENCY • ACCOUNTABILITY • TRUST
          </span>

          <h1>
            Public Money.
            <br />
            <span>Public Knowledge.</span>
          </h1>

          <p>
            Making Kenya's public finances easier to understand.
            Explore budgets, track public projects and participate
            in building accountable communities.
          </p>

          <div className="hero-actions">
            <Link to="/budgets" className="primary-btn">
              Explore Public Funds <ArrowRight size={18} />
            </Link>

            <a href="/#about" className="secondary-btn">
              Learn More
            </a>
          </div>

          <div className="trust-note">
            <ShieldCheck size={19} />
            <span>
              Promoting informed public participation
            </span>
          </div>
        </div>

        <div className="hero-visual">
          <div className="visual-card">
            <div className="visual-icon">
              <Wallet size={35} />
            </div>

            <h3>Follow Public Funds</h3>

            <p>
              Understand how public resources are allocated.
            </p>

            <div className="visual-line"></div>

            <div className="visual-icon teal">
              <Building2 size={35} />
            </div>

            <h3>Track Development</h3>

            <p>
              Explore projects and their reported progress.
            </p>
          </div>
        </div>
      </section>

      {/* ACCOUNTABILITY OVERVIEW */}
      <section className="stats-section" id="budgets">
        <div className="section-heading">
          <span className="eyebrow">THE BIG PICTURE</span>

          <h2>Explore Public Accountability</h2>

          <p>
            Access information that helps citizens understand
            public spending and development.
          </p>
        </div>

        <div className="stats-grid">
          <article className="stat-card">
            <Wallet size={28} />

            <h3>Public Budgets</h3>

            <p>
              Explore allocations and understand how budgets are planned.
            </p>

            <Link to="/budgets">
              Explore budgets <ArrowRight size={16} />
            </Link>
          </article>

          <article className="stat-card">
            <Building2 size={28} />

            <h3>Development Projects</h3>

            <p>
              Follow public projects and review reported progress.
            </p>

            <Link to="/projects">
              View projects <ArrowRight size={16} />
            </Link>
          </article>

          <article className="stat-card">
            <FileText size={28} />

            <h3>Public Reports</h3>

            <p>
              Find reports and information relevant to public accountability.
            </p>

            <Link to="/reports">
              Read reports <ArrowRight size={16} />
            </Link>
          </article>

          <article className="stat-card">
            <Eye size={28} />

            <h3>Citizen Participation</h3>

            <p>
              Learn how to raise concerns and contribute information.
            </p>

            <Link to="/reports">
              Get involved <ArrowRight size={16} />
            </Link>
          </article>
        </div>
      </section>

      {/* ABOUT SECTION */}
      <section className="about-section" id="about">
        <div>
          <span className="eyebrow">OUR PURPOSE</span>

          <h2>
            Accountability starts with access to information.
          </h2>
        </div>

        <p>
          KPAP aims to make public information more accessible,
          understandable and useful to citizens, journalists,
          researchers and public institutions.
        </p>
      </section>

      {/* PROJECTS SECTION */}
      <section className="projects-section" id="projects">
        <span className="eyebrow">PUBLIC DEVELOPMENT</span>

        <h2>
          Follow projects that matter to communities.
        </h2>

        <p>
          Explore project records, reported budgets, locations and
          progress updates as verified information becomes available.
        </p>

        <Link to="/projects" className="primary-btn">
          Explore Project Information <ArrowRight size={18} />
        </Link>
      </section>

      {/* REPORT SECTION */}
      <section className="report-section" id="reports">
        <div>
          <span className="eyebrow">YOUR VOICE MATTERS</span>

          <h2>
            Help strengthen public accountability.
          </h2>

          <p>
            Share a concern or information about a public project.
            Reports will be reviewed before any information is
            presented as verified.
          </p>
        </div>

        <Link to="/reports" className="report-btn">
          Submit a Report <ArrowRight size={18} />
        </Link>
      </section>
    </main>
  );
}

function App() {
  const [currentUserRole, setCurrentUserRole] = useState<UserRole | null>(null);
  return (
    <div className="app">

      {/* MAIN NAVIGATION */}
      <header className="navbar">
        <Link to="/" className="brand">
          <ShieldCheck size={32} />

          <span>
            KPAP
            <small>Kenya Public Accountability</small>
          </span>
        </Link>

        <nav className="nav-links" aria-label="Main navigation">
  <Link to="/#about">About</Link>

  <Link to="/dashboard">Dashboard</Link>

  {hasPermission(
    currentUserRole ?? "citizen",
    "view_public_information"
  ) && (
    <>
      <Link to="/budgets">Public Budgets</Link>
      <Link to="/projects">Projects</Link>
    </>
  )}

  {currentUserRole &&
    hasPermission(currentUserRole, "submit_reports") && (
      <Link to="/submit-report">Submit a Report</Link>
    )}

  {currentUserRole &&
    hasPermission(currentUserRole, "review_citizen_reports") && (
      <Link to="/reports">Citizen Reports</Link>
    )}
</nav>

       <div className="nav-actions">
  <div className="demo-role-switcher">
    <label htmlFor="demo-role">Development demo role</label>

    <select
      id="demo-role"
      value={currentUserRole ?? ""}
      onChange={(event) =>
        setCurrentUserRole(
          event.target.value
            ? (event.target.value as UserRole)
            : null
        )
      }
    >
      <option value="">Signed out</option>
      <option value="citizen">Citizen</option>
      <option value="journalist_researcher">
        Journalist / Researcher
      </option>
      <option value="government_officer">
        Government Officer
      </option>
      <option value="auditor_reviewer">
        Auditor / Reviewer
      </option>
      <option value="administrator">Administrator</option>
    </select>

    <small>Testing only — not real authentication</small>
  </div>

  <Link to="/login" className="login-btn">
    Sign In
  </Link>

  <Link to="/register" className="report-btn">
    Create Account
  </Link>
</div>

        <button className="mobile-menu" aria-label="Open menu">
          <Menu />
        </button>
      </header>

      {/* PAGE ROUTES */}
      <Routes>
        <Route path="/" element={<HomePage />} />

        <Route path="/budgets" element={<Budgets />} />

        <Route path="/projects" element={<Projects />} />

        <Route path="/submit-report" element={<SubmitReport />} />

        <Route path="/login" element={<Login />} />

        <Route
  path="/reports"
  element={
    <ProtectedRoute
      role={currentUserRole}
      permission="review_citizen_reports"
    >
      <Reports />
    </ProtectedRoute>
  }
/>

        <Route path="/dashboard" element={<Dashboard />} />

        <Route path="/register" element={<Register />} />

        <Route
          path="*"
          element={
            <main className="budgets-page">
              <h1>Page not found</h1>

              <Link to="/">
                Return to homepage
              </Link>
            </main>
          }
        />
      </Routes>

      {/* FOOTER */}
      <footer className="footer">
        <strong>KPAP</strong>

        <p>
          Making public information accessible to everyone.
        </p>

        <small>
          Demonstration platform — sample content is not official government data.
        </small>
      </footer>

    </div>
  );
}

export default App;
