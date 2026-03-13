import { Cpu } from 'lucide-react';
import Link from 'next/link';

export function Header() {
  return (
    <header className="h-16 bg-white border-b border-slate-500/20 flex items-center justify-between px-8 z-30 shrink-0">
      <div className="flex items-center gap-10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-slate-900 rounded-lg flex items-center justify-center">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-slate-900 tracking-tight">SmartCorp Oracle</span>
        </div>
        <nav className="hidden md:flex items-center gap-8">
          <Link href="#" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Home</Link>
          <Link href="#" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Features</Link>
          <Link href="#" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Workflow</Link>
          <Link href="#" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Feedback</Link>
        </nav>
      </div>
      <div className="flex items-center gap-4">
        <button className="text-sm font-medium text-slate-500 hover:text-slate-900 px-4 py-2 transition-colors">Chat</button>
        <button className="bg-slate-900 text-white px-6 py-2 rounded-xl text-sm font-semibold hover:bg-slate-800 transition-all shadow-sm">Logout</button>
      </div>
    </header>
  );
}
