
import {
  Wallet,
  Search,
  Filter,
  TrendingUp,
  Building2,
  Landmark,
  Plus,
} from "lucide-react";

import { useState, type FormEvent } from "react";

type Budget = {
  id: number;
  name: string;
  level: string;
  sector: string;
  financialYear: string;
  allocation: number;
  description: string;
  status: string;
};

const sampleBudgets: Budget[] = [
  {
    id: 1,
    name: "National Government",
    level: "National",
    sector: "General Government",
    financialYear: "2026/2027",
    allocation: 1000000000,
    description: "Illustrative national government allocation.",
    status: "Demonstration data",
  },
  {
    id: 2,
    name: "Education Development",
    level: "National",
    sector: "Education",
    financialYear: "2026/2027",
    allocation: 500000000,
    description: "Illustrative education development allocation.",
    status: "Demonstration data",
  },
  {
    id: 3,
    name: "Healthcare Services",
    level: "County",
    sector: "Healthcare",
    financialYear: "2026/2027",
    allocation: 250000000,
    description: "Illustrative healthcare services allocation.",
    status: "Demonstration data",
  },
  {
    id: 4,
    name: "Road Infrastructure",
    level: "County",
    sector: "Infrastructure",
    financialYear: "2026/2027",
    allocation: 150000000,
    description: "Illustrative road infrastructure allocation.",
    status: "Demonstration data",
  },
];

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-KE", {
    style: "currency",
    currency: "KES",
    maximumFractionDigits: 0,
  }).format(amount);
}

export default function Budgets() {
  const [budgets, setBudgets] = useState<Budget[]>(sampleBudgets);

  const [search, setSearch] = useState("");
  const [level, setLevel] = useState("All");

  const [showForm, setShowForm] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  const [name, setName] = useState("");
  const [governmentLevel, setGovernmentLevel] = useState("National");
  const [sector, setSector] = useState("Education");
  const [financialYear, setFinancialYear] = useState("2026/2027");
  const [allocation, setAllocation] = useState("");
  const [description, setDescription] = useState("");

  const filteredBudgets = budgets.filter((budget) => {
    const searchText = search.toLowerCase();

    const matchesSearch =
      budget.name.toLowerCase().includes(searchText) ||
      budget.sector.toLowerCase().includes(searchText);

    const matchesLevel =
      level === "All" || budget.level === level;

    return matchesSearch && matchesLevel;
  });

  const totalAllocation = budgets.reduce(
    (total, budget) => total + budget.allocation,
    0,
  );

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const amount = Number(allocation);

    if (!name.trim() || !description.trim() || !allocation) {
      return;
    }

    if (!Number.isFinite(amount) || amount <= 0) {
      return;
    }

    const newBudget: Budget = {
      id: Math.max(0, ...budgets.map((budget) => budget.id)) + 1,
      name: name.trim(),
      level: governmentLevel,
      sector,
      financialYear,
      allocation: amount,
      description: description.trim(),
      status: "Demonstration data",
    };

    setBudgets((currentBudgets) => [
      newBudget,
      ...currentBudgets,
    ]);

    setSearch("");
    setLevel("All");
    setName("");
    setGovernmentLevel("National");
    setSector("Education");
    setFinancialYear("2026/2027");
    setAllocation("");
    setDescription("");
    setShowForm(false);

    setSuccessMessage(
      "Budget record added successfully. This record is temporary demonstration data.",
    );
  }

  return (
    <div className="budgets-page">
      <div className="budgets-header">
        <div>
          <span className="eyebrow">
            PUBLIC FINANCE TRANSPARENCY
          </span>
          <h1>Public Budgets</h1>
          <p>
            Explore budget allocations and understand how public
            resources are planned.
          </p>
        </div>

        <div className="budget-header-icon">
          <Wallet size={42} />
        </div>
      </div>

      <div className="demo-notice">
        Demonstration only: The figures below are fictional and are
        not official Kenyan government budget figures. New records
        are temporary and are not saved to a database.
      </div>

      <div className="budget-summary">
        <article className="budget-summary-card">
          <Wallet size={25} />
          <span>Total sample allocations</span>
          <h2>{formatCurrency(totalAllocation)}</h2>
        </article>

        <article className="budget-summary-card">
          <Landmark size={25} />
          <span>Budget records</span>
          <h2>{budgets.length}</h2>
        </article>

        <article className="budget-summary-card">
          <TrendingUp size={25} />
          <span>Financial year</span>
          <h2>Multiple years</h2>
        </article>
      </div>

      <div className="budget-actions">
        <button
          type="button"
          className="add-budget-button"
          onClick={() => {
            setShowForm((current) => !current);
            setSuccessMessage("");
          }}
        >
          <Plus size={19} />
          {showForm ? "Close Form" : "Add Budget Record"}
        </button>
      </div>

      {successMessage && (
        <div className="budget-success-message" role="status">
          {successMessage}
        </div>
      )}

      {showForm && (
        <section className="budget-form-section">
          <div className="budget-form-heading">
            <h2>Add a New Budget Record</h2>
            <p>
              Enter the details below to add a demonstration
              budget record.
            </p>
          </div>

          <form
            className="budget-entry-form"
            onSubmit={handleSubmit}
          >
            <div className="budget-form-grid">
              <div className="budget-form-field">
                <label htmlFor="budget-name">
                  Budget Title
                </label>
                <input
                  id="budget-name"
                  type="text"
                  placeholder="e.g. School Development Programme"
                  value={name}
                  onChange={(event) =>
                    setName(event.target.value)
                  }
                  maxLength={120}
                  required
                />
              </div>

              <div className="budget-form-field">
                <label htmlFor="government-level">
                  Government Level
                </label>
                <select
                  id="government-level"
                  value={governmentLevel}
                  onChange={(event) =>
                    setGovernmentLevel(event.target.value)
                  }
                >
                  <option value="National">National</option>
                  <option value="County">County</option>
                </select>
              </div>

              <div className="budget-form-field">
                <label htmlFor="budget-sector">
                  Budget Sector
                </label>
                <select
                  id="budget-sector"
                  value={sector}
                  onChange={(event) =>
                    setSector(event.target.value)
                  }
                >
                  <option value="Education">Education</option>
                  <option value="Healthcare">Healthcare</option>
                  <option value="Infrastructure">Infrastructure</option>
                  <option value="Agriculture">Agriculture</option>
                  <option value="Water">Water</option>
                  <option value="Security">Security</option>
                  <option value="General Government">
                    General Government
                  </option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div className="budget-form-field">
                <label htmlFor="financial-year">
                  Financial Year
                </label>
                <select
                  id="financial-year"
                  value={financialYear}
                  onChange={(event) =>
                    setFinancialYear(event.target.value)
                  }
                >
                  <option value="2025/2026">2025/2026</option>
                  <option value="2026/2027">2026/2027</option>
                  <option value="2027/2028">2027/2028</option>
                  <option value="2028/2029">2028/2029</option>
                </select>
              </div>

              <div className="budget-form-field">
                <label htmlFor="budget-allocation">
                  Allocation Amount (KES)
                </label>
                <input
                  id="budget-allocation"
                  type="number"
                  placeholder="e.g. 50000000"
                  value={allocation}
                  onChange={(event) =>
                    setAllocation(event.target.value)
                  }
                  min="1"
                  step="1"
                  required
                />
              </div>

              <div className="budget-form-field budget-description-field">
                <label htmlFor="budget-description">
                  Description
                </label>
                <textarea
                  id="budget-description"
                  placeholder="Describe the purpose of this budget allocation..."
                  value={description}
                  onChange={(event) =>
                    setDescription(event.target.value)
                  }
                  minLength={10}
                  maxLength={500}
                  rows={4}
                  required
                />
              </div>
            </div>

            <div className="budget-form-actions">
              <button
                type="button"
                className="cancel-budget-button"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="add-budget-button"
              >
                <Plus size={18} />
                Save Budget Record
              </button>
            </div>
          </form>
        </section>
      )}

      <div className="budget-tools">
        <div className="budget-search">
          <Search size={19} />
          <input
            type="search"
            placeholder="Search budget categories..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>

        <div className="budget-filter">
          <Filter size={18} />
          <select
            value={level}
            onChange={(event) => setLevel(event.target.value)}
          >
            <option value="All">All government levels</option>
            <option value="National">National</option>
            <option value="County">County</option>
          </select>
        </div>
      </div>

      <div className="budget-table-container">
        <div className="budget-table-heading">
          <h2>Budget Allocations</h2>
          <span>{filteredBudgets.length} records found</span>
        </div>

        <table className="budget-table">
          <thead>
            <tr>
              <th>Budget Category</th>
              <th>Government Level</th>
              <th>Sector</th>
              <th>Financial Year</th>
              <th>Allocation</th>
              <th>Data Status</th>
            </tr>
          </thead>

          <tbody>
            {filteredBudgets.map((budget) => (
              <tr key={budget.id}>
                <td>
                  <div className="budget-name">
                    <Building2 size={19} />
                    {budget.name}
                  </div>
                </td>

                <td>{budget.level}</td>
                <td>{budget.sector}</td>
                <td>{budget.financialYear}</td>

                <td className="budget-amount">
                  {formatCurrency(budget.allocation)}
                </td>

                <td>
                  <span className="demo-status">
                    {budget.status}
                  </span>
                </td>
              </tr>
            ))}

            {filteredBudgets.length === 0 && (
              <tr>
                <td colSpan={6} className="empty-results">
                  No matching budget records found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
