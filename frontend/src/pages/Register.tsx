
import { useState, type FormEvent } from "react";
import {
  User,
  Mail,
  MapPin,
  Lock,
  Eye,
  EyeOff,
  ShieldCheck,
  UserPlus,
  CheckCircle,
} from "lucide-react";

export default function Register() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [county, setCounty] = useState("");
  const [role, setRole] = useState("Citizen");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  
const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
  event.preventDefault();

  setError("");
  setSuccess(false);

  if (fullName.trim().length < 2) {
    setError("Please enter your full name.");
    return;
  }

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailPattern.test(email.trim())) {
    setError("Please enter a valid email address.");
    return;
  }

  if (county.trim().length < 2) {
    setError("Please enter a valid county.");
    return;
  }

  if (password.length < 12) {
    setError("Your password must contain at least 12 characters.");
    return;
  }

  if (password !== confirmPassword) {
    setError("Your passwords do not match.");
    return;
  }

  setSuccess(true);
};


  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-intro">
          <div className="auth-logo">
            <ShieldCheck size={32} />
          </div>

          <span className="eyebrow">KENYA PUBLIC ACCOUNTABILITY PLATFORM</span>

          <h1>Create Your Account</h1>

          <p>
            Join a platform that makes public information more accessible
            and encourages transparency and accountability.
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <h2>Registration Details</h2>

          <p className="auth-form-description">
            Enter your details to get started.
          </p>

          <div className="auth-field">
            <label htmlFor="fullName">Full Name</label>

            <div className="auth-input-wrapper">
              <User size={18} />
              <input
                id="fullName"
                type="text"
                placeholder="Enter your full name"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                required
                autoComplete="name"
              />
            </div>
          </div>

          <div className="auth-field">
            <label htmlFor="email">Email Address</label>

            <div className="auth-input-wrapper">
              <Mail size={18} />
              <input
                id="email"
                type="email"
                placeholder="Enter your email address"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                autoComplete="email"
              />
            </div>
          </div>

          <div className="auth-field">
            <label htmlFor="county">County</label>

            <div className="auth-input-wrapper">
              <MapPin size={18} />
              <input
                id="county"
                type="text"
                placeholder="Enter your county"
                value={county}
                onChange={(event) => setCounty(event.target.value)}
                required
              />
            </div>
          </div>

          
<div className="auth-field">
  <label htmlFor="role">Account Type</label>

  <select
    id="role"
    value={role}
    onChange={(event) => setRole(event.target.value)}
    required
  >
    <option value="Citizen">Citizen</option>
    <option value="Journalist/Researcher">
      Journalist / Researcher
    </option>
  </select>

  <small>
    Government officers, auditors and administrators must
    receive approval before accessing restricted accounts.
  </small>
</div>

<div className="role-information">
  <ShieldCheck size={20} />

  <div>
    <strong>Account Access and Permissions</strong>

    <p>
      Your account type determines which platform features
      you can access. Restricted roles require verification
      and administrator approval.
    </p>
  </div>
</div>


          <div className="auth-field">
            <label htmlFor="password">Password</label>

            <div className="auth-input-wrapper">
              <Lock size={18} />

              <input
                id="password"
                type={showPassword ? "text" : "password"}
                placeholder="Create a password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                minLength={12}
                autoComplete="new-password"
              />

              <button
                type="button"
                className="auth-password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>

            <small>Use at least 12 characters.</small>
          </div>

          <div className="auth-field">
            <label htmlFor="confirmPassword">Confirm Password</label>

            <div className="auth-input-wrapper">
              <Lock size={18} />

              <input
                id="confirmPassword"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
                autoComplete="new-password"
              />

              <button
                type="button"
                className="auth-password-toggle"
                onClick={() =>
                  setShowConfirmPassword(!showConfirmPassword)
                }
                aria-label={
                  showConfirmPassword
                    ? "Hide confirmation password"
                    : "Show confirmation password"
                }
              >
                {showConfirmPassword ? (
                  <EyeOff size={18} />
                ) : (
                  <Eye size={18} />
                )}
              </button>
            </div>
          </div>

          <label className="auth-privacy">
            <input type="checkbox" required />
            <span>
              I acknowledge the platform's privacy notice and agree to the
              responsible use of this service.
            </span>
          </label>

          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}

          {success && (
            <div className="auth-success">
              <CheckCircle size={19} />
              <span>
                Registration form completed successfully! This is temporary
                demonstration data. No account has been created yet.
              </span>
            </div>
          )}

          <button type="submit" className="auth-submit-button">
            <UserPlus size={19} />
            Create Account
          </button>

          <p className="auth-footer">
            Already have an account?{" "}
            <a href="/login">Sign in</a>
          </p>
        </form>

        <div className="auth-security-note">
          <ShieldCheck size={19} />
          <span>
            Your account security and personal information are important
            to us.
          </span>
        </div>
      </div>
    </div>
  );
}
