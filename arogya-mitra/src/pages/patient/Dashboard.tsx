import React, { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { EmergencyButton } from '@/components/EmergencyButton';
import { Link } from 'wouter';
import { 
  MessageSquare, Mic, FileText, Image as ImageIcon, 
  Calendar, Activity, ArrowRight
} from 'lucide-react';
import api from '@/services/api';

type TimelineEvent = {
  id: number;
  event_type: string;
  title: string;
  description: string;
  event_date: string;
};

export function PatientDashboard() {
  const { user } = useAuth();
  const [events, setEvents] = useState<TimelineEvent[]>([]);

  useEffect(() => {
    async function fetchTimeline() {
      if (!user?.id) return;
      try {
        const res = await api.get(`/patient/timeline?patient_id=${user.id}&limit=5`);
        setEvents(res.data.events);
      } catch (e) {
        console.error("Failed to fetch timeline", e);
      }
    }
    fetchTimeline();
  }, [user?.id]);

  const recentEvents = events.slice(0, 3);

  const quickActions = [
    { name: 'AI Chat', path: '/patient/chat', icon: MessageSquare, color: 'bg-blue-500/10 text-blue-500' },
    { name: 'Voice Assistant', path: '/patient/voice', icon: Mic, color: 'bg-purple-500/10 text-purple-500' },
    { name: 'Upload Report', path: '/patient/upload-report', icon: FileText, color: 'bg-cyan-500/10 text-cyan-500' },
    { name: 'Upload Image', path: '/patient/upload-image', icon: ImageIcon, color: 'bg-emerald-500/10 text-emerald-500' },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Welcome back, {user?.name.split(' ')[0]}</h1>
          <p className="text-muted-foreground mt-1">Here is your health overview for today.</p>
        </div>
        <div className="flex-shrink-0">
          <EmergencyButton />
        </div>
      </div>

      {/* Health Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-card/50 backdrop-blur border-primary/10">
          <CardContent className="p-4 md:p-6 flex flex-col items-center justify-center text-center">
            <Activity className="w-8 h-8 text-primary mb-2 opacity-80" />
            <p className="text-sm text-muted-foreground font-medium">Heart Rate</p>
            <p className="text-2xl font-bold">72 <span className="text-sm font-normal text-muted-foreground">bpm</span></p>
          </CardContent>
        </Card>
        <Card className="bg-card/50 backdrop-blur border-primary/10">
          <CardContent className="p-4 md:p-6 flex flex-col items-center justify-center text-center">
            <div className="w-8 h-8 rounded-full border-4 border-blue-500 flex items-center justify-center mb-2" />
            <p className="text-sm text-muted-foreground font-medium">Blood Pressure</p>
            <p className="text-2xl font-bold">120/80</p>
          </CardContent>
        </Card>
        <Card className="bg-card/50 backdrop-blur border-primary/10">
          <CardContent className="p-4 md:p-6 flex flex-col items-center justify-center text-center">
            <div className="w-8 h-8 flex items-end justify-center mb-2">
              <div className="w-3 bg-secondary rounded-t-sm h-full" />
              <div className="w-3 bg-secondary/60 rounded-t-sm h-3/4 ml-1" />
            </div>
            <p className="text-sm text-muted-foreground font-medium">Weight</p>
            <p className="text-2xl font-bold">62 <span className="text-sm font-normal text-muted-foreground">kg</span></p>
          </CardContent>
        </Card>
        <Card className="bg-card/50 backdrop-blur border-primary/10">
          <CardContent className="p-4 md:p-6 flex flex-col items-center justify-center text-center">
            <FileText className="w-8 h-8 text-cyan-500 mb-2 opacity-80" />
            <p className="text-sm text-muted-foreground font-medium">Reports</p>
            <p className="text-2xl font-bold">12</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Quick Actions */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            {quickActions.map((action) => {
              const Icon = action.icon;
              return (
                <Link key={action.path} href={action.path}>
                  <Card className="hover:shadow-md transition-all cursor-pointer hover:border-primary/50 group h-full">
                    <CardContent className="p-6 flex flex-col items-center text-center h-full justify-center">
                      <div className={`p-4 rounded-full ${action.color} mb-4 group-hover:scale-110 transition-transform`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      <span className="font-medium">{action.name}</span>
                    </CardContent>
                  </Card>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Recent Timeline */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Recent Activity</h2>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/patient/timeline">
                View All <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
            </Button>
          </div>
          <Card>
            <CardContent className="p-0 divide-y">
              {recentEvents.length === 0 ? (
                <p className="p-4 text-muted-foreground text-sm">No recent activity.</p>
              ) : (
                recentEvents.map((event) => (
                  <div key={event.id} className="p-4 flex gap-4">
                    <div className="w-2 h-2 rounded-full bg-primary mt-2 shrink-0" />
                    <div>
                      <h4 className="font-medium">{event.title}</h4>
                      <p className="text-sm text-muted-foreground mb-1">{new Date(event.event_date).toLocaleString()}</p>
                      <p className="text-sm">{event.description}</p>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card className="bg-primary/5 border-primary/20">
            <CardContent className="p-6 flex items-center justify-between">
              <div>
                <h3 className="font-semibold mb-1 text-primary">Need to see a doctor?</h3>
                <p className="text-sm text-muted-foreground">Book a consultation instantly.</p>
              </div>
              <Button asChild>
                <Link href="/patient/consultation">
                  <Calendar className="mr-2 w-4 h-4" /> Book
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
