'use client';

import { X } from 'lucide-react';

interface CreateRoleToolbarProps {
  onClose: () => void;
  disabled?: boolean;
}

export function CreateRoleToolbar({ onClose, disabled = false }: CreateRoleToolbarProps) {
  return (
    <header className="flex items-start justify-between gap-4 border-b border-slate-200 px-6 py-6 sm:px-8">
      <div className="space-y-2">
        <h3 className="text-2xl font-extrabold tracking-tight text-slate-900">Create New Role</h3>
        <p className="text-sm leading-5 text-slate-600">
          Define a new set of access permissions for users.
        </p>
      </div>
      <button
        type="button"
        onClick={onClose}
        disabled={disabled}
        className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
        aria-label="Close create role dialog"
      >
        <X className="h-4 w-4" />
      </button>
    </header>
  );
}
