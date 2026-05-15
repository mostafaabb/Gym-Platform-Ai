"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { 
  LayoutDashboard, 
  Dumbbell, 
  Activity, 
  Calendar, 
  Settings, 
  LogOut,
  ChevronLeft,
  ChevronRight,
  Mic2,
  PieChart,
  User,
  Menu
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

const sidebarItems = [
  { icon: LayoutDashboard, label: "Overview", href: "/dashboard/member" },
  { icon: Dumbbell, label: "Workouts", href: "/dashboard/member/workouts" },
  { icon: Mic2, label: "AI Coach", href: "/dashboard/member/coach" },
  { icon: Activity, label: "Analytics", href: "/dashboard/member/analytics" },
  { icon: Calendar, label: "Schedule", href: "/dashboard/member/schedule" },
  { icon: PieChart, label: "Nutrition", href: "/dashboard/member/nutrition" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = React.useState(false);

  return (
    <div className="flex min-h-screen bg-black text-white">
      {/* Sidebar */}
      <motion.aside
        animate={{ width: isCollapsed ? 80 : 260 }}
      >
        <div className="h-full border-r border-white/5 bg-zinc-950/50 backdrop-blur-xl">
          <div className="flex h-20 items-center justify-between px-6">
          {!isCollapsed && (
            <div className="flex items-center gap-2">
              <Dumbbell className="text-primary" size={24} />
              <span className="text-lg font-bold tracking-tighter">GymFlow</span>
            </div>
          )}
          {isCollapsed && <Dumbbell className="mx-auto text-primary" size={24} />}
          <Button 
            variant="ghost" 
            size="sm" 
            className="hidden md:flex text-zinc-500 hover:text-white"
            onClick={() => setIsCollapsed(!isCollapsed)}
          >
            {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </Button>
        </div>

        <nav className="mt-6 space-y-2 px-3">
          {sidebarItems.map((item) => (
            <Link key={item.href} href={item.href}>
              <div className={cn(
                "group flex items-center rounded-xl px-4 py-3.5 transition-all duration-300",
                pathname === item.href 
                  ? "bg-primary text-white shadow-xl shadow-primary/30" 
                  : "text-zinc-500 hover:bg-white/5 hover:text-white"
              )}>
                <item.icon size={20} className={cn(
                  "shrink-0 transition-transform duration-300 group-hover:scale-110",
                  pathname === item.href ? "text-white" : "group-hover:text-primary"
                )} />
                {!isCollapsed && (
                  <span className="ml-3 font-semibold text-sm tracking-tight">{item.label}</span>
                )}
              </div>
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-8 w-full px-4">
          <Link href="/dashboard/member/profile">
            <div className={cn(
              "flex items-center rounded-xl px-4 py-3 transition-all duration-200 text-zinc-500 hover:bg-white/5 hover:text-white group",
              isCollapsed ? "justify-center" : ""
            )}>
              <User size={20} className="group-hover:text-primary transition-colors" />
              {!isCollapsed && <span className="ml-3 text-sm font-medium">Profile Settings</span>}
            </div>
          </Link>
          <button 
            onClick={() => {
              import("js-cookie").then(c => c.default.remove("access_token"));
              localStorage.removeItem("token");
              window.location.href = "/auth/login";
            }}
            className={cn(
              "mt-2 flex w-full items-center rounded-xl px-4 py-3 text-zinc-500 transition-all duration-200 hover:bg-red-500/10 hover:text-red-500 group",
              isCollapsed ? "justify-center" : ""
            )}
          >
            <LogOut size={20} className="group-hover:-translate-x-1 transition-transform" />
            {!isCollapsed && <span className="ml-3 text-sm font-medium">Log out</span>}
          </button>
        </div>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 min-w-0">
        <header className="flex h-20 items-center justify-between border-b border-white/5 bg-zinc-950/20 px-8 backdrop-blur-md">
          <div className="flex items-center gap-4">
             <Button variant="ghost" size="sm" className="md:hidden">
               <Menu size={24} />
             </Button>
             <h2 className="text-xl font-semibold">
               {sidebarItems.find(i => i.href === pathname)?.label || "Dashboard"}
             </h2>
          </div>
          <div className="flex items-center gap-4">
             <div className="flex h-10 w-10 items-center justify-center rounded-full bg-zinc-900 border border-white/10 overflow-hidden">
                <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="Avatar" />
             </div>
          </div>
        </header>
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
