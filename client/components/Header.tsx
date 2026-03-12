import Link from 'next/link';

export default function Header() {
  return (
    <header className="absolute top-0 left-0 w-full z-50 bg-transparent py-6">
      <nav className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        <div className="text-white font-bold text-2xl tracking-tight">
          SmartCorp Oracle
        </div>
        {/* Desktop Navigation */}
        <ul className="hidden md:flex space-x-10 text-gray-300 font-medium">
          <li><Link href="#features" className="hover:text-white transition">Features</Link></li>
          <li><Link href="#architecture" className="hover:text-white transition">Architecture</Link></li>
          <li><Link href="#workflow" className="hover:text-white transition">Workflow</Link></li>
          <li><Link href="#feedback" className="hover:text-white transition">Feedback</Link></li>
        </ul>
        <div className="flex items-center">
          <button className="bg-white text-brand-navy px-6 py-2.5 rounded-xl font-bold hover:bg-gray-100 transition shadow-sm">
            Get Started
          </button>
        </div>
      </nav>
    </header>
  );
}
