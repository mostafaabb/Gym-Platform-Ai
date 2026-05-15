"use client";

import React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { Dumbbell, Key, Lock, ArrowLeft, Loader2, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import api from "@/lib/api";

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const email = searchParams.get("email") || "";
  
  const [token, setToken] = React.useState("");
  const [newPassword, setNewPassword] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(false);
  const [isSuccess, setIsSuccess] = React.useState(false);
  const [error, setError] = React.useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    
    try {
      await api.post("/auth/reset-password", { token, new_password: newPassword });
      setIsSuccess(true);
      setTimeout(() => {
        router.push("/auth/login");
      }, 3000);
    } catch (err: any) {
      console.error("Reset password failed:", err);
      setError(err.response?.data?.message || "Invalid or expired verification code.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Glows */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/10 blur-[120px] rounded-full animate-pulse" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-600/10 blur-[120px] rounded-full animate-pulse" />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="w-full max-w-md relative z-10">
          <div className="card-premium p-10 space-y-8">
            <div className="text-center">
              <Link href="/" className="inline-flex items-center gap-2 group mb-6">
                <Dumbbell className="text-primary group-hover:scale-110 transition-transform" size={32} />
                <span className="text-2xl font-black tracking-tighter text-white">GYMFLOW</span>
              </Link>
              <h1 className="text-3xl font-bold text-white tracking-tight">Set New Password</h1>
              <p className="text-zinc-500 mt-2">Resetting for <span className="text-white font-medium">{email}</span></p>
            </div>

            {!isSuccess ? (
              <form onSubmit={handleSubmit} className="space-y-6">
                {error && (
                  <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-500 text-sm text-center">
                    {error}
                  </div>
                )}
                
                <div className="space-y-2">
                  <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest ml-1">Verification Code</label>
                  <div className="relative group">
                    <Key className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-primary transition-colors" size={20} />
                    <input 
                      type="text" 
                      required
                      value={token}
                      onChange={(e) => setToken(e.target.value)}
                      placeholder="RESET_123"
                      className="w-full h-14 rounded-2xl border border-white/5 bg-white/5 pl-12 pr-4 text-white outline-none focus:border-primary/50 focus:bg-white/10 transition-all font-mono tracking-widest"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest ml-1">New Password</label>
                  <div className="relative group">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-primary transition-colors" size={20} />
                    <input 
                      type="password" 
                      required
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full h-14 rounded-2xl border border-white/5 bg-white/5 pl-12 pr-4 text-white outline-none focus:border-primary/50 focus:bg-white/10 transition-all"
                    />
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full h-14 btn-primary text-lg"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <Loader2 className="animate-spin mr-2" size={20} />
                  ) : "Update Password"}
                </Button>

                <div className="text-center">
                  <Link href="/auth/login" className="inline-flex items-center text-sm text-zinc-500 hover:text-white transition-colors">
                    <ArrowLeft size={16} className="mr-2" />
                    Back to login
                  </Link>
                </div>
              </form>
            ) : (
              <motion.div 
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
              >
                <div className="text-center py-6">
                  <div className="inline-flex h-20 w-20 items-center justify-center rounded-3xl bg-emerald-500/10 text-emerald-500 mb-6">
                    <CheckCircle2 size={40} />
                  </div>
                  <h2 className="text-2xl font-bold text-white">Password Updated!</h2>
                  <p className="text-zinc-500 mt-4 leading-relaxed">
                    Your password has been reset successfully. Redirecting you to login...
                  </p>
                  <Loader2 className="animate-spin mx-auto mt-8 text-emerald-500/50" size={24} />
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
