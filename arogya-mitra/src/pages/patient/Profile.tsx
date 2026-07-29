import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAuth } from '@/context/AuthContext';
import { User, Mail, Phone, MapPin, Droplet, Ruler, Weight } from 'lucide-react';
import { MOCK_USER_PATIENT } from '@/services/mockData';

export function PatientProfile() {
  const { user } = useAuth();
  
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">My Profile</h1>
        <p className="text-muted-foreground mt-1">Manage your personal and medical information.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <Card className="md:col-span-1">
          <CardContent className="p-6 flex flex-col items-center text-center">
            <div className="w-32 h-32 rounded-full overflow-hidden mb-4 border-4 border-primary/20">
              <img src={user?.avatar || MOCK_USER_PATIENT.avatar} alt="Profile" className="w-full h-full object-cover" />
            </div>
            <h2 className="text-2xl font-bold">{user?.name}</h2>
            <p className="text-muted-foreground mb-4">Patient ID: {MOCK_USER_PATIENT.id}</p>
            <Button variant="outline" className="w-full">Change Photo</Button>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Personal Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Full Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input defaultValue={user?.name} className="pl-9" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input defaultValue={user?.email} className="pl-9" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Phone</Label>
                <div className="relative">
                  <Phone className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input defaultValue="+91 98765 43210" className="pl-9" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Address</Label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input defaultValue="123 Health Ave, Bangalore" className="pl-9" />
                </div>
              </div>
            </div>
            
            <h3 className="font-semibold text-lg pt-4 border-t mt-6">Medical Basics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label>Blood Group</Label>
                <div className="relative">
                  <Droplet className="absolute left-3 top-3 h-4 w-4 text-red-500" />
                  <Input defaultValue={MOCK_USER_PATIENT.bloodGroup} className="pl-9" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Height</Label>
                <div className="relative">
                  <Ruler className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input defaultValue={MOCK_USER_PATIENT.height} className="pl-9" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Weight</Label>
                <div className="relative">
                  <Weight className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input defaultValue={MOCK_USER_PATIENT.weight} className="pl-9" />
                </div>
              </div>
            </div>

            <div className="pt-4 flex justify-end">
              <Button>Save Changes</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
