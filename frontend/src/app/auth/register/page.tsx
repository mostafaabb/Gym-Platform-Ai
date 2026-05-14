"use client";

import React, { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Dumbbell, Loader2, ArrowRight, User, Mail, Shield } from "lucide-react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { Button } from "@/components/ui/Button";

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: ""
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await api.post("/auth/register", {
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName,
        full_name: `${formData.firstName} ${formData.lastName}`
      });
      
      // Redirect to login after successful registration
      router.push("/auth/login?registered=true");
    } catch (err: any) {
      console.error("Registration error:", err);
      const errorDetail = err.response?.data?.detail;
      const errorMessage = typeof errorDetail === "string" 
        ? errorDetail 
        : Array.isArray(errorDetail) 
          ? errorDetail[0]?.msg || "Registration failed. Please try again."
          : "Registration failed. Please try again.";

      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-950 p-4 selection:bg-primary/30">
      {/* Background Orbs */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] h-[500px] w-[500px] rounded-full bg-primary/10 blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-[-10%] right-[-10%] h-[500px] w-[500px] rounded-full bg-purple-500/10 blur-[120px] animate-pulse-slow" style={{ animationDelay: "2s" }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="relative z-10 w-full max-w-lg">
          <div className="flex flex-col items-center mb-10">
          <Link href="/" className="mb-6 flex items-center gap-3 group">
             <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary shadow-xl shadow-primary/20 transition-transform group-hover:scale-110">
                <Dumbbell className="text-white" size={32} />
             </div>
             <span className="text-3xl font-bold tracking-tight text-white">GymFlow <span className="text-primary">AI</span></span>
          </Link>
          <h1 className="text-4xl font-bold text-white tracking-tight">Join the elite</h1>
          <p className="text-zinc-400 mt-3 text-center">Experience the next generation of performance management.</p>
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
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-zinc-300 ml-1">First Name</label>
                <div className="relative group">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-zinc-500 transition-colors group-focus-within:text-primary" />
                  <input 
                    type="text" 
                    value={formData.firstName}
                    onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                    placeholder="John"
                    className="w-full rounded-xl border border-white/5 bg-white/5 py-3.5 pl-12 pr-4 text-base text-white outline-none transition-all focus:border-primary/50 focus:bg-white/10 placeholder:text-zinc-600"
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-zinc-300 ml-1">Last Name</label>
                <input 
                  type="text" 
                  value={formData.lastName}
                  onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                  placeholder="Doe"
                  className="w-full rounded-xl border border-white/5 bg-white/5 py-3.5 px-4 text-base text-white outline-none transition-all focus:border-primary/50 focus:bg-white/10 placeholder:text-zinc-600"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-300 ml-1">Email Address</label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-zinc-500 transition-colors group-focus-within:text-primary" />
                <input 
                  type="email" 
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  placeholder="name@example.com"
                  className="w-full rounded-xl border border-white/5 bg-white/5 py-3.5 pl-12 pr-4 text-base text-white outline-none transition-all focus:border-primary/50 focus:bg-white/10 placeholder:text-zinc-600"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-zinc-300 ml-1">Password</label>
              <div className="relative group">
                <Shield className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-zinc-500 transition-colors group-focus-within:text-primary" />
                <input 
                  type="password" 
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  placeholder="Minimum 8 characters"
                  className="w-full rounded-xl border border-white/5 bg-white/5 py-3.5 pl-12 pr-4 text-base text-white outline-none transition-all focus:border-primary/50 focus:bg-white/10 placeholder:text-zinc-600"
                  required
                />
              </div>
            </div>

            <div className="flex items-center gap-3 px-1">
              <input type="checkbox" className="h-5 w-5 rounded-lg border-white/10 bg-white/5 text-primary focus:ring-primary/50" required />
              <span className="text-xs text-zinc-400">
                I agree to the <Link href="#" className="text-primary hover:underline">Terms of Service</Link> and <Link href="#" className="text-primary hover:underline">Privacy Policy</Link>
              </span>
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
                  Create Elite Account
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
              <span className="bg-zinc-900/50 px-4 text-zinc-500">Already a member?</span>
            </div>
          </div>

          <div className="text-center">
            <Link href="/auth/login">
               <Button variant="ghost" className="text-zinc-400 hover:text-white hover:bg-white/5 transition-all text-sm w-full h-12 rounded-xl">
                 Sign in to your account
               </Button>
            </Link>
          </div>
        </div>
        </div>

      </motion.div>
    </div>
  );
}

