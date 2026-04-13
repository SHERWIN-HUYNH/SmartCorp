'use client';

import { type ComponentType } from 'react';
import { Layers3, Sparkles, ShieldCheck, Rocket } from 'lucide-react';

import { RoleFlowNode } from '@/types/role-flow';

interface CreateRoleSidebarProps {
  nodes: RoleFlowNode[];
}

const stageIconMap: Record<RoleFlowNode['stage'], ComponentType<{ className?: string }>> = {
  draft: Layers3,
  validation: ShieldCheck,
  analysis: Sparkles,
  publish: Rocket,
};

export function CreateRoleSidebar({ nodes }: CreateRoleSidebarProps) {
  return (
    <aside className="hidden bg-slate-50 p-5 lg:block">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Sidebar</p>
      <div className="mt-4 space-y-3">
        {nodes.map((node) => {
          const Icon = stageIconMap[node.stage];
          return (
            <div key={node.id} className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
              <div className="flex items-center gap-2 text-slate-800">
                <Icon className="h-4 w-4" />
                <p className="text-sm font-semibold">{node.title}</p>
              </div>
              <p className="mt-1 text-xs leading-5 text-slate-500">{node.detail}</p>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
