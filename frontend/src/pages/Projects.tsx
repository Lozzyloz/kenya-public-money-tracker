
import {
  Building2,
  MapPin,
  CalendarDays,
  Search,
} from "lucide-react";
import { useState } from "react";

type Project = {
  id: number;
  name: string;
  county: string;
  sector: string;
  financialYear: string;
  status: string;
};

const sampleProjects: Project[] = [
  {
    id: 1,
    name: "Community Health Centre",
    county: "Tharaka Nithi",
    sector: "Healthcare",
    financialYear: "2026/2027",
    status: "Ongoing",
  },
  {
    id: 2,
    name: "Rural Road Improvement",
    county: "Meru",
    sector: "Infrastructure",
    financialYear: "2026/2027",
    status: "Planned",
  },
  {
    id: 3,
    name: "Public Secondary School",
    county: "Embu",
    sector: "Education",
    financialYear: "2026/2027",
    status: "Ongoing",
  },
  {
    id: 4,
    name: "Clean Water Supply",
    county: "Kitui",
    sector: "Water",
    financialYear: "2026/2027",
    status: "Completed",
  },
];

export default function Projects() {
  const [search, setSearch] = useState("");

  const filteredProjects = sampleProjects.filter((project) =>
    `${project.name} ${project.county} ${project.sector}`
      .toLowerCase()
      .includes(search.toLowerCase()),
  );

  return (
    <div className="projects-page">
      <div className="projects-header">
        <div>
          <span className="eyebrow">PUBLIC DEVELOPMENT</span>
          <h1>Development Projects</h1>
          <p>
            Explore public development projects and review
            their reported progress across communities.
          </p>
        </div>

        <Building2 size={45} />
      </div>

      <div className="demo-notice">
        Demonstration only: These projects are fictional sample
        records, not verified government projects.
      </div>

      <div className="project-search">
        <Search size={20} />
        <input
          type="search"
          placeholder="Search projects, counties or sectors..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>

      <div className="project-grid">
        {filteredProjects.map((project) => (
          <article className="project-card" key={project.id}>
            <div className="project-card-icon">
              <Building2 size={25} />
            </div>

            <h2>{project.name}</h2>

            <p>
              <MapPin size={16} />
              {project.county} County
            </p>

            <p>
              <CalendarDays size={16} />
              {project.financialYear}
            </p>

            <div className="project-details">
              <span>{project.sector}</span>
              <span className="project-status">
                {project.status}
              </span>
            </div>
          </article>
        ))}

        {filteredProjects.length === 0 && (
          <p>No matching projects found.</p>
        )}
      </div>
    </div>
  );
}
