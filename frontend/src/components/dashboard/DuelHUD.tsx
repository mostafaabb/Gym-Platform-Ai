"use client";

import React, { useState, useEffect } from "react";
import { Swords, Trophy, Sparkles, X } from "lucide-react";
import { Button } from "@/components/ui/Button";

interface DuelProgressProps {
  exerciseName: string;
  opponentId: number;
  userReps: number;
  opponentReps: number;
  userForm: number;
  opponentForm: number;
  onClose: () => void;
}

export function DuelHUD({
  exerciseName = "Squat Showdown",
  opponentId,
  userReps,
  opponentReps,
  userForm,
  opponentForm,
  onClose
}: DuelProgressProps) {
  return (
    <div className="w-full max-w-md rounded-2xl border border-primary/20 bg-zinc-950/70 p-5 backdrop-blur-lg shadow-2xl relative">
      <button 
        onClick={onClose}
        className="absolute top-3 right-3 text-zinc-500 hover:text-white transition-colors"
      >
        <X size={16} />
      </button>

      <div className="flex items-center justify-between mb-4">
        <span className="flex items-center gap-1.5 text-xs text-primary font-bold uppercase tracking-wider">
          <Swords size={16} className="animate-pulse" /> Live Workout Duel
        </span>
        <span className="text-xs text-zinc-500 font-semibold">{exerciseName}</span>
      </div>
      
      <div className="space-y-4">
        {/* User Progress */}
        <div>
          <div className="flex justify-between text-sm mb-1.5">
            <span className="text-white font-bold">You (Reps: {userReps})</span>
            <span className="text-primary font-extrabold">{userForm}% Form</span>
          </div>
          <div className="h-2.5 w-full rounded-full bg-zinc-900/60 overflow-hidden border border-white/5">
            <div 
              className="h-full bg-gradient-to-r from-primary to-orange-500 transition-all duration-300" 
              style={{ width: `${Math.min(100, (userReps / 15) * 100)}%` }} 
            />
          </div>
        </div>

        {/* Ghost/Challenger Progress */}
        <div>
          <div className="flex justify-between text-sm mb-1.5">
            <span className="text-zinc-400 font-bold">Ghost Challenger (Reps: {opponentReps})</span>
            <span className="text-zinc-500 font-extrabold">{opponentForm}% Form</span>
          </div>
          <div className="h-2.5 w-full rounded-full bg-zinc-900/60 overflow-hidden border border-white/5">
            <div 
              className="h-full bg-zinc-700 transition-all duration-300" 
              style={{ width: `${Math.min(100, (opponentReps / 15) * 100)}%` }} 
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export function DuelVictory({
  onClose,
  points = 150,
  formDifference = 6
}: {
  onClose: () => void;
  points?: number;
  formDifference?: number;
}) {
  return (
    <div className="flex flex-col items-center justify-center p-8 rounded-3xl border border-emerald-500/20 bg-zinc-950/90 backdrop-blur-xl max-w-sm text-center shadow-2xl relative">
      <div className="h-20 w-20 mb-6 flex items-center justify-center rounded-3xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-emerald-500/5 shadow-lg">
        <Trophy size={42} className="animate-bounce" />
      </div>
      
      <h3 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-1.5">
        <Sparkles size={24} className="text-yellow-400" />
        Match Won!
      </h3>
      
      <p className="text-zinc-400 text-sm mt-3 leading-relaxed">
        Outstanding performance! Your movement synchronization and form was +{formDifference}% higher than your challenger's.
      </p>
      
      <div className="mt-6 text-sm font-bold px-4 py-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 text-emerald-400 shadow-inner">
        +{points} Consistency Points Claimed
      </div>

      <Button 
        onClick={onClose}
        className="mt-6 w-full rounded-xl bg-zinc-900 border border-white/5 text-white hover:bg-zinc-800"
      >
        Close Screen
      </Button>
    </div>
  );
}
