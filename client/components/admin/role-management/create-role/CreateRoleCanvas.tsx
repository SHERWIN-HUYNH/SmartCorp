'use client';

import { AlertCircle } from 'lucide-react';

import { Input } from '@/components/ui/input';
import { CreateRoleFormValues } from '@/types/role-flow';

interface CreateRoleCanvasProps {
  form: CreateRoleFormValues;
  onChange: (next: CreateRoleFormValues) => void;
  roleCodeError?: string | null;
}

export function CreateRoleCanvas({ form, onChange, roleCodeError }: CreateRoleCanvasProps) {
  return (
    <section className="space-y-6 px-6 py-6 sm:px-8">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Canvas</p>

      <div className="space-y-2">
        <label className="text-sm font-semibold tracking-tight text-slate-900" htmlFor="role-code">
          Role Code <span className="text-red-700">*</span>
        </label>
        <Input
          id="role-code"
          value={form.roleCode}
          onChange={(event) =>
            onChange({
              ...form,
              roleCode: event.currentTarget.value,
            })
          }
          placeholder="e.g. cloud_admin"
          className="h-12 rounded-xl border-slate-200 bg-slate-100 px-4 text-base text-slate-900 placeholder:text-slate-400"
          autoComplete="off"
        />
        <div className="flex items-center gap-1.5 px-1">
          <AlertCircle className="h-3.5 w-3.5 text-slate-500" />
          <p className="text-xs font-medium text-slate-500">lowercase, no spaces</p>
        </div>
        {roleCodeError && <p className="text-xs font-medium text-red-700">{roleCodeError}</p>}
      </div>

      <div className="space-y-2">
        <label className="text-sm font-semibold tracking-tight text-slate-900" htmlFor="role-description">
          Description
        </label>
        <textarea
          id="role-description"
          value={form.description}
          onChange={(event) =>
            onChange({
              ...form,
              description: event.currentTarget.value,
            })
          }
          placeholder="Briefly describe the responsibilities of this role..."
          className="min-h-[132px] w-full resize-none rounded-xl border border-slate-200 bg-slate-100 p-4 text-sm leading-6 text-slate-900 outline-none transition focus-visible:border-slate-500"
        />
      </div>
    </section>
  );
}
