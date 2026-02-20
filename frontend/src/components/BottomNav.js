import { Link, useLocation } from 'react-router-dom';
import { Home, GraduationCap, FileText, Users, User } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { path: '/dashboard', icon: Home, label: 'Home' },
  { path: '/colleges', icon: GraduationCap, label: 'Colleges' },
  { path: '/applications', icon: FileText, label: 'Applications' },
  { path: '/community', icon: Users, label: 'Community' },
  { path: '/profile', icon: User, label: 'Profile' },
];

export default function BottomNav() {
  const location = useLocation();

  return (
    <nav 
      className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-100 z-50 md:hidden"
      style={{ paddingBottom: 'env(safe-area-inset-bottom, 0px)' }}
      data-testid="bottom-nav"
    >
      <div className="flex items-center justify-around h-16">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path || 
                          (path !== '/dashboard' && location.pathname.startsWith(path));
          
          return (
            <Link
              key={path}
              to={path}
              className={cn(
                "flex flex-col items-center justify-center gap-1 w-full h-full transition-colors",
                isActive 
                  ? "text-primary" 
                  : "text-slate-400 hover:text-slate-600"
              )}
              data-testid={`nav-${label.toLowerCase()}`}
            >
              <Icon 
                className="w-5 h-5" 
                fill={isActive ? "currentColor" : "none"}
                strokeWidth={isActive ? 2.5 : 2}
              />
              <span className="text-xs font-medium">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
