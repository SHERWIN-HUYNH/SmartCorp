'use client';
import { RoleDetails } from "@/components/admin/role-management/RoleDetails";
import { RoleList } from "@/components/admin/role-management/RoleList";
import { DocumentNode, RoleNode, UserNode } from "@/types/role";
import { useState } from "react";


// Mock Data
const mockUsers: UserNode[] = [
  { id: 'u1', name: 'Jane Doe', initials: 'JD', email: 'jane.doe@enterprise.com', status: 'Active', avatarColor: 'bg-blue-100 text-blue-700' },
  { id: 'u2', name: 'Alex Smith', initials: 'AS', email: 'alex.s@enterprise.com', status: 'Active', avatarColor: 'bg-orange-100 text-orange-700' },
  { id: 'u3', name: 'Michael Ross', initials: 'MR', email: 'm.ross@enterprise.com', status: 'On Leave', avatarColor: 'bg-indigo-100 text-indigo-700' },
  { id: 'u4', name: 'Sarah Lee', initials: 'SL', email: 's.lee@enterprise.com', status: 'Active', avatarColor: 'bg-slate-200 text-slate-700' },
  { id: 'u5', name: 'Tom Wilson', initials: 'TW', email: 't.wilson@enterprise.com', status: 'Active', avatarColor: 'bg-blue-200 text-blue-800' },
  { id: 'u6', name: 'Emma Gray', initials: 'EG', email: 'e.gray@enterprise.com', status: 'Restricted', avatarColor: 'bg-amber-100 text-amber-700' },
];

const mockDocuments: DocumentNode[] = [
  { id: 'd1', name: 'Q4 Financial Forecast', type: 'file', uploadedBy: { name: 'Felix Vance', avatarUrl: 'https://i.pravatar.cc/150?u=felix' }, dateAdded: 'Oct 12, 2025' },
  { id: 'd2', name: 'Security Protocols v2', type: 'security', uploadedBy: { name: 'Sarah Jenkins', avatarUrl: 'https://i.pravatar.cc/150?u=sarah' }, dateAdded: 'Sep 30, 2025' },
  { id: 'd3', name: 'Employee Handbook', type: 'handbook', uploadedBy: { name: 'Marcus Chen', avatarUrl: 'https://i.pravatar.cc/150?u=marcus' }, dateAdded: 'Aug 15, 2025' },
  { id: 'd4', name: 'IT Infrastructure Schema', type: 'schema', uploadedBy: { name: 'Alex Smith', avatarUrl: 'https://i.pravatar.cc/150?u=alex' }, dateAdded: 'Jul 22, 2025' },
];

const mockRoles: RoleNode[] = [
  {
    id: 'r1',
    title: 'Financial Analyst',
    description: 'Strategic access to quarterly reports, ledger audits, and risk assessment dashboards for the fiscal year.',
    userCount: 12,
    docCount: 45,
    category: 'Core Access',
    isCore: true,
    users: mockUsers,
    documents: mockDocuments,
  },
  {
    id: 'r2',
    title: 'Internal Auditor',
    description: 'Compliance-focused role with extensive read-access to transactional logs and policy documentation.',
    userCount: 4,
    docCount: 128,
    category: 'Read Only',
    users: [],
    documents: [],
  },
  {
    id: 'r3',
    title: 'System Architect',
    description: 'Top-tier administrative role managing RAG index configuration and vector database connectivity.',
    userCount: 2,
    docCount: 999, // Representing "All Docs"
    category: 'Admin Privileges',
    users: [],
    documents: [],
  },
  {
    id: 'r4',
    title: 'Marketing Lead',
    description: 'Access to brand assets, campaign history, and creative performance RAG indices.',
    userCount: 18,
    docCount: 312,
    category: 'Departmental',
    users: [],
    documents: [],
  },
];

export default function RoleManagementPage() {
    const [selectedRoleId, setSelectedRoleId] = useState<string>(mockRoles[0].id);

    const selectedRole = mockRoles.find(r => r.id === selectedRoleId) || null;
    return (
         <div className="flex flex-1 overflow-hidden">
          <RoleList 
            roles={mockRoles} 
            selectedRoleId={selectedRoleId} 
            onSelectRole={setSelectedRoleId} 
          />
          <RoleDetails role={selectedRole} />
        </div>
    )
}