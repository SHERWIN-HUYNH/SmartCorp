import { Download, Search, Zap, Bot, Map, Link as LinkIcon } from 'lucide-react';

const features = [
  {
    icon: Download,
    title: "Multi-Format Ingestion",
    description: "Seamlessly process PDFs, JSON, Markdown, and direct database streams with automated metadata tagging."
  },
  {
    icon: Search,
    title: "Advanced Extraction",
    description: "High-fidelity entity recognition and table parsing that outperforms standard LLM context windows."
  },
  {
    icon: Zap,
    title: "Hybrid Search & Reranking",
    description: "Combining semantic vector search with keyword precision and cross-encoders for the most relevant results."
  },
  {
    icon: Bot,
    title: "Agentic Self-Correction",
    description: "The system validates its own reasoning steps to ensure factual consistency and hallucination prevention."
  },
  {
    icon: Map,
    title: "Step-by-Step Guidance",
    description: "Visual transparency into how the AI reached a conclusion, allowing human-in-the-loop oversight."
  },
  {
    icon: LinkIcon,
    title: "LangGraph Orchestration",
    description: "Leverage state-of-the-art cyclic graphs for complex, multi-hop reasoning and long-running tasks."
  }
];

export default function Features() {
  return (
    <section className="py-24 px-6 bg-white" id="features">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-brand-navy text-4xl font-bold mb-4">Core Capabilities</h2>
          <p className="text-brand-slate text-lg">Engineered for accuracy, scale, and enterprise security.</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="p-8 bg-white border border-gray-100 rounded-xl shadow-md hover:shadow-lg transition group">
              <div className="w-12 h-12 bg-brand-navy/5 text-brand-navy rounded-lg flex items-center justify-center mb-6 text-2xl group-hover:bg-brand-navy group-hover:text-white transition-colors">
                <feature.icon className="w-6 h-6" />
              </div>
              <h3 className="text-brand-navy text-xl font-bold mb-3">{feature.title}</h3>
              <p className="text-brand-slate">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
