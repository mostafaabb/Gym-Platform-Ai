"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Dumbbell, Mail, ArrowLeft, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/Button";

export default function ForgotPasswordPage() {
  const [isLoading, setIsLoading] = React.useState(false);
  const [isSubmitted, setIsSubmitted] = React.useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      setIsSubmitted(true);
    }, 2000);
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
        className="w-full max-w-md relative z-10"
      >
        <div className="card-premium p-10 space-y-8">
          <div className="text-center">
            <Link href="/" className="inline-flex items-center gap-2 group mb-6">
              <Dumbbell className="text-primary group-hover:scale-110 transition-transform" size={32} />
              <span className="text-2xl font-black tracking-tighter text-white">GYMFLOW</span>
            </Link>
            <h1 className="text-3xl font-bold text-white tracking-tight">Recover Password</h1>
            <p className="text-zinc-500 mt-2">Enter your email to receive recovery instructions.</p>
          </div>

          {!isSubmitted ? (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-bold text-zinc-500 uppercase tracking-widest ml-1">Email Address</label>
                <div className="relative group">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-primary transition-colors" size={20} />
                  <input 
                    type="email" 
                    required
                    placeholder="name@example.com"
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
                ) : "Send Reset Link"}
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
              className="text-center py-6"
            >
              <div className="inline-flex h-20 w-20 items-center justify-center rounded-3xl bg-primary/10 text-primary mb-6">
                <Sparkles size={40} />
              </div>
              <h2 className="text-2xl font-bold text-white">Check your inbox</h2>
              <p className="text-zinc-500 mt-4 leading-relaxed">
                We have sent a password reset link to your email. Please check your spam folder if you don&apos;t see it.
              </p>
              <Button 
                onClick={() => setIsSubmitted(false)}
                variant="ghost" 
                className="mt-8 text-primary hover:bg-primary/5"
              >
                Try a different email
              </Button>
              <div className="mt-6 pt-6 border-t border-white/5">
                <Link href="/auth/login" className="inline-flex items-center text-sm text-zinc-500 hover:text-white transition-colors">
                  <ArrowLeft size={16} className="mr-2" />
                  Return to login
                </Link>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
