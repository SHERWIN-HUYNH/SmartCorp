import {Header} from '@/components/HeaderChatBot';
import SideBar from '@/components/SideBar';
import { ChatArea } from '@/components/ChatArea';
import { InsightsPanel } from '@/components/InsightsPanel';
import { User, Query, Message, FlowNode, Source } from '@/lib/types';

const MOCK_USER: User = {
  name: 'Alex Rivera',
  role: 'System Admin',
  avatar: 'https://picsum.photos/seed/alex/100/100',
};

const MOCK_QUERIES: Query[] = [
  { id: '1', title: 'HR-05 Leave Policy', isActive: true },
  { id: '2', title: 'QT-01 Execution Steps' },
  { id: '3', title: 'Onboarding Guide' },
];

const MOCK_MESSAGES: Message[] = [
  {
    id: 'm1',
    role: 'user',
    content: 'What are the exact steps for process QT-01?',
  },
  {
    id: 'm2',
    role: 'ai',
    content: (
      <>
        <h3 className="font-bold text-slate-900 mb-4">QT-01 Execution Steps</h3>
        <div className="space-y-4 text-sm leading-relaxed text-slate-500">
          <div className="flex gap-4">
            <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-slate-50 flex items-center justify-center font-bold text-slate-900 text-xs border border-slate-500/10">1</span>
            <p><strong className="text-slate-900">Initiate Environment Setup:</strong> Ensure all containerized services are initialized via the Orchestrator panel in the V3 production environment.</p>
          </div>
          <div className="flex gap-4">
            <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-slate-50 flex items-center justify-center font-bold text-slate-900 text-xs border border-slate-500/10">2</span>
            <p><strong className="text-slate-900">Validation Loop:</strong> Run the integrity check script <code className="bg-slate-50 text-slate-900 px-1.5 py-0.5 rounded border border-slate-500/10 font-mono text-[11px]">/bin/check_v2.sh</code> to confirm node heartbeat synchronization.</p>
          </div>
          <div className="flex gap-4">
            <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-slate-50 flex items-center justify-center font-bold text-slate-900 text-xs border border-slate-500/10">3</span>
            <p><strong className="text-slate-900">Final Deployment:</strong> Execute the primary deployment command and monitor the &apos;Process Ready&apos; signal before closing the session.</p>
          </div>
        </div>
      </>
    ),
  },
];

const MOCK_NODES: FlowNode[] = [
  {
    id: 'n1',
    title: 'Router Agent',
    description: 'Classified as Process Execution Query',
    status: 'completed',
  },
  {
    id: 'n2',
    title: 'Self-Correction Loop',
    description: 'Query transformed for better accuracy',
    status: 'active',
  },
  {
    id: 'n3',
    title: 'Retrieval Engine',
    description: 'Hybrid Search & Re-ranking applied',
    status: 'pending',
  },
];

const MOCK_SOURCES: Source[] = [
  { id: 's1', title: 'PDF: QT-01 v2.1', type: 'pdf', url: '#' },
  { id: 's2', title: 'Table: Execution Steps', type: 'table', url: '#' },
];

export default function Home() {
  return (
    <div className="bg-white font-sans text-slate-900 h-screen flex flex-col overflow-hidden">
      <Header />
      <main className="flex flex-1 overflow-hidden">
        <SideBar queries={MOCK_QUERIES} user={MOCK_USER} />
        <ChatArea messages={MOCK_MESSAGES} />
        <InsightsPanel nodes={MOCK_NODES} sources={MOCK_SOURCES} />
      </main>
    </div>
  );
}