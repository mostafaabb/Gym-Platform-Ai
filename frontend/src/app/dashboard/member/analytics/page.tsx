"use client";

import React from "react";
import { motion } from "framer-motion";
import { TrendingUp, BarChart2, PieChart, Download } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function AnalyticsPage() {
  return (
    <div className="space-y-8">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Performance Analytics</h1>
          <p className="text-zinc-500">Visualize your progress and optimize your performance.</p>
        </div>
        <Button variant="outline" className="rounded-xl border-white/5 bg-zinc-900/50 text-white">
          <Download className="mr-2 h-4 w-4" />
          Export Data
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
           <BarChart2 className="text-primary mb-4" size={24} />
           <h3 className="font-semibold text-white">Strength Volume</h3>
           <p className="mt-2 text-2xl font-bold text-white">12,450 kg</p>
           <p className="text-xs text-emerald-400 mt-1">+15% from last week</p>
        </div>
        <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
           <TrendingUp className="text-purple-500 mb-4" size={24} />
           <h3 className="font-semibold text-white">Consistency Score</h3>
           <p className="mt-2 text-2xl font-bold text-white">92%</p>
           <p className="text-xs text-emerald-400 mt-1">Perfect streak: 12 days</p>
        </div>
        <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
           <PieChart className="text-orange-500 mb-4" size={24} />
           <h3 className="font-semibold text-white">Fat Loss Progress</h3>
           <p className="mt-2 text-2xl font-bold text-white">-2.4 kg</p>
           <p className="text-xs text-zinc-500 mt-1">Target: -5.0 kg</p>
        </div>
      </div>

      <div className="rounded-3xl border border-white/5 bg-zinc-900/20 py-32 text-center backdrop-blur-xl">
        <h3 className="text-xl font-semibold text-white">AI Advanced Analysis</h3>
        <p className="mt-2 text-zinc-500">Connecting to GymFlow AI for deeper insights...</p>
      </div>
    </div>
  );
}
