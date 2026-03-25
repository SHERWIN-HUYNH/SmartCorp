import DashboardContent from '@/components/admin/knowledge-base/DashboardContent';
import RightPanel from '@/components/RightPanel';
import { kpiData } from '@/app/dataAdmin';

export default function AdminDashboardPage() {
  return (
    <>
      {/* Greeting */}
      <div className="mb-10">
        <h2 className="text-3xl font-extrabold tracking-tight text-slate-900">Chào mừng trở lại, Trung!</h2>
        <p className="text-slate-500 mt-1 text-lg">Đây là tổng quan hệ thống của bạn hôm nay.</p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        {kpiData.map((kpi) => (
          <div key={kpi.id} className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 hover:shadow-md transition-shadow group">
            <div className="flex justify-between items-start mb-4">
              <div className={`p-3 rounded-xl ${kpi.iconWrapperClass} group-hover:scale-110 transition-transform`}>
                <kpi.icon className={`w-6 h-6 ${kpi.iconClass}`} />
              </div>
              
              {kpi.changeType === 'positive' && (
                <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg">{kpi.changeLabel}</span>
              )}
              {kpi.changeType === 'warning' && (
                <span className="text-xs font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded-lg">{kpi.changeLabel}</span>
              )}
              {kpi.changeType === 'neutral' && (
                <span className="text-xs font-bold text-slate-600 bg-slate-100 px-2 py-1 rounded-lg">{kpi.changeLabel}</span>
              )}
              {kpi.changeType === 'status' && (
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span className="text-xs font-bold text-emerald-600 uppercase tracking-wider">{kpi.statusText}</span>
                </div>
              )}
            </div>
            <p className="text-sm font-medium text-slate-500">{kpi.title}</p>
            <h3 className={`text-3xl font-extrabold mt-1 ${kpi.changeType === 'status' ? 'text-emerald-700 uppercase text-xl' : ''}`}>
              {kpi.value}
            </h3>
          </div>
        ))}
      </div>

      {/* Main Layout Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-10 gap-8">
        <DashboardContent />
        <RightPanel />
      </div>
    </>
  );
}
