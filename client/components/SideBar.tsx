import { Plus } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { Query, User } from '@/lib/types';
import { cn } from '@/lib/utils';

interface SidebarProps {
  queries: Query[];
  user: User;
}

export default function Sidebar({ queries, user }: SidebarProps) {
  return (
    <aside className="w-1/5 flex flex-col p-6 bg-white border-r border-slate-500/20 z-20">
      <button className="w-full bg-slate-900 text-white hover:bg-slate-800 transition-all py-3 px-4 rounded-xl flex items-center justify-center gap-2 mb-8 shadow-sm font-medium">
        <Plus className="h-5 w-5" />
        <span>New Chat</span>
      </button>

      <nav className="flex-1 overflow-y-auto">
        <h2 className="text-xs uppercase font-bold mb-4 tracking-wider text-slate-500">Recent Queries</h2>
        <ul className="space-y-1">
          {queries.map((query) => (
            <li key={query.id}>
              <Link
                href="#"
                className={cn(
                  "block px-3 py-2.5 rounded-xl text-sm font-medium transition-colors border border-transparent",
                  query.isActive
                    ? "bg-slate-50 text-slate-900 border-slate-100"
                    : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
                )}
              >
                {query.title}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      <div className="mt-auto pt-6 border-t flex items-center gap-3 border-slate-500/10">
        <div className="w-10 h-10 rounded-full bg-slate-500/20 overflow-hidden ring-2 ring-white relative">
          <Image
            src={user.avatar}
            alt="User Avatar"
            fill
            className="object-cover"
            referrerPolicy="no-referrer"
          />
        </div>
        <div>
          <p className="text-sm font-semibold text-slate-900">{user.name}</p>
          <p className="text-xs text-slate-500">{user.role}</p>
        </div>
      </div>
    </aside>
  );
}
