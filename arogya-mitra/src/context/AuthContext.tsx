import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api from '../services/api';

type User = {
  id: string;
  name: string;
  email: string;
  role: 'patient' | 'doctor';
  avatar?: string;
  phone?: string;
  specialization?: string;
};

type AuthContextType = {
  user: User | null;
  isAuthenticated: boolean;
  login: (role: 'patient' | 'doctor', data: any) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const storedUser = localStorage.getItem('arogya_mitra_user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Failed to parse user from localStorage');
      }
    }
  }, []);

  const login = async (role: 'patient' | 'doctor', data: any) => {
    if (role === 'doctor') {
      try {
        const response = await api.post('/doctor/login', {
          email: data.email,
          password: data.password,
        });
        const tokenData = response.data;
        localStorage.setItem('arogya_mitra_token', tokenData.access_token);
        
        // Fetch doctor profile
        const profileRes = await api.get('/doctor/me');
        const userData: User = {
          id: profileRes.data.id.toString(),
          name: profileRes.data.name,
          email: profileRes.data.email,
          role: 'doctor',
          specialization: profileRes.data.specialization,
        };
        setUser(userData);
        localStorage.setItem('arogya_mitra_user', JSON.stringify(userData));
      } catch (error) {
        console.error("Doctor login failed", error);
        throw error;
      }
    } else {
      // Patient login — register or find existing patient
      try {
        // Use the demo phone number to always get the seeded demo patient
        const demoPhone = data.phone || "+910000000001";
        let patientData;
        
        try {
          // Try to register — if phone exists, server returns existing patient
          const response = await api.post('/patient/register', {
            name: data.name || "Patient",
            phone: demoPhone,
            age: 35,
            gender: "Male",
            blood_group: "O+"
          });
          patientData = response.data;
        } catch (e) {
          // Fallback: fetch demo patient directly
          const fallback = await api.get('/patient/1');
          patientData = fallback.data;
        }
        
        const userData: User = {
          id: patientData.id.toString(),
          name: patientData.name,
          email: patientData.email || data.email || "",
          phone: patientData.phone,
          role: 'patient',
        };
        setUser(userData);
        localStorage.setItem('arogya_mitra_user', JSON.stringify(userData));
      } catch (error) {
        console.error("Patient login failed", error);
        throw error;
      }
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('arogya_mitra_user');
    localStorage.removeItem('arogya_mitra_token');
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
