
import { RoleNode } from '@/types/role';
import { ChevronRight, Edit2, UserSearch, UserPlus, ArrowRight, Search, ChevronDown, ChevronLeft, FileText, Shield, BookOpen, Network } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useState } from 'react';

interface RoleDetailsProps {
  role: RoleNode | null;
}

export function RoleDetails({ role }: RoleDetailsProps) {
  const [activeTab, setActiveTab] = useState<'users' | 'documents'>('users');

  if (!role) {
    return (
      <section className="w-[60%] flex flex-col bg-white dark:bg-slate-950 items-center justify-center text-slate-500">
        <p>Select a role to view details</p>
      </section>
    );
  }

  const getDocIcon = (type: string) => {
    switch (type) {
      case 'security': return <Shield className="w-5 h-5 text-slate-600 dark:text-slate-400" />;
      case 'handbook': return <BookOpen className="w-5 h-5 text-slate-600 dark:text-slate-400" />;
      case 'schema': return <Network className="w-5 h-5 text-slate-600 dark:text-slate-400" />;
      default: return <FileText className="w-5 h-5 text-slate-600 dark:text-slate-400" />;
    }
  };

  return (
    <section className="w-[60%] flex flex-col bg-white dark:bg-slate-950 overflow-y-auto">
      {/* Detailed Header */}
      <div className="p-10 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div className="flex justify-between items-start mb-6">
          <div className="max-w-xl">
            <nav className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
              <span>Roles</span>
              <ChevronRight className="w-3 h-3" />
              <span className="text-slate-900 dark:text-white">{role.title}</span>
            </nav>
            <h2 className="font-extrabold text-4xl tracking-tighter text-slate-900 dark:text-white mb-3">
              {role.title}
            </h2>
            <p className="text-slate-500 text-lg leading-relaxed">
              {role.description}
            </p>
          </div>
          <Button variant="secondary" className="px-6 py-5 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white rounded-xl font-bold flex items-center gap-2 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
            <Edit2 className="w-4 h-4" />
            <span>Edit Role</span>
          </Button>
        </div>

        {/* Detail Tabs */}
        <div className="flex gap-10">
          <button 
            onClick={() => setActiveTab('users')}
            className={`pb-4 border-b-2 font-bold text-sm tracking-tight transition-colors ${activeTab === 'users' ? 'border-slate-900 dark:border-white text-slate-900 dark:text-white' : 'border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-white'}`}
          >
            Users in Role
          </button>
          <button 
            onClick={() => setActiveTab('documents')}
            className={`pb-4 border-b-2 font-bold text-sm tracking-tight transition-colors ${activeTab === 'documents' ? 'border-slate-900 dark:border-white text-slate-900 dark:text-white' : 'border-transparent text-slate-500 hover:text-slate-900 dark:hover:text-white'}`}
          >
            Accessible Documents
          </button>
        </div>
      </div>

      {/* Tab Content: Users */}
      {activeTab === 'users' && (
        <div className="p-10 flex flex-col gap-6">
          {/* Toolbar */}
          <div className="flex items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <UserSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
              <Input 
                className="w-full bg-slate-50 dark:bg-slate-900 border-none rounded-xl py-6 pl-12 pr-4 text-sm focus-visible:ring-2 focus-visible:ring-slate-200 transition-all" 
                placeholder="Search users in this role..." 
              />
            </div>
            <Button className="px-6 py-6 bg-slate-900 hover:bg-slate-800 text-white rounded-xl font-bold flex items-center gap-3 shadow-lg transition-all active:scale-95">
              <UserPlus className="w-5 h-5" />
              <span>Add User to Role</span>
            </Button>
          </div>

          {/* Users Table */}
          <div className="bg-white dark:bg-slate-950 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-sm">
            <Table>
              <TableHeader className="bg-slate-50 dark:bg-slate-900/50">
                <TableRow className="hover:bg-transparent">
                  <TableHead className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">User</TableHead>
                  <TableHead className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Email</TableHead>
                  <TableHead className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</TableHead>
                  <TableHead className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {role.users.map((user) => (
                  <TableRow key={user.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/50 transition-colors">
                    <TableCell className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <Avatar className="w-9 h-9">
                          <AvatarFallback className={`text-xs font-bold ${user.avatarColor}`}>
                            {user.initials}
                          </AvatarFallback>
                        </Avatar>
                        <span className="font-bold text-sm text-slate-900 dark:text-white">{user.name}</span>
                      </div>
                    </TableCell>
                    <TableCell className="px-6 py-4 text-sm text-slate-500">{user.email}</TableCell>
                    <TableCell className="px-6 py-4">
                      <Badge 
                        variant="outline" 
                        className={`text-[10px] font-bold uppercase tracking-wider border-none ${
                          user.status === 'Active' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                          user.status === 'On Leave' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                          'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                        }`}
                      >
                        {user.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="px-6 py-4 text-right space-x-4">
                      <button className="text-xs font-bold text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors">Change Role</button>
                      <button className="text-xs font-bold text-red-600 hover:opacity-70 transition-colors">Remove</button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Pagination / View All */}
          <div className="flex justify-between items-center py-4 px-2">
            <p className="text-xs text-slate-500 font-medium">Showing {role.users.length} of {role.userCount} users assigned to this role.</p>
            <button className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1 group">
              View All Users
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      )}

      {/* Tab Content: Documents */}
      {activeTab === 'documents' && (
        <div className="p-10 flex flex-col gap-6">
          {/* Toolbar */}
          <div className="flex items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
              <Input 
                className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl py-6 pl-12 pr-4 text-sm focus-visible:ring-2 focus-visible:ring-slate-200 transition-all" 
                placeholder="Search documents..." 
              />
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Sort by:</span>
              <Button variant="outline" className="px-4 py-6 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 rounded-xl font-bold flex items-center gap-2">
                <span>Newest first</span>
                <ChevronDown className="w-4 h-4 text-slate-500" />
              </Button>
            </div>
          </div>

          {/* Documents Table */}
          <div className="bg-white dark:bg-slate-950 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-sm">
            <Table>
              <TableHeader className="bg-slate-50 dark:bg-slate-900/50">
                <TableRow className="hover:bg-transparent">
                  <TableHead className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Document Name</TableHead>
                  <TableHead className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Uploaded By</TableHead>
                  <TableHead className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Date Added</TableHead>
                  <TableHead className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {role.documents?.map((doc) => (
                  <TableRow key={doc.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/50 transition-colors">
                    <TableCell className="px-6 py-6">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                          {getDocIcon(doc.type)}
                        </div>
                        <span className="font-bold text-sm text-slate-900 dark:text-white">{doc.name}</span>
                      </div>
                    </TableCell>
                    <TableCell className="px-6 py-6">
                      <div className="flex items-center gap-3">
                        <Avatar className="w-8 h-8">
                          <AvatarImage src={doc.uploadedBy.avatarUrl} />
                          <AvatarFallback className="text-xs font-bold bg-slate-200 text-slate-700">
                            {doc.uploadedBy.name.split(' ').map(n => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <span className="text-sm text-slate-500">{doc.uploadedBy.name}</span>
                      </div>
                    </TableCell>
                    <TableCell className="px-6 py-6 text-sm text-slate-500">
                      {doc.dateAdded}
                    </TableCell>
                    <TableCell className="px-6 py-6 text-right">
                      <button className="text-xs font-bold text-red-600 hover:opacity-70 transition-colors">Revoke Access</button>
                    </TableCell>
                  </TableRow>
                ))}
                {(!role.documents || role.documents.length === 0) && (
                  <TableRow>
                    <TableCell colSpan={4} className="px-6 py-8 text-center text-slate-500">
                      No documents found for this role.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
            
            {/* Pagination Footer inside table container like the image */}
            {role.documents && role.documents.length > 0 && (
              <div className="bg-slate-50 dark:bg-slate-900/50 border-t border-slate-200 dark:border-slate-800 flex justify-between items-center py-4 px-6">
                <p className="text-xs text-slate-500 font-medium">Showing {role.documents.length} of {role.docCount} documents</p>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="icon" className="w-8 h-8 rounded-lg border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                    <ChevronLeft className="w-4 h-4 text-slate-500" />
                  </Button>
                  <Button variant="outline" size="icon" className="w-8 h-8 rounded-lg border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950">
                    <ChevronRight className="w-4 h-4 text-slate-500" />
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
