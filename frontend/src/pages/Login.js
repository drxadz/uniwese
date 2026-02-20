import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Eye, EyeOff, ArrowRight, Sparkles } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  return (
    <div className="relative flex min-h-screen w-full max-w-[430px] mx-auto flex-col bg-white overflow-y-auto">
      {/* Header */}
      <div className="h-12 w-full" />
      <div className="flex items-center px-6 py-2 justify-between">
        <div className="size-10" />
        <div className="flex-1 text-center">
          <span className="text-primary font-extrabold text-lg tracking-tight">UniWese</span>
        </div>
        <div className="size-10" />
      </div>

      {/* Hero Section */}
      <div className="px-8 pt-12 pb-10 text-left">
        <div className="mb-6 flex">
          <div className="p-3 bg-primary/5 rounded-2xl">
            <Sparkles className="w-8 h-8 text-primary" />
          </div>
        </div>
        <h1 className="text-[#1A1D1F] text-4xl font-extrabold leading-[1.15] tracking-tight mb-4">
          Your Academic Journey <span className="text-primary">Starts Here</span>
        </h1>
        <p className="text-slate-500 text-lg font-medium leading-relaxed">
          Connect with the world's leading universities and industry mentors.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-6 px-8">
        <div className="space-y-5">
          <div className="flex flex-col gap-2">
            <Label className="text-slate-500 text-[13px] font-bold uppercase tracking-wider ml-1">
              Email Address
            </Label>
            <Input
              type="email"
              placeholder="e.g. rahul.sharma@uni.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-xl border border-slate-100 bg-slate-50/50 h-[60px] px-5 text-base font-medium focus:border-primary focus:ring-0 focus:bg-white transition-all placeholder:text-slate-400"
              data-testid="login-email-input"
            />
          </div>

          <div className="flex flex-col gap-2">
            <Label className="text-slate-500 text-[13px] font-bold uppercase tracking-wider ml-1">
              Password
            </Label>
            <div className="relative flex items-center">
              <Input
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-slate-100 bg-slate-50/50 h-[60px] px-5 pr-14 text-base font-medium focus:border-primary focus:ring-0 focus:bg-white transition-all placeholder:text-slate-400"
                data-testid="login-password-input"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-5 text-slate-400 hover:text-primary transition-colors"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <Link 
            to="/forgot-password" 
            className="text-primary text-[15px] font-bold hover:opacity-80 transition-opacity"
          >
            Forgot password?
          </Link>
        </div>

        <Button
          type="submit"
          disabled={loading}
          className="w-full bg-primary hover:bg-primary/90 text-white font-bold text-lg h-[60px] rounded-2xl shadow-lg hover:shadow-xl active:scale-[0.98] transition-all flex items-center justify-center gap-2"
          data-testid="login-submit-btn"
        >
          {loading ? 'Signing in...' : 'Log In'}
          {!loading && <ArrowRight className="w-5 h-5" />}
        </Button>
      </form>

      {/* Divider */}
      <div className="flex items-center py-10 px-8">
        <div className="flex-1 h-[1px] bg-slate-100" />
        <span className="px-5 text-slate-400 text-sm font-semibold uppercase tracking-widest">
          Or continue with
        </span>
        <div className="flex-1 h-[1px] bg-slate-100" />
      </div>

      {/* Social Login */}
      <div className="flex flex-col gap-4 px-8 mb-12">
        <Button
          type="button"
          variant="outline"
          onClick={handleGoogleLogin}
          className="flex items-center justify-center gap-4 w-full border border-slate-200 h-[56px] rounded-2xl font-bold text-[#1A1D1F] hover:bg-slate-50 active:scale-[0.98] transition-all"
          data-testid="google-login-btn"
        >
          <svg className="w-6 h-6" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          <span>Google</span>
        </Button>

        <Button
          type="button"
          variant="outline"
          className="flex items-center justify-center gap-4 w-full border border-slate-200 h-[56px] rounded-2xl font-bold text-[#1A1D1F] hover:bg-slate-50 active:scale-[0.98] transition-all opacity-50 cursor-not-allowed"
          disabled
        >
          <svg className="w-6 h-6 text-[#0A66C2]" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.32 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.79M6.88 8.56a1.68 1.68 0 0 0 1.68-1.68c0-.93-.75-1.69-1.68-1.69a1.69 1.69 0 0 0-1.69 1.69c0 .93.76 1.68 1.69 1.68m1.39 9.94v-8.37H5.5v8.37h2.77z" />
          </svg>
          <span>LinkedIn</span>
        </Button>
      </div>

      {/* Sign Up Link */}
      <div className="mt-auto pb-10 px-8 text-center">
        <p className="text-slate-500 font-medium text-[15px]">
          New to UniWese?{' '}
          <Link 
            to="/register" 
            className="text-primary font-extrabold ml-1 inline-flex items-center hover:underline"
            data-testid="register-link"
          >
            Join the community
          </Link>
        </p>
      </div>

      {/* Home Indicator */}
      <div className="flex justify-center pb-2">
        <div className="w-[134px] h-[5px] bg-slate-200 rounded-full" />
      </div>
    </div>
  );
}
