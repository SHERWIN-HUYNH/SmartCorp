'use client';

import { BrainCircuit, GitBranch } from 'lucide-react';

import { RoleFlowEdge } from '@/types/role-flow';

interface CreateRolePropertiesProps {
  edges: RoleFlowEdge[];
}

export function CreateRoleProperties({ edges }: CreateRolePropertiesProps) {
  return (
    <aside className="space-y-5 border-t border-slate-200 bg-slate-50 px-6 py-6 lg:border-t-0 lg:border-l sm:px-8 lg:px-6">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Properties</p>

      <div className="rounded-xl border border-[#c8d8ff] bg-[#eaf0ff] p-4">
        <div className="flex items-start gap-3">
          <div className="rounded-full bg-[#d5e3fd] p-2">
            <BrainCircuit className="h-4 w-4 text-[#0d1c2f]" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.1em] text-[#0d1c2f]">
              AI Permission Scoring
            </p>
            <p className="mt-1 text-xs leading-5 text-[#57657b]">
              This role will be automatically evaluated for security compliance after creation.
            </p>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-800">Flow Edges</p>
          <span className="text-xs font-semibold text-slate-500">{edges.length}</span>
        </div>
        <div className="mt-3 space-y-2">
          {edges.map((edge) => (
            <div key={edge.id} className="flex items-start gap-2 rounded-lg bg-slate-50 p-2">
              <GitBranch className="mt-0.5 h-3.5 w-3.5 text-slate-500" />
              <p className="text-xs leading-5 text-slate-600">{edge.rule}</p>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
