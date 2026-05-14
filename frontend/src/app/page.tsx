"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  Mic, 
  Activity, 
  Target, 
  Users, 
  Zap, 
  ChevronRight, 
  CheckCircle2,
  BrainCircuit,
  Dumbbell,
  LineChart,
  ShieldCheck
} from "lucide-react";
import { Button } from "@/components/ui/Button";

const Navbar = () => {
  return (
    <motion.nav 
      initial={{ y: -100 }}
      animate={{ y: 0 }}
    >
      <div className="fixed top-0 z-50 w-full border-b border-white/10 bg-black/50 backdrop-blur-xl container mx-auto flex h-20 items-center justify-between px-6">
        <div className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary shadow-lg shadow-primary/20">
            <Dumbbell className="text-white" size={24} />
          </div>
          <span className="text-xl font-bold tracking-tighter text-white">GymFlow AI</span>
        </div>
        
        <div className="hidden items-center gap-8 md:flex">
          <Link href="#features" className="text-sm font-medium text-zinc-400 transition-colors hover:text-white">Features</Link>
          <Link href="#ai" className="text-sm font-medium text-zinc-400 transition-colors hover:text-white">AI Coach</Link>
          <Link href="#pricing" className="text-sm font-medium text-zinc-400 transition-colors hover:text-white">Pricing</Link>
        </div>

        <div className="flex items-center gap-4">
          <Link href="/auth/login">
            <Button variant="ghost" className="text-zinc-400 hover:text-white">Login</Button>
          </Link>
          <Link href="/auth/register">
            <Button className="rounded-full bg-white text-black hover:bg-zinc-200">Get Started</Button>
          </Link>
        </div>
      </div>
    </motion.nav>
  );
};

const FeatureCard = ({ icon: Icon, title, description, delay }: { icon: any, title: string, description: string, delay: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
    viewport={{ once: true }}
  >
    <div className="group relative overflow-hidden rounded-2xl border border-white/5 bg-zinc-900/50 p-8 transition-all hover:border-primary/50 hover:bg-zinc-900">
    <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-zinc-800 transition-colors group-hover:bg-primary/20">
      <Icon className="text-zinc-400 transition-colors group-hover:text-primary" size={24} />
    </div>
      <h3 className="mb-2 text-xl font-semibold text-white">{title}</h3>
      <p className="text-sm leading-relaxed text-zinc-400">{description}</p>
    </div>
  </motion.div>
);

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-black text-white selection:bg-primary/30">
      <Navbar />

      {/* Hero Section */}
      <section className="relative flex min-h-screen items-center justify-center overflow-hidden pt-20">
        <div className="absolute inset-0 z-0">
          <div className="absolute top-1/4 left-1/4 h-[500px] w-[500px] rounded-full bg-primary/10 blur-[120px]" />
          <div className="absolute bottom-1/4 right-1/4 h-[500px] w-[500px] rounded-full bg-purple-500/10 blur-[120px]" />
        </div>

        <div className="container relative z-10 px-6 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 backdrop-blur-md">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex h-2 w-2 rounded-full bg-primary"></span>
              </span>
              <span className="text-xs font-medium text-zinc-300 tracking-wide uppercase">Next Gen Gym OS is Live</span>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <h1 className="mb-8 text-5xl font-extrabold tracking-tight md:text-8xl">
            Elevate Your Gym <br />
            <span className="bg-gradient-to-r from-primary via-blue-400 to-purple-500 bg-clip-text text-transparent">
              With Pure Intelligence
            </span>
            </h1>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <p className="mx-auto mb-10 max-w-2xl text-lg text-zinc-400 md:text-xl">
              Real-time voice coaching, posture analysis, and automated management. 
              The only OS your gym will ever need. Built for performance.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button size="lg" className="h-14 rounded-full bg-white px-8 text-lg font-semibold text-black hover:bg-zinc-200">
              Start Free Trial
              <ChevronRight className="ml-2" size={20} />
            </Button>
            <Button size="lg" variant="outline" className="h-14 rounded-full border-white/10 bg-white/5 px-8 text-lg font-semibold text-white backdrop-blur-md hover:bg-white/10">
              Watch Demo
            </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24">
        <div className="container mx-auto px-6">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-3xl font-bold md:text-5xl">Everything you need to <br /> scale your fitness empire</h2>
            <p className="text-zinc-500">Powerful tools for owners, trainers, and members.</p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <FeatureCard 
              icon={Mic}
              title="AI Voice Coach"
              description="Real-time conversational AI that guides members through workouts, monitors rest, and provides motivation."
              delay={0.1}
            />
            <FeatureCard 
              icon={Activity}
              title="Posture Analysis"
              description="Proprietary computer vision detects form errors in real-time, preventing injury and maximizing results."
              delay={0.2}
            />
            <FeatureCard 
              icon={BrainCircuit}
              title="Workout Intelligence"
              description="Hyper-personalized workout generation based on biometrics, goals, and recovery status."
              delay={0.3}
            />
            <FeatureCard 
              icon={Users}
              title="Multi-Tenant SaaS"
              description="Scale your gym chain with enterprise-grade management, trainer dashboards, and billing."
              delay={0.4}
            />
            <FeatureCard 
              icon={LineChart}
              title="Advanced Analytics"
              description="Deep insights into gym utilization, member retention, and progress tracking."
              delay={0.5}
            />
            <FeatureCard 
              icon={ShieldCheck}
              title="Secure & Private"
              description="Enterprise-level security for all user data, biometrics, and financial records."
              delay={0.6}
            />
          </div>
        </div>
      </section>

      {/* AI Showcase */}
      <section id="ai" className="overflow-hidden py-24 bg-zinc-950">
        <div className="container mx-auto px-6">
          <div className="flex flex-col items-center gap-16 lg:flex-row">
            <div className="flex-1">
              <motion.div
                initial={{ opacity: 0, x: -50 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.8 }}
                viewport={{ once: true }}
              >
                <div className="mb-6 inline-flex rounded-lg bg-primary/10 p-3 text-primary">
                  <BrainCircuit size={32} />
                </div>
                <h2 className="mb-6 text-4xl font-bold leading-tight md:text-5xl">
                  AI that knows your <br /> members better than anyone.
                </h2>
                <p className="mb-8 text-lg text-zinc-400">
                  Our neural engines process thousands of data points per second. 
                  From joint angles to voice fatigue, GymFlow AI provides 
                  coaching that feels human but thinks with superhuman precision.
                </p>
                <ul className="space-y-4">
                  {[
                    "Form correction for 50+ exercises",
                    "Dynamic rest period adjustment",
                    "Progressive overload automation",
                    "Injury risk prediction"
                  ].map((item, i) => (
                    <li key={i} className="flex items-center gap-3 text-zinc-300">
                      <CheckCircle2 className="text-primary" size={20} />
                      {item}
                    </li>
                  ))}
                </ul>
              </motion.div>
            </div>
            <div className="relative flex-1">
              <motion.div
                initial={{ opacity: 0, scale: 0.8, rotate: 5 }}
                whileInView={{ opacity: 1, scale: 1, rotate: 0 }}
                transition={{ duration: 1 }}
                viewport={{ once: true }}
              >
                <div className="relative rounded-3xl border border-white/10 bg-zinc-900 p-2 shadow-2xl">
                  <div className="aspect-video w-full overflow-hidden rounded-2xl bg-black">
                   {/* Placeholder for AI Dashboard Visual */}
                   <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-zinc-900 to-black p-12">
                      <div className="grid grid-cols-2 gap-4 w-full h-full">
                         <div className="rounded-xl bg-zinc-800/50 p-4 border border-white/5 flex flex-col justify-between">
                            <Activity className="text-primary" size={20} />
                            <div>
                               <p className="text-[10px] text-zinc-500 uppercase tracking-widest">Form Score</p>
                               <p className="text-2xl font-bold">98%</p>
                            </div>
                         </div>
                         <div className="rounded-xl bg-zinc-800/50 p-4 border border-white/5 flex flex-col justify-between">
                            <Zap className="text-amber-400" size={20} />
                            <div>
                               <p className="text-[10px] text-zinc-500 uppercase tracking-widest">Intensity</p>
                               <p className="text-2xl font-bold">High</p>
                            </div>
                         </div>
                         <div className="col-span-2 rounded-xl bg-zinc-800/50 p-4 border border-white/5">
                            <div className="flex items-center justify-between mb-4">
                               <p className="text-[10px] text-zinc-500 uppercase tracking-widest">Joint Stability</p>
                               <div className="h-2 w-24 rounded-full bg-zinc-700 overflow-hidden">
                                  <div className="h-full w-3/4 bg-primary" />
                               </div>
                            </div>
                            <div className="h-24 w-full bg-zinc-900/50 rounded-lg flex items-end gap-1 p-2">
                               {[40, 70, 45, 90, 65, 80, 50, 85].map((h, i) => (
                                  <div key={i} className="flex-1 bg-primary/30 rounded-t-sm" style={{ height: `${h}%` }} />
                               ))}
                            </div>
                         </div>
                      </div>
                   </div>
                </div>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24">
        <div className="container mx-auto px-6">
          <div className="rounded-3xl bg-gradient-to-br from-primary/20 via-zinc-900 to-purple-500/10 p-12 text-center border border-white/5">
            <h2 className="mb-6 text-3xl font-bold md:text-5xl">Ready to transform your gym?</h2>
            <p className="mx-auto mb-10 max-w-xl text-zinc-400">
              Join 500+ forward-thinking gyms already using GymFlow AI to dominate their local markets.
            </p>
            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button size="lg" className="rounded-full bg-white px-8 text-black hover:bg-zinc-200">
                Start 14-Day Free Trial
              </Button>
              <Button size="lg" variant="ghost" className="text-white hover:bg-white/5">
                Talk to Sales
              </Button>
            </div>
          </div>
        </div>
      </section>

      <footer className="border-t border-white/5 py-12 bg-black">
        <div className="container mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-2">
            <Dumbbell className="text-primary" size={20} />
            <span className="font-bold tracking-tighter">GymFlow AI</span>
          </div>
          <div className="flex gap-8 text-sm text-zinc-500">
            <Link href="#" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link href="#" className="hover:text-white transition-colors">Terms of Service</Link>
            <Link href="#" className="hover:text-white transition-colors">Contact</Link>
          </div>
          <p className="text-sm text-zinc-600">© 2025 GymFlow AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
