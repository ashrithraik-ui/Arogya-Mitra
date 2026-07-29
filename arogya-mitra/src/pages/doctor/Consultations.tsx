import React, { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Video, User as UserIcon, Calendar, Clock, FileText, Phone } from 'lucide-react';
import api from '@/services/api';
import { Link } from 'wouter';

type Consultation = {
  id: number;
  patient_id: number;
  patient_name?: string;
  patient_phone?: string;
  doctor_id: number;
  status: string;
  chief_complaint: string;
  ai_summary: string;
  created_at: string;
};

export function DoctorConsultations() {
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
    return <div>Loading consultations...</div>;
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Patient Queue</h1>
          <p className="text-muted-foreground mt-1">Manage your pending consultations for today.</p>
        </div>
      </div>

      <div className="grid gap-4">
        {pending.length === 0 ? (
          <p className="text-muted-foreground">No pending consultations found.</p>
        ) : (
          pending.map((consultation, i) => (
            <Card key={consultation.id} className={i === 0 ? "border-secondary/50 shadow-md shadow-secondary/5" : ""}>
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <div className={`p-3 rounded-full ${i === 0 ? 'bg-secondary/20 text-secondary' : 'bg-muted text-muted-foreground'}`}>
                      <UserIcon className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg flex flex-wrap items-center gap-2">
                        <Link href={`/doctor/patient/${consultation.id}`} className="hover:underline">
                          Patient: {consultation.patient_name || `Patient #${consultation.patient_id}`} (Consultation #{consultation.id})
                        </Link>
                        {i === 0 && <Badge className="bg-secondary hover:bg-secondary/80">Next</Badge>}
                        <Badge variant="outline" className="font-normal text-xs">{consultation.status}</Badge>
                      </h3>
                      <p className="text-muted-foreground text-sm mb-2">{consultation.chief_complaint || "Awaiting AI summary..."}</p>
                      
                      <div className="flex flex-wrap items-center gap-4 text-sm font-medium">
                        <span className="flex items-center gap-1 text-primary bg-primary/10 px-2.5 py-0.5 rounded-md font-semibold">
                          <Phone className="w-3.5 h-3.5" /> Patient Contact: {consultation.patient_phone || "N/A"}
                        </span>
                        <span className="flex items-center gap-1 text-muted-foreground">
                          <Clock className="w-4 h-4 text-muted-foreground" /> {new Date(consultation.created_at).toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4 md:mt-0">
                    <Button variant="outline" asChild>
                      <Link href={`/doctor/patient/${consultation.id}`}>
                        <FileText className="w-4 h-4 mr-2" /> View Details
                      </Link>
                    </Button>
                    <Button className={i === 0 ? "bg-secondary text-secondary-foreground hover:bg-secondary/90" : ""} asChild>
                      <Link href={`/doctor/patient/${consultation.id}`}>
                        Take Action
                      </Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
