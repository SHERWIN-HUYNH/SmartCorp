'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import { AuthApiError, getCurrentUser } from '@/lib/auth-api';
import { isRoleInAllowlist } from '@/lib/role-access';

interface AdminRouteGuardProps {
  children: React.ReactNode;
}

export function AdminRouteGuard({ children }: AdminRouteGuardProps) {
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function checkAccess() {
      try {
        const user = await getCurrentUser();

        if (!isRoleInAllowlist(user.role)) {
          router.replace('/chatbot');
          return;
        }

        if (mounted) {
          setIsAuthorized(true);
        }
      } catch (error) {
        if (error instanceof AuthApiError && error.status === 401) {
          router.replace('/login');
          return;
        }

        router.replace('/login');
      }
    }

    void checkAccess();

    return () => {
      mounted = false;
    };
  }, [router]);

  if (!isAuthorized) {
    return <div className="px-8 py-10 text-sm text-slate-500">Checking access...</div>;
  }

  return <>{children}</>;
}
