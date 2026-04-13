"""Create documents and document_permissions tables

Revision ID: 20260413_01
Revises: 20260409_01
Create Date: 2026-04-13 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260413_01"
down_revision = "20260409_01"
branch_labels = None
depends_on = None


DOCUMENT_USER_FK_NAME = "fk_documents_user_id"
DOCUMENT_STATUS_CHECK_NAME = "ck_documents_status"
DOCUMENT_USER_INDEX_NAME = "ix_documents_user_id"
DOCUMENT_USER_STATUS_INDEX_NAME = "idx_documents_user_status"
DOCUMENT_EFFECTIVE_DATE_INDEX_NAME = "idx_documents_effective_date"
DOCUMENT_ACTIVE_HASH_UNIQUE_INDEX_NAME = "uq_documents_user_hash_active"

DOCUMENT_PERMISSION_ROLE_FK_NAME = "fk_document_permissions_role_id"
DOCUMENT_PERMISSION_DOCUMENT_FK_NAME = "fk_document_permissions_document_id"
DOCUMENT_PERMISSION_ROLE_INDEX_NAME = "ix_document_permissions_role_id"
DOCUMENT_PERMISSION_DOCUMENT_INDEX_NAME = "ix_document_permissions_document_id"
DOCUMENT_PERMISSION_UNIQUE_NAME = "uq_role_document_permission"


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


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


def _check_constraint_exists(table_name: str, constraint_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return constraint_name in {
        constraint["name"] for constraint in inspector.get_check_constraints(table_name)
    }


def _unique_constraint_exists(table_name: str, constraint_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return constraint_name in {
        constraint["name"] for constraint in inspector.get_unique_constraints(table_name)
    }


def upgrade() -> None:
    if not _table_exists("documents"):
        op.create_table(
            "documents",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("filename", sa.String(), nullable=False),
            sa.Column("file_url", sa.String(), nullable=False),
            sa.Column("file_size_bytes", sa.BIGINT(), nullable=True),
            sa.Column("mime_type", sa.String(), nullable=True),
            sa.Column("file_hash", sa.String(), nullable=False),
            sa.Column("effective_date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("status", sa.String(), server_default=sa.text("'pending'"), nullable=False),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.CheckConstraint(
                "status IN ('pending', 'processing', 'ready', 'failed', 'deleted')",
                name=DOCUMENT_STATUS_CHECK_NAME,
            ),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name=DOCUMENT_USER_FK_NAME,
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
        )
    else:
        if not _fk_exists("documents", ["user_id"], "users"):
            op.create_foreign_key(
                DOCUMENT_USER_FK_NAME,
                "documents",
                "users",
                ["user_id"],
                ["id"],
                ondelete="CASCADE",
            )

        if not _check_constraint_exists("documents", DOCUMENT_STATUS_CHECK_NAME):
            op.create_check_constraint(
                DOCUMENT_STATUS_CHECK_NAME,
                "documents",
                "status IN ('pending', 'processing', 'ready', 'failed', 'deleted')",
            )

    if not _index_exists("documents", DOCUMENT_USER_INDEX_NAME):
        op.create_index(DOCUMENT_USER_INDEX_NAME, "documents", ["user_id"], unique=False)

    if not _index_exists("documents", DOCUMENT_USER_STATUS_INDEX_NAME):
        op.create_index(
            DOCUMENT_USER_STATUS_INDEX_NAME,
            "documents",
            ["user_id", "status"],
            unique=False,
        )

    if not _index_exists("documents", DOCUMENT_EFFECTIVE_DATE_INDEX_NAME):
        op.create_index(
            DOCUMENT_EFFECTIVE_DATE_INDEX_NAME,
            "documents",
            ["effective_date"],
            unique=False,
        )

    if not _index_exists("documents", DOCUMENT_ACTIVE_HASH_UNIQUE_INDEX_NAME):
        op.create_index(
            DOCUMENT_ACTIVE_HASH_UNIQUE_INDEX_NAME,
            "documents",
            ["user_id", "file_hash"],
            unique=True,
            postgresql_where=sa.text("deleted_at IS NULL"),
        )

    if not _table_exists("document_permissions"):
        op.create_table(
            "document_permissions",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.ForeignKeyConstraint(
                ["role_id"],
                ["roles.id"],
                name=DOCUMENT_PERMISSION_ROLE_FK_NAME,
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["document_id"],
                ["documents.id"],
                name=DOCUMENT_PERMISSION_DOCUMENT_FK_NAME,
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("role_id", "document_id", name=DOCUMENT_PERMISSION_UNIQUE_NAME),
        )
    else:
        if not _fk_exists("document_permissions", ["role_id"], "roles"):
            op.create_foreign_key(
                DOCUMENT_PERMISSION_ROLE_FK_NAME,
                "document_permissions",
                "roles",
                ["role_id"],
                ["id"],
                ondelete="CASCADE",
            )

        if not _fk_exists("document_permissions", ["document_id"], "documents"):
            op.create_foreign_key(
                DOCUMENT_PERMISSION_DOCUMENT_FK_NAME,
                "document_permissions",
                "documents",
                ["document_id"],
                ["id"],
                ondelete="CASCADE",
            )

        if not _unique_constraint_exists("document_permissions", DOCUMENT_PERMISSION_UNIQUE_NAME):
            op.create_unique_constraint(
                DOCUMENT_PERMISSION_UNIQUE_NAME,
                "document_permissions",
                ["role_id", "document_id"],
            )

    if not _index_exists("document_permissions", DOCUMENT_PERMISSION_ROLE_INDEX_NAME):
        op.create_index(
            DOCUMENT_PERMISSION_ROLE_INDEX_NAME,
            "document_permissions",
            ["role_id"],
            unique=False,
        )

    if not _index_exists("document_permissions", DOCUMENT_PERMISSION_DOCUMENT_INDEX_NAME):
        op.create_index(
            DOCUMENT_PERMISSION_DOCUMENT_INDEX_NAME,
            "document_permissions",
            ["document_id"],
            unique=False,
        )


def downgrade() -> None:
    if _table_exists("document_permissions"):
        op.drop_table("document_permissions")

    if _table_exists("documents"):
        op.drop_table("documents")
