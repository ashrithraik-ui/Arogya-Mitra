import React from 'react';
import { motion } from 'framer-motion';

export function EmergencyButton() {
  const handleEmergency = () => {
    alert("Emergency protocols activated. Connecting to nearest hospital and emergency contacts...");
  };

  return (
    <motion.button
      onClick={handleEmergency}
      className="relative group flex flex-col items-center justify-center w-full sm:w-auto overflow-hidden rounded-2xl bg-destructive text-destructive-foreground p-6 shadow-lg shadow-destructive/20 transition-transform active:scale-95"
      whileHover={{ scale: 1.02 }}
      data-testid="button-emergency"
    >
      <div className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />
      
      {/* Pulse effect */}
      <motion.div
        className="absolute inset-0 rounded-2xl border-4 border-destructive"
        animate={{ scale: [1, 1.1, 1], opacity: [0.5, 0, 0.5] }}
        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
      />
      
      <svg
        className="w-10 h-10 mb-2 relative z-10"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
      </svg>
      <span className="text-xl font-bold tracking-wider relative z-10">EMERGENCY SOS</span>
      <span className="text-xs opacity-80 mt-1 relative z-10">Tap to call ambulance</span>
    </motion.button>
  );
}
