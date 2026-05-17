"use client";

import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Utensils, 
  Plus, 
  ChevronRight, 
  Sparkles, 
  Flame, 
  Droplet, 
  Beef, 
  Wheat,
  Camera,
  X,
  Loader2,
  Upload,
  CheckCircle2,
  PlusCircle,
  AlertCircle
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";
import api from "@/lib/api";
import { useDashboardData } from "@/hooks/useDashboardData";

interface MealItem {
  name: string;
}

interface NutritionLog {
  id: number;
  meal_type: string;
  food_items: MealItem[];
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  notes?: string;
  logged_at: string;
}

interface MealPlan {
  id: number;
  goal: string;
  calories_target: number;
  macro_targets: {
    protein: number;
    carbs: number;
    fats: number;
  };
  meals: Array<{
    name: string;
    items: string[];
    calories: number;
  }>;
}

export default function NutritionPage() {
  const { data: dashboardData, loading: dashboardLoading } = useDashboardData();
  const memberId = dashboardData?.context?.member_id || 1; // Fallback to 1 for dev/testing

  // Component States
  const [logs, setLogs] = useState<NutritionLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [generatingPlan, setGeneratingPlan] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState("muscle_gain");
  
  // Modal States
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalTab, setModalTab] = useState<"manual" | "vision">("manual");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [aiAnalyzing, setAiAnalyzing] = useState(false);
  const [aiSuccessMessage, setAiSuccessMessage] = useState<string | null>(null);
  const [aiErrorMessage, setAiErrorMessage] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Manual Log Fields
  const [mealType, setMealType] = useState("breakfast");
  const [foodItems, setFoodItems] = useState("");
  const [calories, setCalories] = useState("");
  const [protein, setProtein] = useState("");
  const [carbs, setCarbs] = useState("");
  const [fat, setFat] = useState("");
  const [notes, setNotes] = useState("");

  // Targets (Sensible defaults, overridden if meal plan is loaded)
  const caloriesTarget = mealPlan?.calories_target || 2400;
  const macroTargets = mealPlan?.macro_targets || { protein: 180, carbs: 220, fats: 65 };

  // Fetch Nutrition Logs and Latest Plan
  const fetchNutritionData = async () => {
    if (!memberId) return;
    setLoading(true);
    try {
      const [historyRes, planRes] = await Promise.all([
        api.get(`/nutrition/member/${memberId}/history`),
        api.get(`/nutrition/member/${memberId}/meal-plan`).catch(() => ({ data: null }))
      ]);

      if (historyRes.data?.logs) {
        setLogs(historyRes.data.logs);
      }
      if (planRes.data) {
        setMealPlan(planRes.data);
      }
    } catch (err) {
      console.error("Failed to fetch nutrition data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (memberId) {
      fetchNutritionData();
    }
  }, [memberId]);

  // Today's Logs Filtering
  const todayLogs = logs.filter(log => {
    const logDate = new Date(log.logged_at);
    const today = new Date();
    return logDate.getDate() === today.getDate() &&
           logDate.getMonth() === today.getMonth() &&
           logDate.getFullYear() === today.getFullYear();
  });

  // Calculate Today's Totals (excluding water logs from calorie/macro math)
  const nonWaterLogs = todayLogs.filter(log => log.meal_type !== "water");
  const todayCalories = nonWaterLogs.reduce((sum, log) => sum + (log.calories || 0), 0);
  const todayProtein = nonWaterLogs.reduce((sum, log) => sum + (log.protein || 0), 0);
  const todayCarbs = nonWaterLogs.reduce((sum, log) => sum + (log.carbs || 0), 0);
  const todayFat = nonWaterLogs.reduce((sum, log) => sum + (log.fat || 0), 0);

  // Water Hydration tracking (calculated from logged "water" logs today)
  const todayWaterMl = todayLogs
    .filter(log => log.meal_type === "water")
    .reduce((sum, log) => {
      // Find if there is ml info, otherwise default to 250ml per entry
      const items = log.food_items;
      if (items && items.length > 0) {
        const item = items[0] as any;
        return sum + (item.amount_ml || 250);
      }
      return sum + 250;
    }, 0);

  const waterTargetMl = 2500; // 2.5 Liters
  const waterGlasses = Math.min(10, Math.round(todayWaterMl / 250));

  // Log glass of water
  const handleLogWater = async () => {
    try {
      await api.post(`/nutrition/log?member_id=${memberId}`, {
        meal_type: "water",
        food_items: [{ name: "Water", amount_ml: 250 }],
        total_calories: 0,
        protein_g: 0,
        carbs_g: 0,
        fat_g: 0,
        notes: "Hydrated with a glass of water"
      });
      fetchNutritionData();
    } catch (err) {
      console.error("Failed to log water:", err);
    }
  };

  // Submit manual log
  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!foodItems.trim()) return;

    setIsSubmitting(true);
    try {
      const itemsArray = foodItems.split(",").map(i => ({ name: i.trim() }));
      await api.post(`/nutrition/log?member_id=${memberId}`, {
        meal_type: mealType.toLowerCase(),
        food_items: itemsArray,
        total_calories: calories ? parseFloat(calories) : 0,
        protein_g: protein ? parseFloat(protein) : 0,
        carbs_g: carbs ? parseFloat(carbs) : 0,
        fat_g: fat ? parseFloat(fat) : 0,
        notes: notes.trim()
      });

      // Clear fields
      setFoodItems("");
      setCalories("");
      setProtein("");
      setCarbs("");
      setFat("");
      setNotes("");
      setIsModalOpen(false);
      fetchNutritionData();
    } catch (err) {
      console.error("Failed to log meal", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Unified AI Vision Meal parser
  const processFile = async (file: File) => {
    if (!file) return;

    setAiAnalyzing(true);
    setAiSuccessMessage(null);
    setAiErrorMessage(null);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await api.post(`/nutrition/snap-log?member_id=${memberId}`, formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });

      const parsedLog = res.data;
      setAiSuccessMessage(`Successfully logged ${parsedLog.meal_type}! Consumed: ${parsedLog.total_calories || 0} kcal.`);
      fetchNutritionData();
      
      // Auto-fill manual tab in case they want to adjust or review macros
      setMealType(parsedLog.meal_type || "lunch");
      setFoodItems(parsedLog.food_items?.map((item: any) => item.name).join(", ") || "");
      setCalories(parsedLog.total_calories?.toString() || "");
      setProtein(parsedLog.protein_g?.toString() || "");
      setCarbs(parsedLog.carbs_g?.toString() || "");
      setFat(parsedLog.fat_g?.toString() || "");
      setNotes(parsedLog.notes || "");
    } catch (err: any) {
      console.error("AI vision error", err);
      setAiErrorMessage(
        err?.response?.data?.detail || 
        "AI Vision scan failed. Please try a different, smaller, or higher contrast meal image."
      );
    } finally {
      setAiAnalyzing(false);
    }
  };

  // Submit image from click selector
  const handleVisionUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  // Drag and drop event handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  // Generate Personalized AI Meal Plan
  const handleGeneratePlan = async () => {
    setGeneratingPlan(true);
    try {
      const res = await api.post(`/ai/nutrition-plan/${memberId}?goal=${selectedGoal}`);
      setMealPlan(res.data);
      fetchNutritionData();
    } catch (err) {
      console.error("Failed to generate AI plan", err);
    } finally {
      setGeneratingPlan(false);
    }
  };

  // Add Recommended Meal directly to log
  const handleAddRecommended = async (recommendedMeal: any) => {
    try {
      await api.post(`/nutrition/log?member_id=${memberId}`, {
        meal_type: recommendedMeal.name.toLowerCase(),
        food_items: recommendedMeal.items.map((i: string) => ({ name: i })),
        total_calories: recommendedMeal.calories,
        protein_g: Math.round(recommendedMeal.calories * 0.08), // Estimate protein
        carbs_g: Math.round(recommendedMeal.calories * 0.1), // Estimate carbs
        fat_g: Math.round(recommendedMeal.calories * 0.03), // Estimate fats
        notes: "Added from AI recommended plan"
      });
      fetchNutritionData();
    } catch (err) {
      console.error("Failed to add recommended meal to log", err);
    }
  };

  // Percent calculation
  const getPercentage = (value: number, target: number) => {
    if (!target) return 0;
    return Math.min(100, Math.round((value / target) * 100));
  };

  const macroData = [
    { label: "Protein", value: todayProtein, target: macroTargets.protein, color: "text-red-500", bg: "bg-red-500" },
    { label: "Carbs", value: todayCarbs, target: macroTargets.carbs, color: "text-amber-500", bg: "bg-amber-500" },
    { label: "Fats", value: todayFat, target: macroTargets.fats, color: "text-blue-500", bg: "bg-blue-500" },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Nutrition AI</h1>
          <p className="text-zinc-500">Track your fuel and optimize your macros with AI.</p>
        </div>
        <div className="flex flex-wrap gap-3">
           <Button 
             onClick={() => {
               setModalTab("manual");
               setAiSuccessMessage(null);
               setIsModalOpen(true);
             }}
             className="rounded-xl bg-white text-black hover:bg-zinc-200 shadow-lg shadow-white/5"
           >
             <Plus className="mr-2 h-4 w-4" />
             Log Meal
           </Button>
           <div className="flex gap-2 items-center bg-zinc-900/50 border border-white/5 p-1 rounded-xl">
             <select 
               value={selectedGoal}
               onChange={(e) => setSelectedGoal(e.target.value)}
               className="bg-transparent text-xs text-white border-0 focus:ring-0 cursor-pointer pr-8 pl-2 outline-none"
             >
               <option className="bg-zinc-900" value="muscle_gain">Muscle Gain</option>
               <option className="bg-zinc-900" value="weight_loss">Weight Loss</option>
               <option className="bg-zinc-900" value="strength">Strength</option>
               <option className="bg-zinc-900" value="general_health">General Health</option>
             </select>
             <Button 
               onClick={handleGeneratePlan}
               disabled={generatingPlan}
               variant="outline" 
               className="rounded-lg py-1 border-white/10 bg-zinc-900/30 text-white backdrop-blur-md hover:bg-white/10 text-xs"
             >
               {generatingPlan ? (
                 <>
                   <Loader2 className="mr-2 h-3.5 w-3.5 animate-spin" />
                   AI Planning...
                 </>
               ) : (
                 <>
                   <Sparkles className="mr-2 h-3.5 w-3.5 text-primary" />
                   AI Generate
                 </>
               )}
             </Button>
           </div>
        </div>
      </div>

      {/* Progress Cards & Macros */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Calorie Progress */}
        <div className="lg:col-span-1 rounded-2xl border border-white/5 bg-zinc-900/50 p-8 flex flex-col items-center justify-center relative overflow-hidden backdrop-blur-md">
           <div className="absolute top-0 right-0 p-4 opacity-5">
              <Flame size={120} className="text-orange-500" />
           </div>
           <div className="relative h-48 w-48 flex items-center justify-center">
              <svg className="h-full w-full -rotate-90" viewBox="0 0 100 100">
                 <circle 
                   className="text-zinc-800" 
                   strokeWidth="6" 
                   stroke="currentColor" 
                   fill="transparent" 
                   r="40" cx="50" cy="50" 
                 />
                 <circle 
                    strokeWidth="6" 
                    strokeDasharray="251.2" 
                    strokeDashoffset={251.2 - (251.2 * Math.min(1.0, todayCalories / caloriesTarget))}
                    strokeLinecap="round" 
                    stroke="url(#calorieGradient)" 
                    fill="transparent" 
                    r="40" cx="50" cy="50" 
                    className="transition-all duration-1000 ease-out"
                 />
                 <defs>
                   <linearGradient id="calorieGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                     <stop offset="0%" stopColor="#3b82f6" />
                     <stop offset="100%" stopColor="#8b5cf6" />
                   </linearGradient>
                 </defs>
              </svg>
              <div className="absolute flex flex-col items-center">
                 <span className="text-3xl font-black text-white">{Math.max(0, caloriesTarget - todayCalories).toLocaleString()}</span>
                 <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">KCAL Left</span>
              </div>
           </div>
           <div className="mt-6 text-center">
              <p className="text-sm text-zinc-400">Target: {caloriesTarget.toLocaleString()} kcal</p>
              <p className="text-xs text-zinc-600 mt-1">Consumed: {todayCalories.toLocaleString()} kcal</p>
           </div>
        </div>

        {/* Macro Bars */}
        <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-3 gap-6">
           {macroData.map((macro, i) => (
             <div key={i} className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 flex flex-col justify-between backdrop-blur-md transition-all hover:border-white/10 group">
                <div className="flex items-center justify-between">
                   <div className={cn("h-10 w-10 rounded-xl bg-white/5 flex items-center justify-center", macro.color)}>
                      <Beef size={20} />
                   </div>
                   <span className="text-xs font-bold text-zinc-500 bg-white/5 px-2 py-0.5 rounded-full">{getPercentage(macro.value, macro.target)}%</span>
                </div>
                <div className="mt-8">
                   <p className="text-xs font-semibold text-zinc-500 uppercase tracking-widest">{macro.label}</p>
                   <p className="text-2xl font-bold text-white mt-1">
                     {Math.round(macro.value)}g <span className="text-sm font-normal text-zinc-600">/ {macro.target}g</span>
                   </p>
                   <div className="mt-4 h-1.5 w-full bg-zinc-800 rounded-full overflow-hidden">
                        <div 
                           style={{ width: `${getPercentage(macro.value, macro.target)}%` }}
                           className={cn("h-full rounded-full transition-all duration-1000 ease-out", macro.bg)}
                        />
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
              Today&apos;s Fuel Log
           </h3>
           <div className="space-y-4">
              {/* Group logged meals by type */}
              {["Breakfast", "Lunch", "Dinner", "Snack"].map((mType) => {
                const loggedForType = nonWaterLogs.filter(log => log.meal_type.toLowerCase() === mType.toLowerCase());

                if (loggedForType.length > 0) {
                  return loggedForType.map((meal, index) => (
                    <div key={meal.id || index} className="group relative rounded-2xl border border-white/5 bg-zinc-900/40 p-6 transition-all hover:bg-zinc-900/80">
                       <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                             <div className="h-12 w-12 rounded-xl bg-white/5 flex items-center justify-center text-zinc-400 group-hover:text-primary transition-colors">
                                <Utensils size={20} />
                             </div>
                             <div>
                                <h4 className="font-bold text-white uppercase tracking-wider text-sm">{mType}</h4>
                                <p className="text-xs text-zinc-500 mt-1">
                                  {meal.calories} kcal • P: {meal.protein}g • C: {meal.carbs}g • F: {meal.fat}g
                                </p>
                             </div>
                          </div>
                          {meal.notes && (
                            <span className="text-[10px] text-zinc-600 bg-zinc-950 px-3 py-1 rounded-lg border border-white/5 italic">
                              &ldquo;{meal.notes}&rdquo;
                            </span>
                          )}
                       </div>
                       <div className="mt-4 flex flex-wrap gap-2">
                          {meal.food_items?.map((item, j) => (
                            <span key={j} className="px-3 py-1 rounded-full bg-white/5 text-[10px] font-medium text-zinc-400 border border-white/5 transition-colors group-hover:border-white/10 group-hover:text-white">
                               {item.name}
                            </span>
                          ))}
                       </div>
                    </div>
                  ));
                } else {
                  return (
                    <button 
                      key={mType}
                      onClick={() => {
                        setMealType(mType.toLowerCase());
                        setModalTab("manual");
                        setAiSuccessMessage(null);
                        setIsModalOpen(true);
                      }}
                      className="w-full h-16 border-2 border-dashed border-white/5 rounded-2xl text-zinc-500 hover:text-white hover:bg-white/5 flex items-center justify-center gap-2 transition-all"
                    >
                      <PlusCircle size={18} className="text-zinc-500 group-hover:text-white" />
                      Add {mType}
                    </button>
                  );
                }
              })}
           </div>
        </div>

        {/* AI Meal Plan Summary */}
        <div className="space-y-6">
           <div className="rounded-2xl border border-primary/20 bg-primary/5 p-6 backdrop-blur-sm relative overflow-hidden shadow-xl shadow-primary/5">
              <div className="absolute -top-4 -right-4 h-24 w-24 bg-primary/20 rounded-full blur-3xl" />
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                 <Sparkles className="text-primary" size={20} />
                 AI Meal Recommendations
              </h3>
              <div className="mt-6 space-y-4">
                 {mealPlan && mealPlan.meals && mealPlan.meals.length > 0 ? (
                   mealPlan.meals.map((planMeal, idx) => (
                     <div key={idx} className="p-4 rounded-xl bg-black/40 border border-white/5 flex flex-col justify-between gap-3">
                        <div>
                          <p className="text-xs font-bold text-primary uppercase tracking-widest">{planMeal.name}</p>
                          <p className="text-sm font-semibold text-white mt-1.5">{planMeal.items.join(" & ")}</p>
                          <p className="text-xs text-zinc-500 mt-1">{planMeal.calories} kcal estimated.</p>
                        </div>
                        <Button 
                          onClick={() => handleAddRecommended(planMeal)}
                          size="sm" 
                          className="w-full rounded-lg bg-primary hover:bg-primary/95 text-white font-bold text-xs"
                        >
                          Add to Log
                        </Button>
                     </div>
                   ))
                 ) : (
                   <div className="p-4 rounded-xl bg-black/30 border border-dashed border-white/10 text-center py-8">
                     <AlertCircle size={32} className="text-zinc-600 mx-auto mb-2" />
                     <p className="text-xs text-zinc-400 font-semibold">No active plan generated yet.</p>
                     <p className="text-[10px] text-zinc-500 mt-1">Select your goal and click &ldquo;AI Generate&rdquo; to plan your fuel strategy.</p>
                   </div>
                 )}
              </div>
           </div>

           {/* Water Tracking */}
           <div className="rounded-2xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-sm shadow-lg">
              <div className="flex items-center justify-between mb-6">
                 <div>
                   <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">Hydration Progress</h3>
                   <p className="text-[10px] text-zinc-600 mt-0.5">Click glass to log 250ml</p>
                 </div>
                 <Droplet size={16} className="text-blue-500 animate-pulse" />
              </div>
              <div className="flex items-center justify-between gap-4">
                 <div className="grid grid-cols-5 gap-2.5">
                    {[...Array(10)].map((_, i) => (
                      <button 
                        key={i} 
                        onClick={handleLogWater}
                        className={cn(
                          "h-8 w-6 rounded-md border transition-all hover:scale-105 active:scale-95 duration-200",
                          i < waterGlasses 
                            ? "bg-blue-500/50 border-blue-400/40 shadow-inner shadow-blue-400/30" 
                            : "bg-white/5 border-white/10 hover:border-blue-500/30"
                        )} 
                      />
                    ))}
                 </div>
                 <div className="text-right min-w-[70px]">
                    <p className="text-xl font-bold text-white">{todayWaterMl / 1000}L</p>
                    <p className="text-[10px] text-zinc-500 uppercase font-bold">Goal: {waterTargetMl / 1000}L</p>
                 </div>
              </div>
           </div>
        </div>
      </div>

      {/* Dynamic Log Modal (Manual Form & AI vision Drag-and-Drop) */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div 
            onClick={() => setIsModalOpen(false)}
            className="absolute inset-0 bg-black/80 backdrop-blur-md transition-opacity duration-300"
          />

          {/* Modal Body */}
          <div 
            className="relative w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-2xl border border-white/10 bg-zinc-950 p-8 shadow-2xl z-10 transform scale-100 opacity-100 transition-all duration-300"
          >
            <button 
              onClick={() => setIsModalOpen(false)}
              className="absolute top-4 right-4 text-zinc-500 hover:text-white"
            >
              <X size={20} />
            </button>

            <h3 className="text-xl font-bold text-white mb-6">Log Your Intake</h3>

            {/* Tab Selector */}
            <div className="flex border-b border-white/5 mb-6">
              <button 
                onClick={() => setModalTab("manual")}
                className={cn(
                  "flex-1 pb-3 text-sm font-semibold text-center border-b-2 transition-all outline-none",
                  modalTab === "manual" 
                    ? "border-primary text-white" 
                    : "border-transparent text-zinc-500 hover:text-zinc-300"
                )}
              >
                Manual Log
              </button>
              <button 
                onClick={() => setModalTab("vision")}
                className={cn(
                  "flex-1 pb-3 text-sm font-semibold text-center border-b-2 transition-all outline-none",
                  modalTab === "vision" 
                    ? "border-primary text-white" 
                    : "border-transparent text-zinc-500 hover:text-zinc-300"
                )}
              >
                <Sparkles className="inline-block mr-1 h-3.5 w-3.5 text-primary" />
                AI Vision Scan
              </button>
            </div>

            {/* Success alert from AI */}
            {aiSuccessMessage && (
              <div className="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-xs flex items-center gap-3">
                <CheckCircle2 size={18} className="flex-shrink-0" />
                <span>{aiSuccessMessage}</span>
              </div>
            )}

            {/* Error alert from AI */}
            {aiErrorMessage && (
              <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-xs flex items-center gap-3">
                <AlertCircle size={18} className="flex-shrink-0" />
                <span>{aiErrorMessage}</span>
              </div>
            )}

            {modalTab === "manual" ? (
              <form onSubmit={handleManualSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">Meal Type</label>
                  <select 
                    value={mealType} 
                    onChange={(e) => setMealType(e.target.value)}
                    className="w-full rounded-xl border border-white/10 bg-zinc-900 text-white p-3 text-sm focus:border-primary focus:ring-0 outline-none"
                  >
                    <option value="breakfast">Breakfast</option>
                    <option value="lunch">Lunch</option>
                    <option value="dinner">Dinner</option>
                    <option value="snack">Snack</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">Food Items</label>
                  <input 
                    type="text" 
                    required
                    placeholder="e.g. Oatmeal, Blueberries, Whey Protein" 
                    value={foodItems}
                    onChange={(e) => setFoodItems(e.target.value)}
                    className="w-full rounded-xl border border-white/10 bg-zinc-900 text-white p-3 text-sm focus:border-primary focus:ring-0 outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">Calories (kcal)</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 450" 
                      value={calories}
                      onChange={(e) => setCalories(e.target.value)}
                      className="w-full rounded-xl border border-white/10 bg-zinc-900 text-white p-3 text-sm focus:border-primary focus:ring-0 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">Protein (g)</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 30" 
                      value={protein}
                      onChange={(e) => setProtein(e.target.value)}
                      className="w-full rounded-xl border border-white/10 bg-zinc-900 text-white p-3 text-sm focus:border-primary focus:ring-0 outline-none"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">Carbs (g)</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 40" 
                      value={carbs}
                      onChange={(e) => setCarbs(e.target.value)}
                      className="w-full rounded-xl border border-white/10 bg-zinc-900 text-white p-3 text-sm focus:border-primary focus:ring-0 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">Fats (g)</label>
                    <input 
                      type="number" 
                      placeholder="e.g. 10" 
                      value={fat}
                      onChange={(e) => setFat(e.target.value)}
                      className="w-full rounded-xl border border-white/10 bg-zinc-900 text-white p-3 text-sm focus:border-primary focus:ring-0 outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">Notes</label>
                  <textarea 
                    placeholder="e.g. Post-workout meal" 
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={2}
                    className="w-full rounded-xl border border-white/10 bg-zinc-900 text-white p-3 text-sm focus:border-primary focus:ring-0 outline-none resize-none"
                  />
                </div>

                <Button 
                  type="submit" 
                  disabled={isSubmitting}
                  className="w-full rounded-xl bg-white text-black hover:bg-zinc-200 mt-6 font-bold py-3.5"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Logging...
                    </>
                  ) : (
                    "Save Meal"
                  )}
                </Button>
              </form>
            ) : (
              <div 
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={cn(
                  "flex flex-col items-center justify-center p-8 border-2 border-dashed rounded-2xl bg-zinc-900/30 cursor-pointer transition-all duration-200",
                  dragActive 
                    ? "border-primary bg-primary/5 scale-[1.02]" 
                    : "border-white/10 hover:border-white/20"
                )}
              >
                {aiAnalyzing ? (
                  <div className="text-center space-y-4 py-8 pointer-events-none">
                    <Loader2 className="h-10 w-10 text-primary animate-spin mx-auto" />
                    <p className="text-sm font-semibold text-white">Analyzing food items & macros...</p>
                    <p className="text-xs text-zinc-500">GPT-4o Vision is processing your meal image</p>
                  </div>
                ) : (
                  <div className="text-center space-y-4 py-8 flex flex-col items-center justify-center pointer-events-none">
                    <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center text-primary mb-2 shadow-lg shadow-primary/5">
                      <Camera size={28} />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-white">Upload Meal Image</p>
                      <p className="text-xs text-zinc-500 mt-1">Drag and drop or click to upload</p>
                    </div>
                    <input 
                      type="file" 
                      ref={fileInputRef}
                      accept="image/*"
                      className="hidden" 
                      onChange={handleVisionUpload}
                    />
                    <Button variant="outline" className="text-xs rounded-xl border-white/10 text-white mt-4 pointer-events-none">
                      <Upload size={14} className="mr-2" />
                      Select File
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
