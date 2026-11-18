
import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  ShieldCheck,
  LogIn,
  CheckCircle,
} from "lucide-react";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  
const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
  event.preventDefault();

  setError("");
  setSuccess(false);

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  if (!emailPattern.test(email.trim())) {
    setError("Please enter a valid email address.");
    return;
  }

  if (password.length < 12) {
    setError("Your password must contain at least 12 characters.");
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

          <span className="eyebrow">
            KENYA PUBLIC ACCOUNTABILITY PLATFORM
          </span>

          <h1>Welcome Back</h1>

          <p>
            Sign in to access your account and stay informed
            about public projects, budgets and accountability.
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <h2>Sign In</h2>

          <p className="auth-form-description">
            Enter your account details below.
          </p>

          <div className="auth-field">
            <label htmlFor="loginEmail">Email Address</label>

            <div className="auth-input-wrapper">
              <Mail size={18} />

              <input
                id="loginEmail"
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
            <label htmlFor="loginPassword">Password</label>

            <div className="auth-input-wrapper">
              <Lock size={18} />

              <input
                id="loginPassword"
                type={showPassword ? "text" : "password"}
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                autoComplete="current-password"
              />

              <button
                type="button"
                className="auth-password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <EyeOff size={18} />
                ) : (
                  <Eye size={18} />
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}

          {success && (
            <div className="auth-success">
              <CheckCircle size={19} />
              <span>
                Sign-in form submitted successfully for demonstration.
                Actual authentication is not connected yet.
              </span>
            </div>
          )}

          <button type="submit" className="auth-submit-button">
            <LogIn size={19} />
            Sign In
          </button>

          <p className="auth-footer">
            Don't have an account?{" "}
            <Link to="/register">Create Account</Link>
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
