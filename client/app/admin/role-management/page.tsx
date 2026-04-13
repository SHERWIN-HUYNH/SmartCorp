'use client';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { RoleDetails } from '@/components/admin/role-management/RoleDetails';
import { RoleList } from '@/components/admin/role-management/RoleList';
import {
  createRole,
  deleteRole,
  listRoles,
  listRoleManagementRoles,
  type RoleOption,
  type RoleManagementRole,
  updateRole,
} from '@/lib/auth-api';
import { RoleNode } from '@/types/role';

function mapRoleToNode(role: RoleManagementRole): RoleNode {
  return {
    id: role.id,
    title: role.name,
    description: role.description || '',
    userCount: role.user_count,
    docCount: role.doc_count,
    category: role.category === 'core' ? 'Core Access' : 'Custom',
    isCore: role.is_system,
    users: [],
    documents: [],
  };
}

function mapRoleOptionToNode(role: RoleOption): RoleNode {
  const normalizedName = role.name.trim().toLowerCase();
  const isCore = normalizedName === 'admin' || normalizedName === 'user';

  return {
    id: role.id,
    title: role.name,
    description: role.description || '',
    userCount: 0,
    docCount: 0,
    category: isCore ? 'Core Access' : 'Custom',
    isCore,
    users: [],
    documents: [],
  };
}

export default function RoleManagementPage() {
  const [roles, setRoles] = useState<RoleNode[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [mutating, setMutating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadRoles = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // Base role list for rendering left panel, available for authenticated users.
      const baseRoles = await listRoles();
      let mapped = baseRoles.map(mapRoleOptionToNode);

      // Enrich with role-management metrics when current user has permission.
      try {
        const response = await listRoleManagementRoles();
        const summaryMap = new Map(response.items.map((role) => [role.id, role]));

        mapped = mapped.map((role) => {
          const summary = summaryMap.get(role.id);
          if (!summary) {
            return role;
          }

          const enriched = mapRoleToNode(summary);
          return {
            ...role,
            userCount: enriched.userCount,
            docCount: enriched.docCount,
            category: enriched.category,
            isCore: enriched.isCore,
          };
        });

        const existingIds = new Set(mapped.map((role) => role.id));
        const extra = response.items
          .filter((role) => !existingIds.has(role.id))
          .map(mapRoleToNode);
        mapped = [...mapped, ...extra];
      } catch {
        // Keep base list visible even if role-management summary endpoint is forbidden.
      }

      setRoles(mapped);

      setSelectedRoleId((prev) => {
        if (mapped.length === 0) {
          return '';
        }
        if (mapped.some((role) => role.id === prev)) {
          return prev;
        }
        return mapped[0].id;
      });
    } catch (loadError) {
      setRoles([]);
      setError(loadError instanceof Error ? loadError.message : 'Failed to load roles.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadRoles();
  }, [loadRoles]);

  const selectedRole = useMemo(
    () => roles.find((role) => role.id === selectedRoleId) || null,
    [roles, selectedRoleId],
  );

  const handleCreateRole = async (payload: { name: string; description?: string }) => {
    setMutating(true);
    setError(null);
    try {
      const createdRole = await createRole(payload);
      await loadRoles();
      setSelectedRoleId(createdRole.id);
    } catch (createError) {
      const message = createError instanceof Error ? createError.message : 'Failed to create role.';
      setError(message);
      throw new Error(message);
    } finally {
      setMutating(false);
    }
  };

  const handleUpdateRole = async (
    roleId: string,
    payload: { title?: string; description?: string },
  ) => {
    setMutating(true);
    setError(null);
    try {
      await updateRole(roleId, {
        name: payload.title,
        description: payload.description,
      });
      await loadRoles();
    } catch (updateError) {
      setError(updateError instanceof Error ? updateError.message : 'Failed to update role.');
    } finally {
      setMutating(false);
    }
  };

  const handleDeleteRole = async (roleId: string) => {
    setMutating(true);
    setError(null);
    try {
      await deleteRole(roleId);
      await loadRoles();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : 'Failed to delete role.');
    } finally {
      setMutating(false);
    }
  };

  return (
    <div className="grid w-full grid-cols-1 gap-6 lg:grid-cols-[minmax(340px,40%)_minmax(0,1fr)]">
      <RoleList
        roles={roles}
        selectedRoleId={selectedRoleId}
        onSelectRole={setSelectedRoleId}
        onCreateRole={handleCreateRole}
        isLoading={loading || mutating}
      />
      <div className="min-w-0">
        {error && <p className="px-6 pt-4 text-sm text-red-600 lg:px-10 lg:pt-6">{error}</p>}
        <RoleDetails
          role={selectedRole}
          onUpdateRole={handleUpdateRole}
          onDeleteRole={handleDeleteRole}
          isMutating={mutating}
        />
      </div>
    </div>
  );
}