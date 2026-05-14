"use client";

import React, { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Dumbbell, Loader2, ArrowRight, Github, Lock, Mail } from "lucide-react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { Button } from "@/components/ui/Button";

export default function LoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post("/auth/login", {
        email: email,
        password: password
      });
      
      // Store token in local storage
      localStorage.setItem("token", response.data.access_token);
      
      // Redirect to member dashboard
      router.push("/dashboard/member");
    } catch (err: any) {
      console.error("Login error:", err);
      const errorDetail = err.response?.data?.detail;
      const errorMessage = typeof errorDetail === "string" 
        ? errorDetail 
        : Array.isArray(errorDetail) 
          ? errorDetail[0]?.msg || "Invalid input data"
          : "Failed to login. Please check your credentials.";
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950 p-4 selection:bg-primary/30">
      {/* Background Orbs */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] right-[-10%] h-[500px] w-[500px] rounded-full bg-primary/20 blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-10%] left-[-10%] h-[500px] w-[500px] rounded-full bg-accent/10 blur-[120px] animate-pulse-slow" style={{ animationDelay: "2s" }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="relative z-10 w-full max-w-md">
          <div className="flex flex-col items-center mb-10">
          <Link href="/" className="mb-6 flex items-center gap-3 group">
             <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary shadow-xl shadow-primary/20 transition-transform group-hover:scale-110">
                <Dumbbell className="text-white" size={32} />
             </div>
             <span className="text-3xl font-bold tracking-tight text-white">GymFlow <span className="text-primary">AI</span></span>
          </Link>
          <h1 className="text-4xl font-bold text-white tracking-tight">Welcome back</h1>
          <p className="text-zinc-400 mt-3 text-center">Your elite fitness journey continues here.</p>
        </div>

        <div className="card-premium">
          {error && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
            >
              <div className="mb-6 rounded-xl bg-red-500/10 border border-red-500/20 p-4 text-sm text-red-500 text-center">
                {error}
              </div>
            </motion.div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-300 ml-1">Email Address</label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-zinc-500 transition-colors group-focus-within:text-primary" />
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full rounded-xl border border-white/5 bg-white/5 py-3.5 pl-12 pr-4 text-base text-white outline-none transition-all focus:border-primary/50 focus:bg-white/10 placeholder:text-zinc-600"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between px-1">
                <label className="text-sm font-medium text-zinc-300">Password</label>
                <Link href="/auth/forgot-password" title="Recover your account" className="text-xs text-primary hover:text-primary/80 transition-colors">Forgot password?</Link>
              </div>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-zinc-500 transition-colors group-focus-within:text-primary" />
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-xl border border-white/5 bg-white/5 py-3.5 pl-12 pr-4 text-base text-white outline-none transition-all focus:border-primary/50 focus:bg-white/10 placeholder:text-zinc-600"
                  required
                />
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full h-14 btn-primary flex items-center justify-center gap-2"
              disabled={isLoading}
            >
              {isLoading ? (
                <Loader2 className="animate-spin" size={20} />
              ) : (
                <>
                  Sign In
                  <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </Button>
          </form>

          <div className="relative my-10">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/5"></div>
            </div>
            <div className="relative flex justify-center text-xs uppercase tracking-widest">
              <span className="bg-zinc-900/50 px-4 text-zinc-500">Or connect via</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Button variant="outline" className="h-12 rounded-xl border-white/5 bg-white/5 text-white hover:bg-white/10 hover:border-white/10 transition-all">
              <Github className="mr-2" size={18} />
              GitHub
            </Button>
            <Button variant="outline" className="h-12 rounded-xl border-white/5 bg-white/5 text-white hover:bg-white/10 hover:border-white/10 transition-all">
              <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.66l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Google
            </Button>
          </div>
        </div>
        </div>

        <p className="mt-10 text-center text-sm text-zinc-500">
          Don&apos;t have an account yet?{" "}
          <Link href="/auth/register" className="text-primary hover:text-primary/80 transition-colors font-semibold">
            Join the elite
          </Link>
        </p>
      </motion.div>
    </div>
  );
}

