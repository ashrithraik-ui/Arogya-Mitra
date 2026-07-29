import React from 'react';
import { motion } from 'framer-motion';
import { Mic } from 'lucide-react';
import { cn } from '@/lib/utils';

interface VoiceAnimationProps {
  state: 'idle' | 'listening' | 'processing' | 'speaking';
  onClick?: () => void;
  className?: string;
}

export function VoiceAnimation({ state, onClick, className }: VoiceAnimationProps) {
  return (
    <div 
      className={cn("relative flex items-center justify-center cursor-pointer", className)} 
      onClick={onClick}
      data-testid={`voice-animation-${state}`}
    >
      {/* Outer Pulse Rings */}
      {(state === 'listening' || state === 'processing') && (
        <>
          <motion.div
            className="absolute rounded-full bg-primary/20"
            style={{ width: '100%', height: '100%' }}
            animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.div
            className="absolute rounded-full bg-secondary/20"
            style={{ width: '100%', height: '100%' }}
            animate={{ scale: [1, 1.8, 1], opacity: [0.3, 0, 0.3] }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
          />
        </>
      )}

      {/* Main Mic Button */}
      <div className={cn(
        "relative z-10 rounded-full flex items-center justify-center text-white shadow-lg transition-colors",
        state === 'idle' ? 'bg-primary hover:bg-primary/90' : 
        state === 'listening' ? 'bg-secondary' : 
        state === 'processing' ? 'bg-muted-foreground' : 
        'bg-primary'
      )} style={{ width: '80%', height: '80%' }}>
        <Mic className="w-1/2 h-1/2" />
      </div>

      {/* Waveform for speaking */}
      {state === 'speaking' && (
        <div className="absolute inset-0 flex items-center justify-center gap-1 z-20">
          {[1, 2, 3, 4, 5].map((i) => (
            <motion.div
              key={i}
              className="w-1.5 bg-white rounded-full"
              animate={{ height: ['20%', '80%', '20%'] }}
              transition={{
                duration: 0.8,
                repeat: Infinity,
                ease: "easeInOut",
                delay: i * 0.1,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
