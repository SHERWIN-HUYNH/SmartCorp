import React from 'react';
import { RefreshCw, FileText, File, X } from 'lucide-react';
import { QueueItemData } from '@/lib/types';

const queueItems: QueueItemData[] = [
  {
    id: '1',
    name: 'QT-06-overtime.pdf',
    size: '1.2 MB',
    progress: 68,
    status: 'indexed', // Using 'indexed' to represent the overall progress text in UI, though it's currently embedding
    type: 'pdf',
    activeSteps: ['uploading', 'parsing', 'chunking', 'embedding']
  },
  {
    id: '2',
    name: 'QT-07-bonus.pdf',
    size: '2.4 MB',
    progress: 82,
    status: 'embedding',
    type: 'pdf',
    activeSteps: ['indexed']
  },
  {
    id: '3',
    name: 'HR-policy-2024.docx',
    size: '854 KB',
    progress: 20,
    status: 'parsing',
    type: 'docx',
    activeSteps: ['uploading', 'parsing']
  }
];

export function ProcessingQueue() {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-headline font-bold text-on-surface flex items-center gap-2">
          <RefreshCw className="text-primary w-5 h-5" />
          Active Processing Queue
        </h3>
        <span className="text-xs font-bold px-2 py-1 bg-secondary-container text-on-secondary-container rounded-lg">
          {queueItems.length} active threads
        </span>
      </div>

      <div className="bg-surface-container-lowest rounded-2xl overflow-hidden shadow-sm border border-outline-variant/10">
        {queueItems.map((item, index) => (
          <div 
            key={item.id} 
            className={`p-4 flex items-center gap-6 ${index !== queueItems.length - 1 ? 'border-b border-outline-variant/5' : ''} ${index === 1 ? 'bg-surface-container-low/30' : ''}`}
          >
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${item.type === 'pdf' ? 'bg-error-container/20 text-error' : 'bg-primary-fixed text-primary'}`}>
              {item.type === 'pdf' ? <FileText className="w-5 h-5" /> : <File className="w-5 h-5" />}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm truncate">{item.name}</span>
                  <span className="text-xs text-outline font-medium">{item.size}</span>
                </div>
                <span className="text-xs font-bold text-primary tracking-wide uppercase">
                  {item.progress}% {item.status === 'indexed' ? 'Indexed' : item.status === 'embedding' ? 'Embedding' : 'Parsing'}
                </span>
              </div>
              
              <div className="w-full bg-surface-container-high rounded-full h-2 overflow-hidden">
                <div 
                  className="bg-primary h-full rounded-full transition-all duration-500" 
                  style={{ width: `${item.progress}%` }}
                ></div>
              </div>
              
              <div className="flex items-center gap-4 mt-3">
                {item.activeSteps.map((step, i) => {
                  const isLast = i === item.activeSteps.length - 1 && item.progress < 100;
                  return (
                    <span key={step} className={`flex items-center gap-1 text-[10px] font-bold uppercase ${isLast ? 'text-outline' : 'text-primary'}`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${isLast ? 'bg-outline' : 'bg-primary'}`}></span> 
                      {step}
                    </span>
                  );
                })}
              </div>
            </div>
            
            <button className="p-2 hover:bg-error-container/20 text-outline hover:text-error rounded-full transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
