from __future__ import annotations

from app.model.user import User


def normalize_role_name(role_name: str | None) -> str:
    if not role_name:
        return ""

    # Normalize role names to avoid case/whitespace duplicates.
    return " ".join(role_name.strip().lower().split())


def resolve_user_role_name(user: User) -> str:
    # During role_id transition, prefer the relational role as source of truth.
    if user.role_id is not None or user.role_ref is not None:
        if user.role_ref and user.role_ref.name:
            return normalize_role_name(user.role_ref.name)

        # Do not fall back to legacy string when a role relationship exists.
        return ""

    if user.role:
        normalized = normalize_role_name(user.role)
        if normalized:
            return normalized

    return ""
