import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface BodyMapProps {
  intensityData: Record<string, number>;
  className?: string;
}

const BodyMap: React.FC<BodyMapProps> = ({ intensityData, className }) => {
  const muscles = [
    { id: "chest", label: "Chest", cx: 100, cy: 80, r: 15 },
    { id: "abs", label: "Abs", cx: 100, cy: 120, r: 12 },
    { id: "quads", label: "Quads", cx: 85, cy: 180, r: 18 },
    { id: "shoulders", label: "Shoulders", cx: 70, cy: 75, r: 10 },
    { id: "arms", label: "Arms", cx: 60, cy: 110, r: 10 },
  ];

  return (
    <div className={cn("relative bg-zinc-950/50 rounded-3xl border border-white/5 p-6 backdrop-blur-xl overflow-hidden", className)}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm font-bold uppercase tracking-widest text-zinc-500">Volume Distribution</h3>
        <div className="flex items-center gap-1">
          <div className="h-2 w-2 rounded-full bg-primary" />
          <span className="text-[10px] text-zinc-400 font-bold uppercase">Live Map</span>
        </div>
      </div>

      <div className="relative h-[300px] flex items-center justify-center">
        <svg viewBox="0 0 200 300" className="h-full w-auto">
          <circle cx="100" cy="40" r="15" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="2" />
          <path d="M70,60 L130,60 L120,150 L80,150 Z" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="2" />
          <path d="M80,150 L70,280 M120,150 L130,280" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="2" />
          <path d="M70,70 L40,140 M130,70 L160,140" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="2" />

          {muscles.map((muscle) => {
            const intensity = intensityData[muscle.id] || 0;
            return (
              <motion.circle
                key={muscle.id}
                cx={muscle.cx}
                cy={muscle.cy}
                r={muscle.r}
                initial={{ fill: "rgba(255,255,255,0.05)" }}
                animate={{ 
                  fill: intensity > 0 ? "rgba(59, 130, 246, 0.4)" : "rgba(255,255,255,0.05)",
                  stroke: intensity > 0 ? "#3b82f6" : "rgba(255,255,255,0.1)"
                }}
                whileHover={{ scale: 1.2, fill: "rgba(59, 130, 246, 0.6)" }}
                className="cursor-pointer transition-colors"
                strokeWidth="1.5"
              />
            );
          })}
        </svg>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2">
         {muscles.map((m) => (
           <div key={m.id} className="flex items-center justify-between p-2 rounded-xl bg-white/5 border border-white/5">
              <span className="text-[10px] text-zinc-500 font-bold uppercase">{m.label}</span>
              <span className="text-[10px] text-white font-black">{intensityData[m.id] || 0}%</span>
           </div>
         ))}
      </div>
    </div>
  );
};

export default BodyMap;
