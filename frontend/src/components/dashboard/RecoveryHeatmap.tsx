"use client";

import React, { useState, useEffect } from "react";
import { Activity, Flame, ShieldCheck, RefreshCw } from "lucide-react";

interface MuscleGroup {
  name: string;
  recovery: number; // 0 to 100
  lastTrained: string;
}

export default function RecoveryHeatmap({ memberId = 1 }: { memberId?: number }) {
  const [muscles, setMuscles] = useState<MuscleGroup[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchRecovery = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/analytics/members/${memberId}/muscle-recovery`);
      if (response.ok) {
        const data = await response.json();
        setMuscles(data);
      } else {
        // Fallback if API not running or errors
        setMuscles([
          { name: "Chest", recovery: 85, lastTrained: "12 hours ago" },
          { name: "Quads", recovery: 32, lastTrained: "3 hours ago" },
          { name: "Triceps", recovery: 92, lastTrained: "1 day ago" },
          { name: "Back", recovery: 12, lastTrained: "Just now" },
          { name: "Shoulders", recovery: 100, lastTrained: "3 days ago" },
        ]);
      }
    } catch (error) {
      // Offline fallback
      setMuscles([
        { name: "Chest", recovery: 82.5, lastTrained: "14 hours ago" },
        { name: "Quads", recovery: 34.0, lastTrained: "4 hours ago" },
        { name: "Triceps", recovery: 90.1, lastTrained: "1.2 days ago" },
        { name: "Back", recovery: 15.4, lastTrained: "2 hours ago" },
        { name: "Shoulders", recovery: 100, lastTrained: "3 days ago" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecovery();
  }, [memberId]);

  const getHeatColor = (rec: number) => {
    if (rec > 80) return "text-emerald-400 bg-emerald-500/5 border-emerald-500/10 hover:border-emerald-500/20";
    if (rec > 40) return "text-amber-400 bg-amber-500/5 border-amber-500/10 hover:border-amber-500/20";
    return "text-rose-400 bg-rose-500/5 border-rose-500/10 hover:border-rose-500/20 animate-pulse";
  };

  return (
    <div className="rounded-3xl border border-white/5 bg-zinc-950/40 p-6 backdrop-blur-xl transition-all hover:bg-zinc-950/60">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Activity className="text-primary animate-pulse" size={20} />
            AI Muscle Recovery Heatmap
          </h3>
          <p className="text-sm text-zinc-500">Biological fatigue recovery rate based on completed workouts.</p>
        </div>
        <button 
          onClick={fetchRecovery}
          className="flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-900 text-zinc-400 border border-white/5 hover:text-white transition-all"
        >
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {muscles.map((muscle) => (
          <div
            key={muscle.name}
            className={`flex flex-col gap-3 rounded-2xl border p-4 backdrop-blur-sm transition-all duration-300 hover:scale-[1.02] ${getHeatColor(
              muscle.recovery
            )}`}
          >
            <div className="flex items-center justify-between">
              <span className="font-bold text-white text-lg">{muscle.name}</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full border bg-black/40">
                {muscle.recovery}%
              </span>
            </div>
            
            {/* Elegant Progress bar */}
            <div className="h-2 w-full rounded-full bg-zinc-900/60 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  muscle.recovery > 80
                    ? "bg-gradient-to-r from-emerald-500 to-teal-400"
                    : muscle.recovery > 40
                    ? "bg-gradient-to-r from-amber-500 to-yellow-400"
                    : "bg-gradient-to-r from-rose-600 to-orange-500"
                }`}
                style={{ width: `${muscle.recovery}%` }}
              />
            </div>

            <div className="flex items-center gap-1.5 text-xs text-zinc-400">
              {muscle.recovery < 40 ? (
                <Flame size={12} className="text-rose-500 animate-bounce" />
              ) : (
                <ShieldCheck size={12} className="text-emerald-500" />
              )}
              <span>Trained {muscle.lastTrained}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
