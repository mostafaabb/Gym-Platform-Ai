"use client";

import React from "react";
import { motion } from "framer-motion";
import { 
  PieChart, 
  Utensils, 
  Plus, 
  Search, 
  ChevronRight, 
  Sparkles,
  Flame,
  Droplet,
  Beef,
  Wheat
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

const macroData = [
  { label: "Protein", value: 145, target: 180, icon: Beef, color: "text-red-500", bg: "bg-red-500" },
  { label: "Carbs", value: 180, target: 220, icon: Wheat, color: "text-amber-500", bg: "bg-amber-500" },
  { label: "Fats", value: 52, target: 65, icon: Droplet, color: "text-blue-500", bg: "bg-blue-500" },
];

const meals = [
  { name: "Breakfast", calories: 520, time: "8:00 AM", items: ["Oatmeal", "Whey Protein", "Blueberries"] },
  { name: "Lunch", calories: 750, time: "1:15 PM", items: ["Grilled Chicken", "Quinoa", "Avocado"] },
  { name: "Snack", calories: 200, time: "4:30 PM", items: ["Greek Yogurt", "Almonds"] },
];

export default function NutritionPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Nutrition AI</h1>
          <p className="text-zinc-500">Track your fuel and optimize your macros with AI.</p>
        </div>
        <div className="flex gap-3">
           <Button className="rounded-xl bg-white text-black hover:bg-zinc-200">
             <Plus className="mr-2 h-4 w-4" />
             Log Meal
           </Button>
           <Button variant="outline" className="rounded-xl border-white/10 bg-zinc-900/50 text-white backdrop-blur-md hover:bg-white/10">
             <Sparkles className="mr-2 h-4 w-4" />
             Generate Plan
           </Button>
        </div>
      </div>

      {/* Progress Circles & Macros */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Calorie Progress */}
        <div className="lg:col-span-1 rounded-2xl border border-white/5 bg-zinc-900/50 p-8 flex flex-col items-center justify-center relative overflow-hidden">
           <div className="absolute top-0 right-0 p-4 opacity-10">
              <Flame size={120} className="text-orange-500" />
           </div>
           <div className="relative h-48 w-48 flex items-center justify-center">
                     <svg className="h-full w-full text-primary" viewBox="0 0 100 100">
                 <circle className="text-zinc-800" strokeWidth="8" stroke="currentColor" fill="transparent" r="42" cx="50" cy="50" />
                         <motion.circle 
                            strokeWidth="8" 
                            strokeDasharray="264" 
                            initial={{ strokeDashoffset: 264 }}
                            animate={{ strokeDashoffset: 264 - (264 * 0.65) }}
                            strokeLinecap="round" 
                            stroke="currentColor" 
                            fill="transparent" 
                            r="42" cx="50" cy="50" 
                         />
              </svg>
              <div className="absolute flex flex-col items-center">
                 <span className="text-4xl font-black text-white">1,620</span>
                 <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">KCAL Left</span>
              </div>
           </div>
           <div className="mt-6 text-center">
              <p className="text-sm text-zinc-400">Target: 2,400 kcal</p>
           </div>
        </div>

        {/* Macro Bars */}
        <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-3 gap-6">
           {macroData.map((macro, i) => (
             <div key={i} className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 flex flex-col justify-between">
                <div className="flex items-center justify-between">
                   <div className={cn("h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center", macro.color)}>
                      <macro.icon size={20} />
                   </div>
                   <span className="text-xs font-bold text-zinc-500">{Math.round((macro.value / macro.target) * 100)}%</span>
                </div>
                <div className="mt-8">
                   <p className="text-xs font-medium text-zinc-500 uppercase tracking-widest">{macro.label}</p>
                   <p className="text-2xl font-bold text-white">{macro.value}g <span className="text-sm font-normal text-zinc-600">/ {macro.target}g</span></p>
                            <div className="mt-4 h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
                                 <motion.div 
                                    initial={{ width: 0 }}
                                    animate={{ width: `${(macro.value / macro.target) * 100}%` }}
                                 >
                                    <div className={cn("h-full rounded-full", macro.bg)} />
                                 </motion.div>
                            </div>
                </div>
             </div>
           ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Meal Log */}
        <div className="lg:col-span-2 space-y-6">
           <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Utensils className="text-primary" size={20} />
              Today&apos;s Meals
           </h3>
           <div className="space-y-4">
              {meals.map((meal, i) => (
                <div key={i} className="group relative rounded-2xl border border-white/5 bg-zinc-900/50 p-6 transition-all hover:bg-zinc-900">
                   <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                         <div className="h-12 w-12 rounded-xl bg-white/5 flex items-center justify-center text-zinc-400">
                            <Utensils size={20} />
                         </div>
                         <div>
                            <h4 className="font-bold text-white">{meal.name}</h4>
                            <p className="text-xs text-zinc-500">{meal.time} • {meal.calories} kcal</p>
                         </div>
                      </div>
                      <Button variant="ghost" size="sm" className="rounded-full text-zinc-500 opacity-0 group-hover:opacity-100 transition-opacity">
                         <ChevronRight size={20} />
                      </Button>
                   </div>
                   <div className="mt-4 flex flex-wrap gap-2">
                      {meal.items.map((item, j) => (
                        <span key={j} className="px-3 py-1 rounded-full bg-white/5 text-[10px] font-medium text-zinc-400 border border-white/5">
                           {item}
                        </span>
                      ))}
                   </div>
                </div>
              ))}
              <Button variant="ghost" className="w-full h-16 border-2 border-dashed border-white/5 rounded-2xl text-zinc-500 hover:text-white hover:bg-white/5 transition-all">
                 <Plus className="mr-2 h-4 w-4" />
                 Add Dinner
              </Button>
           </div>
        </div>

        {/* AI Meal Plan Summary */}
        <div className="space-y-6">
           <div className="rounded-2xl border border-primary/20 bg-primary/5 p-6 backdrop-blur-sm relative overflow-hidden">
              <div className="absolute -top-4 -right-4 h-24 w-24 bg-primary/20 rounded-full blur-3xl" />
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                 <Sparkles className="text-primary" size={20} />
                 AI Meal Recommendation
              </h3>
              <div className="mt-6 space-y-4">
                 <div className="p-4 rounded-xl bg-black/40 border border-white/5">
                    <p className="text-xs font-bold text-primary uppercase tracking-widest">Next Meal: Dinner</p>
                    <p className="text-sm font-medium text-white mt-2">Grilled Salmon with Quinoa</p>
                    <p className="text-xs text-zinc-500 mt-1">High protein, moderate healthy fats to support muscle recovery.</p>
                    <div className="mt-4 flex items-center justify-between text-[10px] font-bold text-zinc-400 uppercase tracking-tighter">
                       <span>P: 42g</span>
                       <span>C: 30g</span>
                       <span>F: 18g</span>
                    </div>
                 </div>
                 <Button className="w-full rounded-xl bg-primary text-white hover:bg-primary/90">
                    Add to Log
                 </Button>
              </div>
           </div>

           {/* Water Tracking */}
           <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-6">
                 <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">Hydration</h3>
                 <Droplet size={16} className="text-blue-500" />
              </div>
              <div className="flex items-center justify-between">
                 <div className="flex gap-2">
                    {[...Array(8)].map((_, i) => (
                      <div key={i} className={cn(
                        "h-8 w-6 rounded-md border border-white/10 transition-colors",
                        i < 5 ? "bg-blue-500/40 border-blue-500/20" : "bg-white/5"
                      )} />
                    ))}
                 </div>
                 <div className="text-right">
                    <p className="text-lg font-bold text-white">1.2L</p>
                    <p className="text-[10px] text-zinc-500 uppercase font-bold">Goal: 2.5L</p>
                 </div>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
