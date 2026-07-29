import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send, HeartPulse, Mic, UserCheck, Plus, History, Stethoscope, MessageSquare, Phone } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { Link } from 'wouter';

type Message = {
  id: string;
  role: 'user' | 'ai' | 'doctor';
  content: string;
  timestamp?: string;
  doctor_name?: string;
};

type ConsultationSummary = {
  id: number;
  chief_complaint: string;
  status: string;
  created_at: string;
  doctor_name?: string;
};

export function PatientChat() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'init',
      role: 'ai',
      content: 'Hello! I am ArogyaMitra AI. Please describe your symptoms or health concern, and I will assist you.'
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [consultationId, setConsultationId] = useState<number | null>(null);
  const [assignedDoctor, setAssignedDoctor] = useState<string | null>(null);
  const [assignedDoctorPhone, setAssignedDoctorPhone] = useState<string | null>(null);
  const [consultationsList, setConsultationsList] = useState<ConsultationSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreatingNew, setIsCreatingNew] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Fetch saved chat history for selected or active consultation
  const loadChatData = async (targetId: number | null = consultationId, isInitial = false) => {
    const activePatientId = user?.id ? parseInt(user.id) : 1;
    try {
      if (isInitial) setLoading(true);
      const url = targetId 
        ? `/patient/active-chat?patient_id=${activePatientId}&consultation_id=${targetId}`
        : `/patient/active-chat?patient_id=${activePatientId}`;
      
      const res = await api.get(url);
      const data = res.data;

      if (data.consultation_id) {
        setConsultationId(data.consultation_id);
      }
      if (data.doctor_assigned) {
        setAssignedDoctor(data.doctor_assigned);
      }
      if (data.doctor_phone) {
        setAssignedDoctorPhone(data.doctor_phone);
      }

      if (data.all_consultations) {
        setConsultationsList(data.all_consultations);
      }

      if (data.history && data.history.length > 0) {
        const loadedMsgs: Message[] = data.history.map((h: any, idx: number) => ({
          id: `hist_${idx}_${h.timestamp || idx}`,
          role: h.role === 'patient' || h.role === 'user' ? 'user' : h.role === 'doctor' ? 'doctor' : 'ai',
          content: h.message || h.content,
          timestamp: h.timestamp ? new Date(h.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : undefined,
          doctor_name: h.doctor_name || data.doctor_assigned || 'Doctor',
        }));

        setMessages(loadedMsgs);
      } else if (targetId && data.history?.length === 0) {
        setMessages([
          {
            id: 'init_new',
            role: 'ai',
            content: 'This is a new follow-up chat session. Please send your message or update below.'
          }
        ]);
      }
    } catch (e) {
      console.error("Failed to load chat history", e);
    } finally {
      if (isInitial) setLoading(false);
    }
  };

  useEffect(() => {
    loadChatData(consultationId, true);

    const interval = setInterval(() => {
      loadChatData(consultationId, false);
    }, 3000);

    return () => clearInterval(interval);
  }, [user?.id, consultationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleStartNewChat = async () => {
    if (isCreatingNew) return;
    const activePatientId = user?.id ? parseInt(user.id) : 1;
    setIsCreatingNew(true);
    try {
      const response = await api.post('/patient/new-chat', {
        patient_id: activePatientId,
        chief_complaint: 'Follow-up Chat Session',
      });
      const newConsId = response.data.consultation_id;
      setConsultationId(newConsId);
      await loadChatData(newConsId, true);
    } catch (error) {
      console.error("Failed to start new chat", error);
      alert("Could not start a new chat session. Please try again.");
    } finally {
      setIsCreatingNew(false);
    }
  };

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const activePatientId = user?.id ? parseInt(user.id) : 1;
    if (!input.trim()) return;

    const userMessage = input;
    const newMsg: Message = { 
      id: Date.now().toString(), 
      role: 'user', 
      content: userMessage,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages((prev) => [...prev, newMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await api.post('/patient/chat', {
        patient_id: activePatientId,
        consultation_id: consultationId,
        message: userMessage,
      });

      const data = response.data;
      if (data.consultation_id) {
        setConsultationId(data.consultation_id);
      }

      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'ai',
          content: data.ai_response,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'ai',
          content: 'Sorry, I encountered an error while processing your message. Please try again.',
        },
      ]);
    } finally {
      setIsTyping(false);
      // Reload chat data immediately to refresh history
      loadChatData(consultationId, false);
    }
  };

  return (
    <div className="h-[calc(100vh-9rem)] flex flex-col bg-card rounded-xl border shadow-sm overflow-hidden">
      {/* Header */}
      <CardHeader className="border-b px-6 py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-card shrink-0">
        <div className="flex items-center gap-3">
          <div className="bg-primary/10 p-2 rounded-full">
            <HeartPulse className="w-5 h-5 text-primary" />
          </div>
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              ArogyaMitra Consultation Chat
              {consultationId && (
                <span className="text-xs font-normal text-muted-foreground bg-muted px-2 py-0.5 rounded-md">
                  Session #{consultationId}
                </span>
              )}
            </CardTitle>
            <p className="text-xs text-muted-foreground flex flex-wrap items-center gap-2">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-pulse"></span>
                {assignedDoctor ? `Assigned Doctor: Dr. ${assignedDoctor}` : 'Connected & Synced with Doctor'}
              </span>
              {assignedDoctor && (
                <span className="font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md flex items-center gap-1">
                  <Phone className="w-3 h-3" />
                  {assignedDoctorPhone || '+91 98765 43210'}
                </span>
              )}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Chat Selector Dropdown if multiple chats exist */}
          {consultationsList.length > 0 && (
            <div className="flex items-center gap-1">
              <History className="w-4 h-4 text-muted-foreground" />
              <select
                className="text-xs bg-muted border rounded-md px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary"
                value={consultationId || ''}
                onChange={(e) => {
                  const targetId = parseInt(e.target.value);
                  if (targetId) {
                    setConsultationId(targetId);
                    loadChatData(targetId, true);
                  }
                }}
              >
                {consultationsList.map((c) => (
                  <option key={c.id} value={c.id}>
                    Chat #{c.id}: {c.chief_complaint?.slice(0, 25) || 'Consultation'} ({c.status})
                  </option>
                ))}
              </select>
            </div>
          )}

          <Button 
            variant="default" 
            size="sm" 
            onClick={handleStartNewChat} 
            disabled={isCreatingNew}
            className="bg-primary text-primary-foreground hover:bg-primary/90 gap-1"
          >
            <Plus className="w-4 h-4" />
            {isCreatingNew ? 'Creating...' : 'New Follow-Up Chat'}
          </Button>

          <Button variant="outline" size="sm" asChild>
            <Link href="/patient/voice">
              <Mic className="w-4 h-4 mr-1" /> Voice
            </Link>
          </Button>
        </div>
      </CardHeader>

      {/* Chat Messages */}
      <CardContent className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
        {loading ? (
          <div className="text-center py-8 text-muted-foreground text-sm flex flex-col items-center gap-2">
            <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
            Loading your conversation history...
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${
                  msg.role === 'user'
                    ? 'justify-end'
                    : msg.role === 'doctor'
                    ? 'justify-start'
                    : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[88%] sm:max-w-[80%] rounded-2xl p-4 shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-br-sm'
                      : msg.role === 'doctor'
                      ? 'bg-emerald-500/10 border-2 border-emerald-500/30 text-foreground font-medium rounded-xl space-y-2'
                      : 'bg-muted rounded-bl-sm text-foreground'
                  }`}
                >
                  {/* Doctor Header if role is doctor */}
                  {msg.role === 'doctor' && (
                    <div className="flex items-center gap-2 pb-2 border-b border-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-semibold text-xs uppercase tracking-wider">
                      <Stethoscope className="w-4 h-4" />
                      <span>Doctor Response ({msg.doctor_name || assignedDoctor || 'Doctor'})</span>
                    </div>
                  )}

                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>

                  {msg.timestamp && (
                    <div className={`text-[10px] mt-1 text-right ${msg.role === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                      {msg.timestamp}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}

            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-start"
              >
                <div className="bg-muted rounded-2xl rounded-bl-sm p-4 flex items-center gap-1">
                  <motion.div className="w-2 h-2 bg-foreground/40 rounded-full" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0 }} />
                  <motion.div className="w-2 h-2 bg-foreground/40 rounded-full" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }} />
                  <motion.div className="w-2 h-2 bg-foreground/40 rounded-full" animate={{ y: [0, -5, 0] }} transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }} />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        )}
        <div ref={messagesEndRef} />
      </CardContent>

      {/* Input Bar */}
      <div className="p-4 border-t bg-card shrink-0">
        <form onSubmit={handleSend} className="flex gap-2 max-w-4xl mx-auto">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your query or follow-up question..."
            className="flex-1 rounded-full px-6"
          />
          <Button type="submit" size="icon" className="rounded-full shrink-0" disabled={!input.trim() || isTyping}>
            <Send className="w-4 h-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
