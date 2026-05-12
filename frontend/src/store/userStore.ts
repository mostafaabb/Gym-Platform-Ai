import { create } from "zustand";

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  bio?: string;
  phone?: string;
  dateOfBirth?: string;
  gender?: "male" | "female" | "other";
  height?: number;
  weight?: number;
  fitnessGoal?: string;
  experience?: "beginner" | "intermediate" | "advanced";
  preferences?: {
    theme?: "light" | "dark" | "system";
    notifications?: boolean;
    emailUpdates?: boolean;
  };
}

export interface UserState {
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;

  setProfile: (profile: UserProfile | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  updateProfile: (updates: Partial<UserProfile>) => void;
  clearError: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  profile: null,
  isLoading: false,
  error: null,

  setProfile: (profile) => set({ profile }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  updateProfile: (updates) =>
    set((state) => ({
      profile: state.profile ? { ...state.profile, ...updates } : null,
    })),

  clearError: () => set({ error: null }),
}));
