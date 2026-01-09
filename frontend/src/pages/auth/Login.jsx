import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Mail, Lock, Chrome } from 'lucide-react';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!email.toLowerCase().endsWith('@gmail.com')) {
      setError('Please sign in with your Google (gmail.com) email');
      setLoading(false);
      return;
    }

    try {
      // Get device fingerprint (basic implementation)
      const deviceFingerprint = `${navigator.userAgent}-${navigator.language}`;
      
      const result = await login({
        email,
        password,
        device_fingerprint: deviceFingerprint,
        device_name: navigator.platform,
        browser: navigator.userAgent.split(' ').pop(),
        os: navigator.platform,
      });

      setLoading(false);

      if (result.success) {
        // Navigate based on role from context or localStorage
        const userData = result.user || JSON.parse(localStorage.getItem('user'));
        console.log('Login successful, user:', userData);
        
        if (!userData) {
          setError('User data not found after login');
          return;
        }

        const role = userData.role;
        console.log('User role:', role);

        if (role === 'ADMIN') {
          navigate('/admin', { replace: true });
        } else if (role === 'TEACHER') {
          navigate('/teacher', { replace: true });
        } else if (role === 'STUDENT') {
          navigate('/student', { replace: true });
        } else {
          console.error('Unknown user role:', role);
          setError('Invalid user role: ' + role);
        }
      } else {
        console.error('Login failed:', result.error);
        setError(result.error || 'Login failed');
      }
    } catch (error) {
      console.error('Unexpected error:', error);
      setError('An unexpected error occurred');
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    // Google login will be implemented with Firebase
    try {
      // Placeholder for Google OAuth implementation
      console.log('Google login clicked');
      alert('Google login feature coming soon! For now, use email/password.');
    } catch (err) {
      setError('Google login failed');
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center px-4 bg-gradient-to-br from-brand-deepBlue via-brand-indigo to-gray-900 overflow-hidden relative">
      {/* Decorative Background Elements - Animated Orbs */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-brand-cyan/10 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2 animate-float"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-brand-softPurple/10 rounded-full blur-3xl translate-x-1/2 translate-y-1/2 animate-float-delay"></div>
      <div className="absolute top-1/3 right-0 w-72 h-72 bg-brand-indigo/5 rounded-full blur-3xl animate-pulse"></div>
      
      {/* Grid Pattern Background */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(0,229,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,229,255,0.03)_1px,transparent_1px)] bg-[size:50px_50px]"></div>

      {/* Animated Orbs */}
      <div className="absolute top-20 left-20 w-20 h-20 bg-brand-cyan/20 rounded-full blur-2xl animate-pulse"></div>
      <div className="absolute bottom-32 right-32 w-32 h-32 bg-brand-softPurple/15 rounded-full blur-3xl animate-pulse delay-1000"></div>

      {/* Main Content */}
      <div className="max-w-md w-full relative z-10">
        {/* Top Branding Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-brand-cyan to-brand-indigo rounded-2xl mb-6 shadow-glass animate-bounce-slow">
            <div className="text-2xl">📍</div>
          </div>
          <h1 className="neon-title text-4xl mb-3">Attendance Pro</h1>
          <p className="text-gray-300 text-sm mb-4 font-medium">Next-Generation Attendance Management</p>
          <p className="text-gray-400 text-xs leading-relaxed px-4">
            Powered by geolocation technology and AI-driven face recognition. Secure, fast, and built for modern institutions.
          </p>
          <div className="flex items-center justify-center gap-2 text-xs text-gray-400 mt-4">
            <div className="w-1 h-1 bg-brand-cyan rounded-full"></div>
            <span>Secure • Reliable • Enterprise-Grade</span>
            <div className="w-1 h-1 bg-brand-cyan rounded-full"></div>
          </div>
        </div>

        {/* Glass Card */}
        <div className="glass p-8 rounded-2xl border border-white/10 backdrop-blur-xl shadow-2xl hover:shadow-glass transition-shadow duration-300">
          {/* Tagline */}
          <div className="mb-8 text-center border-b border-white/10 pb-6">
            <h2 className="text-xl font-bold text-white mb-2">Welcome Back</h2>
            <p className="text-gray-400 text-sm leading-relaxed">
              Access your dashboard with state-of-the-art biometric and location verification. Simple. Secure. Smart.
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 bg-red-500/20 border border-red-500/50 text-red-100 px-4 py-3 rounded-2xl text-sm flex items-start gap-3 animate-shake">
              <span className="text-lg flex-shrink-0">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-5 mb-6">
            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
                <Mail size={16} className="text-brand-cyan" /> Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field"
                placeholder="admin@system.com"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Enter your registered email</p>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
                <Lock size={16} className="text-brand-cyan" /> Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field"
                placeholder="••••••••"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Your secure password</p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-3 text-lg font-semibold mt-8 hover:shadow-glass transition-all duration-300"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Signing in...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3 mb-6">
            <div className="h-px bg-gradient-to-r from-white/0 via-white/20 to-white/0 flex-1"></div>
            <span className="text-xs text-gray-400 font-medium">OR</span>
            <div className="h-px bg-gradient-to-r from-white/0 via-white/20 to-white/0 flex-1"></div>
          </div>

          {/* Google Sign-In Button */}
          <button
            onClick={handleGoogleLogin}
            type="button"
            className="w-full flex items-center justify-center gap-3 bg-white/10 hover:bg-white/20 text-white py-3 px-4 rounded-2xl border border-white/20 transition-all duration-300 font-medium group"
          >
            <Chrome size={20} className="text-brand-cyan group-hover:scale-110 transition-transform" />
            <span>Continue with Google</span>
          </button>

          {/* Footer Links */}
          <div className="mt-8 space-y-4 text-center text-sm border-t border-white/10 pt-6">
            <div className="text-gray-400">
              New here?{' '}
              <Link to="/register" className="text-brand-cyan hover:text-brand-cyan/80 font-semibold transition">
                Create your account
              </Link>
            </div>
            <div className="text-gray-500">
              <Link to="#" className="hover:text-gray-400 transition text-xs">
                Forgot password?
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom Info */}
        <div className="mt-8 text-center text-xs text-gray-500 space-y-2">
          <p>🔒 Military-grade encryption protects your data</p>
          <p>✅ ISO 27001 certified • GDPR compliant</p>
        </div>
      </div>
    </div>
  );
};

export default Login;
