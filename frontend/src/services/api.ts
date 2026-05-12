import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from "axios";
import { useAuthStore } from "@/store/authStore";
import Cookies from "js-cookie";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

class ApiClient {
  private axiosInstance: AxiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        "Content-Type": "application/json",
      },
      withCredentials: true,
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.axiosInstance.interceptors.request.use(
      (config: CustomAxiosRequestConfig) => {
        const token = Cookies.get("access_token") || useAuthStore.getState().token;

        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error) => {
        const config = error.config as CustomAxiosRequestConfig;

        if (error.response?.status === 401 && !config._retry) {
          config._retry = true;

          try {
            const refreshToken =
              Cookies.get("refresh_token") ||
              useAuthStore.getState().refreshToken;

            if (refreshToken) {
              const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken,
              });

              const { access_token, refresh_token } = response.data;

              Cookies.set("access_token", access_token, {
                expires: 1,
                path: "/",
              });
              Cookies.set("refresh_token", refresh_token, {
                expires: 7,
                path: "/",
              });

              useAuthStore.getState().setToken(access_token, refresh_token);

              config.headers.Authorization = `Bearer ${access_token}`;
              return this.axiosInstance(config);
            }
          } catch (refreshError) {
            useAuthStore.getState().logout();
            window.location.href = "/auth/login";
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Generic request method
  async request<T>(
    config: AxiosRequestConfig
  ): Promise<AxiosResponse<T, any>> {
    return this.axiosInstance.request<T>(config);
  }

  // GET request
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.get<T>(url, config);
    return response.data;
  }

  // POST request
  async post<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.axiosInstance.post<T>(url, data, config);
    return response.data;
  }

  // PUT request
  async put<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.axiosInstance.put<T>(url, data, config);
    return response.data;
  }

  // PATCH request
  async patch<T>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.axiosInstance.patch<T>(url, data, config);
    return response.data;
  }

  // DELETE request
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.delete<T>(url, config);
    return response.data;
  }

  // Get the raw axios instance
  getInstance(): AxiosInstance {
    return this.axiosInstance;
  }
}

export const apiClient = new ApiClient();

// Auth API endpoints
export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post("/auth/login", { email, password }),

  register: (email: string, password: string, name: string) =>
    apiClient.post("/auth/register", { email, password, name }),

  logout: () => apiClient.post("/auth/logout", {}),

  getCurrentUser: () => apiClient.get("/auth/me"),

  forgotPassword: (email: string) =>
    apiClient.post("/auth/forgot-password", { email }),

  resetPassword: (token: string, newPassword: string) =>
    apiClient.post("/auth/reset-password", { token, new_password: newPassword }),

  refreshToken: (refreshToken: string) =>
    apiClient.post("/auth/refresh", { refresh_token: refreshToken }),
};

// User API endpoints
export const userApi = {
  getProfile: () => apiClient.get("/user/profile"),

  updateProfile: (data: Record<string, unknown>) =>
    apiClient.put("/user/profile", data),

  uploadAvatar: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post("/user/avatar", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  changePassword: (currentPassword: string, newPassword: string) =>
    apiClient.post("/user/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
    }),
};

// Workout API endpoints
export const workoutApi = {
  getWorkouts: (params?: Record<string, unknown>) =>
    apiClient.get("/workouts", { params }),

  getWorkout: (id: string) => apiClient.get(`/workouts/${id}`),

  createWorkout: (data: Record<string, unknown>) =>
    apiClient.post("/workouts", data),

  updateWorkout: (id: string, data: Record<string, unknown>) =>
    apiClient.put(`/workouts/${id}`, data),

  deleteWorkout: (id: string) => apiClient.delete(`/workouts/${id}`),

  startWorkout: (id: string) =>
    apiClient.post(`/workouts/${id}/start`, {}),

  completeWorkout: (id: string, data: Record<string, unknown>) =>
    apiClient.post(`/workouts/${id}/complete`, data),
};

// Analytics API endpoints
export const analyticsApi = {
  getDashboard: (params?: Record<string, unknown>) =>
    apiClient.get("/analytics/dashboard", { params }),

  getProgress: (params?: Record<string, unknown>) =>
    apiClient.get("/analytics/progress", { params }),

  getStats: (params?: Record<string, unknown>) =>
    apiClient.get("/analytics/stats", { params }),
};

// AI Coach API endpoints
export const coachApi = {
  getCoachRecommendations: (params?: Record<string, unknown>) =>
    apiClient.get("/coach/recommendations", { params }),

  askCoach: (question: string) =>
    apiClient.post("/coach/ask", { question }),

  getWorkoutPlan: (id: string) => apiClient.get(`/coach/plans/${id}`),

  generateWorkoutPlan: (data: Record<string, unknown>) =>
    apiClient.post("/coach/generate-plan", data),
};

// Nutrition API endpoints
export const nutritionApi = {
  getMeals: (params?: Record<string, unknown>) =>
    apiClient.get("/nutrition/meals", { params }),

  logMeal: (data: Record<string, unknown>) =>
    apiClient.post("/nutrition/log", data),

  getNutritionPlan: (id: string) => apiClient.get(`/nutrition/plans/${id}`),

  generateNutritionPlan: (data: Record<string, unknown>) =>
    apiClient.post("/nutrition/generate-plan", data),

  getNutritionStats: (params?: Record<string, unknown>) =>
    apiClient.get("/nutrition/stats", { params }),
};
