"use client";

import Link from 'next/link';
import { FormEvent, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { User, Mail, Lock, LayoutGrid } from 'lucide-react';

const STRONG_PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

export default function SignupPage() {
  const router = useRouter();
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api';

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const passwordsMatch = useMemo(() => {
    if (!password && !confirmPassword) {
      return true;
    }
    return password === confirmPassword;
  }, [password, confirmPassword]);

  const isStrongPassword = useMemo(() => {
    if (!password) {
      return true;
    }
    return STRONG_PASSWORD_REGEX.test(password);
  }, [password]);

  const showPasswordMismatch = isSubmitted && !passwordsMatch;
  const showWeakPassword = isSubmitted && !isStrongPassword;
  const showTermsError = isSubmitted && !acceptedTerms;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    setIsSubmitted(true);
    setErrorMessage(null);

    if (!passwordsMatch || !isStrongPassword || !acceptedTerms) {
      event.preventDefault();
      return;
    }

    event.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch(`${apiBaseUrl}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          name,
          email,
          password,
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        const detail = payload?.detail;
        if (typeof detail === 'string') {
          throw new Error(detail);
        }
        throw new Error('Signup failed. Please try again.');
      }

      router.push('/chatbot');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Unexpected error happened.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col font-sans relative">
      {/* Header / Logo */}
      <div className="absolute top-0 left-0 w-full p-6 flex items-center">
        <Link href="/" className="flex items-center gap-2">
          <div className="bg-[#0F172A] p-1.5 rounded-md">
            <LayoutGrid className="w-6 h-6 text-white" />
          </div>
          <span className="font-bold text-xl text-[#0F172A]">SmartCorp Oracle</span>
        </Link>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col justify-center items-center px-4 py-12 sm:px-6 lg:px-8 mt-12">
        <div className="bg-white w-full max-w-[520px] rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 p-8 sm:p-12">
          <div className="text-center mb-8">
            <h1 className="text-2xl sm:text-3xl font-bold text-[#0F172A] mb-3">
              Create your enterprise account
            </h1>
            <p className="text-slate-500 text-sm sm:text-base">
              Empower your business with the next generation of data intelligence.
            </p>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            {/* Full Name */}
            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-slate-400" />
                </div>
                <input
                  type="text"
                  placeholder="Enter your full name"
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  className="block w-full pl-11 pr-4 py-3 border border-slate-200 rounded-xl text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-shadow"
                  required
                />
              </div>
            </div>

            {/* Work Email */}
            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-1.5">
                Work Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-slate-400" />
                </div>
                <input
                  type="email"
                  placeholder="name@company.com"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  className="block w-full pl-11 pr-4 py-3 border border-slate-200 rounded-xl text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-shadow"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-1.5">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-400" />
                </div>
                <input
                  type="password"
                  placeholder="Min. 8 characters"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="block w-full pl-11 pr-4 py-3 border border-slate-200 rounded-xl text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-shadow"
                  required
                />
              </div>
              {showWeakPassword && (
                <p className="mt-1.5 text-sm text-red-600">
                  Password must include uppercase, lowercase, number, and special character.
                </p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-1.5">
                Confirm Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-400" />
                </div>
                <input
                  type="password"
                  placeholder="Re-enter your password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  className={`block w-full pl-11 pr-4 py-3 border rounded-xl text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:border-transparent transition-shadow ${
                    showPasswordMismatch
                      ? 'border-red-300 focus:ring-red-500'
                      : 'border-slate-200 focus:ring-slate-900'
                  }`}
                  required
                />
              </div>
              {showPasswordMismatch && (
                <p className="mt-1.5 text-sm text-red-600">
                  Password and confirm password must match.
                </p>
              )}
            </div>

            {/* Terms */}
            <div className="flex items-start pt-2">
              <div className="flex items-center h-5">
                <input
                  id="terms"
                  type="checkbox"
                  checked={acceptedTerms}
                  onChange={(event) => setAcceptedTerms(event.target.checked)}
                  className="w-4 h-4 border border-slate-300 rounded bg-white checked:bg-[#0F172A] checked:border-[#0F172A] focus:ring-2 focus:ring-slate-900 focus:ring-offset-2 transition-colors cursor-pointer"
                />
              </div>
              <label htmlFor="terms" className="ml-3 text-sm text-slate-600">
                I agree to the <Link href="#" className="text-[#EA580C] hover:underline">Terms of Service</Link> and <Link href="#" className="text-[#EA580C] hover:underline">Privacy Policy</Link>.
              </label>
            </div>
            {showTermsError && (
              <p className="-mt-2 text-sm text-red-600">You must accept Terms of Service and Privacy Policy.</p>
            )}

            {errorMessage && (
              <p className="text-sm text-red-600">{errorMessage}</p>
            )}

            {/* Submit Button */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-3.5 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-[#0F172A] hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 transition-colors"
              >
                {isLoading ? 'Creating account...' : 'Create Account'}
              </button>
            </div>
          </form>

          {/* Divider */}
          <div className="mt-8 relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-4 text-slate-400 font-medium tracking-wider">
                Or sign up with
              </span>
            </div>
          </div>

          {/* Google Workspace */}
          <div className="mt-8">
            <button className="w-full flex items-center justify-center gap-3 py-3.5 px-4 border border-slate-200 rounded-xl shadow-sm bg-white text-sm font-semibold text-[#0F172A] hover:bg-slate-50 transition-colors">
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google Workspace
            </button>
          </div>

          <div className="mt-10 text-center text-sm text-slate-600">
            Already have an account?{' '}
            <Link href="/login" className="font-bold text-[#0F172A] hover:underline">
              Sign in
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-8 text-center text-xs text-slate-400 flex justify-center gap-6">
        <span>© 2024 SmartCorp Oracle</span>
        <Link href="#" className="hover:text-slate-600 transition-colors">Contact Support</Link>
        <Link href="#" className="hover:text-slate-600 transition-colors">Legal</Link>
      </footer>
    </div>
  );
}
