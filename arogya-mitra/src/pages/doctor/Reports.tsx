import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { FileText, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export function DoctorReports() {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Patient Reports</h1>
        <p className="text-muted-foreground mt-1">Review lab results and medical documents.</p>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search patient name or report ID..." className="pl-9" />
        </div>
        <Button variant="outline">Filter</Button>
      </div>

      <div className="grid gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardContent className="p-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="bg-primary/10 p-3 rounded-lg">
                  <FileText className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Complete Blood Count</h3>
                  <p className="text-sm text-muted-foreground">Patient: Rahul Verma • Uploaded 2 hours ago</p>
                </div>
              </div>
              <Button>Review</Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
