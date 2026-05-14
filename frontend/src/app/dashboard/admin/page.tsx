"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  Shield, 
  Building2, 
  Users, 
  Server, 
  Globe, 
  Activity, 
  Search,
  MoreVertical,
  Plus,
  CreditCard,
  AlertTriangle,
  ChevronRight
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

const platformMetrics = [
  { label: "Total Gyms", value: "1,240", icon: Building2, color: "text-blue-500" },
  { label: "Total Users", value: "854k", icon: Users, color: "text-purple-500" },
  { label: "System Health", value: "99.9%", icon: Server, color: "text-emerald-500" },
  { label: "ARR", value: "$4.2M", icon: CreditCard, color: "text-amber-500" },
];

const gymInstances = [
  { name: "Iron Paradise", owner: "Dwayne Johnson", plan: "Enterprise", status: "Active", users: 1248 },
  { name: "Gold's Gym HQ", owner: "Joe Gold", plan: "Enterprise", status: "Active", users: 5620 },
  { name: "Muscle Beach", owner: "Arnold S.", plan: "Basic", status: "Active", users: 432 },
  { name: "Local Box", owner: "John Doe", plan: "Free", status: "Past Due", users: 85 },
];

export default function AdminDashboard() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div className="flex items-center gap-4">
           <div className="h-14 w-14 rounded-2xl bg-zinc-900 border border-white/10 flex items-center justify-center text-primary shadow-2xl shadow-primary/10">
              <Shield size={32} />
           </div>
           <div>
              <h1 className="text-3xl font-bold text-white tracking-tight">System Admin</h1>
              <p className="text-zinc-500">Platform-wide control and instance management.</p>
           </div>
        </div>
        <div className="flex gap-3">
           <Button className="rounded-xl bg-white text-black hover:bg-zinc-200">
             <Plus className="mr-2 h-4 w-4" />
             Register Gym
           </Button>
        </div>
      </div>

      {/* Grid Summary */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
         {platformMetrics.map((metric, i) => (
           <div key={i} className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-4">
                 <div className={cn("h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center", metric.color)}>
                    <metric.icon size={20} />
                 </div>
              </div>
              <p className="text-xs font-medium text-zinc-500 uppercase tracking-widest">{metric.label}</p>
              <h3 className="text-2xl font-bold text-white mt-1">{metric.value}</h3>
           </div>
         ))}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
         {/* Gym Instances Table */}
         <div className="lg:col-span-2 rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-8">
               <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Building2 size={20} className="text-zinc-500" />
                  Gym Instances
               </h3>
               <div className="relative">
                  <Search size={16} className="absolute left-3 top-2.5 text-zinc-500" />
                  <input 
                    placeholder="Search instances..."
                    className="bg-white/5 border border-white/10 rounded-xl py-2 pl-9 pr-4 text-xs outline-none focus:border-primary/50 text-white"
                  />
               </div>
            </div>
            
            <div className="overflow-x-auto">
               <table className="w-full text-left text-sm">
                  <thead>
                     <tr className="text-zinc-500 border-b border-white/5">
                        <th className="pb-4 font-semibold uppercase tracking-wider text-[10px]">Gym Name</th>
                        <th className="pb-4 font-semibold uppercase tracking-wider text-[10px]">Owner</th>
                        <th className="pb-4 font-semibold uppercase tracking-wider text-[10px]">Plan</th>
                        <th className="pb-4 font-semibold uppercase tracking-wider text-[10px]">Status</th>
                        <th className="pb-4 font-semibold uppercase tracking-wider text-[10px] text-right">Users</th>
                        <th className="pb-4"></th>
                     </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                     {gymInstances.map((gym, i) => (
                       <tr key={i} className="group hover:bg-white/5 transition-colors">
                          <td className="py-4 font-medium text-white">{gym.name}</td>
                          <td className="py-4 text-zinc-400">{gym.owner}</td>
                          <td className="py-4">
                             <span className="px-2 py-1 rounded-md bg-white/5 text-[10px] font-bold text-zinc-300">
                                {gym.plan}
                             </span>
                          </td>
                          <td className="py-4">
                             <div className="flex items-center gap-2">
                                <span className={cn(
                                  "h-1.5 w-1.5 rounded-full",
                                  gym.status === "Active" ? "bg-emerald-500" : "bg-red-500"
                                )} />
                                <span className="text-xs text-zinc-400">{gym.status}</span>
                             </div>
                          </td>
                          <td className="py-4 text-right text-zinc-300">{gym.users}</td>
                          <td className="py-4 text-right">
                             <Button variant="ghost" size="icon" className="text-zinc-500 group-hover:text-white">
                                <MoreVertical size={16} />
                             </Button>
                          </td>
                       </tr>
                     ))}
                  </tbody>
               </table>
            </div>
         </div>

         {/* System Logs & Health */}
         <div className="space-y-6">
            <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
               <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
                  <Activity size={20} className="text-emerald-500" />
                  System Health
               </h3>
               <div className="space-y-4">
                  {[
                    { label: "API Gateway", status: "Healthy", uptime: "99.98%" },
                    { label: "AI Inference Engine", status: "Healthy", uptime: "99.92%" },
                    { label: "Database (PostgreSQL)", status: "Healthy", uptime: "100%" },
                    { label: "Redis Cache", status: "Degraded", uptime: "98.5%" },
                  ].map((sys, i) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-white/5">
                       <div>
                          <p className="text-xs font-bold text-white">{sys.label}</p>
                          <p className="text-[10px] text-zinc-500 uppercase">{sys.uptime}</p>
                       </div>
                       <span className={cn(
                         "text-[10px] font-bold px-2 py-1 rounded-md",
                         sys.status === "Healthy" ? "text-emerald-500 bg-emerald-500/10" : "text-amber-500 bg-amber-500/10"
                       )}>{sys.status}</span>
                    </div>
                  ))}
               </div>
            </div>

            {/* Platform Alerts */}
            <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-6 backdrop-blur-sm">
               <h3 className="text-sm font-bold text-red-500 flex items-center gap-2 mb-4 uppercase tracking-widest">
                  <AlertTriangle size={16} />
                  Platform Alerts
               </h3>
               <div className="space-y-3">
                  <div className="p-3 rounded-lg bg-black/40 border border-white/5">
                     <p className="text-xs font-bold text-white">Instance &apos;Local Box&apos; past due</p>
                     <p className="text-[10px] text-zinc-500 mt-1">Subscription expired 3 days ago. Auto-suspend scheduled.</p>
                  </div>
                  <div className="p-3 rounded-lg bg-black/40 border border-white/5">
                     <p className="text-xs font-bold text-white">AI Engine latency spike</p>
                     <p className="text-[10px] text-zinc-500 mt-1">Average inference time increased by 250ms in US-EAST-1.</p>
                  </div>
               </div>
            </div>
         </div>
      </div>
    </div>
  );
}
