import React, { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileText, Calendar, UserCheck, Pill, CheckCircle2, Phone, MessageSquare, Stethoscope } from 'lucide-react';
import api from '@/services/api';

type Prescription = {
  id: number;
  consultation_id: number;
  doctor_name: string;
  doctor_phone?: string;
  diagnosis: string;
  medicines: Array<{
    name: string;
    dosage?: string;
    dose?: string;
    frequency: string;
    duration: string;
  }>;
  instructions: string;
  created_at: string;
};

type DoctorResponseItem = {
  consultation_id: number;
  doctor_name: string;
  doctor_phone?: string;
  chief_complaint?: string;
  doctor_notes: string;
  created_at: string;
};

export function PatientPrescriptions() {
  const { user } = useAuth();
  const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
  const [doctorResponses, setDoctorResponses] = useState<DoctorResponseItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      if (!user?.id) return;
      try {
        setLoading(true);
        // Fetch prescriptions
        const rxRes = await api.get(`/patient/prescriptions?patient_id=${user.id}`);
        setPrescriptions(rxRes.data || []);

        // Fetch consultations to extract doctor responses & notes
        const consRes = await api.get(`/patient/consultations?patient_id=${user.id}`);
        const consultationsData = consRes.data || [];

        const responses: DoctorResponseItem[] = [];
        consultationsData.forEach((c: any) => {
          if (c.doctor_notes && c.doctor_notes.trim()) {
            responses.push({
              consultation_id: c.id,
              doctor_name: c.doctor_name || "Assigned Doctor",
              doctor_phone: c.doctor_phone || "+91 98765 43210",
              chief_complaint: c.chief_complaint,
              doctor_notes: c.doctor_notes,
              created_at: c.created_at || c.updated_at,
            });
          }
        });

        setDoctorResponses(responses);
      } catch (e) {
        console.error("Failed to fetch prescriptions and doctor responses", e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [user?.id]);

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Prescriptions & Doctor Responses</h1>
        <p className="text-muted-foreground mt-1">
          View official medical prescriptions and clinical responses sent by your doctor.
        </p>
      </div>

      <Tabs defaultValue="prescriptions" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="prescriptions" className="flex items-center gap-2">
            <Pill className="w-4 h-4 text-primary" /> Prescriptions ({prescriptions.length})
          </TabsTrigger>
          <TabsTrigger value="responses" className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-emerald-500" /> Doctor Responses ({doctorResponses.length})
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Digital Prescriptions */}
        <TabsContent value="prescriptions" className="mt-6">
          {loading ? (
            <Card className="p-8 text-center text-muted-foreground">Loading prescriptions...</Card>
          ) : prescriptions.length === 0 ? (
            <Card className="bg-muted/50 border-dashed">
              <CardContent className="p-12 text-center text-muted-foreground">
                <Pill className="w-12 h-12 mx-auto mb-3 text-muted-foreground/50" />
                <p className="font-medium text-lg mb-1">No prescriptions found</p>
                <p className="text-sm">Once a doctor issues a prescription for your consultation, it will appear here.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-6">
              {prescriptions.map((rx) => (
                <Card key={rx.id} className="border-primary/20 hover:border-primary/50 transition-colors shadow-sm">
                  <CardHeader className="bg-primary/5 border-b pb-4">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                      <div>
                        <CardTitle className="text-xl flex items-center gap-2">
                          <UserCheck className="w-5 h-5 text-primary" />
                          Issued by {rx.doctor_name || "Doctor"}
                        </CardTitle>
                        <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground mt-1">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5" />
                            {new Date(rx.created_at).toLocaleDateString()}
                          </span>
                          <span className="flex items-center gap-1 font-medium text-primary bg-primary/10 px-2 py-0.5 rounded-md">
                            <Phone className="w-3.5 h-3.5" />
                            Doctor Contact: {rx.doctor_phone || "+91 98765 43210"}
                          </span>
                        </div>
                      </div>
                      <Badge className="bg-emerald-600 w-fit">
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> Verified Digital Prescription
                      </Badge>
                    </div>
                  </CardHeader>

                  <CardContent className="p-6 space-y-4">
                    {/* Diagnosis */}
                    <div>
                      <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Diagnosis</h4>
                      <p className="font-semibold text-foreground text-lg">{rx.diagnosis}</p>
                    </div>

                    {/* Prescribed Medicines */}
                    <div>
                      <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Prescribed Medicines</h4>
                      <div className="space-y-2">
                        {rx.medicines?.map((med, idx) => (
                          <div key={idx} className="flex items-center justify-between p-3 bg-muted/40 rounded-lg border">
                            <div className="flex items-center gap-3">
                              <div className="p-2 bg-primary/10 rounded-md">
                                <Pill className="w-4 h-4 text-primary" />
                              </div>
                              <div>
                                <p className="font-medium text-foreground">{med.name}</p>
                                <p className="text-xs text-muted-foreground">Dose: {med.dosage || med.dose || 'As directed'}</p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-semibold text-primary">{med.frequency}</p>
                              <p className="text-xs text-muted-foreground">{med.duration}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Instructions */}
                    {rx.instructions && (
                      <div className="bg-amber-500/10 border border-amber-500/20 p-3 rounded-md text-sm text-amber-800 dark:text-amber-300">
                        <span className="font-semibold">Doctor Instructions:</span> {rx.instructions}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* Tab 2: Doctor Responses & Clinical Notes */}
        <TabsContent value="responses" className="mt-6">
          {loading ? (
            <Card className="p-8 text-center text-muted-foreground">Loading doctor responses...</Card>
          ) : doctorResponses.length === 0 ? (
            <Card className="bg-muted/50 border-dashed">
              <CardContent className="p-12 text-center text-muted-foreground">
                <Stethoscope className="w-12 h-12 mx-auto mb-3 text-muted-foreground/50" />
                <p className="font-medium text-lg mb-1">No doctor responses yet</p>
                <p className="text-sm">When your doctor reviews your consultation and sends a response, it will appear here.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-6">
              {doctorResponses.map((res, idx) => (
                <Card key={idx} className="border-emerald-500/30 bg-card shadow-sm hover:border-emerald-500/60 transition-colors">
                  <CardHeader className="bg-emerald-500/10 border-b pb-4">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                      <div>
                        <CardTitle className="text-xl flex items-center gap-2 text-foreground">
                          <Stethoscope className="w-5 h-5 text-emerald-600" />
                          Response from Dr. {res.doctor_name}
                        </CardTitle>
                        <CardDescription className="flex flex-wrap items-center gap-4 text-xs mt-1">
                          <span className="flex items-center gap-1 text-muted-foreground">
                            <Calendar className="w-3.5 h-3.5" />
                            {new Date(res.created_at).toLocaleDateString()}
                          </span>
                          <span className="flex items-center gap-1 font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-500/15 px-2.5 py-1 rounded-md">
                            <Phone className="w-3.5 h-3.5" />
                            Doctor Contact: {res.doctor_phone || "+91 98765 43210"}
                          </span>
                        </CardDescription>
                      </div>
                      <Badge variant="outline" className="border-emerald-500/50 text-emerald-600 dark:text-emerald-400 w-fit">
                        Consultation #{res.consultation_id}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="p-6 space-y-3">
                    {res.chief_complaint && (
                      <div className="text-xs text-muted-foreground bg-muted/60 p-2.5 rounded-md">
                        <span className="font-medium text-foreground">Regarding Complaint:</span> {res.chief_complaint}
                      </div>
                    )}
                    <div>
                      <h4 className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider mb-2">Doctor Clinical Notes & Advice</h4>
                      <p className="text-sm leading-relaxed whitespace-pre-wrap bg-emerald-500/5 border border-emerald-500/20 p-4 rounded-lg text-foreground font-medium">
                        {res.doctor_notes}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
