
import { useState, type FormEvent } from "react";
import { FileText, Send } from "lucide-react";

export default function SubmitReport() {
  const [projectName, setProjectName] = useState("");
  const [county, setCounty] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (
      !projectName.trim() ||
      !county ||
      !category ||
      !description.trim()
    ) {
      setError("Please complete all required fields.");
      return;
    }

    if (projectName.trim().length < 3) {
      setError("Project name must contain at least 3 characters.");
      return;
    }

    if (description.trim().length < 10) {
      setError("Description must contain at least 10 characters.");
      return;
    }

    if (description.trim().length > 2000) {
      setError("Description cannot exceed 2,000 characters.");
      return;
    }

    setSuccess(
      "Your demonstration report has been submitted successfully!"
    );

    setProjectName("");
    setCounty("");
    setCategory("");
    setDescription("");
  };

  return (
    <main className="submit-report-page">
      <div className="submit-report-container">
        <div className="submit-report-heading">
          <FileText size={35} />
          <span className="eyebrow">CITIZEN PARTICIPATION</span>

          <h1>Submit a Report</h1>

          <p>
            Share a question or concern about a public
            development project. Your feedback can help
            improve transparency and accountability.
          </p>
        </div>

        <div className="demo-notice">
          Demonstration form: Reports are not yet saved
          to a database or sent to government offices.
          Please do not enter private or sensitive information.
        </div>

        <form className="submit-report-form" onSubmit={handleSubmit}>
          {error && (
            <div className="form-error" role="alert">
              {error}
            </div>
          )}

          {success && (
            <div className="form-success" role="status">
              {success}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="projectName">Project Name</label>

            <input
              id="projectName"
              type="text"
              placeholder="Enter the project name"
              value={projectName}
              onChange={(event) => setProjectName(event.target.value)}
              minLength={3}
              maxLength={120}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="county">County</label>

            <select
              id="county"
              value={county}
              onChange={(event) => setCounty(event.target.value)}
              required
            >
              <option value="">Select a county</option>
              <option value="Nairobi">Nairobi</option>
              <option value="Meru">Meru</option>
              <option value="Tharaka Nithi">Tharaka Nithi</option>
              <option value="Embu">Embu</option>
              <option value="Kitui">Kitui</option>
              <option value="Kiambu">Kiambu</option>
              <option value="Kisumu">Kisumu</option>
              <option value="Mombasa">Mombasa</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="category">Report Category</label>

            <select
              id="category"
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              required
            >
              <option value="">Select a category</option>
              <option value="Infrastructure">Infrastructure</option>
              <option value="Education">Education</option>
              <option value="Healthcare">Healthcare</option>
              <option value="Water">Water and Sanitation</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="description">Report Description</label>

            <textarea
              id="description"
              placeholder="Explain your question or concern..."
              rows={6}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              minLength={10}
              maxLength={2000}
              required
            />

            <small>
              {description.length}/2000 characters
            </small>
          </div>

          <button type="submit" className="submit-report-button">
            <Send size={18} />
            Submit Demonstration Report
          </button>
        </form>
      </div>
    </main>
  );
}
