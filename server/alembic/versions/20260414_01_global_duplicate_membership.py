"""Add document memberships and global active file hash uniqueness

Revision ID: 20260414_01
Revises: 20260413_01
Create Date: 2026-04-14 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260414_01"
down_revision = "20260413_01"
branch_labels = None
depends_on = None

DOCUMENT_OLD_ACTIVE_HASH_UNIQUE_INDEX_NAME = "uq_documents_user_hash_active"
DOCUMENT_GLOBAL_ACTIVE_HASH_UNIQUE_INDEX_NAME = "uq_documents_file_hash_active"

DOCUMENT_MEMBERSHIP_TABLE = "document_memberships"
DOCUMENT_MEMBERSHIP_USER_FK_NAME = "fk_document_memberships_user_id"
DOCUMENT_MEMBERSHIP_DOCUMENT_FK_NAME = "fk_document_memberships_document_id"
DOCUMENT_MEMBERSHIP_USER_INDEX_NAME = "ix_document_memberships_user_id"
DOCUMENT_MEMBERSHIP_DOCUMENT_INDEX_NAME = "ix_document_memberships_document_id"
DOCUMENT_MEMBERSHIP_UNIQUE_NAME = "uq_document_membership_user_document"


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


def _unique_constraint_exists(table_name: str, constraint_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return constraint_name in {
        constraint["name"] for constraint in inspector.get_unique_constraints(table_name)
    }


def _has_active_hash_duplicates() -> bool:
    bind = op.get_bind()
    result = bind.execute(
        sa.text(
            """
            SELECT 1
            FROM documents
            WHERE deleted_at IS NULL
            GROUP BY file_hash
            HAVING COUNT(*) > 1
            LIMIT 1
            """
        )
    ).first()
    return result is not None


def upgrade() -> None:
    if _has_active_hash_duplicates():
        raise RuntimeError(
            "Cannot enforce global unique active file_hash: found duplicate active hashes. "
            "Please merge or soft-delete duplicates before running this migration."
        )

    if not _table_exists(DOCUMENT_MEMBERSHIP_TABLE):
        op.create_table(
            DOCUMENT_MEMBERSHIP_TABLE,
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                name=DOCUMENT_MEMBERSHIP_USER_FK_NAME,
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["document_id"],
                ["documents.id"],
                name=DOCUMENT_MEMBERSHIP_DOCUMENT_FK_NAME,
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "document_id", name=DOCUMENT_MEMBERSHIP_UNIQUE_NAME),
        )
    else:
        if not _fk_exists(DOCUMENT_MEMBERSHIP_TABLE, ["user_id"], "users"):
            op.create_foreign_key(
                DOCUMENT_MEMBERSHIP_USER_FK_NAME,
                DOCUMENT_MEMBERSHIP_TABLE,
                "users",
                ["user_id"],
                ["id"],
                ondelete="CASCADE",
            )

        if not _fk_exists(DOCUMENT_MEMBERSHIP_TABLE, ["document_id"], "documents"):
            op.create_foreign_key(
                DOCUMENT_MEMBERSHIP_DOCUMENT_FK_NAME,
                DOCUMENT_MEMBERSHIP_TABLE,
                "documents",
                ["document_id"],
                ["id"],
                ondelete="CASCADE",
            )

        if not _unique_constraint_exists(DOCUMENT_MEMBERSHIP_TABLE, DOCUMENT_MEMBERSHIP_UNIQUE_NAME):
            op.create_unique_constraint(
                DOCUMENT_MEMBERSHIP_UNIQUE_NAME,
                DOCUMENT_MEMBERSHIP_TABLE,
                ["user_id", "document_id"],
            )

    if not _index_exists(DOCUMENT_MEMBERSHIP_TABLE, DOCUMENT_MEMBERSHIP_USER_INDEX_NAME):
        op.create_index(
            DOCUMENT_MEMBERSHIP_USER_INDEX_NAME,
            DOCUMENT_MEMBERSHIP_TABLE,
            ["user_id"],
            unique=False,
        )

    if not _index_exists(DOCUMENT_MEMBERSHIP_TABLE, DOCUMENT_MEMBERSHIP_DOCUMENT_INDEX_NAME):
        op.create_index(
            DOCUMENT_MEMBERSHIP_DOCUMENT_INDEX_NAME,
            DOCUMENT_MEMBERSHIP_TABLE,
            ["document_id"],
            unique=False,
        )

    if not _index_exists("documents", DOCUMENT_GLOBAL_ACTIVE_HASH_UNIQUE_INDEX_NAME):
        op.create_index(
            DOCUMENT_GLOBAL_ACTIVE_HASH_UNIQUE_INDEX_NAME,
            "documents",
            ["file_hash"],
            unique=True,
            postgresql_where=sa.text("deleted_at IS NULL"),
        )

    if _index_exists("documents", DOCUMENT_OLD_ACTIVE_HASH_UNIQUE_INDEX_NAME):
        op.drop_index(DOCUMENT_OLD_ACTIVE_HASH_UNIQUE_INDEX_NAME, table_name="documents")


def downgrade() -> None:
    if _index_exists("documents", DOCUMENT_GLOBAL_ACTIVE_HASH_UNIQUE_INDEX_NAME):
        op.drop_index(DOCUMENT_GLOBAL_ACTIVE_HASH_UNIQUE_INDEX_NAME, table_name="documents")

    if not _index_exists("documents", DOCUMENT_OLD_ACTIVE_HASH_UNIQUE_INDEX_NAME):
        op.create_index(
            DOCUMENT_OLD_ACTIVE_HASH_UNIQUE_INDEX_NAME,
            "documents",
            ["user_id", "file_hash"],
            unique=True,
            postgresql_where=sa.text("deleted_at IS NULL"),
        )

    if _table_exists(DOCUMENT_MEMBERSHIP_TABLE):
        op.drop_table(DOCUMENT_MEMBERSHIP_TABLE)
