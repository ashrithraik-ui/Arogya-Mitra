import React, { useState, useEffect } from 'react';
import { Link } from 'wouter';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { MedicalBackground } from '@/components/MedicalBackground';
import { motion, useScroll, useTransform } from 'framer-motion';
import { 
  HeartPulse, ShieldCheck, Stethoscope, Activity, 
  Brain, FileText, Mic, Phone, Sparkles, ArrowRight, CheckCircle2,
  Server, Wifi, WifiOff, Settings
} from 'lucide-react';
import heroImg from '@/assets/images/hero-medical-ai.svg';
import { ThemeToggle } from '@/components/ThemeToggle';
import api from '@/services/api';

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

export function Home() {
  const { scrollYProgress } = useScroll();
  const y = useTransform(scrollYProgress, [0, 1], ['0%', '50%']);

  // Server IP connection state
  const [showIpConfig, setShowIpConfig] = useState(false);
  const [serverIp, setServerIp] = useState('');
  const [connStatus, setConnStatus] = useState<'idle' | 'testing' | 'ok' | 'fail'>('idle');
  const [connMsg, setConnMsg] = useState('');

  useEffect(() => {
    const saved = localStorage.getItem('arogya_mitra_api_url') || '';
    setServerIp(saved);
    // Auto-show IP config if on Android/mobile and no IP is set
    if (!saved && /Android|Mobile/i.test(navigator.userAgent)) {
      setShowIpConfig(true);
    }
  }, []);

  const handleTestConnection = async () => {
    setConnStatus('testing');
    setConnMsg('Connecting...');
    const formatted = serverIp.trim()
      ? (serverIp.trim().startsWith('http') ? serverIp.trim() : `http://${serverIp.trim()}`)
      : '';
    if (formatted) {
      localStorage.setItem('arogya_mitra_api_url', formatted);
    } else {
      localStorage.removeItem('arogya_mitra_api_url');
    }
    try {
      const res = await api.get('/health');
      setConnStatus('ok');
      setConnMsg(`✅ Connected to server at ${formatted || 'localhost:8000'}`);
    } catch (e) {
      setConnStatus('fail');
      setConnMsg('❌ Cannot reach server. Check IP, port, and that backend is running.');
    }
  };
  return (
    <div className="min-h-screen bg-background overflow-x-hidden selection:bg-primary/20">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-md border-b border-border/50 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <HeartPulse className="text-primary h-6 w-6" />
            <span className="font-bold text-xl tracking-tight">ArogyaMitra</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium">
            <a href="#features" className="text-muted-foreground hover:text-foreground transition-colors">Features</a>
            <a href="#how-it-works" className="text-muted-foreground hover:text-foreground transition-colors">How it Works</a>
            <a href="#for-doctors" className="text-muted-foreground hover:text-foreground transition-colors">For Providers</a>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Button variant="ghost" size="icon" onClick={() => setShowIpConfig(!showIpConfig)} title="Server Connection">
              {connStatus === 'ok' ? <Wifi className="w-5 h-5 text-emerald-500" /> : <Server className="w-5 h-5" />}
            </Button>
            <div className="hidden sm:flex items-center gap-2">
              <Button variant="ghost" asChild>
                <Link href="/patient/login">Sign In</Link>
              </Button>
              <Button asChild>
                <Link href="/patient/register">Get Started</Link>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Server IP Connection Banner */}
      {showIpConfig && (
        <div className="fixed top-16 left-0 right-0 z-40 bg-card/95 backdrop-blur-md border-b shadow-lg px-4 py-4">
          <div className="max-w-2xl mx-auto">
            <div className="flex items-center gap-2 mb-2">
              <Server className="w-4 h-4 text-primary" />
              <span className="text-sm font-semibold">Connect to Backend Server</span>
              <button onClick={() => setShowIpConfig(false)} className="ml-auto text-muted-foreground hover:text-foreground text-xs">✕ Close</button>
            </div>
            <div className="flex gap-2">
              <Input
                placeholder="e.g. 192.168.1.5:8000"
                value={serverIp}
                onChange={(e) => setServerIp(e.target.value)}
                className="flex-1 font-mono text-sm h-9"
              />
              <Button size="sm" onClick={handleTestConnection} disabled={connStatus === 'testing'}>
                {connStatus === 'testing' ? 'Testing...' : 'Connect'}
              </Button>
            </div>
            {connMsg && (
              <p className={`text-xs mt-2 ${connStatus === 'ok' ? 'text-emerald-600' : connStatus === 'fail' ? 'text-red-500' : 'text-muted-foreground'}`}>
                {connMsg}
              </p>
            )}
            <p className="text-[10px] text-muted-foreground mt-1">
              Enter your PC's IP address and port (e.g. <code className="bg-muted px-1 rounded">http://192.168.x.x:8000</code>). For emulator use <code className="bg-muted px-1 rounded">http://10.0.2.2:8000</code>
            </p>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 md:pt-48 md:pb-32 overflow-hidden">
        <MedicalBackground />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div 
              initial="hidden"
              animate="visible"
              variants={staggerContainer}
              className="max-w-2xl"
            >
              <motion.div variants={fadeIn} className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
                <Sparkles className="w-4 h-4" />
                The Future of Indian Healthcare
              </motion.div>
              <motion.h1 variants={fadeIn} className="text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.1] mb-6">
                Your Intelligent <br/>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">Health Companion</span>
              </motion.h1>
              <motion.p variants={fadeIn} className="text-lg md:text-xl text-muted-foreground mb-8 leading-relaxed max-w-lg">
                ArogyaMitra combines advanced AI with clinical precision to help you understand your health, manage records, and connect with top doctors seamlessly.
              </motion.p>
              <motion.div variants={fadeIn} className="flex flex-col sm:flex-row gap-4 flex-wrap">
                <Button size="lg" className="h-14 px-8 text-lg rounded-full" asChild>
                  <Link href="/patient/register">Join as Patient <ArrowRight className="ml-2 w-5 h-5" /></Link>
                </Button>
                {/* HTML tel: Click-to-Call Link */}
                <Button size="lg" className="h-14 px-8 text-lg rounded-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold shadow-lg" asChild>
                  <a href="tel:+919876543210">
                    <Phone className="mr-2 w-5 h-5" /> 📞 Click to Call AI (+91)
                  </a>
                </Button>
                <Button size="lg" variant="secondary" className="h-14 px-8 text-lg rounded-full bg-blue-600 hover:bg-blue-500 text-white font-bold shadow-lg" onClick={() => window.open('http://localhost:8000/call', '_blank')}>
                  <Mic className="mr-2 w-5 h-5" /> 🌐 Web Voice Call
                </Button>
                <Button size="lg" variant="outline" className="h-14 px-8 text-lg rounded-full border-primary/20 hover:bg-primary/5" asChild>
                  <Link href="/doctor/login">Provider Portal</Link>
                </Button>
              </motion.div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative lg:h-[600px] flex items-center justify-center"
            >
              {/* Decorative elements behind image */}
              <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 to-secondary/20 rounded-[2.5rem] blur-3xl transform rotate-6 scale-105"></div>
              
              <div className="relative w-full max-w-md aspect-[4/5] rounded-[2rem] overflow-hidden border border-white/10 shadow-2xl shadow-primary/20">
                <div className="absolute inset-0 bg-background/20 backdrop-blur-sm z-10 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-300">
                  <div className="bg-background/90 text-foreground px-4 py-2 rounded-full font-medium shadow-lg flex items-center gap-2">
                    <Activity className="w-4 h-4 text-primary" /> AI Active
                  </div>
                </div>
                <img 
                  src={heroImg} 
                  alt="ArogyaMitra AI Interface" 
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    // Fallback if image fails to load
                    e.currentTarget.style.display = 'none';
                    e.currentTarget.parentElement?.classList.add('bg-gradient-to-br', 'from-primary/20', 'to-secondary/20');
                  }}
                />
              </div>

              {/* Floating detail cards */}
              <motion.div 
                animate={{ y: [0, -10, 0] }} 
                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                className="absolute -left-6 top-1/4 bg-background/80 backdrop-blur-md p-4 rounded-2xl border shadow-xl"
              >
                <div className="flex items-center gap-3">
                  <div className="bg-green-500/10 p-2 rounded-full"><CheckCircle2 className="w-5 h-5 text-green-500" /></div>
                  <div>
                    <p className="text-xs text-muted-foreground font-medium">Vitals Status</p>
                    <p className="text-sm font-bold">All Normal</p>
                  </div>
                </div>
              </motion.div>

              <motion.div 
                animate={{ y: [0, 10, 0] }} 
                transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                className="absolute -right-6 bottom-1/3 bg-background/80 backdrop-blur-md p-4 rounded-2xl border shadow-xl"
              >
                <div className="flex items-center gap-3">
                  <div className="bg-primary/10 p-2 rounded-full"><Brain className="w-5 h-5 text-primary" /></div>
                  <div>
                    <p className="text-xs text-muted-foreground font-medium">AI Analysis</p>
                    <p className="text-sm font-bold">Report Scanned</p>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">A complete ecosystem for your health</h2>
            <p className="text-lg text-muted-foreground">Everything you need to understand, track, and improve your wellbeing.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { icon: Brain, title: "AI Symptom Checker", desc: "Chat naturally with our medical AI to understand your symptoms before seeing a doctor." },
              { icon: FileText, title: "Smart Report Analysis", desc: "Upload complex lab reports and get plain-English explanations instantly." },
              { icon: Mic, title: "Voice Assistant", desc: "Don't want to type? Just speak to ArogyaMitra for hands-free health logging." },
              { icon: Activity, title: "Vitals Tracking", desc: "Keep a continuous timeline of your blood pressure, sugar, weight, and more." },
              { icon: ShieldCheck, title: "ABHA Integrated", desc: "Fully compliant with Indian health data standards for total security and privacy." },
              { icon: Stethoscope, title: "Instant Consultations", desc: "Connect with verified specialists via secure video or book in-person visits." },
            ].map((feature, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="bg-card p-8 rounded-3xl border hover:border-primary/30 transition-colors shadow-sm hover:shadow-md"
              >
                <div className="w-12 h-12 bg-primary/10 rounded-2xl flex items-center justify-center mb-6">
                  <feature.icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* For Doctors */}
      <section id="for-doctors" className="py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-secondary/5 skew-y-3 transform origin-bottom-left"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">ArogyaMitra <span className="text-secondary">Pro</span></h2>
              <p className="text-xl text-foreground/80 mb-8 leading-relaxed">
                Empowering Indian doctors with AI-assisted diagnostics, streamlined patient queues, and digital prescriptions.
              </p>
              <ul className="space-y-4 mb-8">
                {[
                  "AI-pre-screened patient summaries save 40% consultation time",
                  "View high-res medical images and AI-annotated lab reports",
                  "Generate compliant digital prescriptions in seconds",
                  "Manage video and in-person queues from one unified dashboard"
                ].map((item, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <CheckCircle2 className="w-6 h-6 text-secondary shrink-0 mt-0.5" />
                    <span className="text-lg">{item}</span>
                  </li>
                ))}
              </ul>
              <Button size="lg" className="bg-secondary text-secondary-foreground hover:bg-secondary/90 h-14 px-8 rounded-full" asChild>
                <Link href="/doctor/login">Access Provider Portal</Link>
              </Button>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-secondary/20 blur-3xl rounded-full"></div>
              <div className="bg-card border-secondary/20 border shadow-2xl rounded-2xl p-6 relative z-10">
                <div className="border-b pb-4 mb-4 flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-lg">Patient Summary (AI Generated)</h3>
                    <p className="text-sm text-muted-foreground">Ananya Sharma • 32F • ID: #8492</p>
                  </div>
                  <div className="bg-secondary/10 text-secondary px-3 py-1 rounded-full text-xs font-bold uppercase">Ready for review</div>
                </div>
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-1">Chief Complaint</h4>
                    <p className="text-sm">Persistent mild headache for 48 hours. Hydration normal. Pain scale 3/10.</p>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-1">Recent Lab Result</h4>
                    <div className="bg-secondary/5 border border-secondary/20 p-3 rounded flex items-center gap-3">
                      <FileText className="w-5 h-5 text-secondary" />
                      <div>
                        <p className="text-sm font-medium">Complete Blood Count</p>
                        <p className="text-xs text-muted-foreground">All indicators within normal range.</p>
                      </div>
                    </div>
                  </div>
                  <Button className="w-full bg-secondary/10 text-secondary hover:bg-secondary/20" variant="ghost">Start Video Consultation</Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-primary text-primary-foreground text-center px-4">
        <div className="max-w-3xl mx-auto space-y-8">
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight">Your health in your hands.</h2>
          <p className="text-xl opacity-90 leading-relaxed">
            Join thousands of patients taking control of their medical journey with the power of AI.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
            <Button size="lg" variant="secondary" className="h-14 px-8 text-lg rounded-full bg-white text-primary hover:bg-gray-100" asChild>
              <Link href="/patient/register">Create Free Account</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <HeartPulse className="text-primary h-6 w-6" />
              <span className="font-bold text-xl tracking-tight">ArogyaMitra</span>
            </div>
            <p className="text-muted-foreground max-w-sm">
              A premium AI-powered healthcare platform bridging the gap between patients and doctors across India.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Platform</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><Link href="/patient/login" className="hover:text-primary">Patient Portal</Link></li>
              <li><Link href="/doctor/login" className="hover:text-primary">Provider Portal</Link></li>
              <li><a href="#" className="hover:text-primary">ABHA Integration</a></li>
              <li><a href="#" className="hover:text-primary">Security</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Company</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#" className="hover:text-primary">About Us</a></li>
              <li><a href="#" className="hover:text-primary">Careers</a></li>
              <li><a href="#" className="hover:text-primary">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-primary">Terms of Service</a></li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 pt-8 border-t text-center text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} ArogyaMitra Health Technologies. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
