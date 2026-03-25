'use client';

import React, { useState } from 'react';
import { UploadCloud, X, ChevronDown } from 'lucide-react';

const availableRoles = ['Admin', 'Manager', 'Viewer', 'Legal', 'DevOps'];

export function UploadSection() {
  const [selectedRoles, setSelectedRoles] = useState<string[]>(['Admin', 'Manager']);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const toggleRole = (role: string) => {
    setSelectedRoles(prev => 
      prev.includes(role) ? prev.filter(r => r !== role) : [...prev, role]
    );
  };

  const removeRole = (role: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedRoles(prev => prev.filter(r => r !== role));
  };

  return (
    <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
      {/* Drag & Drop */}
      <div className="lg:col-span-5 bg-surface-container-lowest border-2 border-dashed border-outline-variant rounded-2xl p-8 flex flex-col items-center justify-center gap-4 group hover:bg-primary-fixed/5 transition-all cursor-pointer">
        <div className="w-16 h-16 rounded-full bg-primary-fixed flex items-center justify-center text-on-primary-fixed transition-transform group-hover:scale-110">
          <UploadCloud className="w-8 h-8" />
        </div>
        <div className="text-center">
          <h3 className="font-headline font-bold text-lg">Drag & Drop Zone</h3>
          <p className="text-sm text-on-surface-variant px-4 mt-1">
            Supported formats: PDF, DOCX, JSON, MD. Maximum file size: 50MB.
          </p>
        </div>
        <button className="mt-2 text-primary text-sm font-bold border-b-2 border-primary/20 hover:border-primary transition-all">
          Browse local storage
        </button>
      </div>

      {/* Metadata Form */}
      <div className="lg:col-span-7 bg-surface-container-lowest rounded-2xl p-8 shadow-sm border border-outline-variant/10 flex flex-col justify-between">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className="text-xs font-bold text-outline uppercase tracking-wider">Process Code</label>
            <input 
              className="w-full bg-surface-container border-none rounded-xl text-sm py-2 px-4 focus:ring-2 focus:ring-primary/5 focus:outline-none" 
              placeholder="e.g. QT-06" 
              type="text" 
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-bold text-outline uppercase tracking-wider">Version</label>
            <input 
              className="w-full bg-surface-container border-none rounded-xl text-sm py-2 px-4 focus:ring-2 focus:ring-primary/5 focus:outline-none" 
              placeholder="v1.4.2" 
              type="text" 
            />
          </div>
          <div className="space-y-1 col-span-2 sm:col-span-1">
            <label className="text-xs font-bold text-outline uppercase tracking-wider">Effective Date</label>
            <input 
              className="w-full bg-surface-container border-none rounded-xl text-sm py-2 px-4 focus:ring-2 focus:ring-primary/5 focus:outline-none" 
              type="date" 
            />
          </div>
        </div>

        {/* Role Access Multi-Selection */}
        <div className="mt-4 space-y-2">
          <label className="text-xs font-bold text-outline uppercase tracking-wider">Role Access</label>
          <div className="relative">
            <div 
              className="w-full bg-surface-container border border-transparent rounded-xl p-2 flex flex-wrap gap-2 items-start content-start min-h-[44px] max-h-[88px] overflow-y-auto focus-within:ring-2 focus-within:ring-primary/10 transition-all cursor-pointer"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            >
              {selectedRoles.map(role => (
                <span key={role} className="flex items-center gap-1 px-3 py-1 bg-primary text-white text-xs font-bold rounded-lg shrink-0">
                  {role}
                  <X className="w-3 h-3 cursor-pointer hover:text-white/80" onClick={(e) => removeRole(role, e)} />
                </span>
              ))}
              {selectedRoles.length === 0 && <span className="text-outline text-sm ml-1 mt-0.5">Select roles...</span>}
              <ChevronDown className="w-4 h-4 ml-auto mt-1 text-outline shrink-0" />
            </div>

            {/* Dropdown */}
            {isDropdownOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setIsDropdownOpen(false)}></div>
                <div className="absolute top-full left-0 w-full mt-2 bg-white rounded-xl shadow-2xl border border-slate-200 z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                  <div className="p-1 max-h-48 overflow-y-auto">
                    {availableRoles.map(role => (
                      <label key={role} className="px-4 py-2 hover:bg-slate-50 text-sm font-medium flex items-center gap-3 text-on-surface cursor-pointer rounded-lg">
                        <input 
                          type="checkbox" 
                          checked={selectedRoles.includes(role)}
                          onChange={() => toggleRole(role)}
                          className="rounded border-slate-300 text-primary focus:ring-primary w-4 h-4" 
                        />
                        {role}
                      </label>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="mt-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-surface-container-highest peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
            <span className="text-sm font-semibold text-on-surface">Use LlamaParse for complex tables</span>
          </div>
          <button className="w-full sm:w-auto bg-primary-container text-white px-8 py-3 rounded-xl font-bold text-sm shadow-xl shadow-primary-container/20 hover:scale-[1.02] active:scale-[0.98] transition-all">
            Upload & Process All
          </button>
        </div>
      </div>
    </section>
  );
}
