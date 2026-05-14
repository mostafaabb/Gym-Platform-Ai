"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  Users, 
  Activity, 
  Calendar, 
  AlertCircle, 
  ChevronRight, 
  UserPlus, 
  MessageCircle,
  Video,
  CheckCircle2,
  Clock,
  ExternalLink
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

const activeClients = [
  { id: 1, name: "Felix Henderson", status: "Training", exercise: "Bench Press", score: 92, lastActive: "Live" },
  { id: 2, name: "Sarah Jenkins", status: "Training", exercise: "Squats", score: 78, lastActive: "Live", alert: "Form Error: Knee Caving" },
  { id: 3, name: "Michael Chen", status: "Resting", exercise: "Deadlift", score: 95, lastActive: "2m ago" },
];

const upcomingSessions = [
  { id: 1, client: "Emma Wilson", time: "10:00 AM", type: "Personal Training" },
  { id: 2, client: "David Miller", time: "11:30 AM", type: "Form Assessment" },
  { id: 3, client: "Group Class", time: "1:00 PM", type: "HIIT Session" },
];

const ClientCard = ({ client }: { client: any }) => (
  <motion.div
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    className="group relative overflow-hidden rounded-2xl border border-white/5 bg-zinc-900/50 p-5 transition-all hover:bg-zinc-900"
  >
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="relative h-12 w-12 rounded-full bg-zinc-800 p-0.5">
           <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${client.name}`} alt="Avatar" className="rounded-full" />
           {client.lastActive === "Live" && (
             <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-zinc-900 bg-emerald-500" />
           )}
        </div>
        <div>
          <h4 className="font-bold text-white">{client.name}</h4>
          <p className="text-xs text-zinc-500">{client.status} • {client.exercise}</p>
        </div>
      </div>
      <div className="text-right">
         <p className={cn(
           "text-lg font-black",
           client.score > 90 ? "text-emerald-400" : "text-amber-400"
         )}>{client.score}%</p>
         <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">Form Score</p>
      </div>
    </div>

    {client.alert && (
      <div className="mt-4 flex items-center gap-2 rounded-xl bg-red-500/10 p-3 text-red-500 border border-red-500/20">
        <AlertCircle size={16} />
        <span className="text-xs font-medium">{client.alert}</span>
      </div>
    )}

    <div className="mt-6 flex items-center justify-between">
       <div className="flex gap-2">
          <Button size="sm" variant="ghost" className="h-9 w-9 rounded-full bg-white/5 text-zinc-400 hover:text-white">
             <MessageCircle size={16} />
          </Button>
          <Button size="sm" variant="ghost" className="h-9 w-9 rounded-full bg-white/5 text-zinc-400 hover:text-white">
             <Video size={16} />
          </Button>
       </div>
       <Button size="sm" className="h-9 rounded-full bg-primary/10 text-primary hover:bg-primary/20 text-xs font-bold px-4">
          View Live Feed
          <ChevronRight size={14} className="ml-1" />
       </Button>
    </div>
  </motion.div>
);

export default function TrainerDashboard() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Trainer Dashboard</h1>
          <p className="text-zinc-500">Monitoring 12 active clients across 3 gyms.</p>
        </div>
        <div className="flex gap-3">
           <Button className="rounded-xl bg-primary text-white hover:bg-primary/90">
             <UserPlus className="mr-2 h-4 w-4" />
             Add New Client
           </Button>
           <Button variant="outline" className="rounded-xl border-white/10 bg-zinc-900/50 text-white backdrop-blur-md hover:bg-white/10">
             <Calendar className="mr-2 h-4 w-4" />
             Manage Schedule
           </Button>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Active Clients Monitoring */}
        <div className="lg:col-span-2 space-y-6">
           <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                 <Activity className="text-emerald-500" size={20} />
                 Live Client Monitoring
              </h3>
              <span className="px-2 py-1 rounded-full bg-emerald-500/10 text-emerald-500 text-[10px] font-bold uppercase tracking-widest">
                 3 Online Now
              </span>
           </div>
           <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {activeClients.map(client => (
                <ClientCard key={client.id} client={client} />
              ))}
           </div>

           {/* Client List Table Mini */}
           <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm mt-8">
              <h3 className="mb-6 text-sm font-semibold uppercase tracking-wider text-zinc-500">Client Management</h3>
              <div className="space-y-4">
                 {[
                   { name: "John Smith", goal: "Muscle Gain", progress: 85, lastSeen: "Today" },
                   { name: "Alice Cooper", goal: "Weight Loss", progress: 62, lastSeen: "Yesterday" },
                   { name: "Bob Wilson", goal: "Powerlifting", progress: 91, lastSeen: "3 days ago" },
                 ].map((c, i) => (
                    <div key={i} className="flex items-center justify-between group">
                       <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-full bg-zinc-800" />
                          <div>
                             <p className="text-sm font-medium text-white">{c.name}</p>
                             <p className="text-[10px] text-zinc-500">{c.goal}</p>
                          </div>
                       </div>
                       <div className="flex items-center gap-8">
                          <div className="w-24 h-1.5 bg-zinc-800 rounded-full overflow-hidden hidden md:block">
                             <div className="h-full bg-primary" style={{ width: `${c.progress}%` }} />
                          </div>
                          <span className="text-xs text-zinc-500 w-20 text-right">{c.lastSeen}</span>
                          <Button variant="ghost" size="sm" className="text-zinc-500 group-hover:text-white">
                             <ExternalLink size={16} />
                          </Button>
                       </div>
                    </div>
                 ))}
              </div>
           </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-8">
           {/* Schedule */}
           <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-6">
                 <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">Today&apos;s Schedule</h3>
                 <Clock size={16} className="text-zinc-500" />
              </div>
              <div className="space-y-6">
                 {upcomingSessions.map((session, i) => (
                    <div key={i} className="flex gap-4 relative">
                       {i !== upcomingSessions.length - 1 && (
                         <div className="absolute left-[19px] top-10 bottom-[-24px] w-[2px] bg-zinc-800" />
                       )}
                       <div className="h-10 w-10 rounded-full bg-zinc-800 border border-white/5 flex items-center justify-center shrink-0 z-10 text-xs font-bold text-zinc-400">
                          {session.time.split(':')[0]}
                       </div>
                       <div className="pb-6">
                          <p className="text-sm font-bold text-white">{session.client}</p>
                          <p className="text-xs text-zinc-500">{session.time} • {session.type}</p>
                       </div>
                    </div>
                 ))}
              </div>
              <Button variant="ghost" className="w-full text-xs text-primary mt-2">
                 View Full Calendar
              </Button>
           </div>

           {/* Alerts & Tasks */}
           <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
              <h3 className="mb-6 text-sm font-semibold uppercase tracking-wider text-zinc-500">Action Required</h3>
              <div className="space-y-4">
                 <div className="flex items-start gap-3 p-3 rounded-xl bg-orange-500/5 border border-orange-500/10">
                    <AlertCircle className="text-orange-500 shrink-0" size={18} />
                    <div>
                       <p className="text-xs font-bold text-white">Review Workout Plan</p>
                       <p className="text-[10px] text-zinc-500 mt-1">Emma Wilson reached her target weight. Time to adjust macros.</p>
                    </div>
                 </div>
                 <div className="flex items-start gap-3 p-3 rounded-xl bg-primary/5 border border-primary/10">
                    <CheckCircle2 className="text-primary shrink-0" size={18} />
                    <div>
                       <p className="text-xs font-bold text-white">New Client Request</p>
                       <p className="text-[10px] text-zinc-500 mt-1">A member from &apos;Iron Paradise&apos; wants to book an intro.</p>
                    </div>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
