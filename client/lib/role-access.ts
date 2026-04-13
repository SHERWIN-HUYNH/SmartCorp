function normalizeRoleName(role: string | null | undefined): string {
  if (!role) {
    return '';
  }

  return role.trim().toLowerCase().replace(/\s+/g, ' ');
}

function parseRoleAllowlist(raw: string): string[] {
  const trimmed = raw.trim();
  let candidates: string[] = [];

  if (trimmed.startsWith('[') && trimmed.endsWith(']')) {
    try {
      const parsed = JSON.parse(trimmed);
      if (Array.isArray(parsed)) {
        candidates = parsed.map((role) => String(role));
      }
    } catch {
      candidates = [];
    }
  }

  if (candidates.length === 0) {
    candidates = trimmed.split(',');
  }

  const normalized = candidates
    .map((role) => normalizeRoleName(role))
    .filter((role) => role.length > 0);

  return normalized.length > 0 ? normalized : ['admin'];
}

export function getRoleManagerAllowlist(): string[] {
  const raw = process.env.NEXT_PUBLIC_ROLE_MANAGER_ALLOWLIST ?? 'admin';
  return parseRoleAllowlist(raw);
}

export function isRoleInAllowlist(role: string | null | undefined): boolean {
  const normalizedRole = normalizeRoleName(role);
  if (!normalizedRole) {
    return false;
  }

  return getRoleManagerAllowlist().includes(normalizedRole);
}

export function getLandingPathForRole(role: string | null | undefined): '/admin' | '/chatbot' {
  return isRoleInAllowlist(role) ? '/admin' : '/chatbot';
}
