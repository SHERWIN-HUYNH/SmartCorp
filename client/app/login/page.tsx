"use client";

import Link from 'next/link';
import { Eye, EyeOff, Building, Database } from 'lucide-react';
import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';

import { AuthApiError, login } from '@/lib/auth-api';
import { getLandingPathForRole } from '@/lib/role-access';

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage(null);
    setIsLoading(true);

    try {
      if (!email.trim() || !password.trim()) {
        setErrorMessage('Email and password are required.');
        return;
      }
      const response = await login(email, password);
      console.log('Login successful. User role:', response.user.role);
      router.push(getLandingPathForRole(response.user.role));
    } catch (error) {
      if (error instanceof AuthApiError) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage('Unexpected error happened. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col font-sans">
      {/* Main Content */}
      <div className="flex-1 flex flex-col justify-center items-center px-4 py-12 sm:px-6 lg:px-8">
        
        {/* Header / Logo */}
        <div className="mb-8 text-center flex flex-col items-center">
          <Link href="/" className="flex items-center gap-3 mb-8">
            <div className="bg-[#0F172A] p-2 rounded-xl">
              <Database className="w-7 h-7 text-white" />
            </div>
            <span className="font-bold text-2xl text-[#0F172A]">SmartCorp Oracle</span>
          </Link>
          <h1 className="text-3xl sm:text-4xl font-bold text-[#0F172A] mb-3">
            Welcome back!
          </h1>
          <p className="text-slate-500 text-sm sm:text-base">
            Please login to your account.
          </p>
        </div>

        <div className="bg-white w-full max-w-[480px] rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 p-8 sm:p-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Email Address */}
            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Email Address
              </label>
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="block w-full px-4 py-3.5 border border-slate-200 rounded-xl text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-shadow"
                required
              />
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-[#0F172A]">
                  Password
                </label>
                <Link href="#" className="text-sm font-medium text-slate-500 hover:text-[#0F172A] underline decoration-slate-300 underline-offset-4 transition-colors">
                  Forgot Password?
                </Link>
              </div>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  className="block w-full pl-4 pr-11 py-3.5 border border-slate-200 rounded-xl text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-shadow"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center cursor-pointer"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-slate-400 hover:text-slate-600 transition-colors" />
                  ) : (
                    <Eye className="h-5 w-5 text-slate-400 hover:text-slate-600 transition-colors" />
                  )}
                </button>
              </div>
            </div>

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
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
            </div>
          </form>

          {/* Divider */}
          <div className="mt-8 relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-white px-4 text-slate-500">
                Or continue with
              </span>
            </div>
          </div>

          {/* SSO Login */}
          <div className="mt-8">
            <button className="w-full flex items-center justify-center gap-2 py-3.5 px-4 border border-slate-300 rounded-xl shadow-sm bg-white text-sm font-semibold text-[#0F172A] hover:bg-slate-50 transition-colors">
              <Building className="w-4 h-4" />
              SSO / Enterprise Login
            </button>
          </div>
        </div>

        <div className="mt-10 text-center text-sm text-slate-500">
          Don&apos;t have an account?{' '}
          <Link href="/signup" className="font-bold text-[#0F172A] hover:underline underline-offset-4">
            Sign up
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="py-8 text-center text-xs text-slate-400">
        © 2024 SmartCorp Oracle. All rights reserved.
      </footer>
    </div>
  );
}
