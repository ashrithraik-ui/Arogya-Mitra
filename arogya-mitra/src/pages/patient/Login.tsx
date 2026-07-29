import React from 'react';
import { useLocation, Link } from 'wouter';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '@/context/AuthContext';
import { MedicalBackground } from '@/components/MedicalBackground';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { HeartPulse, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

const loginSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address." }),
  password: z.string().min(6, { message: "Password must be at least 6 characters." }),
});

export function PatientLogin() {
  const [, setLocation] = useLocation();
  const { login } = useAuth();
  
  const form = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "ananya@example.com",
      password: "password123",
    },
  });

  const [isLoading, setIsLoading] = React.useState(false);

  async function onSubmit(values: z.infer<typeof loginSchema>) {
    try {
      setIsLoading(true);
      await login('patient', values);
      setLocation('/patient/dashboard');
    } catch (e) {
      alert("Login failed. Please check your credentials.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen relative flex items-center justify-center bg-background overflow-hidden p-4">
      <MedicalBackground />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md relative z-10"
      >
        <div className="flex justify-center mb-8">
          <Link href="/">
            <div className="flex items-center gap-2 cursor-pointer bg-card/50 backdrop-blur px-4 py-2 rounded-full border shadow-sm">
              <HeartPulse className="text-primary h-6 w-6" />
              <span className="font-bold text-lg">ArogyaMitra</span>
            </div>
          </Link>
        </div>

        <Card className="backdrop-blur-xl bg-card/80 border-primary/20 shadow-2xl shadow-primary/5">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl font-bold tracking-tight">Patient Login</CardTitle>
            <CardDescription>
              Enter your credentials to access your health portal
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input placeholder="name@example.com" {...field} data-testid="input-email" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Password</FormLabel>
                      <FormControl>
                        <Input type="password" placeholder="••••••••" {...field} data-testid="input-password" />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button type="submit" className="w-full mt-6" data-testid="button-submit">
                  Sign In
                  <ArrowRight className="ml-2 w-4 h-4" />
                </Button>
              </form>
            </Form>
            
            <div className="mt-6 text-center text-sm text-muted-foreground">
              Don't have an account?{' '}
              <Link href="/patient/register" className="text-primary hover:underline font-medium">
                Create one
              </Link>
            </div>
            
            <div className="mt-4 pt-4 border-t border-border/50 text-center text-sm text-muted-foreground">
              Are you a healthcare provider?{' '}
              <Link href="/doctor/login" className="text-secondary hover:underline font-medium">
                Doctor Login
              </Link>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
