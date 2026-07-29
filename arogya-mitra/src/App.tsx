import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { Toaster as SonnerToaster } from 'react-hot-toast';
import { TooltipProvider } from '@/components/ui/tooltip';
import NotFound from '@/pages/not-found';
import { Route, Switch, Router as WouterRouter } from 'wouter';
import { AuthProvider } from '@/context/AuthContext';
import { ProtectedRoute } from '@/components/ProtectedRoute';

// Public Pages
import { Home } from '@/pages/Home';
import { PatientLogin } from '@/pages/patient/Login';
import { PatientRegister } from '@/pages/patient/Register';
import { DoctorLogin } from '@/pages/doctor/Login';

// Layouts
import { PatientLayout } from '@/layouts/PatientLayout';
import { DoctorLayout } from '@/layouts/DoctorLayout';

// Patient Pages
import { PatientDashboard } from '@/pages/patient/Dashboard';
import { PatientChat } from '@/pages/patient/Chat';
import { PatientVoice } from '@/pages/patient/Voice';
import { PatientUploadReport } from '@/pages/patient/UploadReport';
import { PatientUploadImage } from '@/pages/patient/UploadImage';
import { PatientTimeline } from '@/pages/patient/Timeline';
import { PatientConsultation } from '@/pages/patient/Consultation';
import { PatientPrescriptions } from '@/pages/patient/Prescriptions';
import { PatientProfile } from '@/pages/patient/Profile';
import { PatientSettings } from '@/pages/patient/Settings';

// Doctor Pages
import { DoctorDashboard } from '@/pages/doctor/Dashboard';
import { DoctorConsultations } from '@/pages/doctor/Consultations';
import { DoctorReports } from '@/pages/doctor/Reports';
import { DoctorImages } from '@/pages/doctor/Images';
import { DoctorPrescription } from '@/pages/doctor/Prescription';
import { DoctorHistory } from '@/pages/doctor/History';
import { PatientView } from '@/pages/doctor/PatientView';

const queryClient = new QueryClient();

function PatientRoutes() {
  return (
    <PatientLayout>
      <Switch>
        <Route path="/patient/dashboard" component={PatientDashboard} />
        <Route path="/patient/chat" component={PatientChat} />
        <Route path="/patient/voice" component={PatientVoice} />
        <Route path="/patient/upload-report" component={PatientUploadReport} />
        <Route path="/patient/upload-image" component={PatientUploadImage} />
        <Route path="/patient/timeline" component={PatientTimeline} />
        <Route path="/patient/prescriptions" component={PatientPrescriptions} />
        <Route path="/patient/consultation" component={PatientConsultation} />
        <Route path="/patient/profile" component={PatientProfile} />
        <Route path="/patient/settings" component={PatientSettings} />
        <Route component={NotFound} />
      </Switch>
    </PatientLayout>
  );
}

function DoctorRoutes() {
  return (
    <DoctorLayout>
      <Switch>
        <Route path="/doctor/dashboard" component={DoctorDashboard} />
        <Route path="/doctor/consultations" component={DoctorConsultations} />
        <Route path="/doctor/reports" component={DoctorReports} />
        <Route path="/doctor/images" component={DoctorImages} />
        <Route path="/doctor/prescription" component={DoctorPrescription} />
        <Route path="/doctor/history" component={DoctorHistory} />
        <Route path="/doctor/patient/:id" component={PatientView} />
        <Route component={NotFound} />
      </Switch>
    </DoctorLayout>
  );
}

function Router() {
  return (
    <Switch>
      <Route path="/" component={Home} />
      <Route path="/patient/login" component={PatientLogin} />
      <Route path="/patient/register" component={PatientRegister} />
      <Route path="/doctor/login" component={DoctorLogin} />
      
      <Route path="/patient/*">
        <ProtectedRoute component={PatientRoutes} allowedRole="patient" />
      </Route>
      
      <Route path="/doctor/*">
        <ProtectedRoute component={DoctorRoutes} allowedRole="doctor" />
      </Route>
      
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider>
          <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}>
            <Router />
          </WouterRouter>
          <Toaster />
          <SonnerToaster position="top-right" />
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
