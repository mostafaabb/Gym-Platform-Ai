"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Mic, 
  MicOff, 
  Video, 
  VideoOff, 
  Volume2, 
  MessageSquare, 
  Sparkles,
  Dumbbell,
  Play,
  Square,
  AlertTriangle,
  ChevronRight,
  Info
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";
import PoseTracker from "@/components/cv/PoseTracker";
import { useCoachSocket } from "@/hooks/useCoachSocket";

export default function AICoachPage() {
  const [isActive, setIsActive] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isCameraOn, setIsCameraOn] = useState(true);
  
  // Mock token - in real app, get from auth context
  const { messages, formAlert, score, sendMessage, sendLandmarks } = useCoachSocket("mock-token");

  const handleLandmarks = (landmarks: any) => {
    // Throttle sends to avoid overloading the socket
    if (isActive && Math.random() > 0.9) {
      sendLandmarks(landmarks, "bench_press");
    }
  };

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col lg:flex-row gap-6 overflow-hidden">
      {/* Live Feed & Pose Detection */}
      <div className="flex-1 relative rounded-3xl bg-zinc-950 border border-white/5 overflow-hidden group">
        {!isActive ? (
          <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-zinc-950/80 backdrop-blur-md">
            <div className="h-20 w-20 rounded-full bg-primary flex items-center justify-center mb-6 shadow-2xl shadow-primary/40">
              <Dumbbell className="text-white" size={40} />
            </div>
            <h2 className="text-3xl font-bold text-white mb-2">Ready to Start?</h2>
            <p className="text-zinc-500 mb-8 max-w-sm text-center">Your AI coach will guide you through every rep with voice and real-time form correction.</p>
            <Button 
              size="lg" 
              onClick={() => setIsActive(true)}
              className="rounded-full bg-primary hover:bg-primary/90 px-10 h-14 text-lg font-bold"
            >
              <Play className="mr-2 h-5 w-5 fill-current" />
              Begin Session
            </Button>
          </div>
        ) : (
          <>
            <PoseTracker isActive={isCameraOn} onLandmarksUpdate={handleLandmarks} />
            
            {/* Form Alerts */}
            <AnimatePresence>
              {formAlert && (
                <motion.div 
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="absolute top-10 left-1/2 -translate-x-1/2 z-30 flex items-center gap-3 px-6 py-3 rounded-full bg-red-500 text-white font-bold shadow-2xl shadow-red-500/40"
                >
                  <AlertTriangle size={20} className="animate-pulse" />
                  {formAlert}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Rep Counter */}
            <div className="absolute top-10 left-10 z-30">
               <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-4 min-w-[120px]">
                  <p className="text-[10px] text-zinc-400 uppercase tracking-widest font-bold">Reps Done</p>
                  <div className="flex items-baseline gap-2">
                     <span className="text-4xl font-black text-primary">6</span>
                     <span className="text-zinc-500">/ 8</span>
                  </div>
               </div>
            </div>

            {/* Performance Metrics Overlay */}
            <div className="absolute bottom-10 right-10 z-30 space-y-4">
               <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-2xl p-4">
                  <div className="flex items-center justify-between gap-8 mb-2">
                     <span className="text-xs font-bold text-zinc-400">Form Score</span>
                     <span className={cn(
                       "text-xs font-bold",
                       score > 90 ? "text-emerald-400" : "text-amber-400"
                     )}>{score || 94}%</span>
                  </div>
                  <div className="h-1.5 w-48 bg-zinc-800 rounded-full overflow-hidden">
                     <motion.div 
                       animate={{ width: `${score || 94}%` }}
                       className="h-full bg-emerald-400" 
                     />
                  </div>
               </div>
            </div>
          </>
        )}

        {/* Controls Bar */}
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-30 flex items-center gap-4 px-6 py-4 rounded-3xl bg-zinc-900/60 backdrop-blur-2xl border border-white/10 shadow-2xl transition-opacity opacity-0 group-hover:opacity-100">
          <Button 
            variant="ghost" 
            size="icon" 
            className={cn("rounded-2xl h-12 w-12", isMuted ? "bg-red-500/20 text-red-500" : "bg-white/5 text-white")}
            onClick={() => setIsMuted(!isMuted)}
          >
            {isMuted ? <MicOff size={20} /> : <Mic size={20} />}
          </Button>
          <Button 
            variant="ghost" 
            size="icon" 
            className={cn("rounded-2xl h-12 w-12", !isCameraOn ? "bg-red-500/20 text-red-500" : "bg-white/5 text-white")}
            onClick={() => setIsCameraOn(!isCameraOn)}
          >
            {isCameraOn ? <Video size={20} /> : <VideoOff size={20} />}
          </Button>
          <div className="h-8 w-[1px] bg-white/10 mx-2" />
          <Button 
            className="rounded-2xl h-12 bg-red-500 hover:bg-red-600 text-white font-bold px-6"
            onClick={() => setIsActive(false)}
          >
            <Square className="mr-2 h-4 w-4 fill-current" />
            End Session
          </Button>
        </div>
      </div>

      {/* AI Conversation & Logic */}
      <div className="w-full lg:w-[400px] flex flex-col gap-6">
        {/* Voice Visualizer */}
        <div className="rounded-3xl bg-zinc-900/50 border border-white/5 p-6 backdrop-blur-sm">
           <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                 <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                 <span className="text-xs font-bold text-zinc-400 uppercase tracking-widest">AI Coach Live</span>
              </div>
              <Volume2 className="text-primary" size={20} />
           </div>
           
           <div className="flex items-center justify-center gap-1.5 h-16">
              {[...Array(12)].map((_, i) => (
                <motion.div
                  key={i}
                  animate={{ height: isActive && !isMuted ? [10, 40, 20, 50, 15] : 4 }}
                  transition={{ repeat: Infinity, duration: 1.5, delay: i * 0.1 }}
                  className="w-1.5 rounded-full bg-primary/40"
                />
              ))}
           </div>
        </div>

        {/* Chat History */}
        <div className="flex-1 rounded-3xl bg-zinc-900/50 border border-white/5 flex flex-col overflow-hidden backdrop-blur-sm">
           <div className="p-4 border-b border-white/5 bg-white/5 flex items-center gap-2">
              <MessageSquare size={16} className="text-zinc-500" />
              <span className="text-sm font-semibold text-zinc-300">Live Transcript</span>
           </div>
           
           <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {messages.length === 0 && (
                <div className="text-center text-zinc-600 mt-20 italic">
                  Start speaking to begin your session...
                </div>
              )}
              {messages.map((m, i) => (
                <div key={i} className={cn(
                  "flex flex-col gap-2",
                  m.role === "ai" ? "items-start" : "items-end"
                )}>
                   <div className={cn(
                     "max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed",
                     m.role === "ai" 
                      ? "bg-white/5 text-zinc-300 rounded-tl-none border border-white/5" 
                      : "bg-primary text-white rounded-tr-none"
                   )}>
                      {m.content}
                   </div>
                </div>
              ))}
           </div>

           <div className="p-4 bg-white/5">
              <div className="relative">
                 <input 
                   placeholder="Speak naturally or type..."
                   onKeyDown={(e) => {
                     if (e.key === "Enter") {
                        sendMessage(e.currentTarget.value);
                        e.currentTarget.value = "";
                     }
                   }}
                   className="w-full bg-zinc-950 border border-white/10 rounded-2xl py-3 pl-4 pr-12 text-sm outline-none focus:border-primary/50 transition-all text-white"
                 />
                 <Button size="icon" className="absolute right-1.5 top-1.5 h-8 w-8 rounded-xl bg-primary">
                    <ChevronRight size={18} />
                 </Button>
              </div>
           </div>
        </div>

        {/* Current Exercise Info */}
        <div className="rounded-3xl bg-gradient-to-br from-primary/20 to-purple-500/20 border border-white/5 p-6 backdrop-blur-sm">
           <div className="flex items-center gap-3 mb-4">
              <div className="h-10 w-10 rounded-xl bg-white/10 flex items-center justify-center text-white">
                 <Info size={20} />
              </div>
              <div>
                 <h4 className="font-bold text-white">Flat Bench Press</h4>
                 <p className="text-xs text-zinc-400">Set 2 of 4</p>
              </div>
           </div>
           <p className="text-xs text-zinc-300 leading-relaxed italic">
              &quot;Focus on a controlled descent and an explosive push. Don&apos;t lock out your elbows.&quot;
           </p>
        </div>
      </div>
    </div>
  );
}
