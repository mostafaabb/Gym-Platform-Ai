"use client";

import React from "react";
import { motion } from "framer-motion";
import { Dumbbell, Plus, Search, Filter } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function WorkoutsPage() {
  return (
    <div className="space-y-8">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Your Workouts</h1>
          <p className="text-zinc-500">Manage and track your elite training routines.</p>
        </div>
        <Button className="rounded-xl bg-primary text-white hover:bg-primary/90">
          <Plus className="mr-2 h-4 w-4" />
          Create New Routine
        </Button>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col gap-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
          <input 
            type="text" 
            placeholder="Search workouts..." 
            className="w-full rounded-xl border border-white/5 bg-zinc-900/50 py-3 pl-12 pr-4 text-white outline-none focus:border-primary/50"
          />
        </div>
        <Button variant="outline" className="rounded-xl border-white/5 bg-zinc-900/50 text-zinc-400">
          <Filter className="mr-2 h-4 w-4" />
          Filter
        </Button>
      </div>

      {/* Empty State / List */}
      <div className="rounded-3xl border border-dashed border-white/10 bg-zinc-900/20 py-20 text-center">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-zinc-900 text-zinc-700">
          <Dumbbell size={32} />
        </div>
        <h3 className="text-xl font-semibold text-white">No workouts found</h3>
        <p className="mt-2 text-zinc-500">Start your journey by creating your first workout plan.</p>
        <Button variant="ghost" className="mt-6 text-primary hover:text-primary/80">
          Browse Templates
        </Button>
      </div>
    </div>
  );
}
