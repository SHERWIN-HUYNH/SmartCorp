import { Paperclip, ArrowUp } from 'lucide-react';

export function ChatInput() {
  return (
    <footer className="p-6 bg-white border-t border-slate-500/10">
      <div className="max-w-3xl mx-auto flex items-center gap-4 mb-3 px-1">
        <div className="flex items-center gap-2">
          <label htmlFor="model-select" className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Model:</label>
          <select id="model-select" className="bg-white border border-slate-500/20 text-slate-900 text-xs rounded-xl focus:ring-slate-900 focus:border-slate-900 py-1.5 pl-3 pr-8 appearance-none cursor-pointer">
            <option>Pro</option>
            <option defaultValue="Standard">Standard</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="length-select" className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Length:</label>
          <select id="length-select" className="bg-white border border-slate-500/20 text-slate-900 text-xs rounded-xl focus:ring-slate-900 focus:border-slate-900 py-1.5 pl-3 pr-8 appearance-none cursor-pointer">
            <option>Short</option>
            <option defaultValue="Medium">Medium</option>
            <option>Long</option>
          </select>
        </div>
      </div>
      
      <div className="max-w-3xl mx-auto relative flex items-center">
        <button className="absolute left-4 text-slate-500 hover:text-slate-900 transition-colors bg-white hover:bg-slate-50 border border-slate-500/10 p-1 rounded-lg" title="Add Documents">
          <Paperclip className="h-5 w-5" />
        </button>
        <input 
          type="text" 
          placeholder="Ask about any internal process or document..." 
          className="w-full pl-12 pr-16 py-4 bg-slate-50 border border-slate-500/20 rounded-xl focus:ring-2 focus:ring-slate-900 focus:border-transparent outline-none text-slate-900 placeholder:text-slate-500 shadow-inner text-sm"
        />
        <button className="absolute right-3 bg-slate-900 hover:bg-slate-800 text-white p-2.5 rounded-xl transition-all shadow-md active:scale-95">
          <ArrowUp className="h-5 w-5" />
        </button>
      </div>
      <p className="text-center text-[10px] text-slate-500 mt-4">SmartCorp Oracle can make mistakes. Check important info.</p>
    </footer>
  );
}
