import { useState, useEffect } from "react";
import api from "@/lib/api";

export const useDashboardData = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const meResponse = await api.get("/auth/me");
        const { user, auth, context } = meResponse.data;
        
        let stats = null;
        let progress = null;
        let nutrition = null;
        let leaderboard = null;

        if (context?.member_id) {
          try {
            const analyticsResponse = await api.get(`/analytics/members/${context.member_id}`);
            stats = analyticsResponse.data.stats;
            progress = analyticsResponse.data.progress;
            
            const nutritionResponse = await api.get(`/analytics/members/${context.member_id}/nutrition`);
            nutrition = nutritionResponse.data;

            const leaderboardResponse = await api.get(`/api/v1/leaderboard?gym_id=${context.gym_id}&limit=5`);
            leaderboard = leaderboardResponse.data;
          } catch (err) {
            console.warn("Could not fetch analytics, using defaults:", err);
          }
        }

        setData({ user, auth, context, stats, progress, nutrition, leaderboard });
      } catch (err: any) {
        setError(err.message || "Failed to fetch dashboard data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, loading, error };
};
