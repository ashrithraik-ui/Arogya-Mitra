import React from 'react';
import { useLocation } from 'wouter';
import { useAuth } from '@/context/AuthContext';

export function ProtectedRoute({ 
  component: Component, 
  allowedRole 
}: { 
  component: React.ComponentType; 
  allowedRole: 'patient' | 'doctor';
}) {
  const { isAuthenticated, user } = useAuth();
  const [, setLocation] = useLocation();

  React.useEffect(() => {
    if (!isAuthenticated) {
      setLocation(`/${allowedRole}/login`);
    } else if (user?.role !== allowedRole) {
      setLocation(`/${user?.role}/dashboard`);
    }
  }, [isAuthenticated, user, allowedRole, setLocation]);

  if (!isAuthenticated || user?.role !== allowedRole) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return <Component />;
}
