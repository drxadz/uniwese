import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AuthCallback() {
  const navigate = useNavigate();
  const { setUserFromCallback } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    // Prevent double processing in StrictMode
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      try {
        // Extract session_id from URL hash
        const hash = window.location.hash;
        const sessionIdMatch = hash.match(/session_id=([^&]+)/);
        
        if (!sessionIdMatch) {
          toast.error('Invalid authentication response');
          navigate('/login');
          return;
        }

        const sessionId = sessionIdMatch[1];

        // Exchange session_id for user session
        const response = await fetch(`${API}/auth/session`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ session_id: sessionId })
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Authentication failed');
        }

        const userData = await response.json();
        setUserFromCallback(userData);
        
        toast.success(`Welcome, ${userData.name}!`);
        
        // Navigate to dashboard with user data
        navigate('/dashboard', { state: { user: userData }, replace: true });
      } catch (error) {
        console.error('Auth callback error:', error);
        toast.error(error.message || 'Authentication failed');
        navigate('/login');
      }
    };

    processAuth();
  }, [navigate, setUserFromCallback]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-muted-foreground">Completing sign in...</p>
      </div>
    </div>
  );
}
