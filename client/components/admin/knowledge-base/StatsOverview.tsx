'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { FolderOpen, AlignLeft, ShieldCheck, LucideIcon } from 'lucide-react';

import { getDocumentStats, type DocumentStatsResponse } from '@/lib/auth-api';

type StatItem = {
  id: string;
  label: string;
  value: string;
  icon: LucideIcon;
  iconBgClass: string;
  iconColorClass: string;
  trend?: { value: string; isPositive: boolean };
};

export function StatsOverview() {
  const [statsData, setStatsData] = useState<DocumentStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    async function loadStats() {
      try {
        const result = await getDocumentStats();
        if (mounted) {
          setStatsData(result);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    void loadStats();
    return () => {
      mounted = false;
    };
  }, []);

  const stats = useMemo<StatItem[]>(() => {
    const total = statsData?.total ?? 0;
    const pending = statsData?.pending ?? 0;
    const processing = statsData?.processing ?? 0;
    const ready = statsData?.ready ?? 0;
    const deleted = statsData?.deleted ?? 0;

    const activeDocs = Math.max(total - deleted, 0);
    const queueDepth = pending + processing;
    const healthPercent = activeDocs > 0 ? (ready / activeDocs) * 100 : 100;

    return [
      {
        id: '1',
        label: 'Total Documents',
        value: total.toLocaleString(),
        icon: FolderOpen,
        iconBgClass: 'bg-primary-fixed/30',
        iconColorClass: 'text-primary',
      },
      {
        id: '2',
        label: 'Processing Queue',
        value: queueDepth.toLocaleString(),
        icon: AlignLeft,
        iconBgClass: 'bg-secondary-container/30',
        iconColorClass: 'text-secondary',
      },
      {
        id: '3',
        label: 'Index Health',
        value: `${healthPercent.toFixed(1)}%`,
        icon: ShieldCheck,
        iconBgClass: 'bg-emerald-100/50',
        iconColorClass: 'text-emerald-600',
        trend: { value: 'pulse', isPositive: healthPercent >= 95 },
      },
    ];
  }, [statsData]);

  return (
    <section className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div className="space-y-1">
          <h2 className="text-3xl font-headline font-extrabold tracking-tight text-on-surface">
            Knowledge Base & Document Indexing
          </h2>
          <p className="text-on-surface-variant font-medium">
            Manage corporate knowledge vectors and LLM context windows.
          </p>
          {loading && <p className="text-xs text-outline">Loading metrics...</p>}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.id} className="bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-outline-variant/10 flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-xs font-bold text-outline uppercase tracking-wider">{stat.label}</p>
                <div className="flex items-center gap-2">
                  <h4 className="text-3xl font-headline font-extrabold text-on-surface">{stat.value}</h4>
                  {stat.trend && (
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  )}
                </div>
              </div>
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${stat.iconBgClass} ${stat.iconColorClass}`}>
                <Icon className="w-6 h-6" />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
