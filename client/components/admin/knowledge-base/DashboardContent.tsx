'use client';

import { useState, useRef, useEffect } from 'react';
import { ArrowUp, Minus, Info, Calendar, Filter, ChevronDown } from 'lucide-react';
import { topDocuments } from '@/app/dataAdmin';

export default function DashboardContent() {
  const [timeFilterOpen, setTimeFilterOpen] = useState(false);
  const [selectedTime, setSelectedTime] = useState('7 Ngày qua');
  
  const [deptFilterOpen, setDeptFilterOpen] = useState(false);
  const [selectedDept, setSelectedDept] = useState('Tất cả phòng ban');

  const timeOptions = ['7 Ngày qua', '30 ngày', '6 tháng', '1 năm'];
  const deptOptions = [
    'Tất cả phòng ban', 
    'HR (Nhân sự)', 
    'Vận hành', 
    'Sản xuất', 
    'Safety (An toàn)', 
    'IT', 
    'Security (Bảo mật)', 
    'Kế toán', 
    'Marketing',
    'Kinh doanh',
    'Pháp chế'
  ];

  // Close dropdowns when clicking outside
  const timeRef = useRef<HTMLDivElement>(null);
  const deptRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (timeRef.current && !timeRef.current.contains(event.target as Node)) {
        setTimeFilterOpen(false);
      }
      if (deptRef.current && !deptRef.current.contains(event.target as Node)) {
        setDeptFilterOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="lg:col-span-7 bg-white rounded-2xl shadow-sm border border-slate-200 flex flex-col relative z-10">
      {/* Header */}
      <div className="p-6 border-b border-slate-100 flex flex-col md:flex-row md:justify-between md:items-center gap-4 bg-white rounded-t-2xl">
        <h3 className="text-xl font-bold text-slate-900">Top 5 Tài liệu được trích dẫn nhiều nhất</h3>
        
        <div className="flex items-center gap-3">
          {/* Time Filter */}
          <div className="relative" ref={timeRef}>
            <button 
              onClick={() => setTimeFilterOpen(!timeFilterOpen)}
              className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
            >
              <Calendar className="w-4 h-4 text-slate-500" />
              <span>{selectedTime}</span>
              <ChevronDown className="w-4 h-4 text-slate-400 ml-1" />
            </button>
            
            {timeFilterOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white border border-slate-200 rounded-xl shadow-lg z-50 py-1">
                {timeOptions.map(option => (
                  <button
                    key={option}
                    onClick={() => {
                      setSelectedTime(option);
                      setTimeFilterOpen(false);
                    }}
                    className={`w-full text-left px-4 py-2 text-sm hover:bg-slate-50 transition-colors ${selectedTime === option ? 'text-blue-600 font-bold bg-blue-50/50' : 'text-slate-700'}`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Department Filter */}
          <div className="relative" ref={deptRef}>
            <button 
              onClick={() => setDeptFilterOpen(!deptFilterOpen)}
              className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
            >
              <Filter className="w-4 h-4 text-slate-500" />
              <span className="max-w-[120px] truncate">{selectedDept}</span>
              <ChevronDown className="w-4 h-4 text-slate-400 ml-1" />
            </button>
            
            {deptFilterOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white border border-slate-200 rounded-xl shadow-lg z-50 py-1 max-h-64 overflow-y-auto custom-scrollbar">
                {deptOptions.map(option => (
                  <button
                    key={option}
                    onClick={() => {
                      setSelectedDept(option);
                      setDeptFilterOpen(false);
                    }}
                    className={`w-full text-left px-4 py-2 text-sm hover:bg-slate-50 transition-colors ${selectedDept === option ? 'text-blue-600 font-bold bg-blue-50/50' : 'text-slate-700'}`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* List */}
      <div className="p-0 flex-1 flex flex-col">
        {topDocuments.map((doc) => (
          <div key={doc.id} className="flex items-center justify-between p-6 border-b border-slate-100 last:border-0 hover:bg-slate-50/50 transition-colors">
            <div className="flex items-center gap-5 w-[40%]">
              <div className={`w-12 h-12 rounded-xl ${doc.iconWrapperClass} flex items-center justify-center flex-shrink-0`}>
                <doc.icon className={`w-6 h-6 ${doc.iconClass}`} />
              </div>
              <div className="min-w-0">
                <h4 className="text-base font-bold text-slate-900 truncate">{doc.title}</h4>
                <div className="flex flex-wrap gap-2 mt-1.5">
                  {doc.tags.map(tag => (
                    <span key={tag} className="text-[11px] font-bold px-2.5 py-0.5 bg-slate-100 text-slate-600 rounded-full">{tag}</span>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="flex-1 px-8 hidden md:block">
              <svg className="w-full h-10 drop-shadow-sm" preserveAspectRatio="none" viewBox="0 0 100 30">
                <path d={doc.sparklinePath} fill="none" stroke="#0F172A" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5"></path>
              </svg>
            </div>
            
            <div className="text-right w-32 flex flex-col items-end">
              <p className="text-3xl font-black text-slate-900 leading-none">{doc.views}</p>
              <div className={`flex items-center justify-end gap-1 mt-2 ${doc.trendType === 'steady' ? 'text-amber-600' : 'text-emerald-600'}`}>
                {doc.trendType === 'steady' ? <Minus className="w-3.5 h-3.5" /> : <ArrowUp className="w-3.5 h-3.5" />}
                <span className="text-xs font-bold">
                  {doc.trendType === 'steady' ? 'Steady usage' : `+${doc.trendPercentage}% vs last week`}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 rounded-b-2xl">
        <p className="text-xs text-slate-500 flex items-center gap-1.5 font-medium">
          <Info className="w-4 h-4" />
          Dữ liệu được cập nhật theo thời gian thực từ hệ thống RAG.
        </p>
      </div>
    </div>
  );
}
