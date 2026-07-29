import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Pill, Send, CheckCircle2 } from 'lucide-react';
import { toast } from 'react-hot-toast';
import api from '@/services/api';
import { useAuth } from '@/context/AuthContext';

const rxSchema = z.object({
  consultationId: z.string().min(1, "Please select or enter a Consultation ID"),
  diagnosis: z.string().min(1, "Diagnosis is required"),
  medication: z.string().min(1, "Medication name is required"),
  dosage: z.string().min(1, "Dosage is required"),
  frequency: z.string().min(1, "Frequency is required"),
  duration: z.string().min(1, "Duration is required"),
  instructions: z.string().optional(),
});

type ConsultationItem = {
  id: number;
  patient_name?: string;
  chief_complaint?: string;
};

export function DoctorPrescription() {
  const { user } = useAuth();
  const [consultations, setConsultations] = useState<ConsultationItem[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<z.infer<typeof rxSchema>>({
    resolver: zodResolver(rxSchema),
    defaultValues: {
      consultationId: "",
      diagnosis: "",
      medication: "",
      dosage: "",
      frequency: "",
      duration: "",
      instructions: "",
    },
  });

  useEffect(() => {
    async function loadConsultations() {
      try {
        const res = await api.get('/doctor/consultations');
        setConsultations(res.data || []);
      } catch (e) {
        console.error("Failed to load consultations", e);
      }
    }
    loadConsultations();
  }, []);

  async function onSubmit(values: z.infer<typeof rxSchema>) {
    setIsSubmitting(true);
    try {
      await api.post('/doctor/prescription', {
        consultation_id: parseInt(values.consultationId),
        doctor_id: parseInt(user?.id || "1"),
        diagnosis: values.diagnosis,
        medicines: [
          {
            name: values.medication,
            dose: values.dosage,
            frequency: values.frequency,
            duration: values.duration,
          }
        ],
        instructions: values.instructions || "",
      });

      toast.success("Prescription issued and sent directly to patient!");
      form.reset();
    } catch (e: any) {
      console.error("Prescription submission failed", e);
      toast.error(e.response?.data?.detail || "Failed to send prescription. Please check fields.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-3xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Write e-Prescription</h1>
        <p className="text-muted-foreground mt-1">Issue digital prescriptions saved locally and sent directly to the patient.</p>
      </div>

      <Card className="border-secondary/20 shadow-md">
        <CardHeader className="bg-secondary/5 border-b">
          <CardTitle className="flex items-center gap-2">
            <Pill className="text-secondary w-5 h-5" />
            New Prescription Form
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              
              {/* Consultation Selection */}
              <FormField
                control={form.control}
                name="consultationId"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Select Patient Consultation</FormLabel>
                    <FormControl>
                      <select
                        {...field}
                        className="w-full h-10 px-3 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-secondary"
                      >
                        <option value="">-- Choose Consultation --</option>
                        {consultations.map((c) => (
                          <option key={c.id} value={c.id}>
                            #{c.id} - Patient: {c.patient_name || 'Unknown'} ({c.chief_complaint?.slice(0, 30)}...)
                          </option>
                        ))}
                      </select>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Diagnosis */}
              <FormField
                control={form.control}
                name="diagnosis"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Diagnosis</FormLabel>
                    <FormControl>
                      <Input placeholder="e.g. Acute Bronchitis, Mild Dermatitis" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Medicines Box */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-muted/30 p-4 rounded-lg border">
                <FormField
                  control={form.control}
                  name="medication"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Medication Name</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. Amoxicillin / Paracetamol" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="dosage"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Dosage</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. 500 mg" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="frequency"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Frequency</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. Twice daily after meals (1-0-1)" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="duration"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Duration</FormLabel>
                      <FormControl>
                        <Input placeholder="e.g. 5 Days" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Instructions */}
              <FormField
                control={form.control}
                name="instructions"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Instructions & Advice for Patient</FormLabel>
                    <FormControl>
                      <Textarea placeholder="Drink plenty of water, rest for 3 days, avoid cold drinks..." {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex justify-end gap-3 pt-4">
                <Button type="button" variant="outline" onClick={() => form.reset()}>
                  Reset
                </Button>
                <Button type="submit" className="bg-secondary text-secondary-foreground hover:bg-secondary/90" disabled={isSubmitting}>
                  <Send className="mr-2 h-4 w-4" />
                  {isSubmitting ? "Issuing..." : "Send Prescription to Patient"}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}
