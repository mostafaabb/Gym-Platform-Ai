"use client";

import React from "react";
import Link from "next/link";
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
import api from "@/lib/api";

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
    <div className="card-premium h-full">
      <div className="flex items-center justify-between">
        <div className={`flex h-12 w-12 items-center justify-center rounded-xl bg-white/5 border border-white/5 ${color} transition-transform hover:scale-110 duration-300`}>
          <Icon size={24} />
        </div>
        <div className="flex items-center gap-1 text-xs font-bold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full">
          <TrendingUp size={12} />
          {trend}
        </div>
      </div>
      <div className="mt-5">
        <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">{label}</p>
        <p className="text-3xl font-bold text-white mt-1">{value}</p>
      </div>
    </div>
  </motion.div>
);

const RecommendedWorkout = ({ title, duration, intensity, image }: any) => (
  <div className="group relative flex items-center gap-4 rounded-2xl border border-white/5 bg-white/5 p-4 transition-all hover:bg-white/10 hover:translate-x-1 cursor-pointer">
    <div className="h-16 w-16 overflow-hidden rounded-xl bg-zinc-800 border border-white/5 flex items-center justify-center text-zinc-500 group-hover:text-primary transition-colors">
       <Play size={24} className="fill-current" />
    </div>
    <div className="flex-1">
      <h4 className="font-bold text-white group-hover:text-primary transition-colors">{title}</h4>
      <p className="text-xs text-zinc-500 mt-0.5">{duration} • {intensity}</p>
    </div>
    <Button size="sm" variant="ghost" className="rounded-full text-zinc-600 group-hover:text-primary group-hover:bg-primary/10">
      <ChevronRight size={18} />
    </Button>
  </div>
);

export default function MemberDashboard() {
  const [userData, setUserData] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await api.get("/auth/me");
        setUserData(response.data.user);
      } catch (err) {
        console.error("Failed to fetch user:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  const firstName = userData?.first_name || "User";

  return (
    <div className="space-y-10 pb-10">
      {/* Welcome Header */}
      <div className="flex flex-col justify-between gap-6 md:flex-row md:items-center">
        <div>
          <h1 className="text-4xl font-bold text-white tracking-tight">
            {loading ? "Loading..." : `Welcome back, ${firstName}! 👋`}
          </h1>
          <p className="text-zinc-400 mt-1">You&apos;re <span className="text-primary font-bold">3 workouts</span> away from your weekly goal.</p>
        </div>
        <div className="flex gap-4">
           <Link href="/dashboard/member/workouts">
             <Button className="btn-primary h-12 shadow-primary/40">
               <Play className="mr-2 h-4 w-4 fill-current" />
               Start Workout
             </Button>
           </Link>
           <Link href="/dashboard/member/coach">
             <Button variant="outline" className="h-12 rounded-xl border-white/10 bg-white/5 text-white hover:bg-white/10 backdrop-blur-md">
               <BrainCircuit className="mr-2 h-4 w-4 text-primary" />
               Ask AI Coach
             </Button>
           </Link>
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
        <div className="lg:col-span-2 card-premium">
          <div className="mb-8 flex items-center justify-between">
            <div>
               <h3 className="text-xl font-bold text-white">Workout Consistency</h3>
               <p className="text-sm text-zinc-500">Your performance over the last week</p>
            </div>
            <select className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-zinc-400 outline-none focus:border-primary/50">
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
            </select>
          </div>
          <div className="h-[320px] w-full">
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
                  contentStyle={{ backgroundColor: '#09090b', border: '1px solid #ffffff10', borderRadius: '16px', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#3b82f6" 
                  strokeWidth={4}
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
          <div className="rounded-3xl border border-primary/30 bg-primary/5 p-8 backdrop-blur-xl relative overflow-hidden group shadow-2xl shadow-primary/10">
            <div className="absolute -top-10 -right-10 h-40 w-40 bg-primary/20 blur-[80px] rounded-full" />
            <div className="relative">
               <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary shadow-xl shadow-primary/20 mb-6">
                  <BrainCircuit className="text-white" size={24} />
               </div>
               <h3 className="text-xl font-bold text-white tracking-tight">AI Daily Insight</h3>
               <p className="mt-4 text-sm leading-relaxed text-zinc-300">
                 &quot;{firstName}, your recovery score is high (88%). Today is perfect for a high-intensity chest session. Should I prepare your routine?&quot;
               </p>
               <div className="mt-8 flex gap-3">
                  <Button className="flex-1 btn-primary text-sm h-11">
                     Let&apos;s go
                  </Button>
                  <Button variant="ghost" className="flex-1 rounded-xl text-zinc-400 hover:text-white hover:bg-white/5 text-sm h-11">
                     Skip
                  </Button>
               </div>
            </div>
          </div>

          {/* Recommended Workouts */}
          <div className="card-premium">
            <div className="flex items-center justify-between mb-6">
               <h3 className="text-sm font-bold uppercase tracking-widest text-zinc-500">Recommended</h3>
               <Sparkles className="text-primary animate-pulse" size={18} />
            </div>
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
            <Link href="/dashboard/member/workouts">
              <Button variant="ghost" className="mt-6 w-full text-sm text-primary hover:bg-primary/5 group">
                View All Routines
                <ArrowUpRight className="ml-2 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" size={16} />
              </Button>
            </Link>
          </div>
        </div>
      </div>
      
      {/* Bottom Row - Recent Activity */}
      <div className="card-premium">
         <div className="mb-8 flex items-center justify-between">
            <div>
               <h3 className="text-xl font-bold text-white">Recent Training History</h3>
               <p className="text-sm text-zinc-500">Your last 3 gym sessions</p>
            </div>
            <Link href="/dashboard/member/analytics">
              <Button variant="outline" className="rounded-xl border-white/10 text-xs px-4 h-9 hover:bg-white/5 transition-colors">View Full History</Button>
            </Link>
         </div>
         <div className="space-y-2">
            {[
              { name: "Full Body Blast", date: "Yesterday, 6:30 PM", calories: "640 kcal", duration: "55m", score: "92" },
              { name: "Morning Yoga", date: "Oct 12, 8:00 AM", calories: "210 kcal", duration: "30m", score: "98" },
              { name: "Leg Power Drills", date: "Oct 10, 5:15 PM", calories: "780 kcal", duration: "70m", score: "85" },
            ].map((workout, i) => (
              <div key={i} className="flex items-center justify-between rounded-2xl p-5 transition-all hover:bg-white/5 group border border-transparent hover:border-white/5 cursor-pointer">
                 <div className="flex items-center gap-5">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-800 text-zinc-400 group-hover:bg-primary group-hover:text-white transition-all duration-300">
                       <Dumbbell size={22} />
                    </div>
                    <div>
                       <p className="font-bold text-white group-hover:text-primary transition-colors">{workout.name}</p>
                       <p className="text-xs text-zinc-500 mt-0.5">{workout.date}</p>
                    </div>
                 </div>
                 <div className="flex items-center gap-12">
                    <div className="hidden text-right md:block">
                       <p className="text-sm font-bold text-zinc-300">{workout.calories}</p>
                       <p className="text-[10px] text-zinc-500 uppercase tracking-widest mt-0.5">Energy</p>
                    </div>
                    <div className="hidden text-right md:block">
                       <p className="text-sm font-bold text-zinc-300">{workout.duration}</p>
                       <p className="text-[10px] text-zinc-500 uppercase tracking-widest mt-0.5">Time</p>
                    </div>
                    <div className="text-right bg-emerald-400/10 px-4 py-2 rounded-xl border border-emerald-400/20">
                       <p className="text-sm font-black text-emerald-400">{workout.score}%</p>
                       <p className="text-[10px] text-zinc-500 uppercase tracking-widest mt-0.5">Score</p>
                    </div>
                 </div>
              </div>
            ))}
         </div>
      </div>
    </div>
  );
}
