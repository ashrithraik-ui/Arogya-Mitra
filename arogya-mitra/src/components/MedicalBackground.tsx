import React from 'react';
import { motion } from 'framer-motion';

export function MedicalBackground() {
  return (
    <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none opacity-20 dark:opacity-10" data-testid="medical-background">
      <svg
        className="absolute top-[20%] left-[-10%] w-[120%] h-auto text-primary"
        viewBox="0 0 1000 200"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <motion.path
          d="M0 100 H300 L320 80 L350 150 L380 50 L400 100 H1000"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ duration: 3, repeat: Infinity, repeatType: "loop", ease: "linear" }}
        />
        <motion.path
          d="M0 100 H300 L320 80 L350 150 L380 50 L400 100 H1000"
          stroke="currentColor"
          strokeWidth="4"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="opacity-30 blur-sm"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ duration: 3, repeat: Infinity, repeatType: "loop", ease: "linear" }}
        />
      </svg>

      {/* Decorative Crosses */}
      <div className="absolute top-[10%] right-[10%] opacity-20">
        <svg width="40" height="40" viewBox="0 0 40 40" fill="currentColor" className="text-secondary">
          <path d="M16 0h8v16h16v8H24v16h-8V24H0v-8h16V0z" />
        </svg>
      </div>
      <div className="absolute bottom-[20%] left-[15%] opacity-10">
        <svg width="60" height="60" viewBox="0 0 40 40" fill="currentColor" className="text-primary">
          <path d="M16 0h8v16h16v8H24v16h-8V24H0v-8h16V0z" />
        </svg>
      </div>
      
      {/* DNA Helix abstraction */}
      <svg className="absolute bottom-[-10%] right-[-5%] w-[40%] h-auto text-secondary opacity-20" viewBox="0 0 200 400" fill="none">
        <motion.path
          d="M 50 0 C 150 100, 150 100, 50 200 C -50 300, -50 300, 50 400"
          stroke="currentColor" strokeWidth="2" strokeDasharray="4 4"
        />
        <motion.path
          d="M 150 0 C 50 100, 50 100, 150 200 C 250 300, 250 300, 150 400"
          stroke="currentColor" strokeWidth="2" strokeDasharray="4 4"
        />
        <line x1="60" y1="50" x2="140" y2="50" stroke="currentColor" strokeWidth="1" />
        <line x1="100" y1="100" x2="100" y2="100" stroke="currentColor" strokeWidth="1" />
        <line x1="60" y1="150" x2="140" y2="150" stroke="currentColor" strokeWidth="1" />
        <line x1="60" y1="250" x2="140" y2="250" stroke="currentColor" strokeWidth="1" />
        <line x1="100" y1="300" x2="100" y2="300" stroke="currentColor" strokeWidth="1" />
        <line x1="60" y1="350" x2="140" y2="350" stroke="currentColor" strokeWidth="1" />
      </svg>
      
      <div className="absolute inset-0 bg-gradient-to-b from-transparent to-background/90" />
    </div>
  );
}
