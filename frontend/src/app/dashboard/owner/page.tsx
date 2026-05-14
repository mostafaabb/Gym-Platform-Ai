"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  BarChart3, 
  Users, 
  TrendingUp, 
  DollarSign, 
  ArrowUpRight, 
  ArrowDownRight,
  MoreHorizontal,
  Building2,
  Calendar,
  PieChart,
  UserCheck,
  Zap
} from "lucide-react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from "recharts";
import { Button } from "@/components/ui/Button";

const revenueData = [
  { name: "Jan", total: 4200 },
  { name: "Feb", total: 3800 },
  { name: "Mar", total: 5100 },
  { name: "Apr", total: 4800 },
  { name: "May", total: 6200 },
  { name: "Jun", total: 7500 },
];

const gymUtilization = [
  { time: "6am", users: 45 },
  { time: "9am", users: 80 },
  { time: "12pm", users: 30 },
  { time: "3pm", users: 55 },
  { time: "6pm", users: 120 },
  { time: "9pm", users: 40 },
];

const SummaryCard = ({ icon: Icon, label, value, trend, isPositive }: any) => (
  <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
    <div className="flex items-center justify-between mb-4">
      <div className="h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center text-zinc-400">
        <Icon size={20} />
      </div>
      <div className={cn(
        "flex items-center gap-1 text-xs font-bold",
        isPositive ? "text-emerald-500" : "text-red-500"
      )}>
        {isPositive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
        {trend}
      </div>
    </div>
    <p className="text-xs font-medium text-zinc-500 uppercase tracking-widest">{label}</p>
    <h3 className="text-2xl font-bold text-white mt-1">{value}</h3>
  </div>
);

export default function OwnerDashboard() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div className="flex items-center gap-4">
           <div className="h-14 w-14 rounded-2xl bg-primary flex items-center justify-center text-white shadow-2xl shadow-primary/20">
              <Building2 size={32} />
           </div>
           <div>
              <h1 className="text-3xl font-bold text-white tracking-tight">Iron Paradise</h1>
              <p className="text-zinc-500">Gym Management & Business Intelligence</p>
           </div>
        </div>
        <div className="flex gap-3">
           <Button variant="outline" className="rounded-xl border-white/10 bg-zinc-900/50 text-white">
             <Calendar className="mr-2 h-4 w-4" />
             Last 30 Days
           </Button>
           <Button className="rounded-xl bg-white text-black hover:bg-zinc-200">
             <Zap className="mr-2 h-4 w-4 fill-current" />
             AI Business Insights
           </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <SummaryCard 
          icon={DollarSign} 
          label="Monthly Revenue" 
          value="$12,450" 
          trend="+15.2%" 
          isPositive={true} 
        />
        <SummaryCard 
          icon={Users} 
          label="Active Members" 
          value="1,248" 
          trend="+4.3%" 
          isPositive={true} 
        />
        <SummaryCard 
          icon={TrendingUp} 
          label="Retention Rate" 
          value="94.2%" 
          trend="-0.8%" 
          isPositive={false} 
        />
        <SummaryCard 
          icon={UserCheck} 
          label="Staff Efficiency" 
          value="88%" 
          trend="+2.1%" 
          isPositive={true} 
        />
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Revenue Chart */}
        <div className="lg:col-span-2 rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
           <div className="flex items-center justify-between mb-8">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                 <BarChart3 className="text-primary" size={20} />
                 Revenue Performance
              </h3>
              <Button variant="ghost" size="sm" className="text-zinc-500">
                 <MoreHorizontal size={20} />
              </Button>
           </div>
           <div className="h-[350px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                 <BarChart data={revenueData}>
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
                      cursor={{ fill: '#ffffff05' }}
                      contentStyle={{ backgroundColor: '#18181b', border: '1px solid #ffffff10', borderRadius: '12px' }}
                    />
                    <Bar dataKey="total" radius={[6, 6, 0, 0]}>
                       {revenueData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={index === revenueData.length - 1 ? '#3b82f6' : '#27272a'} />
                       ))}
                    </Bar>
                 </BarChart>
              </ResponsiveContainer>
           </div>
        </div>

        {/* Gym Utilization / Peak Hours */}
        <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
           <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
              <PieChart className="text-purple-500" size={20} />
              Peak Utilization
           </h3>
           <div className="space-y-6">
              {gymUtilization.map((item, i) => (
                <div key={i} className="space-y-2">
                   <div className="flex items-center justify-between text-xs font-bold">
                      <span className="text-zinc-400">{item.time}</span>
                      <span className={cn(
                        item.users > 100 ? "text-red-500" : "text-zinc-300"
                      )}>{item.users} members</span>
                   </div>
                   <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
                      <motion.div 
                        initial={{ width: 0 }}
                        animate={{ width: `${(item.users / 150) * 100}%` }}
                      >
                        <div className={cn(
                          "h-full rounded-full",
                          item.users > 100 ? "bg-red-500" : "bg-primary"
                        )} />
                      </motion.div>
                   </div>
                </div>
              ))}
           </div>
           <div className="mt-8 p-4 rounded-xl bg-primary/5 border border-primary/10">
              <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">AI Insight</p>
              <p className="text-xs text-zinc-300 mt-2 leading-relaxed">
                 Peak hours are shifting towards 6pm. Consider adding another trainer or HIIT class during this window to optimize throughput.
              </p>
           </div>
        </div>
      </div>

      {/* Trainer Performance */}
      <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
         <div className="flex items-center justify-between mb-8">
            <h3 className="text-lg font-bold text-white">Trainer Performance</h3>
            <Button variant="ghost" className="text-xs text-primary">View Full Report</Button>
         </div>
         <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { name: "Mark Peterson", clients: 42, rating: 4.9, sessions: 156 },
              { name: "Sarah Connor", clients: 38, rating: 4.8, sessions: 142 },
              { name: "James Bond", clients: 25, rating: 4.5, sessions: 98 },
            ].map((trainer, i) => (
              <div key={i} className="p-4 rounded-2xl border border-white/5 bg-white/5 group hover:bg-white/10 transition-colors">
                 <div className="flex items-center gap-3 mb-4">
                    <div className="h-10 w-10 rounded-full bg-zinc-800" />
                    <div>
                       <p className="text-sm font-bold text-white">{trainer.name}</p>
                       <p className="text-xs text-zinc-500">Senior Trainer</p>
                    </div>
                 </div>
                 <div className="grid grid-cols-3 gap-2">
                    <div className="text-center">
                       <p className="text-xs font-bold text-white">{trainer.clients}</p>
                       <p className="text-[9px] text-zinc-500 uppercase">Clients</p>
                    </div>
                    <div className="text-center">
                       <p className="text-xs font-bold text-white">{trainer.rating}</p>
                       <p className="text-[9px] text-zinc-500 uppercase">Rating</p>
                    </div>
                    <div className="text-center">
                       <p className="text-xs font-bold text-white">{trainer.sessions}</p>
                       <p className="text-[9px] text-zinc-500 uppercase">Sessions</p>
                    </div>
                 </div>
              </div>
            ))}
         </div>
      </div>
    </div>
  );
}
