import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Eye, EyeOff, ArrowRight, ArrowLeft, UserPlus } from 'lucide-react';

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!name || !email || !password || !confirmPassword) {
      toast.error('Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      await register(name, email, password);
      toast.success('Account created successfully!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.message || 'Registration failed');
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
        <button 
          onClick={() => navigate('/login')}
          className="flex items-center justify-center size-10 rounded-full hover:bg-slate-50 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-slate-900" />
        </button>
        <div className="flex-1 text-center">
          <span className="text-primary font-extrabold text-lg tracking-tight">UniWese</span>
        </div>
        <div className="size-10" />
      </div>

      {/* Hero Section */}
      <div className="px-8 pt-8 pb-8 text-left">
        <div className="mb-6 flex">
          <div className="p-3 bg-primary/5 rounded-2xl">
            <UserPlus className="w-8 h-8 text-primary" />
          </div>
        </div>
        <h1 className="text-[#1A1D1F] text-3xl font-extrabold leading-[1.15] tracking-tight mb-3">
          Create Your <span className="text-primary">Account</span>
        </h1>
        <p className="text-slate-500 text-base font-medium leading-relaxed">
          Join thousands of students on their journey to top universities.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-5 px-8">
        <div className="space-y-4">
          <div className="flex flex-col gap-2">
            <Label className="text-slate-500 text-[13px] font-bold uppercase tracking-wider ml-1">
              Full Name
            </Label>
            <Input
              type="text"
              placeholder="e.g. Rahul Sharma"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-xl border border-slate-100 bg-slate-50/50 h-[56px] px-5 text-base font-medium focus:border-primary focus:ring-0 focus:bg-white transition-all placeholder:text-slate-400"
              data-testid="register-name-input"
            />
          </div>

          <div className="flex flex-col gap-2">
            <Label className="text-slate-500 text-[13px] font-bold uppercase tracking-wider ml-1">
              Email Address
            </Label>
            <Input
              type="email"
              placeholder="e.g. rahul.sharma@uni.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-xl border border-slate-100 bg-slate-50/50 h-[56px] px-5 text-base font-medium focus:border-primary focus:ring-0 focus:bg-white transition-all placeholder:text-slate-400"
              data-testid="register-email-input"
            />
          </div>

          <div className="flex flex-col gap-2">
            <Label className="text-slate-500 text-[13px] font-bold uppercase tracking-wider ml-1">
              Password
            </Label>
            <div className="relative flex items-center">
              <Input
                type={showPassword ? 'text' : 'password'}
                placeholder="Min. 6 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-slate-100 bg-slate-50/50 h-[56px] px-5 pr-14 text-base font-medium focus:border-primary focus:ring-0 focus:bg-white transition-all placeholder:text-slate-400"
                data-testid="register-password-input"
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

          <div className="flex flex-col gap-2">
            <Label className="text-slate-500 text-[13px] font-bold uppercase tracking-wider ml-1">
              Confirm Password
            </Label>
            <Input
              type={showPassword ? 'text' : 'password'}
              placeholder="Re-enter password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full rounded-xl border border-slate-100 bg-slate-50/50 h-[56px] px-5 text-base font-medium focus:border-primary focus:ring-0 focus:bg-white transition-all placeholder:text-slate-400"
              data-testid="register-confirm-password-input"
            />
          </div>
        </div>

        <Button
          type="submit"
          disabled={loading}
          className="w-full bg-primary hover:bg-primary/90 text-white font-bold text-lg h-[56px] rounded-2xl shadow-lg hover:shadow-xl active:scale-[0.98] transition-all flex items-center justify-center gap-2 mt-2"
          data-testid="register-submit-btn"
        >
          {loading ? 'Creating account...' : 'Create Account'}
          {!loading && <ArrowRight className="w-5 h-5" />}
        </Button>
      </form>

      {/* Divider */}
      <div className="flex items-center py-8 px-8">
        <div className="flex-1 h-[1px] bg-slate-100" />
        <span className="px-5 text-slate-400 text-sm font-semibold uppercase tracking-widest">
          Or
        </span>
        <div className="flex-1 h-[1px] bg-slate-100" />
      </div>

      {/* Social Login */}
      <div className="px-8 mb-8">
        <Button
          type="button"
          variant="outline"
          onClick={handleGoogleLogin}
          className="flex items-center justify-center gap-4 w-full border border-slate-200 h-[56px] rounded-2xl font-bold text-[#1A1D1F] hover:bg-slate-50 active:scale-[0.98] transition-all"
          data-testid="google-signup-btn"
        >
          <svg className="w-6 h-6" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
          </svg>
          <span>Continue with Google</span>
        </Button>
      </div>

      {/* Login Link */}
      <div className="mt-auto pb-10 px-8 text-center">
        <p className="text-slate-500 font-medium text-[15px]">
          Already have an account?{' '}
          <Link 
            to="/login" 
            className="text-primary font-extrabold ml-1 inline-flex items-center hover:underline"
            data-testid="login-link"
          >
            Log in
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
