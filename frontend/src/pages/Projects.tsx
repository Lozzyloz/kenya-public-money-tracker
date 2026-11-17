
import {
  Building2,
  MapPin,
  CalendarDays,
  Search,
  Plus,
  X,
  Filter,
} from "lucide-react";
import { useState, type FormEvent } from "react";

type Project = {
  id: number;
  name: string;
  county: string;
  sector: string;
  financialYear: string;
  status: string;
  description: string;
  budget: number;
  startDate: string;
  completionDate: string;
};

const sampleProjects: Project[] = [
  {
    id: 1,
    name: "Community Health Centre",
    county: "Tharaka Nithi",
    sector: "Healthcare",
    financialYear: "2026/2027",
    status: "Ongoing",
    description:
      "Construction of a community health centre to improve access to healthcare services.",
    budget: 50000000,
    startDate: "2026-07-01",
    completionDate: "2027-06-30",
  },
  {
    id: 2,
    name: "Rural Road Improvement",
    county: "Meru",
    sector: "Infrastructure",
    financialYear: "2026/2027",
    status: "Planned",
    description:
      "Improvement of rural roads to support transportation and local economic activities.",
    budget: 75000000,
    startDate: "2026-08-01",
    completionDate: "2027-05-30",
  },
  {
    id: 3,
    name: "Public Secondary School",
    county: "Embu",
    sector: "Education",
    financialYear: "2026/2027",
    status: "Ongoing",
    description:
      "Development of additional learning facilities in a public secondary school.",
    budget: 35000000,
    startDate: "2026-07-15",
    completionDate: "2027-04-30",
  },
  {
    id: 4,
    name: "Clean Water Supply",
    county: "Kitui",
    sector: "Water",
    financialYear: "2026/2027",
    status: "Completed",
    description:
      "Installation of a clean water supply system to improve access to safe water.",
    budget: 25000000,
    startDate: "2026-01-01",
    completionDate: "2026-10-30",
  },
];

const counties = [
  "Mombasa",
  "Kwale",
  "Kilifi",
  "Tana River",
  "Lamu",
  "Taita Taveta",
  "Garissa",
  "Wajir",
  "Mandera",
  "Marsabit",
  "Isiolo",
  "Meru",
  "Tharaka Nithi",
  "Embu",
  "Kitui",
  "Machakos",
  "Makueni",
  "Nyandarua",
  "Nyeri",
  "Kirinyaga",
  "Murang'a",
  "Kiambu",
  "Turkana",
  "West Pokot",
  "Samburu",
  "Trans Nzoia",
  "Uasin Gishu",
  "Elgeyo Marakwet",
  "Nandi",
  "Baringo",
  "Laikipia",
  "Nakuru",
  "Narok",
  "Kajiado",
  "Kericho",
  "Bomet",
  "Kakamega",
  "Vihiga",
  "Bungoma",
  "Busia",
  "Siaya",
  "Kisumu",
  "Homa Bay",
  "Migori",
  "Kisii",
  "Nyamira",
  "Nairobi",
];

const sectors = [
  "Education",
  "Healthcare",
  "Infrastructure",
  "Water",
  "Agriculture",
  "Energy",
  "Security",
  "Other",
];

const formatCurrency = (amount: number) =>
  new Intl.NumberFormat("en-KE", {
    style: "currency",
    currency: "KES",
    maximumFractionDigits: 0,
  }).format(amount);

const formatDate = (date: string) => {
  if (!date) return "Not provided";

  return new Date(`${date}T00:00:00`).toLocaleDateString("en-KE", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
};

const getTimelineStatus = (project: Project) => {
  if (project.status === "Completed") {
    return "Completed";
  }

  const today = new Date().toISOString().split("T")[0];

  if (today < project.startDate) {
    return "Not Started";
  }

  if (today > project.completionDate) {
    return "Overdue";
  }

  return "In Progress";
};

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>(sampleProjects);

  const [search, setSearch] = useState("");
  const [selectedCounty, setSelectedCounty] = useState("All");
  const [selectedSector, setSelectedSector] = useState("All");
  const [selectedStatus, setSelectedStatus] = useState("All");

  const [showForm, setShowForm] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  const [formData, setFormData] = useState({
    name: "",
    county: "",
    sector: "",
    financialYear: "2026/2027",
    status: "Planned",
    description: "",
    budget: "",
    startDate: "",
    completionDate: "",
  });

  const totalBudget = projects.reduce(
    (total, project) => total + project.budget,
    0,
  );

  const totalProjects = projects.length;

  const plannedProjects = projects.filter(
    (project) => project.status === "Planned",
  ).length;

  const ongoingProjects = projects.filter(
    (project) => project.status === "Ongoing",
  ).length;

  const completedProjects = projects.filter(
    (project) => project.status === "Completed",
  ).length;

  const filteredProjects = projects.filter((project) => {
    const matchesSearch =
      project.name.toLowerCase().includes(search.toLowerCase()) ||
      project.county.toLowerCase().includes(search.toLowerCase()) ||
      project.sector.toLowerCase().includes(search.toLowerCase());

    const matchesCounty =
      selectedCounty === "All" || project.county === selectedCounty;

    const matchesSector =
      selectedSector === "All" || project.sector === selectedSector;

    const matchesStatus =
      selectedStatus === "All" || project.status === selectedStatus;

    return (
      matchesSearch &&
      matchesCounty &&
      matchesSector &&
      matchesStatus
    );
  });

  const handleChange = (
    event: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >,
  ) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const resetForm = () => {
    setFormData({
      name: "",
      county: "",
      sector: "",
      financialYear: "2026/2027",
      status: "Planned",
      description: "",
      budget: "",
      startDate: "",
      completionDate: "",
    });
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const budgetAmount = Number(formData.budget);

    if (!Number.isFinite(budgetAmount) || budgetAmount <= 0) {
      setSuccessMessage("Please enter a valid positive project budget.");
      return;
    }

    if (formData.completionDate < formData.startDate) {
      setSuccessMessage(
        "Expected completion date cannot be earlier than the start date.",
      );
      return;
    }

    const newProject: Project = {
      id: Date.now(),
      ...formData,
      budget: budgetAmount,
    };

    setProjects((previous) => [newProject, ...previous]);

    resetForm();
    setSearch("");
    setSelectedCounty("All");
    setSelectedSector("All");
    setSelectedStatus("All");
    setShowForm(false);

    setSuccessMessage(
      "Project added successfully! This is temporary demonstration data.",
    );
  };

  const clearFilters = () => {
    setSearch("");
    setSelectedCounty("All");
    setSelectedSector("All");
    setSelectedStatus("All");
  };

  return (
    <div className="projects-page">
      <div className="page-header">
        <div>
          <h1>Public Projects</h1>
          <p>
            Track public development projects across Kenya.
          </p>
        </div>
      </div>

      <div className="demo-notice">
        <strong>Demonstration data:</strong> Project records currently shown
        are sample data. Newly registered projects are temporarily stored
        in the browser session.
      </div>

      {successMessage && (
        <div className="project-success-message">
          {successMessage}
          <button
            type="button"
            onClick={() => setSuccessMessage("")}
            aria-label="Close message"
          >
            <X size={16} />
          </button>
        </div>
      )}

      {/* PROJECT SUMMARY */}
      <div className="project-summary-grid">
        <div className="project-summary-card">
          <span>Total Projects</span>
          <h2>{totalProjects}</h2>
          <p>Registered projects</p>
        </div>

        <div className="project-summary-card">
          <span>Total Estimated Budget</span>
          <h2>{formatCurrency(totalBudget)}</h2>
          <p>Combined project allocation</p>
        </div>

        <div className="project-summary-card">
          <span>Ongoing Projects</span>
          <h2>{ongoingProjects}</h2>
          <p>Projects in progress</p>
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

      {/* PROJECT ACTIONS */}
      <div className="project-actions">
        <button
          type="button"
          className="add-project-button"
          onClick={() => {
            setShowForm(!showForm);
            setSuccessMessage("");
          }}
        >
          <Plus size={18} />
          {showForm ? "Close Form" : "Add New Project"}
        </button>
      </div>

      {/* PROJECT REGISTRATION FORM */}
      {showForm && (
        <div className="project-form-section">
          <div className="project-form-heading">
            <h2>Register New Project</h2>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              aria-label="Close form"
            >
              <X size={20} />
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="project-form-grid">
              <div className="project-form-field">
                <label htmlFor="name">Project Name</label>
                <input
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Enter project name"
                  required
                />
              </div>

              <div className="project-form-field">
                <label htmlFor="county">County</label>
                <select
                  id="county"
                  name="county"
                  value={formData.county}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select county</option>
                  {counties.map((county) => (
                    <option key={county} value={county}>
                      {county}
                    </option>
                  ))}
                </select>
              </div>

              <div className="project-form-field">
                <label htmlFor="sector">Sector</label>
                <select
                  id="sector"
                  name="sector"
                  value={formData.sector}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select sector</option>
                  {sectors.map((sector) => (
                    <option key={sector} value={sector}>
                      {sector}
                    </option>
                  ))}
                </select>
              </div>

              <div className="project-form-field">
                <label htmlFor="financialYear">Financial Year</label>
                <select
                  id="financialYear"
                  name="financialYear"
                  value={formData.financialYear}
                  onChange={handleChange}
                >
                  <option value="2025/2026">2025/2026</option>
                  <option value="2026/2027">2026/2027</option>
                  <option value="2027/2028">2027/2028</option>
                  <option value="2028/2029">2028/2029</option>
                </select>
              </div>

              <div className="project-form-field">
                <label htmlFor="budget">Estimated Budget (KES)</label>
                <input
                  id="budget"
                  name="budget"
                  type="number"
                  min="1"
                  value={formData.budget}
                  onChange={handleChange}
                  placeholder="Enter estimated budget"
                  required
                />
              </div>

              <div className="project-form-field">
                <label htmlFor="status">Project Status</label>
                <select
                  id="status"
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                >
                  <option value="Planned">Planned</option>
                  <option value="Ongoing">Ongoing</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>

              <div className="project-form-field">
                <label htmlFor="startDate">Start Date</label>
                <input
                  id="startDate"
                  name="startDate"
                  type="date"
                  value={formData.startDate}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="project-form-field">
                <label htmlFor="completionDate">
                  Expected Completion Date
                </label>
                <input
                  id="completionDate"
                  name="completionDate"
                  type="date"
                  value={formData.completionDate}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="project-form-field project-description-field">
                <label htmlFor="description">Project Description</label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  placeholder="Describe the project..."
                  rows={4}
                  required
                />
              </div>
            </div>

            <div className="project-form-buttons">
              <button type="submit" className="add-project-button">
                Save Project
              </button>

              <button
                type="button"
                className="cancel-project-button"
                onClick={() => {
                  resetForm();
                  setShowForm(false);
                }}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

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
            onChange={(event) => setSelectedCounty(event.target.value)}
          >
            <option value="All">All Counties</option>
            {counties.map((county) => (
              <option key={county} value={county}>
                {county}
              </option>
            ))}
          </select>

          <select
            aria-label="Filter by sector"
            value={selectedSector}
            onChange={(event) => setSelectedSector(event.target.value)}
          >
            <option value="All">All Sectors</option>
            {sectors.map((sector) => (
              <option key={sector} value={sector}>
                {sector}
              </option>
            ))}
          </select>

          <select
            aria-label="Filter by project status"
            value={selectedStatus}
            onChange={(event) => setSelectedStatus(event.target.value)}
          >
            <option value="All">All Statuses</option>
            <option value="Planned">Planned</option>
            <option value="Ongoing">Ongoing</option>
            <option value="Completed">Completed</option>
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
          filteredProjects.map((project) => (
            <div className="project-card" key={project.id}>
              <div className="project-card-top">
                <div className="project-card-icon">
                  <Building2 size={22} />
                </div>

                <span
                  className={`project-status status-${project.status.toLowerCase()}`}
                >
                  {project.status}
                </span>
              </div>

              <h3>{project.name}</h3>

              <div className="project-location">
                <MapPin size={16} />
                <span>{project.county} County</span>
              </div>

              <p className="project-description">
                {project.description}
              </p>

              <div className="project-information">
                <div>
                  <span>Sector</span>
                  <strong>{project.sector}</strong>
                </div>

                <div>
                  <span>Financial Year</span>
                  <strong>{project.financialYear}</strong>
                </div>

                <div>
                  <span>Estimated Budget</span>
                  <strong>{formatCurrency(project.budget)}</strong>
                </div>
              </div>

              {/* TIMELINE STATUS */}
              <div className="project-timeline-status">
                <span>Timeline Status</span>
                <strong
                  className={`timeline-${getTimelineStatus(project)
                    .toLowerCase()
                    .replace(" ", "-")}`}
                >
                  {getTimelineStatus(project)}
                </strong>
              </div>

              <div className="project-timeline">
                <div>
                  <CalendarDays size={16} />
                  <span>
                    Start Date: {formatDate(project.startDate)}
                  </span>
                </div>

                <div>
                  <CalendarDays size={16} />
                  <span>
                    Expected Completion: {formatDate(project.completionDate)}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
