import Link from "next/link";

export default function CTA() {
  return (
    <section className="bg-brand-deepNavy py-24 px-6 text-center relative overflow-hidden">
      {/* Optional background accent */}
      <div className="absolute inset-0 bg-gradient-to-tr from-brand-navy to-slate-900 opacity-50"></div>
      <div className="max-w-3xl mx-auto relative z-10">
        <h2 className="text-white text-3xl md:text-5xl font-bold mb-8 leading-tight">
          Ready to upgrade your internal workflow?
        </h2>
        <Link href="/signup" className="bg-white text-brand-navy px-10 py-5 rounded-xl font-bold text-xl hover:bg-gray-100 transition shadow-xl">
          Create Free Account
        </Link>
      </div>
    </section>
  );
}
