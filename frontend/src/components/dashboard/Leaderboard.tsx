import React from "react";
import { motion } from "framer-motion";
import { Trophy, Medal, Award, Star } from "lucide-react";
import { cn } from "@/lib/utils";

interface LeaderboardEntry {
  rank: number;
  name: string;
  score: number;
  avg_form: number;
  avatar?: string;
}

interface LeaderboardProps {
  entries: LeaderboardEntry[];
  title?: string;
}

const Leaderboard: React.FC<LeaderboardProps> = ({ entries, title = "Gym Leaderboard" }) => {
  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1: return <Trophy className="text-amber-400" size={18} />;
      case 2: return <Medal className="text-zinc-300" size={18} />;
      case 3: return <Medal className="text-amber-700" size={18} />;
      default: return <span className="text-zinc-500 text-xs font-bold w-4 text-center">{rank}</span>;
    }
  };

  return (
    <div className="rounded-3xl border border-white/5 bg-zinc-900/50 p-6 backdrop-blur-xl">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Award className="text-primary" size={20} />
          {title}
        </h3>
        <Star className="text-zinc-500" size={16} />
      </div>

      <div className="space-y-4">
        {entries.map((entry, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.1 }}
            className={cn(
              "flex items-center justify-between p-3 rounded-2xl transition-all",
              i === 0 ? "bg-primary/10 border border-primary/20" : "hover:bg-white/5"
            )}
          >
            <div className="flex items-center gap-4">
              <div className="flex h-8 w-8 items-center justify-center shrink-0">
                {getRankIcon(entry.rank)}
              </div>
              <div className="h-10 w-10 rounded-full bg-zinc-800 border border-white/10 overflow-hidden shrink-0">
                <img 
                  src={entry.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${entry.name}`} 
                  alt={entry.name} 
                />
              </div>
              <div>
                <p className="text-sm font-bold text-white leading-none">{entry.name}</p>
                <p className="text-[10px] text-zinc-500 mt-1 uppercase tracking-widest font-bold">
                  Form: {entry.avg_form.toFixed(1)}%
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm font-black text-primary">{entry.score}</p>
              <p className="text-[9px] text-zinc-600 uppercase font-bold">Pts</p>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Leaderboard;
