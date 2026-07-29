import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { History as HistoryIcon, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';

export function DoctorHistory() {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Consultation History</h1>
        <p className="text-muted-foreground mt-1">Review your past patient interactions.</p>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
        <Input placeholder="Search by patient name, date, or symptom..." className="pl-9" />
      </div>

      <Card className="border-dashed">
        <CardContent className="p-12 text-center text-muted-foreground flex flex-col items-center justify-center">
          <HistoryIcon className="w-12 h-12 mb-4 opacity-20" />
          <p>Search for a patient to view consultation history.</p>
        </CardContent>
      </Card>
    </div>
  );
}
