"""Add document listing performance indexes

Revision ID: 20260417_01
Revises: 20260414_01
Create Date: 2026-04-17 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260417_01"
down_revision = "20260414_01"
branch_labels = None
depends_on = None


INDEX_ACTIVE_CREATED_ID = "idx_documents_active_created_id"
INDEX_USER_ACTIVE_CREATED_ID = "idx_documents_user_active_created_id"
INDEX_USER_STATUS_ACTIVE_CREATED_ID = "idx_documents_user_status_active_created_id"


def _index_exists(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _index_exists("documents", INDEX_ACTIVE_CREATED_ID):
        op.create_index(
            INDEX_ACTIVE_CREATED_ID,
            "documents",
            ["created_at", "id"],
            unique=False,
            postgresql_where=sa.text("deleted_at IS NULL"),
        )

    if not _index_exists("documents", INDEX_USER_ACTIVE_CREATED_ID):
        op.create_index(
            INDEX_USER_ACTIVE_CREATED_ID,
            "documents",
            ["user_id", "created_at", "id"],
            unique=False,
            postgresql_where=sa.text("deleted_at IS NULL"),
        )

    if not _index_exists("documents", INDEX_USER_STATUS_ACTIVE_CREATED_ID):
        op.create_index(
            INDEX_USER_STATUS_ACTIVE_CREATED_ID,
            "documents",
            ["user_id", "status", "created_at", "id"],
            unique=False,
            postgresql_where=sa.text("deleted_at IS NULL"),
        )


def downgrade() -> None:
    if _index_exists("documents", INDEX_USER_STATUS_ACTIVE_CREATED_ID):
        op.drop_index(INDEX_USER_STATUS_ACTIVE_CREATED_ID, table_name="documents")

    if _index_exists("documents", INDEX_USER_ACTIVE_CREATED_ID):
        op.drop_index(INDEX_USER_ACTIVE_CREATED_ID, table_name="documents")

    if _index_exists("documents", INDEX_ACTIVE_CREATED_ID):
        op.drop_index(INDEX_ACTIVE_CREATED_ID, table_name="documents")
