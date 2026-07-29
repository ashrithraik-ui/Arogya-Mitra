import React, { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Image as ImageIcon, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Link } from 'wouter';
import api from '@/services/api';

export function DoctorImages() {
  const [consultations, setConsultations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    async function fetchConsultations() {
      try {
        const res = await api.get('/doctor/consultations');
        // Filter consultations that have uploaded images or vision observations
        setConsultations(res.data);
      } catch (err) {
        console.error("Failed to fetch doctor images", err);
      } finally {
        setIsLoading(false);
      }
    }
    fetchConsultations();
  }, []);

  const imageConsultations = consultations.filter((c: any) =>
    (c.uploaded_files && c.uploaded_files.length > 0) || c.vision_observations
  );

  const filtered = imageConsultations.filter((c: any) =>
    (c.chief_complaint || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (c.patient_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.id.toString().includes(searchTerm)
  );

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Medical Images</h1>
        <p className="text-muted-foreground mt-1">Review X-rays, MRI scans, and visual symptoms uploaded by patients.</p>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search consultation or symptom..." 
            className="pl-9"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {isLoading ? (
        <p className="text-center py-12 text-muted-foreground">Loading medical images...</p>
      ) : filtered.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            No medical image consultations found.
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {filtered.map((c) => {
            const firstFile = c.uploaded_files?.[0];
            const imgUrl = firstFile
              ? (firstFile.startsWith('/') 
                  ? `http://localhost:8000${firstFile}` 
                  : firstFile.startsWith('http') 
                    ? firstFile 
                    : `http://localhost:8000/uploads/${firstFile.split('\\').pop()?.split('/').pop()}`)
              : null;
            
            return (
              <Card key={c.id} className="overflow-hidden hover:shadow-md transition-shadow cursor-pointer group">
                <div className="aspect-video bg-muted border-b relative flex flex-col items-center justify-center">
                  {imgUrl ? (
                    <img src={imgUrl} alt={`Scan for consultation #${c.id}`} className="w-full h-full object-cover" />
                  ) : (
                    <>
                      <ImageIcon className="w-12 h-12 text-emerald-500 mb-2" />
                      <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">Medical Image Uploaded</span>
                    </>
                  )}
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <Button variant="secondary" asChild className="bg-white/20 hover:bg-white/40 text-white border-0 backdrop-blur-sm">
                      <Link href={`/doctor/patient/${c.id}`}>View & Respond</Link>
                    </Button>
                  </div>
                </div>
                <CardContent className="p-4">
                  <h3 className="font-semibold truncate">Consultation #{c.id} — {c.patient_name || 'Patient'}</h3>
                  <p className="text-sm text-muted-foreground truncate">{c.chief_complaint || 'Medical image analysis'}</p>
                  <div className="flex items-center justify-between mt-3 text-xs text-muted-foreground">
                    <span>{c.uploaded_files?.length || 0} image(s)</span>
                    <span className="capitalize font-medium text-primary">{c.status}</span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
