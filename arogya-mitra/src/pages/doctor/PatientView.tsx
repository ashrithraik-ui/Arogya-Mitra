import React, { useEffect, useState } from 'react';
import { useParams } from 'wouter';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Timeline } from '@/components/Timeline';
import { User, Phone, Mail, Activity, FileText, ImageIcon, MessageSquare } from 'lucide-react';
import api from '@/services/api';

export function PatientView() {
  const { id } = useParams();
  
  const [consultation, setConsultation] = useState<any>(null);
  const [patient, setPatient] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        // Fetch consultation details
        const consRes = await api.get(`/doctor/consultation/${id}`);
        const consData = consRes.data;
        setConsultation(consData);

        // Fetch patient details
        if (consData.patient_id) {
          const patRes = await api.get(`/patient/${consData.patient_id}`);
          setPatient(patRes.data);

          // Fetch timeline
          const timeRes = await api.get(`/patient/timeline?patient_id=${consData.patient_id}`);
          const mappedEvents = timeRes.data.events.map((e: any) => {
            let type = 'consultation';
            if (e.event_type === 'REPORT_OCR') type = 'report';
            if (e.event_type === 'VISION_ANALYSIS') type = 'image';
            if (e.event_type === 'PRESCRIPTION') type = 'prescription';

            return {
              id: e.id.toString(),
              date: new Date(e.event_date).toLocaleString(),
              type,
              title: e.title,
              summary: e.description,
              details: e.metadata_json ? JSON.stringify(JSON.parse(e.metadata_json), null, 2) : 'No additional details',
            };
          });
          setEvents(mappedEvents);
        }
      } catch (error) {
        console.error("Failed to load patient view data", error);
      } finally {
        setIsLoading(false);
      }
    }
    fetchData();
  }, [id]);

  const handleAction = async (action: string) => {
    try {
      await api.post('/doctor/consultation', {
        consultation_id: parseInt(id || "0"),
        action: action,
        notes: `Doctor ${action}ed the consultation.`
      });
      alert(`Successfully ${action}ed the consultation.`);
      // Reload consultation to get new status
      const consRes = await api.get(`/doctor/consultation/${id}`);
      setConsultation(consRes.data);
    } catch (error) {
      console.error(`Failed to ${action} consultation`, error);
      alert(`Failed to ${action} the consultation.`);
    }
  };

  const [doctorNoteInput, setDoctorNoteInput] = useState('');
  const [isSubmittingNote, setIsSubmittingNote] = useState(false);

  const handleSendResponse = async () => {
    if (!doctorNoteInput.trim()) return;
    setIsSubmittingNote(true);
    try {
      await api.post('/doctor/consultation', {
        consultation_id: parseInt(id || "0"),
        action: 'accept',
        notes: doctorNoteInput,
      });
      alert("Doctor response sent to patient successfully!");
      setDoctorNoteInput('');
      // Reload consultation to show new notes
      const consRes = await api.get(`/doctor/consultation/${id}`);
      setConsultation(consRes.data);
      
      // Reload timeline
      if (consRes.data.patient_id) {
        const timeRes = await api.get(`/patient/timeline?patient_id=${consRes.data.patient_id}`);
        const mappedEvents = timeRes.data.events.map((e: any) => {
          let type = 'consultation';
          if (e.event_type === 'REPORT_OCR') type = 'report';
          if (e.event_type === 'VISION_ANALYSIS') type = 'image';
          if (e.event_type === 'PRESCRIPTION') type = 'prescription';
          if (e.event_type === 'DOCTOR_NOTE') type = 'prescription';

          return {
            id: e.id.toString(),
            date: new Date(e.event_date).toLocaleString(),
            type,
            title: e.title,
            summary: e.description,
            details: e.metadata_json ? JSON.stringify(JSON.parse(e.metadata_json), null, 2) : 'No additional details',
          };
        });
        setEvents(mappedEvents);
      }
    } catch (error) {
      console.error("Failed to send doctor response", error);
      alert("Failed to send doctor response.");
    } finally {
      setIsSubmittingNote(false);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground">Loading patient data...</div>;
  }

  if (!consultation || !patient) {
    return <div className="p-8 text-center text-muted-foreground">Failed to load data. Please ensure the consultation exists and belongs to you.</div>;
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Consultation #{consultation.id}</h1>
          <p className="text-muted-foreground mt-1">Status: <span className="capitalize font-medium text-primary">{consultation.status}</span></p>
        </div>
        <div className="flex gap-2">
          {consultation.status === 'pending' && (
            <Button onClick={() => handleAction('accept')} className="bg-secondary text-secondary-foreground hover:bg-secondary/90">
              Accept Consultation
            </Button>
          )}
          {(consultation.status === 'pending' || consultation.status === 'in_progress') && (
            <Button onClick={() => handleAction('call')} variant="outline">
              Initiate Call
            </Button>
          )}
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card className="md:col-span-1 h-fit">
          <CardContent className="p-6">
            <div className="flex flex-col items-center text-center mb-6">
              <div className="w-24 h-24 rounded-full overflow-hidden mb-4 border-2 border-primary/20 bg-muted flex items-center justify-center">
                <User className="w-12 h-12 text-muted-foreground" />
              </div>
              <h2 className="text-xl font-bold">{patient.name}</h2>
              <p className="text-sm text-muted-foreground">{patient.age || 'N/A'} yrs • {patient.gender || 'N/A'}</p>
            </div>
            
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-3 font-bold text-primary bg-primary/10 p-3 rounded-lg border border-primary/20">
                <Phone className="w-4 h-4 text-primary shrink-0" />
                <div>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-medium">Patient Contact Number</p>
                  <p className="text-base">{patient.phone || 'N/A'}</p>
                </div>
              </div>
              {patient.email && (
                <div className="flex items-center gap-3 text-muted-foreground px-1">
                  <Mail className="w-4 h-4" /> {patient.email}
                </div>
              )}
              
              <div className="border-t pt-3 mt-3 grid grid-cols-2 gap-2 text-center">
                <div className="bg-muted p-2 rounded">
                  <p className="text-xs text-muted-foreground">Blood Group</p>
                  <p className="font-semibold">{patient.blood_group || 'N/A'}</p>
                </div>
                <div className="bg-muted p-2 rounded">
                  <p className="text-xs text-muted-foreground">Allergies</p>
                  <p className="font-semibold">{patient.allergies || 'None'}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="md:col-span-2 space-y-6">
          <Tabs defaultValue="chat" className="w-full">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="chat">Live Chat</TabsTrigger>
              <TabsTrigger value="images">Images</TabsTrigger>
              <TabsTrigger value="summary">AI Summary</TabsTrigger>
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
              <TabsTrigger value="reports">Reports</TabsTrigger>
            </TabsList>
            
            <div className="mt-6 bg-card border rounded-xl p-6 min-h-[350px]">
              <TabsContent value="chat" className="mt-0 space-y-4">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-primary" />
                  Live Patient & AI Chat History
                </h3>

                {consultation.conversation_history && consultation.conversation_history.length > 0 ? (
                  <div className="space-y-3 max-h-[400px] overflow-y-auto p-4 bg-muted/40 rounded-xl border">
                    {consultation.conversation_history.map((msg: any, idx: number) => {
                      const isPatient = msg.role === 'patient' || msg.role === 'user';
                      const isDoctor = msg.role === 'doctor';
                      return (
                        <div
                          key={idx}
                          className={`p-3 rounded-lg text-sm ${
                            isPatient
                              ? 'bg-primary/10 border border-primary/20 text-foreground ml-auto max-w-[85%]'
                              : isDoctor
                              ? 'bg-emerald-500/10 border border-emerald-500/30 text-foreground mr-auto max-w-[85%]'
                              : 'bg-background border text-foreground mr-auto max-w-[85%]'
                          }`}
                        >
                          <div className="flex items-center justify-between text-xs font-semibold mb-1 opacity-70">
                            <span>
                              {isPatient ? 'Patient' : isDoctor ? `Dr. ${msg.doctor_name || 'Doctor'}` : 'AI Assistant'}
                            </span>
                            {msg.timestamp && (
                              <span>{new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                            )}
                          </div>
                          <p className="whitespace-pre-wrap leading-relaxed">{msg.message || msg.content}</p>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-muted-foreground py-8 text-center">No conversation history recorded yet.</p>
                )}
              </TabsContent>

              <TabsContent value="images" className="mt-0 space-y-4">
                <h3 className="text-lg font-semibold flex items-center gap-2">
                  <ImageIcon className="w-5 h-5 text-emerald-500" />
                  Uploaded Patient Images & Scans
                </h3>

                {consultation.uploaded_files && consultation.uploaded_files.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 my-4">
                    {consultation.uploaded_files.map((file: string, idx: number) => {
                      const imgUrl = file.startsWith('/') 
                        ? `http://localhost:8000${file}` 
                        : file.startsWith('http') 
                          ? file 
                          : `http://localhost:8000/uploads/${file.split('\\').pop()?.split('/').pop()}`;
                      return (
                        <div key={idx} className="border rounded-lg overflow-hidden bg-background shadow-sm">
                          <img 
                            src={imgUrl} 
                            alt={`Uploaded Scan ${idx + 1}`} 
                            className="w-full h-48 object-cover hover:object-contain transition-all" 
                          />
                          <div className="p-2 text-xs text-muted-foreground flex justify-between items-center bg-muted/30">
                            <span>Image #{idx + 1}</span>
                            <a href={imgUrl} target="_blank" rel="noreferrer" className="text-primary underline">View Full Image</a>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {consultation.vision_observations ? (
                  <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg space-y-2">
                    <p className="text-xs font-semibold text-emerald-600 uppercase tracking-wider">AI Vision Analysis Findings:</p>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{consultation.vision_observations}</p>
                  </div>
                ) : (
                  <p className="text-muted-foreground py-8 text-center">No image vision analysis available for this consultation.</p>
                )}
              </TabsContent>


              <TabsContent value="summary" className="mt-0 space-y-4">
                <h3 className="text-lg font-semibold">Chief Complaint</h3>
                <p className="text-muted-foreground p-3 bg-muted rounded-md">{consultation.chief_complaint || "None"}</p>
                
                <h3 className="text-lg font-semibold mt-4">AI Structured Summary</h3>
                <div className="text-muted-foreground p-3 bg-muted rounded-md whitespace-pre-wrap">
                  {consultation.ai_summary || "AI Summary is not ready yet."}
                </div>
              </TabsContent>

              <TabsContent value="timeline" className="mt-0">
                 {events.length > 0 ? <Timeline events={events} /> : <p className="text-center text-muted-foreground py-12">No timeline events.</p>}
              </TabsContent>
              
              <TabsContent value="reports" className="mt-0 text-center text-muted-foreground py-12">
                <FileText className="w-12 h-12 mx-auto mb-4 opacity-20" />
                <p>{consultation.ocr_extracted_text ? consultation.ocr_extracted_text : "No reports uploaded for this consultation."}</p>
              </TabsContent>
            </div>
          </Tabs>

          {/* Doctor Response / Notes Box */}
          <Card className="border-primary/30">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Activity className="w-5 h-5 text-primary" />
                Doctor's Response to Patient
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {consultation.doctor_notes && (
                <div className="p-3 bg-primary/10 border border-primary/20 rounded-md">
                  <p className="text-xs font-semibold text-primary mb-1">Previous Response Sent:</p>
                  <p className="text-sm whitespace-pre-wrap">{consultation.doctor_notes}</p>
                </div>
              )}
              <textarea
                className="w-full min-h-[100px] p-3 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Write your clinical evaluation, response, or advice for the patient..."
                value={doctorNoteInput}
                onChange={(e) => setDoctorNoteInput(e.target.value)}
              />
              <div className="flex justify-end">
                <Button onClick={handleSendResponse} disabled={isSubmittingNote || !doctorNoteInput.trim()}>
                  {isSubmittingNote ? "Sending..." : "Send Response to Patient"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

