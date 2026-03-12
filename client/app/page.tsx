import Header from '@/components/Header';
import Hero from '@/components/Hero';
import Features from '@/components/Features';
import Workflow from '@/components/Workflow';
import CTA from '@/components/CTA';
import Footer from '@/components/Footer';

export default function Home() {
  return (
    <main className="min-h-screen bg-white font-sans antialiased text-brand-slate">
      <Header />
      <Hero />
      <Features />
      <Workflow />
      <CTA />
      <Footer />
    </main>
  );
}
