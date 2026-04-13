'use client';

import { useEffect, useMemo, useState } from 'react';

import { Button } from '@/components/ui/button';
import { CreateRoleFormValues, RoleFlowEdge, RoleFlowNode } from '@/types/role-flow';

import { CreateRoleCanvas } from './CreateRoleCanvas';
import { CreateRoleProperties } from './CreateRoleProperties';
import { CreateRoleSidebar } from './CreateRoleSidebar';
import { CreateRoleToolbar } from './CreateRoleToolbar';

const FLOW_NODES: RoleFlowNode[] = [
  {
    id: 'draft-node',
    title: 'Draft Role Code',
    detail: 'Capture the canonical identifier used across policy checks.',
    stage: 'draft',
  },
  {
    id: 'validation-node',
    title: 'Validate Format',
    detail: 'Ensure format remains lowercase and deterministic.',
    stage: 'validation',
  },
  {
    id: 'analysis-node',
    title: 'Security Analysis',
    detail: 'AI scoring inspects privilege profile and policy risk.',
    stage: 'analysis',
  },
  {
    id: 'publish-node',
    title: 'Publish Role',
    detail: 'Persist role and surface it in Access Control immediately.',
    stage: 'publish',
  },
];

const FLOW_EDGES: RoleFlowEdge[] = [
  {
    id: 'edge-1',
    source: 'draft-node',
    target: 'validation-node',
    rule: 'Role code passes pattern check',
  },
  {
    id: 'edge-2',
    source: 'validation-node',
    target: 'analysis-node',
    rule: 'No duplicate role code detected',
  },
  {
    id: 'edge-3',
    source: 'analysis-node',
    target: 'publish-node',
    rule: 'Security score generated successfully',
  },
];

interface CreateRoleModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (payload: { name: string; description?: string }) => Promise<void>;
  isSubmitting?: boolean;
}

function normalizeRoleCode(input: string): string {
  return input.trim().toLowerCase();
}

function validateRoleCode(input: string): string | null {
  if (!input.trim()) {
    return 'Role code is required.';
  }

  if (!/^[a-z0-9_]+$/.test(input.trim())) {
    return 'Role code must contain only lowercase letters, numbers, and underscores.';
  }

  return null;
}

const INITIAL_FORM: CreateRoleFormValues = {
  roleCode: '',
  description: '',
};

export function CreateRoleModal({ open, onClose, onSubmit, isSubmitting = false }: CreateRoleModalProps) {
  const [form, setForm] = useState<CreateRoleFormValues>(INITIAL_FORM);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setForm(INITIAL_FORM);
      setSubmitError(null);
    }
  }, [open]);

  useEffect(() => {
    if (!open) {
      return;
    }

    const onEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !isSubmitting) {
        onClose();
      }
    };

    window.addEventListener('keydown', onEscape);
    return () => window.removeEventListener('keydown', onEscape);
  }, [open, onClose, isSubmitting]);

  const roleCodeError = useMemo(() => validateRoleCode(form.roleCode), [form.roleCode]);

  if (!open) {
    return null;
  }

  const handleSubmit = async () => {
    const nextRoleCode = normalizeRoleCode(form.roleCode);
    const validationError = validateRoleCode(nextRoleCode);

    if (validationError) {
      setSubmitError(validationError);
      return;
    }

    setSubmitError(null);

    try {
      await onSubmit({
        name: nextRoleCode,
        description: form.description.trim() ? form.description.trim() : undefined,
      });
      onClose();
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'Failed to create role.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-[rgba(25,28,30,0.4)] backdrop-blur-[1px]"
        onClick={() => {
          if (!isSubmitting) {
            onClose();
          }
        }}
      />
      <div className="relative z-10 w-full max-w-5xl overflow-hidden rounded-xl bg-white shadow-[0px_20px_40px_-10px_rgba(15,23,42,0.08)]">
        <CreateRoleToolbar onClose={onClose} disabled={isSubmitting} />

        <div className="grid gap-0 lg:grid-cols-[220px_minmax(0,1fr)_260px]">
          <CreateRoleSidebar nodes={FLOW_NODES} />
          <CreateRoleCanvas form={form} onChange={setForm} roleCodeError={submitError ?? roleCodeError} />
          <CreateRoleProperties edges={FLOW_EDGES} />
        </div>

        <footer className="flex flex-col-reverse gap-3 border-t border-slate-200 px-6 py-5 sm:flex-row sm:items-center sm:justify-end sm:px-8">
          <Button
            type="button"
            variant="secondary"
            disabled={isSubmitting}
            onClick={onClose}
            className="h-12 rounded-xl bg-slate-200 px-8 font-bold text-slate-700 hover:bg-slate-300"
          >
            Cancel
          </Button>
          <Button
            type="button"
            disabled={isSubmitting || Boolean(roleCodeError)}
            onClick={() => {
              void handleSubmit();
            }}
            className="h-12 rounded-xl bg-[#131b2e] px-8 font-bold text-white hover:bg-[#0e1525]"
          >
            {isSubmitting ? 'Creating...' : 'Create Role'}
          </Button>
        </footer>
      </div>
    </div>
  );
}
