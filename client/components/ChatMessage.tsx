import { Message } from '@/lib/types';
import { Sparkles, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end items-start gap-4">
        <div className="max-w-[80%] bg-slate-100 text-slate-900 p-4 rounded-xl rounded-tr-none border border-slate-200 shadow-sm">
          <p className="text-sm font-medium">{message.content}</p>
        </div>
        <div className="w-8 h-8 rounded-full bg-slate-900 flex-shrink-0 shadow-sm" />
      </div>
    );
  }

  return (
    <div className="flex justify-start items-start gap-4">
      <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center flex-shrink-0 shadow-sm">
        <Sparkles className="h-4 w-4 text-white" />
      </div>
      <div className="max-w-[85%] bg-white p-6 rounded-xl rounded-tl-none border border-slate-500/10 shadow-md relative group">
        {message.content}
        
        <div className="mt-6 pt-4 border-t border-slate-500/10 flex items-center justify-between">
          <div className="flex gap-3">
            <button className="text-slate-500 hover:text-slate-900 transition-colors" title="Copy to clipboard">
              <Copy className="h-4 w-4" />
            </button>
            <button className="text-slate-500 hover:text-green-600 transition-colors" title="Helpful">
              <ThumbsUp className="h-4 w-4" />
            </button>
            <button className="text-slate-500 hover:text-red-600 transition-colors" title="Not helpful">
              <ThumbsDown className="h-4 w-4" />
            </button>
          </div>
          <span className="text-[10px] text-slate-500 font-medium italic">Verified by Agentic Flow v4.2</span>
        </div>
      </div>
    </div>
  );
}
