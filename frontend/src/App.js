import { useEffect, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";

// Pages
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import AuthCallback from "@/pages/AuthCallback";
import Dashboard from "@/pages/Dashboard";
import Profile from "@/pages/Profile";
import CollegeDirectory from "@/pages/CollegeDirectory";
import CollegeDetail from "@/pages/CollegeDetail";
import MyApplications from "@/pages/MyApplications";
import ApplicationForm from "@/pages/ApplicationForm";
import Community from "@/pages/Community";
import ThreadDetail from "@/pages/ThreadDetail";
import LoanAssistance from "@/pages/LoanAssistance";
import Accommodation from "@/pages/Accommodation";
import AdminDashboard from "@/pages/AdminDashboard";

// Components
import BottomNav from "@/components/BottomNav";
import ProtectedRoute from "@/components/ProtectedRoute";

// Context
import { AuthProvider, useAuth } from "@/context/AuthContext";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function AppContent() {
  const location = useLocation();
  const { user, loading } = useAuth();

  // Check for session_id in URL hash (OAuth callback)
  // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }

  // Pages where bottom nav should be hidden
  const hideBottomNav = ['/login', '/register', '/auth/callback'].includes(location.pathname) || 
                         location.pathname.startsWith('/admin');

  // Show loading while checking auth
  if (loading && !['/login', '/register'].includes(location.pathname)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={user ? <Navigate to="/dashboard" replace /> : <Login />} />
        <Route path="/register" element={user ? <Navigate to="/dashboard" replace /> : <Register />} />
        <Route path="/auth/callback" element={<AuthCallback />} />

        {/* Protected routes */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="/colleges" element={<ProtectedRoute><CollegeDirectory /></ProtectedRoute>} />
        <Route path="/colleges/:collegeId" element={<ProtectedRoute><CollegeDetail /></ProtectedRoute>} />
        <Route path="/applications" element={<ProtectedRoute><MyApplications /></ProtectedRoute>} />
        <Route path="/apply/:collegeId" element={<ProtectedRoute><ApplicationForm /></ProtectedRoute>} />
        <Route path="/community" element={<ProtectedRoute><Community /></ProtectedRoute>} />
        <Route path="/community/:threadId" element={<ProtectedRoute><ThreadDetail /></ProtectedRoute>} />
        <Route path="/loans" element={<ProtectedRoute><LoanAssistance /></ProtectedRoute>} />
        <Route path="/accommodation" element={<ProtectedRoute><Accommodation /></ProtectedRoute>} />

        {/* Admin routes */}
        <Route path="/admin/*" element={<ProtectedRoute requireAdmin><AdminDashboard /></ProtectedRoute>} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>

      {/* Bottom Navigation - Mobile */}
      {!hideBottomNav && user && <BottomNav />}
      
      {/* Toast notifications */}
      <Toaster position="top-center" richColors />
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
