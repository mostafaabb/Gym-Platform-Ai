"use client";

import React from "react";
import { User, Mail, Shield, Bell, CreditCard, LogOut } from "lucide-react";
import { Button } from "@/components/ui/Button";
import api from "@/lib/api";

export default function ProfilePage() {
  const [userData, setUserData] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await api.get("/auth/me");
        setUserData(response.data.user);
      } catch (err) {
        console.error("Failed to fetch user:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  const fullName = userData?.full_name || "Gym Member";
  const email = userData?.email || "member@example.com";
  const [firstName, lastName] = fullName.split(" ");

  if (loading) {
    return <div className="flex h-96 items-center justify-center text-white">Loading your profile...</div>;
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight">Profile Settings</h1>
        <p className="text-zinc-500">Manage your elite account and preferences.</p>
      </div>

      <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
        <div className="md:col-span-1 space-y-4">
           <div className="flex flex-col items-center p-8 rounded-3xl border border-white/5 bg-zinc-900/50 backdrop-blur-sm">
              <div className="relative h-24 w-24 overflow-hidden rounded-full border-2 border-primary">
                 <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${fullName}`} alt="Avatar" />
              </div>
              <h3 className="mt-4 text-xl font-bold text-white">{fullName}</h3>
              <p className="text-sm text-zinc-500 uppercase tracking-widest text-[10px] font-black">{userData?.role?.replace("_", " ")}</p>
              <Button variant="outline" size="sm" className="mt-6 w-full rounded-xl border-white/10 text-xs">
                 Change Avatar
              </Button>
           </div>
           
           <nav className="space-y-1">
              {[
                { icon: User, label: "Personal Info", active: true },
                { icon: Bell, label: "Notifications", active: false },
                { icon: Shield, label: "Security", active: false },
                { icon: CreditCard, label: "Billing", active: false },
              ].map((item, i) => (
                <button key={i} className={`flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all ${item.active ? 'bg-primary text-white' : 'text-zinc-500 hover:bg-white/5 hover:text-white'}`}>
                   <item.icon size={18} />
                   {item.label}
                </button>
              ))}
              <button 
                onClick={() => {
                  import("js-cookie").then(c => c.default.remove("access_token"));
                  localStorage.removeItem("token");
                  window.location.href = "/auth/login";
                }}
                className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-red-500 hover:bg-red-500/10 transition-all mt-4"
              >
                 <LogOut size={18} />
                 Logout
              </button>
           </nav>
        </div>

        <div className="md:col-span-2 space-y-6">
           <div className="rounded-3xl border border-white/5 bg-zinc-900/30 p-8 space-y-6">
              <div className="grid grid-cols-2 gap-6">
                 <div className="space-y-2">
                    <label className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">First Name</label>
                    <input type="text" defaultValue={firstName} className="w-full rounded-xl border border-white/5 bg-white/5 py-3 px-4 text-white outline-none focus:border-primary/50" />
                 </div>
                 <div className="space-y-2">
                    <label className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Last Name</label>
                    <input type="text" defaultValue={lastName || ""} className="w-full rounded-xl border border-white/5 bg-white/5 py-3 px-4 text-white outline-none focus:border-primary/50" />
                 </div>
              </div>
              <div className="space-y-2">
                 <label className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Email Address</label>
                 <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
                    <input type="email" defaultValue={email} className="w-full rounded-xl border border-white/5 bg-white/5 py-3 pl-12 pr-4 text-white outline-none focus:border-primary/50" />
                 </div>
              </div>
              <div className="pt-4">
                 <Button className="w-full md:w-auto px-8 rounded-xl bg-primary text-white">
                    Save Changes
                 </Button>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}
