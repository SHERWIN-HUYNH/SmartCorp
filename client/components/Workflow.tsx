const steps = [
  {
    num: "01",
    title: "Start with a query",
    desc: "Natural language input via chat, API, or automated system triggers."
  },
  {
    num: "02",
    title: "Intelligent Retrieval",
    desc: "Finding context across your entire fragmented enterprise data landscape."
  },
  {
    num: "03",
    title: "Agentic Reasoning",
    desc: "Thinking through requirements, cross-referencing, and logic validation."
  },
  {
    num: "04",
    title: "Actionable Output",
    desc: "Generating reports, updating systems, or providing verified answers."
  }
];

export default function Workflow() {
  return (
    <section className="py-24 px-6 bg-brand-lightGray" id="workflow">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-brand-navy text-4xl font-bold mb-4">A clear path from question to execution</h2>
          <p className="text-brand-slate text-lg">Our four-step cycle ensures every internal process is handled with precision.</p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, index) => (
            <div key={index} className="bg-white p-10 rounded-xl shadow-md border border-gray-100 relative group">
              <span className="text-4xl font-bold text-gray-100 absolute top-4 right-6 group-hover:text-brand-navy/20 transition">{step.num}</span>
              <h4 className="text-brand-navy font-bold text-xl mb-3">{step.title}</h4>
              <p className="text-sm text-brand-slate">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
