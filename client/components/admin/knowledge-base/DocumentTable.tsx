'use client';

import React, { useState } from 'react';
import { 
  Search, Filter, Download, Settings, FileText, 
  File, Database, Edit2, Eye, RefreshCw, Trash2, AlertTriangle,
  ChevronLeft, ChevronRight
} from 'lucide-react';
import { DocumentData } from '@/types';

const documents: DocumentData[] = [
  {
    id: '1',
    name: 'Employee_Handbook_2024.pdf',
    type: 'PDF Document',
    size: '4.5MB',
    processCode: 'HR-01',
    version: 'v2.1',
    effectiveDate: 'Jan 01, 2024',
    roles: ['Admin', 'Manager'],
    status: 'indexed'
  },
  {
    id: '2',
    name: 'Cloud_Infrastructure_Specs.docx',
    type: 'Word Doc',
    size: '1.2MB',
    processCode: 'IT-05',
    version: 'v1.0',
    effectiveDate: 'Mar 15, 2024',
    roles: ['DevOps'],
    status: 'chunking'
  },
  {
    id: '3',
    name: 'Compliance_Schema_2024.json',
    type: 'JSON Data',
    size: '0.5MB',
    processCode: 'LEG-09',
    version: 'v3.4',
    effectiveDate: 'Feb 20, 2024',
    roles: ['Legal'],
    status: 'failed'
  }
];

export function DocumentTable() {
  const [openPopoverId, setOpenPopoverId] = useState<string | null>(null);

  const togglePopover = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setOpenPopoverId(openPopoverId === id ? null : id);
  };

  // Close popover when clicking outside
  React.useEffect(() => {
    const handleClickOutside = () => setOpenPopoverId(null);
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  return (
    <section className="space-y-4 mb-12">
      {/* Search & Filters */}
      <div className="bg-surface-container-low p-4 rounded-2xl flex flex-wrap items-center gap-4 shadow-sm border border-outline-variant/10">
        <div className="flex-1 min-w-[300px] relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-outline w-4 h-4" />
          <input 
            className="w-full bg-surface-container-lowest border-none rounded-xl pl-10 pr-4 py-2.5 text-sm focus:ring-2 focus:ring-primary/5 focus:outline-none shadow-sm transition-all" 
            placeholder="Search by Document Name or Code..." 
            type="text" 
          />
        </div>
        <div className="flex gap-3 items-center">
          <select className="bg-surface-container-lowest border-none rounded-xl text-sm font-medium py-2.5 px-4 focus:ring-2 focus:ring-primary/5 focus:outline-none shadow-sm min-w-[120px]">
            <option>Format: All</option>
            <option>PDF</option>
            <option>DOCX</option>
            <option>JSON</option>
          </select>
          <select className="bg-surface-container-lowest border-none rounded-xl text-sm font-medium py-2.5 px-4 focus:ring-2 focus:ring-primary/5 focus:outline-none shadow-sm min-w-[120px]">
            <option>Status: All</option>
            <option>Indexed</option>
            <option>Processing</option>
            <option>Pending</option>
            <option>Failed</option>
          </select>
          <button className="px-4 py-2 bg-surface-container-lowest border border-outline-variant/30 rounded-xl flex items-center gap-2 text-sm font-semibold hover:bg-surface-container-low transition-colors shadow-sm">
            <Filter className="w-4 h-4" />
            Filters
          </button>
        </div>
      </div>

      {/* Table Container */}
      <div className="bg-surface-container-lowest rounded-2xl shadow-sm border border-slate-200 overflow-visible">
        <div className="p-6 border-b border-slate-200 flex items-center justify-between">
          <h3 className="font-headline font-bold text-on-surface">Document Index Registry</h3>
          <div className="flex gap-2">
            <button className="p-2 rounded-lg hover:bg-surface-container-low transition-colors text-outline">
              <Download className="w-5 h-5" />
            </button>
            <button className="p-2 rounded-lg hover:bg-surface-container-low transition-colors text-outline">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 text-xs font-bold text-outline uppercase tracking-wider border-r border-slate-200/60 last:border-0">Document Name</th>
                <th className="px-6 py-4 text-xs font-bold text-outline uppercase tracking-wider border-r border-slate-200/60 last:border-0">Process Code</th>
                <th className="px-6 py-4 text-xs font-bold text-outline uppercase tracking-wider border-r border-slate-200/60 last:border-0">V. Effective</th>
                <th className="px-6 py-4 text-xs font-bold text-outline uppercase tracking-wider border-r border-slate-200/60 last:border-0">Allowed Roles</th>
                <th className="px-6 py-4 text-xs font-bold text-outline uppercase tracking-wider border-r border-slate-200/60 last:border-0">Status</th>
                <th className="px-6 py-4 text-xs font-bold text-outline uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-slate-50/50 transition-colors group">
                  <td className="px-6 py-4 border-r border-slate-100 last:border-0">
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded flex items-center justify-center ${
                        doc.type.includes('PDF') ? 'bg-red-50 text-red-500' : 
                        doc.type.includes('Word') ? 'bg-blue-50 text-blue-500' : 
                        'bg-yellow-50 text-yellow-600'
                      }`}>
                        {doc.type.includes('PDF') ? <FileText className="w-4 h-4" /> : 
                         doc.type.includes('Word') ? <File className="w-4 h-4" /> : 
                         <Database className="w-4 h-4" />}
                      </div>
                      <div>
                        <p className="text-sm font-bold text-on-surface">{doc.name}</p>
                        <p className="text-[10px] text-outline">{doc.type} • {doc.size}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 border-r border-slate-100 last:border-0">
                    <span className="px-2 py-1 bg-primary-fixed text-on-primary-fixed text-[10px] font-extrabold rounded-md uppercase">
                      {doc.processCode}
                    </span>
                  </td>
                  <td className="px-6 py-4 border-r border-slate-100 last:border-0">
                    <div className="text-[11px]">
                      <p className="font-bold text-on-surface">{doc.version}</p>
                      <p className="text-outline">{doc.effectiveDate}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 border-r border-slate-100 last:border-0 relative">
                    <div className="relative" onClick={(e) => e.stopPropagation()}>
                      <button 
                        className="w-full flex flex-wrap gap-1 p-1 bg-surface-container-low border border-slate-200 rounded-lg hover:border-primary/30 transition-all text-left items-start content-start max-h-[60px] overflow-y-auto"
                        onClick={(e) => togglePopover(doc.id, e)}
                      >
                        {doc.roles.map(role => (
                          <span key={role} className="px-2 py-0.5 bg-primary text-white text-[10px] font-bold rounded shrink-0">
                            {role}
                          </span>
                        ))}
                        <Edit2 className="w-3.5 h-3.5 ml-auto mt-0.5 text-outline shrink-0" />
                      </button>

                      {/* Permission Popover */}
                      {openPopoverId === doc.id && (
                        <div className="absolute left-0 top-full mt-2 z-[60] w-48 bg-white rounded-xl shadow-2xl border border-slate-200 p-4 space-y-3 animate-in fade-in zoom-in duration-200">
                          <p className="text-[10px] font-bold text-outline uppercase tracking-widest">Update Permissions</p>
                          <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
                            {['Admin', 'Manager', 'Viewer', 'Legal', 'DevOps'].map(role => (
                              <label key={role} className="flex items-center gap-2 cursor-pointer">
                                <input 
                                  type="checkbox" 
                                  defaultChecked={doc.roles.includes(role)}
                                  className="w-3.5 h-3.5 rounded border-slate-300 text-primary focus:ring-primary shrink-0" 
                                />
                                <span className="text-xs font-medium text-on-surface">{role}</span>
                              </label>
                            ))}
                          </div>
                          <div className="flex gap-2 pt-2 border-t border-slate-100">
                            <button 
                              className="flex-1 py-1.5 bg-primary text-white text-[10px] font-bold rounded-lg hover:opacity-90 transition-all"
                              onClick={() => setOpenPopoverId(null)}
                            >
                              Save
                            </button>
                            <button 
                              className="flex-1 py-1.5 bg-slate-100 text-slate-600 text-[10px] font-bold rounded-lg hover:bg-slate-200 transition-colors"
                              onClick={() => setOpenPopoverId(null)}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 border-r border-slate-100 last:border-0">
                    {doc.status === 'indexed' && (
                      <span className="px-2 py-1 bg-emerald-100 text-emerald-700 text-[10px] font-extrabold rounded-full uppercase flex items-center w-fit gap-1">
                        <span className="w-1 h-1 rounded-full bg-emerald-500"></span> Indexed
                      </span>
                    )}
                    {doc.status === 'chunking' && (
                      <span className="px-2 py-1 bg-amber-100 text-amber-700 text-[10px] font-extrabold rounded-full uppercase flex items-center w-fit gap-1">
                        <span className="w-1 h-1 rounded-full bg-amber-500 animate-pulse"></span> Chunking
                      </span>
                    )}
                    {doc.status === 'failed' && (
                      <span className="px-2 py-1 bg-error-container/20 text-error text-[10px] font-extrabold rounded-full uppercase flex items-center w-fit gap-1">
                        <span className="w-1 h-1 rounded-full bg-error"></span> Failed
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      {doc.status !== 'failed' ? (
                        <>
                          <button className="p-2 hover:bg-slate-100 rounded-lg text-outline"><Eye className="w-4 h-4" /></button>
                          <button className="p-2 hover:bg-slate-100 rounded-lg text-outline"><RefreshCw className="w-4 h-4" /></button>
                        </>
                      ) : (
                        <>
                          <button className="p-2 hover:bg-slate-100 rounded-lg text-outline"><AlertTriangle className="w-4 h-4" /></button>
                          <button className="p-2 hover:bg-slate-100 rounded-lg text-outline"><RefreshCw className="w-4 h-4" /></button>
                        </>
                      )}
                      <button className="p-2 hover:bg-error-container/10 text-error rounded-lg"><Trash2 className="w-4 h-4" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-6 border-t border-slate-200 bg-slate-50/50 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-outline font-medium">
            Showing <span className="text-on-surface font-bold">1-3</span> of <span className="text-on-surface font-bold">1,245</span> documents
          </p>
          <div className="flex items-center gap-2">
            <button className="p-2 px-3 text-sm font-bold text-outline hover:text-on-surface hover:bg-white border border-slate-200 rounded-lg transition-all flex items-center gap-1 disabled:opacity-50 disabled:cursor-not-allowed" disabled>
              <ChevronLeft className="w-4 h-4" /> Prev
            </button>
            <div className="flex items-center gap-1">
              <button className="w-9 h-9 flex items-center justify-center rounded-lg bg-slate-900 text-white font-bold text-sm shadow-md">1</button>
              <button className="w-9 h-9 flex items-center justify-center rounded-lg text-outline hover:text-on-surface hover:bg-white font-bold text-sm border border-transparent hover:border-slate-200 transition-all">2</button>
            </div>
            <button className="p-2 px-3 text-sm font-bold text-outline hover:text-on-surface hover:bg-white border border-slate-200 rounded-lg transition-all flex items-center gap-1">
              Next <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
