import { Message } from '@/lib/types';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';

interface ChatAreaProps {
  messages: Message[];
}

export function ChatArea({ messages }: ChatAreaProps) {
  return (
    <section className="flex-1 flex flex-col bg-white border-r border-slate-500/20">
      <div className="flex-1 overflow-y-auto p-8 space-y-8">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
      </div>
      <ChatInput />
    </section>
  );
}
