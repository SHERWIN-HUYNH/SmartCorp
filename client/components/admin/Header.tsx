'use client'
import { ChevronRight, Search, Bell, Settings } from 'lucide-react';
import { usePathname } from 'next/navigation';

const routeBreadcrumbs: Record<string, string> = {
  '/admin/dashboard': 'Dashboard',
  '/admin/knowledge-base': 'Knowledge Base',
  '/admin/users': 'Users',
  '/admin/settings': 'Settings',
};
export default function Header() {

    const pathname = usePathname();
  const breadcrumbText = routeBreadcrumbs[pathname] || 'Dashboard';
  return (
    <header className="fixed top-0 right-0 left-64 h-16 bg-white/80 backdrop-blur-md border-b border-slate-200 flex justify-between items-center px-8 z-40">
      <div className="flex items-center gap-6 flex-1">
        <nav className="flex items-center gap-2 text-sm font-medium text-slate-500">
          <span className="hover:text-slate-900 transition-colors cursor-pointer">Admin</span>
          <ChevronRight className="w-4 h-4" />
          <span className="text-slate-900 font-bold">{breadcrumbText}</span>
        </nav>
        <div className="relative w-full max-w-md ml-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input 
            type="text" 
            placeholder="Tìm kiếm hệ thống..." 
            className="w-full bg-slate-100 border-none rounded-full py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all placeholder:text-slate-400" 
          />
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button className="relative hover:bg-slate-100 rounded-full p-2 transition-all text-slate-500">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-red-500 text-[10px] text-white flex items-center justify-center rounded-full border-2 border-white font-bold">3</span>
        </button>
        <button className="hover:bg-slate-100 rounded-full p-2 transition-all text-slate-500">
          <Settings className="w-5 h-5" />
        </button>
        <div className="h-8 w-[1px] bg-slate-200 mx-2"></div>
        <div className="flex items-center gap-3 cursor-pointer">
          <span className="text-sm font-bold text-slate-900">Trung N.</span>
          <img alt="Trung N." className="w-8 h-8 rounded-full bg-slate-200" src="https://i.pravatar.cc/150?u=trung" />
        </div>
      </div>
    </header>
  );
}
