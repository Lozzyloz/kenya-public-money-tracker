from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origins: list[str] = ["http://localhost:5173"]

    upload_dir: str = "uploads"
    # Only enable behind a proxy you control (Nginx, Cloudflare); otherwise
    # clients could spoof their IP address with a header.
    trust_proxy_headers: bool = False
    report_rate_limit: int = 10
    report_rate_window_seconds: int = 3600

    login_fail_limit_email: int = 5
    login_fail_limit_ip: int = 30
    login_window_seconds: int = 900

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
