import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-slate-950 py-16 px-6 border-t border-white/5">
      <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-12 text-gray-400">
        <div>
          <h5 className="text-white font-bold mb-6">Explore</h5>
          <ul className="space-y-4 text-sm">
            <li><Link href="#" className="hover:text-white transition">Documentation</Link></li>
            <li><Link href="#" className="hover:text-white transition">Templates</Link></li>
            <li><Link href="#" className="hover:text-white transition">Integrations</Link></li>
            <li><Link href="#" className="hover:text-white transition">API Reference</Link></li>
          </ul>
        </div>
        <div>
          <h5 className="text-white font-bold mb-6">Account</h5>
          <ul className="space-y-4 text-sm">
            <li><Link href="#" className="hover:text-white transition">Sign In</Link></li>
            <li><Link href="#" className="hover:text-white transition">Billing</Link></li>
            <li><Link href="#" className="hover:text-white transition">Security Settings</Link></li>
            <li><Link href="#" className="hover:text-white transition">Developer Portal</Link></li>
          </ul>
        </div>
        <div>
          <h5 className="text-white font-bold mb-6">Legal</h5>
          <ul className="space-y-4 text-sm">
            <li><Link href="#" className="hover:text-white transition">Privacy Policy</Link></li>
            <li><Link href="#" className="hover:text-white transition">Terms of Service</Link></li>
            <li><Link href="#" className="hover:text-white transition">Cookie Policy</Link></li>
            <li><Link href="#" className="hover:text-white transition">GDPR Compliance</Link></li>
          </ul>
        </div>
        <div>
          <div className="text-white font-bold text-xl mb-6">SmartCorp Oracle</div>
          <p className="text-xs leading-relaxed mb-6">
            Advanced Agentic RAG for the modern enterprise. Built for security, speed, and accuracy.
          </p>
          <p className="text-xs">© 2024 SmartCorp. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
