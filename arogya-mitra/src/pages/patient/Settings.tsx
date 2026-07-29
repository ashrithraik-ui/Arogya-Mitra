import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Wifi, Server, CheckCircle2, AlertCircle } from 'lucide-react';
import api from '@/services/api';

export function PatientSettings() {
  const [serverIp, setServerIp] = useState('');
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'testing' | 'connected' | 'error'>('idle');
  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    const savedUrl = localStorage.getItem('arogya_mitra_api_url') || '';
    setServerIp(savedUrl);
  }, []);

  const handleSaveIp = async () => {
    setConnectionStatus('testing');
    setStatusMsg('Testing connection to server...');

    const formattedUrl = serverIp.trim() 
      ? (serverIp.startsWith('http') ? serverIp.trim() : `http://${serverIp.trim()}`)
      : '';

    if (formattedUrl) {
      localStorage.setItem('arogya_mitra_api_url', formattedUrl);
    } else {
      localStorage.removeItem('arogya_mitra_api_url');
    }

    try {
      const res = await api.get('/health');
      if (res.data && res.data.status === 'healthy') {
        setConnectionStatus('connected');
        setStatusMsg(`Successfully connected to backend server at ${res.config.baseURL}`);
      } else {
        setConnectionStatus('connected');
        setStatusMsg(`Connected to ${res.config.baseURL}`);
      }
    } catch (e: any) {
      console.error("Connection test failed", e);
      setConnectionStatus('error');
      setStatusMsg(`Could not connect. Please check IP address and ensure backend server is running.`);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings & IP Connection</h1>
        <p className="text-muted-foreground mt-1">Manage application settings and backend server connection IP.</p>
      </div>

      <div className="grid gap-6">
        {/* IP Connection Settings Card for Android & LAN */}
        <Card className="border-primary/30 shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg">
              <Server className="w-5 h-5 text-primary" />
              Backend Server IP Connection (Android & Mobile)
            </CardTitle>
            <CardDescription>
              Connect your Android App to your local computer running the ArogyaMitra backend server.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="server-ip">Server IP & Port</Label>
              <div className="flex gap-2">
                <Input
                  id="server-ip"
                  placeholder="e.g. 192.168.1.5:8000 or 10.0.2.2:8000"
                  value={serverIp}
                  onChange={(e) => setServerIp(e.target.value)}
                  className="flex-1 font-mono text-sm"
                />
                <Button onClick={handleSaveIp} disabled={connectionStatus === 'testing'}>
                  {connectionStatus === 'testing' ? 'Testing...' : 'Save & Test'}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Tip for Android Studio Emulator: use <code className="bg-muted px-1.5 py-0.5 rounded text-foreground font-mono">http://10.0.2.2:8000</code>. For real Android phone over Wi-Fi, use your PC's IP address e.g. <code className="bg-muted px-1.5 py-0.5 rounded text-foreground font-mono">http://192.168.x.x:8000</code>.
              </p>
            </div>

            {statusMsg && (
              <div className={`p-3 rounded-md text-xs flex items-center gap-2 ${
                connectionStatus === 'connected' 
                  ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-700 dark:text-emerald-300'
                  : connectionStatus === 'error'
                  ? 'bg-destructive/10 border border-destructive/30 text-destructive'
                  : 'bg-muted text-muted-foreground'
              }`}>
                {connectionStatus === 'connected' && <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />}
                {connectionStatus === 'error' && <AlertCircle className="w-4 h-4 text-destructive shrink-0" />}
                <span>{statusMsg}</span>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Notifications</CardTitle>
            <CardDescription>Configure how you want to be alerted.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Push Notifications</Label>
                <p className="text-sm text-muted-foreground">Receive push notifications for appointments.</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Email Alerts</Label>
                <p className="text-sm text-muted-foreground">Get daily health summaries via email.</p>
              </div>
              <Switch defaultChecked />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Privacy & Security</CardTitle>
            <CardDescription>Manage your data and security settings.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Share Health Data</Label>
                <p className="text-sm text-muted-foreground">Allow ArogyaMitra AI to learn from your data anonymously.</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="pt-4 space-y-2">
              <Button variant="outline" className="w-full sm:w-auto mr-2">Change Password</Button>
              <Button variant="destructive" className="w-full sm:w-auto">Delete Account</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
