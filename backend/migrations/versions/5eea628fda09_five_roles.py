"""five roles

Revision ID: 5eea628fda09
Revises: ded157940337
"""
from alembic import op
import sqlalchemy as sa

revision = "5eea628fda09"
down_revision = "ded157940337"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.alter_column("users", "role", type_=sa.String(30), existing_type=sa.String(20))
    op.execute("UPDATE users SET role = 'administrator' WHERE role = 'admin'")
    op.execute("UPDATE users SET role = 'auditor_reviewer' WHERE role = 'reviewer'")
    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role IN ('administrator','auditor_reviewer','citizen',"
        "'journalist_researcher','government_officer')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.execute("UPDATE users SET role = 'admin' WHERE role = 'administrator'")
    op.execute("UPDATE users SET role = 'reviewer' WHERE role = 'auditor_reviewer'")
    op.execute(
        "UPDATE users SET role = 'citizen' "
        "WHERE role IN ('journalist_researcher','government_officer')"
    )
    op.alter_column("users", "role", type_=sa.String(20), existing_type=sa.String(30))
    op.create_check_constraint(
        "ck_users_role", "users", "role IN ('admin','reviewer','citizen')"
    )
