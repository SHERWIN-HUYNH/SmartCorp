import { FileText } from 'lucide-react';

export default function Hero() {
  return (
    <section className="bg-brand-deepNavy pt-40 pb-24 px-6 overflow-hidden relative">
      {/* Optional background pattern/gradient for depth */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(14,165,233,0.15),transparent)] pointer-events-none"></div>
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center relative z-10">
        {/* Left Content */}
        <div>
          <div className="inline-block text-brand-accent font-bold tracking-widest text-sm mb-6 uppercase">AI PROCESS PLATFORM</div>
          <h1 className="text-white text-5xl lg:text-7xl font-bold leading-tight mb-8">
            Build stronger operational efficiency with Agentic RAG.
          </h1>
          <p className="text-gray-300 text-xl mb-10 max-w-xl">
            Empower your enterprise with an internal process assistant that doesn&apos;t just find information—it reasons through it to execute complex workflows.
          </p>
          <div className="flex flex-wrap gap-4">
            <button className="bg-white text-brand-navy px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-100 transition shadow-lg">
              Try Demo
            </button>
            <button className="border border-gray-600 text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-white/10 transition">
              See Architecture
            </button>
          </div>
        </div>
        {/* Right Mockup */}
        <div className="relative animate-float">
          <div className="bg-white rounded-xl shadow-2xl p-4 md:p-6 max-w-lg mx-auto border border-white/10">
            <div className="flex items-center gap-2 mb-4 border-b pb-3">
              <div className="w-3 h-3 rounded-full bg-red-400"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
              <div className="w-3 h-3 rounded-full bg-green-400"></div>
              <span className="ml-2 text-xs text-gray-400 font-mono">system_oracle_v2.0</span>
            </div>
            <div className="space-y-4">
              <div className="bg-blue-50 p-3 rounded-lg text-sm text-brand-navy font-medium">
                <strong>Query:</strong> &quot;Verify compliance specs for QT-01 internal documentation.&quot;
              </div>
              <div className="flex gap-3">
                <div className="w-8 h-8 bg-brand-navy rounded-full flex-shrink-0 flex items-center justify-center text-white text-[10px]">AI</div>
                <div className="bg-gray-100 p-4 rounded-lg text-sm text-brand-slate">
                  <p className="mb-2"><strong>Retrieving QT-01...</strong></p>
                  <div className="flex items-center gap-2 bg-white p-2 rounded border border-gray-200 text-xs mb-3">
                    <FileText className="w-4 h-4 text-brand-accent inline mr-1" /> doc_QT-01_vfinal.pdf
                  </div>
                  <p>Extraction complete. I&apos;ve identified 3 compliance discrepancies in Section 4.2. Would you like me to draft the correction notice?</p>
                </div>
              </div>
            </div>
          </div>
          {/* Decorative background glow */}
          <div className="absolute -z-10 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-brand-accent/20 blur-3xl rounded-full"></div>
        </div>
      </div>
    </section>
  );
}
