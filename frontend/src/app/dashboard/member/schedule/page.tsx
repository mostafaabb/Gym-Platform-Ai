"use client";

import React from "react";
import { Calendar as CalendarIcon, Clock, MapPin, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function SchedulePage() {
  return (
    <div className="space-y-8">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Your Schedule</h1>
          <p className="text-zinc-500">Plan your training and book your classes.</p>
        </div>
        <div className="flex items-center gap-2 rounded-xl bg-zinc-900/50 p-1 border border-white/5">
          <Button variant="ghost" size="sm" className="h-9 w-9 p-0 text-zinc-500 hover:text-white">
            <ChevronLeft size={18} />
          </Button>
          <span className="px-4 text-sm font-medium text-white">May 2026</span>
          <Button variant="ghost" size="sm" className="h-9 w-9 p-0 text-zinc-500 hover:text-white">
            <ChevronRight size={18} />
          </Button>
        </div>
      </div>

      <div className="space-y-4">
        {[
          { time: "09:00 AM", title: "Heavy Bench Press", instructor: "Felix", location: "Power Rack 1", color: "bg-primary" },
          { time: "11:30 AM", title: "HIIT Cardio Blast", instructor: "Sarah", location: "Studio A", color: "bg-purple-500" },
          { time: "05:00 PM", title: "Leg Day Destruction", instructor: "Marco", location: "Leg Area", color: "bg-orange-500" },
        ].map((item, i) => (
          <div key={i} className="group relative flex items-center gap-6 rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm transition-all hover:bg-zinc-900">
            <div className="text-center min-w-[80px]">
              <p className="text-lg font-bold text-white">{item.time.split(" ")[0]}</p>
              <p className="text-xs text-zinc-500">{item.time.split(" ")[1]}</p>
            </div>
            <div className={`h-12 w-1.5 rounded-full ${item.color}`} />
            <div className="flex-1">
              <h3 className="text-lg font-bold text-white">{item.title}</h3>
              <div className="flex items-center gap-4 mt-2">
                <div className="flex items-center gap-1.5 text-xs text-zinc-400">
                  <Clock size={14} />
                  60 min
                </div>
                <div className="flex items-center gap-1.5 text-xs text-zinc-400">
                  <MapPin size={14} />
                  {item.location}
                </div>
              </div>
            </div>
            <Button variant="ghost" className="text-zinc-500 group-hover:text-white">
              Details
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}
