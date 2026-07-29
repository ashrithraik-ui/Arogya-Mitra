import React, { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Link } from 'wouter';
import { Users, FileText, Calendar, ArrowRight } from 'lucide-react';
import api from '@/services/api';

type Consultation = {
  id: number;
  patient_id: number;
  doctor_id: number;
  status: string;
  chief_complaint: string;
  ai_summary: string;
  created_at: string;
};

export function DoctorDashboard() {
  const { user } = useAuth();
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchConsultations() {
      try {
        const response = await api.get('/doctor/consultations');
        setConsultations(response.data);
      } catch (e) {
        console.error("Failed to fetch consultations", e);
      } finally {
        setIsLoading(false);
      }
    }
    fetchConsultations();
  }, []);

  const pending = consultations.filter(c => c.status === 'pending' || c.status === 'in_progress');

  if (isLoading) {
    return <div>Loading dashboard...</div>;
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Provider Dashboard</h1>
          <p className="text-muted-foreground mt-1">Welcome back, {user?.name}. You have {pending.length} patients waiting today.</p>
        </div>
        <Button className="bg-secondary text-secondary-foreground hover:bg-secondary/90" asChild>
          <Link href="/doctor/consultations">Go to Queue</Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-secondary/20">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="bg-secondary/10 p-4 rounded-full text-secondary">
              <Users className="w-8 h-8" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Patients Today</p>
              <h2 className="text-3xl font-bold">{pending.length}</h2>
            </div>
          </CardContent>
        </Card>
        <Card className="border-secondary/20">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="bg-secondary/10 p-4 rounded-full text-secondary">
              <Calendar className="w-8 h-8" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Pending Consultations</p>
              <h2 className="text-3xl font-bold">{pending.length}</h2>
            </div>
          </CardContent>
        </Card>
        <Card className="border-secondary/20">
          <CardContent className="p-6 flex items-center gap-4">
            <div className="bg-secondary/10 p-4 rounded-full text-secondary">
              <FileText className="w-8 h-8" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Consultations</p>
              <h2 className="text-3xl font-bold">{consultations.length}</h2>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        <Card className="flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xl">Today's Queue</CardTitle>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/doctor/consultations">View All <ArrowRight className="w-4 h-4 ml-1" /></Link>
            </Button>
          </CardHeader>
          <CardContent className="flex-1">
            <div className="space-y-4 mt-2">
              {pending.length === 0 ? (
                <p className="text-sm text-muted-foreground">No pending consultations.</p>
              ) : (
                pending.slice(0, 5).map((c, i) => (
                  <div key={c.id} className={`flex items-center justify-between p-3 rounded-lg border ${i === 0 ? 'bg-secondary/5 border-secondary/30' : 'bg-card'}`}>
                    <div>
                      <h4 className="font-semibold flex items-center gap-2">
                        Patient #{c.patient_id}
                        {i === 0 && <span className="px-2 py-0.5 rounded text-[10px] bg-secondary text-secondary-foreground font-bold uppercase">Next</span>}
                      </h4>
                      <p className="text-sm text-muted-foreground">{new Date(c.created_at).toLocaleTimeString()} • {c.chief_complaint || "Awaiting Info"}</p>
                    </div>
                    <Button size="sm" variant={i === 0 ? 'default' : 'outline'} className={i === 0 ? 'bg-secondary hover:bg-secondary/90 text-secondary-foreground' : ''} asChild>
                      <Link href={`/doctor/patient/${c.id}`}>View</Link>
                    </Button>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="relative pl-6 border-l-2 border-muted space-y-6 pb-4">
              {consultations.slice(0, 3).map((c, i) => (
                <div className="relative" key={c.id}>
                  <div className="absolute -left-[31px] bg-background border-2 border-secondary w-4 h-4 rounded-full mt-1"></div>
                  <p className="font-medium">Consultation {c.status}</p>
                  <p className="text-sm text-muted-foreground">Patient #{c.patient_id}</p>
                  <p className="text-xs text-muted-foreground mt-1">{new Date(c.created_at).toLocaleString()}</p>
                </div>
              ))}
              {consultations.length === 0 && <p className="text-sm text-muted-foreground">No recent activity.</p>}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
