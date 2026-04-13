import Sidebar from '@/components/admin/Sidebar';
import Header from '@/components/admin/Header';
import { AdminRouteGuard } from '@/components/auth/AdminRouteGuard';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AdminRouteGuard>
      <div className="min-h-screen bg-[#f7f9fb] font-sans text-slate-900">
        <Sidebar />
        <main className="ml-64">
          <Header />
          <div className="pt-24 px-8 pb-12 max-w-[1600px] mx-auto">
            {children}
          </div>
        </main>
      </div>
    </AdminRouteGuard>
  );
}
