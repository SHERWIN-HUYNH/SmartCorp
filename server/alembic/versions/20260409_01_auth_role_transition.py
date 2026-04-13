"""Auth-safe role transition: add roles table and users.role_id

Revision ID: 20260409_01
Revises:
Create Date: 2026-04-09 00:00:00
"""

from __future__ import annotations

import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260409_01"
down_revision = None
branch_labels = None
depends_on = None


ROLE_INDEX_NAME = "ix_roles_name"
USER_ROLE_INDEX_NAME = "ix_users_role_id"
USER_ROLE_FK_NAME = "fk_users_role_id"


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _index_exists(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def _fk_exists(table_name: str, constrained_columns: list[str], referred_table: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    for foreign_key in inspector.get_foreign_keys(table_name):
        if (
            foreign_key.get("referred_table") == referred_table
            and foreign_key.get("constrained_columns") == constrained_columns
        ):
            return True
    return False


def upgrade() -> None:
    bind = op.get_bind()

    if not _table_exists("roles"):
        op.create_table(
            "roles",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists("roles", ROLE_INDEX_NAME):
        op.create_index(ROLE_INDEX_NAME, "roles", ["name"], unique=True)

    # Seed baseline roles used by auth and permissions.
    bind.execute(
        sa.text(
            """
            INSERT INTO roles (id, name, description)
            VALUES (:id, :name, :description)
            ON CONFLICT (name) DO NOTHING
            """
        ),
        [
            {"id": str(uuid.uuid4()), "name": "user", "description": "Default end-user role"},
            {"id": str(uuid.uuid4()), "name": "admin", "description": "Administrator role"},
        ],
    )

    if _table_exists("users"):
        if not _column_exists("users", "role_id"):
            op.add_column("users", sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=True))

        if not _index_exists("users", USER_ROLE_INDEX_NAME):
            op.create_index(USER_ROLE_INDEX_NAME, "users", ["role_id"], unique=False)

        if not _fk_exists("users", ["role_id"], "roles"):
            op.create_foreign_key(
                USER_ROLE_FK_NAME,
                "users",
                "roles",
                ["role_id"],
                ["id"],
            )

        if _column_exists("users", "role") and _column_exists("users", "role_id"):
            bind.execute(
                sa.text(
                    """
                    UPDATE users AS u
                    SET role_id = r.id
                    FROM roles AS r
                    WHERE u.role_id IS NULL
                      AND u.role = r.name
                    """
                )
            )


def downgrade() -> None:
    if _table_exists("users"):
        if _fk_exists("users", ["role_id"], "roles"):
            op.drop_constraint(USER_ROLE_FK_NAME, "users", type_="foreignkey")

        if _index_exists("users", USER_ROLE_INDEX_NAME):
            op.drop_index(USER_ROLE_INDEX_NAME, table_name="users")

        if _column_exists("users", "role_id"):
            op.drop_column("users", "role_id")

    # Keep roles table/data because other modules may depend on it.
