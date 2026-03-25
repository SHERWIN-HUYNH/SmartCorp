import { Database, LayoutDashboard, BookOpen, Users, BarChart3 } from 'lucide-react';
import Link from 'next/link';

export default function Sidebar() {
  
  return (
    <aside className="fixed left-0 top-0 h-full w-64 border-r-0 bg-[#0F172A] shadow-2xl flex flex-col py-6 z-50">
      <div className="px-6 mb-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
            <Database className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-tight leading-none">SmartCorp Oracle</h1>
            <p className="text-[10px] text-slate-500 font-semibold tracking-widest uppercase mt-1">Enterprise Admin</p>
          </div>
        </div>
      </div>
      
      <nav className="flex-1 space-y-1">
        <Link href="/admin" className="bg-slate-800 text-white rounded-lg px-4 py-3 mx-2 flex items-center gap-3 font-semibold tracking-tight transition-all duration-200 ease-in-out">
          <LayoutDashboard className="w-5 h-5" />
          <span>Dashboard</span>
        </Link>
        <Link href="/admin/knowledge-base" className="text-slate-400 hover:text-white px-4 py-3 mx-2 flex items-center gap-3 font-semibold tracking-tight transition-colors hover:bg-slate-800/50 rounded-lg">
          <BookOpen className="w-5 h-5" />
          <span>Knowledge Base</span>
        </Link>
        <Link href="/admin/role-management" className="text-slate-400 hover:text-white px-4 py-3 mx-2 flex items-center gap-3 font-semibold tracking-tight transition-colors hover:bg-slate-800/50 rounded-lg">
          <Users className="w-5 h-5" />
          <span>Role Management</span>
        </Link>
        <Link href="/admin/analytics" className="text-slate-400 hover:text-white px-4 py-3 mx-2 flex items-center gap-3 font-semibold tracking-tight transition-colors hover:bg-slate-800/50 rounded-lg">
          <BarChart3 className="w-5 h-5" />
          <span>Analytics</span>
        </Link>
      </nav>

      <div className="px-6 mt-auto pt-6 border-t border-slate-800/50">
        <div className="flex items-center gap-3 p-2 rounded-xl bg-slate-800/30">
          <img alt="Trung N." className="w-10 h-10 rounded-full border-2 border-slate-700" src="https://i.pravatar.cc/150?u=trung" />
          <div className="overflow-hidden">
            <p className="text-sm font-bold text-white truncate">Trung N.</p>
            <p className="text-xs text-slate-500 truncate">System Architect</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
