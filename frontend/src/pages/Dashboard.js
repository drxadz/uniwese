import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  GraduationCap, FileText, Users, Wallet, Home as HomeIcon, 
  ArrowRight, Bell, Search, Star, TrendingUp, Calendar,
  ChevronRight, Plus, MapPin
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [applications, setApplications] = useState([]);
  const [colleges, setColleges] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [profileRes, appsRes, collegesRes] = await Promise.all([
        fetch(`${API}/profile`, { credentials: 'include' }),
        fetch(`${API}/applications`, { credentials: 'include' }),
        fetch(`${API}/colleges?limit=5`, { credentials: 'include' })
      ]);

      if (profileRes.ok) setProfile(await profileRes.json());
      if (appsRes.ok) setApplications(await appsRes.json());
      if (collegesRes.ok) {
        const data = await collegesRes.json();
        setColleges(data.colleges || []);
      }
    } catch (error) {
      console.error('Dashboard fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    { icon: GraduationCap, label: 'Colleges', path: '/colleges', color: 'bg-blue-500' },
    { icon: FileText, label: 'Applications', path: '/applications', color: 'bg-green-500' },
    { icon: Users, label: 'Community', path: '/community', color: 'bg-purple-500' },
    { icon: Wallet, label: 'Loans', path: '/loans', color: 'bg-orange-500' },
  ];

  const getStatusColor = (status) => {
    const colors = {
      submitted: 'bg-blue-100 text-blue-800',
      under_review: 'bg-yellow-100 text-yellow-800',
      accepted: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      withdrawn: 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-24 md:pb-8">
      {/* Header */}
      <div className="bg-primary text-white px-6 pt-12 pb-8 rounded-b-3xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="text-primary-foreground/80 text-sm font-medium">Welcome back,</p>
            <h1 className="text-2xl font-bold">{user?.name || 'Student'}</h1>
          </div>
          <div className="flex gap-2">
            <Button 
              variant="ghost" 
              size="icon" 
              className="text-white hover:bg-white/20 rounded-full"
              onClick={() => navigate('/search')}
            >
              <Search className="w-5 h-5" />
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              className="text-white hover:bg-white/20 rounded-full relative"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </Button>
          </div>
        </div>

        {/* Profile Completion */}
        <Card className="bg-white/10 border-0 backdrop-blur-sm">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-white/90">Profile Completion</span>
              <span className="text-sm font-bold text-white">{profile?.profile_completion || 0}%</span>
            </div>
            <Progress value={profile?.profile_completion || 0} className="h-2 bg-white/20" />
            {profile?.profile_completion < 100 && (
              <Link 
                to="/profile" 
                className="text-xs text-white/80 mt-2 flex items-center gap-1 hover:text-white"
              >
                Complete your profile to unlock premium features
                <ArrowRight className="w-3 h-3" />
              </Link>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="px-6 -mt-4">
        <div className="grid grid-cols-4 gap-3">
          {quickActions.map(({ icon: Icon, label, path, color }) => (
            <Link
              key={path}
              to={path}
              className="flex flex-col items-center gap-2 p-3 bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow"
              data-testid={`quick-action-${label.toLowerCase()}`}
            >
              <div className={`w-12 h-12 ${color} rounded-xl flex items-center justify-center`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
              <span className="text-xs font-medium text-slate-700">{label}</span>
            </Link>
          ))}
        </div>
      </div>

      {/* My Applications */}
      <div className="px-6 mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-slate-900">My Applications</h2>
          <Link to="/applications" className="text-primary text-sm font-semibold flex items-center gap-1">
            View All <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        {applications.length === 0 ? (
          <Card className="border-dashed border-2">
            <CardContent className="p-6 text-center">
              <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <h3 className="font-semibold text-slate-700 mb-1">No applications yet</h3>
              <p className="text-sm text-slate-500 mb-4">Start exploring colleges and submit your first application</p>
              <Button onClick={() => navigate('/colleges')} data-testid="explore-colleges-btn">
                Explore Colleges
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {applications.slice(0, 3).map((app) => (
              <Card key={app.application_id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-slate-900">{app.college_name}</h3>
                      <p className="text-sm text-slate-500">{app.course}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge className={getStatusColor(app.status)}>
                          {app.status.replace('_', ' ')}
                        </Badge>
                        <span className="text-xs text-slate-400">{app.intake}</span>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" onClick={() => navigate(`/applications`)}>
                      <ChevronRight className="w-5 h-5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Recommended Colleges */}
      <div className="px-6 mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-slate-900">Recommended Colleges</h2>
          <Link to="/colleges" className="text-primary text-sm font-semibold flex items-center gap-1">
            View All <ChevronRight className="w-4 h-4" />
          </Link>
        </div>

        {colleges.length === 0 ? (
          <Card className="border-dashed border-2">
            <CardContent className="p-6 text-center">
              <GraduationCap className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <h3 className="font-semibold text-slate-700 mb-1">Loading colleges...</h3>
              <p className="text-sm text-slate-500">Check back soon for recommendations</p>
            </CardContent>
          </Card>
        ) : (
          <div className="flex gap-4 overflow-x-auto pb-2 hide-scrollbar">
            {colleges.map((college) => (
              <Card 
                key={college.college_id} 
                className="min-w-[280px] hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => navigate(`/colleges/${college.college_id}`)}
              >
                <div 
                  className="h-32 bg-gradient-to-br from-primary/20 to-primary/5 rounded-t-lg flex items-center justify-center"
                  style={college.cover_image ? { backgroundImage: `url(${college.cover_image})`, backgroundSize: 'cover' } : {}}
                >
                  {!college.cover_image && <GraduationCap className="w-12 h-12 text-primary/40" />}
                </div>
                <CardContent className="p-4">
                  <h3 className="font-semibold text-slate-900 mb-1 truncate">{college.name}</h3>
                  <div className="flex items-center gap-1 text-sm text-slate-500 mb-2">
                    <MapPin className="w-3 h-3" />
                    <span>{college.city}, {college.country}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                      <span className="text-sm font-medium">{college.average_rating || 'N/A'}</span>
                    </div>
                    {college.ranking && (
                      <Badge variant="secondary">#{college.ranking}</Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Upcoming Deadlines */}
      <div className="px-6 mt-8 mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-slate-900">Upcoming Deadlines</h2>
        </div>
        <Card className="bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-100">
          <CardContent className="p-4 flex items-center gap-4">
            <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
              <Calendar className="w-6 h-6 text-orange-600" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-slate-900">Fall 2025 Applications</h3>
              <p className="text-sm text-slate-500">Most US universities - Dec 15, 2024</p>
            </div>
            <Badge className="bg-orange-100 text-orange-800">45 days</Badge>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
