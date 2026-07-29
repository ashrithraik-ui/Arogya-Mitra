import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar, Clock, Video, User as UserIcon } from 'lucide-react';
import { MOCK_CONSULTATIONS } from '@/services/mockData';

export function PatientConsultation() {
  const [activeTab, setActiveTab] = useState<'upcoming' | 'past'>('upcoming');

  const upcoming = MOCK_CONSULTATIONS.filter(c => c.status === 'upcoming');
  const past = MOCK_CONSULTATIONS.filter(c => c.status === 'completed');
  
  const displayList = activeTab === 'upcoming' ? upcoming : past;

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Consultations</h1>
          <p className="text-muted-foreground mt-1">Manage your upcoming and past doctor appointments.</p>
        </div>
        <Button>Book New Appointment</Button>
      </div>

      <div className="flex gap-2 p-1 bg-muted rounded-lg w-fit">
        <button 
          className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === 'upcoming' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
          onClick={() => setActiveTab('upcoming')}
        >
          Upcoming ({upcoming.length})
        </button>
        <button 
          className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${activeTab === 'past' ? 'bg-background shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground'}`}
          onClick={() => setActiveTab('past')}
        >
          Past ({past.length})
        </button>
      </div>

      <div className="grid gap-4">
        {displayList.length === 0 ? (
          <Card className="bg-muted/50 border-dashed">
            <CardContent className="p-12 text-center text-muted-foreground">
              No {activeTab} consultations found.
            </CardContent>
          </Card>
        ) : (
          displayList.map(consultation => (
            <Card key={consultation.id} className="hover:border-primary/50 transition-colors">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-start gap-4">
                    <div className="bg-primary/10 p-3 rounded-full">
                      {consultation.type === 'video' ? (
                        <Video className="w-6 h-6 text-primary" />
                      ) : (
                        <UserIcon className="w-6 h-6 text-primary" />
                      )}
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg flex items-center gap-2">
                        Dr. Sarah Lee
                        <Badge variant="outline" className="font-normal text-xs">{consultation.type === 'video' ? 'Video Call' : 'In-Person'}</Badge>
                      </h3>
                      <p className="text-muted-foreground text-sm mb-2">{consultation.reason}</p>
                      <div className="flex items-center gap-4 text-sm font-medium">
                        <span className="flex items-center gap-1 text-foreground/80">
                          <Calendar className="w-4 h-4" /> {consultation.date.split(',')[0]}
                        </span>
                        <span className="flex items-center gap-1 text-foreground/80">
                          <Clock className="w-4 h-4" /> {consultation.date.split(',')[1] || 'TBD'}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4 md:mt-0">
                    {activeTab === 'upcoming' ? (
                      <>
                        <Button variant="outline">Reschedule</Button>
                        <Button>Join Call</Button>
                      </>
                    ) : (
                      <>
                        <Button variant="outline">View Notes</Button>
                        <Button>Book Again</Button>
                      </>
                    )}
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
