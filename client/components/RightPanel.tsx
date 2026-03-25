import { PlusCircle, ArrowRight, Key } from 'lucide-react';
import { recentUpdates } from '@/app/dataAdmin';

export default function RightPanel() {
  return (
    <div className="lg:col-span-3 space-y-6">
      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-4">Thao tác nhanh</h3>
        <div className="space-y-3">
          <button className="w-full bg-[#0F172A] text-white py-4 px-5 rounded-lg font-bold flex items-center justify-between group hover:shadow-lg transition-all">
            <span className="flex items-center gap-3">
              <PlusCircle className="w-5 h-5" />
              Tải tài liệu mới
            </span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
          <button className="w-full bg-slate-50 text-[#0F172A] py-4 px-5 rounded-lg font-bold flex items-center justify-between group hover:bg-slate-100 transition-all border border-slate-200">
            <span className="flex items-center gap-3">
              <Key className="w-5 h-5" />
              Quản lý vai trò
            </span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>

      {/* Latest Updates */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-6">Cập nhật tài liệu mới nhất</h3>
        <ul className="space-y-6 max-h-[350px] overflow-y-auto pr-4 custom-scrollbar">
          {recentUpdates.map((update, index) => (
            <li key={update.id} className="flex gap-4 relative">
              {index !== recentUpdates.length - 1 && (
                <div className="absolute left-[11px] top-6 bottom-[-24px] w-[2px] bg-slate-100"></div>
              )}
              <div className={`w-6 h-6 rounded-full ${update.iconWrapperClass} flex-shrink-0 z-10 flex items-center justify-center`}>
                <update.icon className={`w-3 h-3 ${update.iconClass}`} />
              </div>
              <div>
                <p className="text-sm font-bold text-slate-900">{update.title}</p>
                <p className="text-xs text-slate-500 mt-1">Bởi {update.author} • {update.time}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
