'use client';
import { RoleNode } from '@/types/role';
import { PlusCircle, ChevronRight, Users, FileText } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface RoleListProps {
  roles: RoleNode[];
  selectedRoleId: string;
  onSelectRole: (id: string) => void;
}

export function RoleList({ roles, selectedRoleId, onSelectRole }: RoleListProps) {
  // Group roles by category
  const groupedRoles = roles.reduce((acc, role) => {
    if (!acc[role.category]) {
      acc[role.category] = [];
    }
    acc[role.category].push(role);
    return acc;
  }, {} as Record<string, RoleNode[]>);

  return (
    <section className="w-[40%] flex flex-col bg-slate-50 dark:bg-slate-900/50 border-r border-slate-200 dark:border-slate-800">
      <div className="p-6 pb-4 flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h2 className="font-extrabold text-2xl tracking-tight text-slate-900 dark:text-white">Role Hierarchy</h2>
          <Badge variant="secondary" className="bg-slate-900 text-white hover:bg-slate-800 dark:bg-slate-800 dark:text-white">
            {roles.length} ROLES
          </Badge>
        </div>
        <Button className="w-full py-6 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold flex items-center justify-center gap-3 shadow-md transition-all">
          <PlusCircle className="w-5 h-5" />
          <span>Create New Role</span>
        </Button>
      </div>

      <ScrollArea className="flex-1 px-6 pb-8">
        <div className="space-y-6">
          {Object.entries(groupedRoles).map(([category, categoryRoles]) => (
            <div key={category} className="space-y-4">
              {categoryRoles.map((role) => {
                const isSelected = role.id === selectedRoleId;
                return (
                  <div
                    key={role.id}
                    onClick={() => onSelectRole(role.id)}
                    className={`p-5 rounded-xl transition-all cursor-pointer group ${
                      isSelected
                        ? 'bg-white dark:bg-slate-800 border-l-4 border-slate-900 dark:border-white shadow-sm'
                        : 'bg-slate-100 dark:bg-slate-800/50 hover:bg-slate-200 dark:hover:bg-slate-800'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <span className={`text-xs font-bold tracking-widest uppercase ${isSelected ? 'text-slate-900 dark:text-white' : 'text-slate-500'}`}>
                        {category}
                      </span>
                      {isSelected && <ChevronRight className="text-slate-900 dark:text-white w-5 h-5" />}
                    </div>
                    <h3 className="font-bold text-lg mb-1 text-slate-900 dark:text-white">{role.title}</h3>
                    <p className="text-slate-500 text-sm line-clamp-2 mb-4">{role.description}</p>
                    
                    <div className="flex items-center gap-4">
                      <div className={`flex items-center gap-1.5 text-xs font-semibold ${isSelected ? 'text-slate-700 dark:text-slate-300' : 'text-slate-500'}`}>
                        <Users className="w-4 h-4" />
                        {role.userCount} Users
                      </div>
                      <div className={`flex items-center gap-1.5 text-xs font-semibold ${isSelected ? 'text-slate-700 dark:text-slate-300' : 'text-slate-500'}`}>
                        <FileText className="w-4 h-4" />
                        {role.docCount} Docs
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </ScrollArea>
    </section>
  );
}
