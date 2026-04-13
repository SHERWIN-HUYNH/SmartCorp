from __future__ import annotations

from app.model.user import User


def normalize_role_name(role_name: str | None) -> str:
    if not role_name:
        return ""

    # Normalize role names to avoid case/whitespace duplicates.
    return " ".join(role_name.strip().lower().split())


def resolve_user_role_name(user: User) -> str:
    if user.role:
        normalized = normalize_role_name(user.role)
        if normalized:
            return normalized

    if user.role_ref and user.role_ref.name:
        return normalize_role_name(user.role_ref.name)

    return ""
