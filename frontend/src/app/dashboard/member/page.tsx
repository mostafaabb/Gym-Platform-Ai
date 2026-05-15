"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  Activity, 
  Flame, 
  TrendingUp, 
  Clock, 
  ChevronRight,
  Sparkles,
  Play,
  ArrowUpRight,
  BrainCircuit,
  Dumbbell,
  MessageSquare
} from "lucide-react";
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from "recharts";
import { Button } from "@/components/ui/Button";

const activityData = [
  { name: "Mon", value: 45 },
  { name: "Tue", value: 52 },
  { name: "Wed", value: 38 },
  { name: "Thu", value: 65 },
  { name: "Fri", value: 48 },
  { name: "Sat", value: 72 },
  { name: "Sun", value: 58 },
];

const StatCard = ({ icon: Icon, label, value, trend, color }: any) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
  >
    <div className="relative overflow-hidden rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm transition-all hover:bg-zinc-900">
      <div className="flex items-center justify-between">
        <div className={`flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-800 ${color}`}>
          <Icon size={20} />
        </div>
        <div className="flex items-center gap-1 text-xs font-medium text-emerald-400">
          <TrendingUp size={12} />
          {trend}
        </div>
      </div>
      <div className="mt-4">
        <p className="text-sm text-zinc-500">{label}</p>
        <p className="text-2xl font-bold text-white">{value}</p>
      </div>
    </div>
  </motion.div>
);

const RecommendedWorkout = ({ title, duration, intensity, image }: any) => (
  <div className="group relative flex items-center gap-4 rounded-xl border border-white/5 bg-zinc-900/30 p-4 transition-all hover:bg-zinc-900/80">
    <div className="h-16 w-16 overflow-hidden rounded-lg bg-zinc-800">
       <div className="flex h-full w-full items-center justify-center text-zinc-600">
         <Play size={24} />
       </div>
    </div>
    <div className="flex-1">
      <h4 className="font-medium text-white">{title}</h4>
      <p className="text-xs text-zinc-500">{duration} • {intensity}</p>
    </div>
    <Button size="sm" variant="ghost" className="rounded-full text-zinc-500 group-hover:text-primary">
      <ChevronRight size={18} />
    </Button>
  </div>
);

export default function MemberDashboard() {
  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Welcome back, Felix! 👋</h1>
          <p className="text-zinc-500">You&apos;re 3 workouts away from your weekly goal.</p>
        </div>
        <div className="flex gap-3">
           <Button className="rounded-xl bg-white text-black hover:bg-zinc-200">
             <Play className="mr-2 h-4 w-4 fill-current" />
             Start Workout
           </Button>
           <Button variant="outline" className="rounded-xl border-white/10 bg-zinc-900/50 text-white backdrop-blur-md hover:bg-white/10">
             <BrainCircuit className="mr-2 h-4 w-4" />
             Ask AI
           </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard 
          icon={Activity} 
          label="Calories Burned" 
          value="2,450" 
          trend="+12%" 
          color="text-primary"
        />
        <StatCard 
          icon={Flame} 
          label="Avg. Intensity" 
          value="85%" 
          trend="+5%" 
          color="text-orange-500"
        />
        <StatCard 
          icon={Clock} 
          label="Training Time" 
          value="12.5h" 
          trend="+2.1h" 
          color="text-purple-500"
        />
        <StatCard 
          icon={Sparkles} 
          label="Form Score" 
          value="94/100" 
          trend="+2%" 
          color="text-amber-400"
        />
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Activity Chart */}
        <div className="lg:col-span-2 rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
          <div className="mb-6 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Workout Consistency</h3>
            <select className="bg-transparent text-xs text-zinc-500 outline-none">
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
            </select>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff05" />
                <XAxis 
                  dataKey="name" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#71717a', fontSize: 12 }}
                  dy={10}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#71717a', fontSize: 12 }}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#18181b', border: '1px solid #ffffff10', borderRadius: '12px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#3b82f6" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorValue)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sidebar Cards */}
        <div className="space-y-6">
          {/* AI Coach Suggestion */}
          <div className="rounded-2xl border border-primary/20 bg-primary/5 p-6 backdrop-blur-sm relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4">
               <Sparkles className="text-primary animate-pulse" size={24} />
            </div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              AI Insight
            </h3>
            <p className="mt-3 text-sm leading-relaxed text-zinc-300">
              &quot;Felix, your recovery score is high (88%). Today is perfect for a high-intensity chest session. Should I prepare your routine?&quot;
            </p>
            <div className="mt-6 flex gap-2">
               <Button className="flex-1 rounded-xl bg-primary text-white hover:bg-primary/90 text-sm">
                  Let&apos;s go
               </Button>
               <Button variant="ghost" className="flex-1 rounded-xl text-zinc-400 hover:text-white text-sm">
                  Not now
               </Button>
            </div>
          </div>

          {/* Recommended Workouts */}
          <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
            <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-zinc-500">Recommended for You</h3>
            <div className="space-y-4">
              <RecommendedWorkout 
                title="Hypertrophy Chest" 
                duration="45m" 
                intensity="High"
              />
              <RecommendedWorkout 
                title="Active Recovery" 
                duration="20m" 
                intensity="Low"
              />
              <RecommendedWorkout 
                title="Deadlift Focus" 
                duration="60m" 
                intensity="Extreme"
              />
            </div>
            <Button variant="ghost" className="mt-4 w-full text-xs text-primary">
              View All Workouts
              <ArrowUpRight className="ml-1" size={14} />
            </Button>
          </div>
        </div>
      </div>
      
      {/* Bottom Row - Recent Activity */}
      <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
         <h3 className="mb-6 text-lg font-semibold text-white">Recent Workouts</h3>
         <div className="space-y-1">
            {[
              { name: "Full Body Blast", date: "Yesterday, 6:30 PM", calories: "640 kcal", duration: "55m", score: "92" },
              { name: "Morning Yoga", date: "Oct 12, 8:00 AM", calories: "210 kcal", duration: "30m", score: "98" },
              { name: "Leg Power Drills", date: "Oct 10, 5:15 PM", calories: "780 kcal", duration: "70m", score: "85" },
            ].map((workout, i) => (
              <div key={i} className="flex items-center justify-between rounded-xl p-4 transition-colors hover:bg-white/5">
                 <div className="flex items-center gap-4">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-zinc-800 text-zinc-400">
                       <Dumbbell size={18} />
                    </div>
                    <div>
                       <p className="font-medium text-white">{workout.name}</p>
                       <p className="text-xs text-zinc-500">{workout.date}</p>
                    </div>
                 </div>
                 <div className="flex items-center gap-8">
                    <div className="hidden text-right md:block">
                       <p className="text-sm font-medium text-zinc-300">{workout.calories}</p>
                       <p className="text-[10px] text-zinc-500 uppercase tracking-widest">Calories</p>
                    </div>
                    <div className="hidden text-right md:block">
                       <p className="text-sm font-medium text-zinc-300">{workout.duration}</p>
                       <p className="text-[10px] text-zinc-500 uppercase tracking-widest">Duration</p>
                    </div>
                    <div className="text-right">
                       <p className="text-sm font-bold text-emerald-400">{workout.score}%</p>
                       <p className="text-[10px] text-zinc-500 uppercase tracking-widest">Form</p>
                    </div>
                 </div>
              </div>
            ))}
         </div>
      </div>
    </div>
  );
}
