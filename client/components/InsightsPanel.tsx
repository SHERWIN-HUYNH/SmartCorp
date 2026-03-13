import { Sparkles, Book, Copy, Share2, GraduationCap, FileText, Table } from 'lucide-react';
import { FlowNode, Source } from '@/lib/types';

interface InsightsPanelProps {
  nodes: FlowNode[];
  sources: Source[];
}

export function InsightsPanel({ nodes, sources }: InsightsPanelProps) {
  return (
    <aside className="w-1/4 bg-white flex flex-col p-6 overflow-y-auto border-l border-slate-500/20">
      <header className="flex items-center justify-between mb-8">
        <h2 className="font-bold text-slate-900 flex items-center gap-2 text-lg">
          <Sparkles className="h-5 w-5 text-slate-900" />
          Quick Actions
        </h2>
      </header>

      <section className="space-y-3 mb-10">
        <button className="w-full flex items-center gap-3 px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-900 hover:bg-slate-50 transition-colors shadow-sm">
          <Book className="h-5 w-5 text-slate-500" />
          Save to Notebook
        </button>
        <button className="w-full flex items-center gap-3 px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-900 hover:bg-slate-50 transition-colors shadow-sm">
          <Copy className="h-5 w-5 text-slate-500" />
          Copy Response
        </button>
        <button className="w-full flex items-center gap-3 px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-900 hover:bg-slate-50 transition-colors shadow-sm">
          <Share2 className="h-5 w-5 text-slate-500" />
          Share
        </button>
        <button className="w-full flex items-center gap-3 px-4 py-3 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-900 hover:bg-slate-50 transition-colors shadow-sm">
          <GraduationCap className="h-5 w-5 text-slate-500" />
          Add to Study Guide
        </button>
      </section>

      <section>
        <h3 className="text-xs uppercase font-bold text-slate-500 mb-4 tracking-wider">Sources Cited</h3>
        <div className="flex flex-col items-start gap-3">
          {sources.map((source) => (
            <a 
              key={source.id} 
              href={source.url}
              className="flex items-center gap-2 px-3 py-2 bg-white border border-slate-500/20 rounded-xl text-xs font-medium text-slate-900 hover:border-slate-900 hover:text-slate-900 transition-all shadow-sm"
            >
              {source.type === 'pdf' ? (
                <FileText className="h-4 w-4 text-red-500" />
              ) : (
                <Table className="h-4 w-4 text-slate-900" />
              )}
              {source.title}
            </a>
          ))}
        </div>
      </section>

      <div className="mt-auto p-4 bg-slate-900 rounded-xl text-white shadow-md">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-tight">Performance</span>
          <span className="text-[10px] font-mono text-green-400">124.5 tps</span>
        </div>
        <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
          <div className="bg-slate-900 h-full w-[85%] border-r border-slate-600" />
        </div>
      </div>
    </aside>
  );
}
