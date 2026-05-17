"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  Activity, 
  Flame, 
  Clock, 
  Sparkles, 
  TrendingUp, 
  Play, 
  ChevronRight, 
  BrainCircuit, 
  Target, 
  Award,
  Swords
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
import Leaderboard from "@/components/dashboard/Leaderboard";
import BodyMap from "@/components/dashboard/BodyMap";
import { useDashboardData } from "@/hooks/useDashboardData";
import RecoveryHeatmap from "@/components/dashboard/RecoveryHeatmap";
import { DuelHUD, DuelVictory } from "@/components/dashboard/DuelHUD";


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

const RecommendedWorkout = ({ title, duration, intensity }: any) => (
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
  const { data, loading } = useDashboardData();
  
  const user = data?.user;
  const stats = data?.stats;
  const firstName = user?.first_name || "User";

  // New Live Duel states
  const [inDuel, setInDuel] = React.useState(false);
  const [duelVictory, setDuelVictory] = React.useState(false);
  const [userReps, setUserReps] = React.useState(0);
  const [opponentReps, setOpponentReps] = React.useState(0);
  
  // Injury Prediction State
  const [injuryReport, setInjuryReport] = React.useState<any>(null);
  
  React.useEffect(() => {
    fetch("http://localhost:8000/api/ai/injury-prediction/1")
      .then(res => res.json())
      .then(data => setInjuryReport(data))
      .catch(() => {
        setInjuryReport({
          injury_risk_score: 24.5,
          risk_level: "low",
          risk_factors: [],
          recommendations: ["Ensure full joint mobility pre-workout", "Increase hydration levels"]
        });
      });
  }, []);

  React.useEffect(() => {
    if (inDuel) {
      setUserReps(0);
      setOpponentReps(0);
      const interval = setInterval(() => {
        setUserReps((prev) => {
          if (prev >= 15) {
            clearInterval(interval);
            setDuelVictory(true);
            setInDuel(false);
            return 15;
          }
          return prev + 1;
        });
        setOpponentReps((prev) => Math.min(13, prev + (Math.random() > 0.4 ? 1 : 0)));
      }, 800);
      return () => clearInterval(interval);
    }
  }, [inDuel]);


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
           <Button 
             onClick={() => setInDuel(true)} 
             className="rounded-xl h-12 bg-orange-600 hover:bg-orange-500 text-white shadow-lg shadow-orange-500/20"
           >
             <Swords className="mr-2 h-4 w-4" />
             Live Workout Duel
           </Button>
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
          value={stats?.total_calories?.toLocaleString() || "2,450"} 
          trend="+12%" 
          color="text-primary"
        />
        <StatCard 
          icon={Flame} 
          label="Workouts Done" 
          value={stats?.total_workouts || "12"} 
          trend="+5%" 
          color="text-orange-500"
        />
        <StatCard 
          icon={Clock} 
          label="Training Time" 
          value={`${stats?.total_hours?.toFixed(1) || "12.5"}h`} 
          trend="+2.1h" 
          color="text-purple-500"
        />
        <StatCard 
          icon={Sparkles} 
          label="Avg. Session" 
          value={stats?.average_sessions_per_week?.toFixed(1) || "3.2"} 
          trend="+2%" 
          color="text-amber-400"
        />
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Recommended & Activity */}
        <div className="lg:col-span-2 space-y-8">
           <div className="rounded-3xl border border-white/5 bg-zinc-900/50 p-8 backdrop-blur-xl">
              <h3 className="text-xl font-bold text-white flex items-center gap-2 mb-6">
                 <Target className="text-primary" size={24} />
                 Recommended for Today
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <RecommendedWorkout title="Elite Chest Mastery" duration="45 mins" intensity="High" />
                 <RecommendedWorkout title="AI Form Corrector: Squats" duration="20 mins" intensity="Technical" />
              </div>
           </div>

           {/* Dynamic Biological Recovery Heatmap */}
           <RecoveryHeatmap memberId={1} />

           {/* Activity Chart */}
           <div className="card-premium">
            <div className="mb-8 flex items-center justify-between">
              <div>
                 <h3 className="text-xl font-bold text-white">Workout Consistency</h3>
                 <p className="text-sm text-zinc-500">Your performance over the last week</p>
              </div>
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
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#71717a', fontSize: 12 }} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#71717a', fontSize: 12 }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#09090b', border: '1px solid #ffffff10', borderRadius: '16px' }}
                    itemStyle={{ color: '#fff' }}
                  />
                  <Area type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={4} fillOpacity={1} fill="url(#colorValue)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
           </div>
        </div>

        {/* Sidebar: Leaderboard & Body Map */}
        <div className="space-y-8">
           <BodyMap 
             intensityData={{
               chest: 85,
               abs: 40,
               quads: 92,
               shoulders: 65,
               arms: 55
             }} 
           />
           
           <Leaderboard 
             entries={data?.leaderboard || [
               { rank: 1, name: "Alex Rivers", score: 1250, avg_form: 98.2 },
               { rank: 2, name: "Sarah Chen", score: 1180, avg_form: 96.5 },
               { rank: 3, name: "Mike Ross", score: 950, avg_form: 94.0 },
               { rank: 4, name: "James Wilson", score: 820, avg_form: 92.8 },
               { rank: 5, name: "Emma Watson", score: 750, avg_form: 91.5 },
             ]} 
           />

           {/* Biomechanical Injury Risk Alert */}
           {injuryReport && (
             <div className={`rounded-3xl border p-6 backdrop-blur-xl relative overflow-hidden group shadow-2xl transition-all hover:scale-[1.02] ${
               injuryReport.risk_level === "high" 
                 ? "border-rose-500/30 bg-rose-500/5 shadow-rose-500/5"
                 : injuryReport.risk_level === "moderate"
                 ? "border-amber-500/30 bg-amber-500/5 shadow-amber-500/5"
                 : "border-emerald-500/10 bg-emerald-500/5 shadow-emerald-500/5"
             }`}>
               <div className="relative z-10">
                 <div className="flex items-center gap-3 mb-4">
                   <div className={`h-10 w-10 rounded-2xl flex items-center justify-center text-white ${
                     injuryReport.risk_level === "high" 
                       ? "bg-rose-600 animate-pulse"
                       : injuryReport.risk_level === "moderate"
                       ? "bg-amber-600"
                       : "bg-emerald-600"
                   }`}>
                     <Activity size={20} />
                   </div>
                   <div>
                     <h4 className="font-bold text-white text-sm">AI Biomechanical Stress Index</h4>
                     <p className="text-[10px] text-zinc-500 font-semibold tracking-wider uppercase mt-0.5">ACWR Workload Engine</p>
                   </div>
                 </div>
                 
                 <div className="flex justify-between items-end border-b border-white/5 pb-4 mb-4">
                   <span className="text-zinc-400 text-xs">Biomechanical Risk Score</span>
                   <span className={`text-2xl font-black ${
                     injuryReport.risk_level === "high" 
                       ? "text-rose-500"
                       : injuryReport.risk_level === "moderate"
                       ? "text-amber-500"
                       : "text-emerald-500"
                   }`}>{injuryReport.injury_risk_score} / 100</span>
                 </div>

                 {injuryReport.risk_factors && injuryReport.risk_factors.length > 0 && (
                   <div className="mb-4">
                     <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider mb-2">Key Risk Factors</p>
                     <ul className="space-y-1">
                       {injuryReport.risk_factors.map((factor: string, index: number) => (
                         <li key={index} className="text-xs text-rose-400 flex items-center gap-1">
                           • {factor}
                         </li>
                       ))}
                     </ul>
                   </div>
                 )}

                 {injuryReport.recommendations && injuryReport.recommendations.length > 0 && (
                   <div>
                     <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider mb-2">Recovery Recommendations</p>
                     <ul className="space-y-1">
                       {injuryReport.recommendations.map((rec: string, index: number) => (
                         <li key={index} className="text-xs text-zinc-300 flex items-center gap-1.5">
                           ✔ {rec}
                         </li>
                       ))}
                     </ul>
                   </div>
                 )}
               </div>
             </div>
           )}

           {/* AI Coach Suggestion */}
           <div className="rounded-3xl border border-primary/30 bg-primary/5 p-8 backdrop-blur-xl relative overflow-hidden group shadow-2xl shadow-primary/10">
             <div className="absolute -top-10 -right-10 h-40 w-40 bg-primary/20 blur-[80px] rounded-full" />
             <div className="relative z-10">
                <div className="flex items-center gap-3 mb-4">
                   <div className="h-10 w-10 rounded-2xl bg-primary flex items-center justify-center text-white">
                      <BrainCircuit size={20} />
                   </div>
                   <h4 className="font-bold text-white">AI Coach Tip</h4>
                </div>
                <p className="text-sm text-zinc-300 leading-relaxed italic">
                   &quot;Your left shoulder is slightly dropping on bench press reps. Focus on symmetry and engaging your lats more during the descent.&quot;
                </p>
                <div className="mt-6 pt-6 border-t border-white/5">
                   <Button variant="ghost" className="w-full text-xs text-primary hover:bg-primary/10">View Detailed Form Analysis</Button>
                </div>
             </div>
           </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-8">
              <div>
                 <h3 className="text-xl font-bold text-white">Recent Training History</h3>
                 <p className="text-sm text-zinc-500">Your last 3 gym sessions</p>
              </div>
              <Link href="/dashboard/member/analytics">
                <Button variant="outline" className="rounded-xl border-white/10 text-xs px-4 h-9 hover:bg-white/5 transition-colors">View Full History</Button>
              </Link>
            </div>
            <div className="space-y-4">
              {[
                { name: "Full Body Blast", date: "Yesterday, 6:30 PM", calories: "640 kcal", duration: "55m", score: "92" },
                { name: "Morning Yoga", date: "Oct 12, 8:00 AM", calories: "210 kcal", duration: "30m", score: "98" },
                { name: "Leg Power Drills", date: "Oct 10, 5:15 PM", calories: "780 kcal", duration: "70m", score: "85" },
              ].map((workout, i) => (
                <div key={i} className="flex items-center justify-between rounded-2xl p-5 transition-all hover:bg-white/5 group border border-transparent hover:border-white/5 cursor-pointer">
                  <div className="flex items-center gap-5">
                      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-800 text-zinc-400 group-hover:bg-primary group-hover:text-white transition-all duration-300">
                        <Activity size={22} />
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

      {/* Real-time Duel HUD Overlay */}
      {inDuel && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-md p-4">
          <DuelHUD
            exerciseName="Squat Duel Challenge"
            opponentId={2}
            userReps={userReps}
            opponentReps={opponentReps}
            userForm={94}
            opponentForm={88}
            onClose={() => setInDuel(false)}
          />
        </div>
      )}

      {/* Duel Victory Overlay */}
      {duelVictory && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-lg p-4">
          <DuelVictory
            onClose={() => setDuelVictory(false)}
            points={150}
            formDifference={6}
          />
        </div>
      )}
    </div>
  );
}
