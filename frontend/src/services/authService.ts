import axios, { AxiosResponse } from 'axios';
import env from '../config/env';

// Types matching our backend API
export interface User {
  id: number;
  name: string;
  username: string;
  email: string;
  profile_image_url: string;
  is_superuser: boolean;
  tier_id: number | null;
  // Japanese Learning Fields
  native_language: string;
  current_jlpt_level: string;
  target_jlpt_level: string;
  daily_study_goal: number;
  study_streak: number;
  best_streak: number;
  total_sentences_learned: number;
  total_study_time_minutes: number;
  preferred_study_time: string;
  study_reminders_enabled: boolean;
  audio_enabled: boolean;
  furigana_enabled: boolean;
  romaji_enabled: boolean;
  difficulty_preference: string;
  last_study_date: string | null;
}

export interface LoginCredentials {
  username: string; // Our API uses username, not email for login
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterCredentials {
  name: string;
  username: string;
  email: string;
  password: string;
}

// Create API instance with proper configuration
const api = axios.create({
  baseURL: env.API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  // Log requests in development
  if (env.ENABLE_DEBUG_LOGS && __DEV__) {
    console.log(`🔗 API Request: ${config.method?.toUpperCase()} ${config.url}`);
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    if (env.ENABLE_DEBUG_LOGS && __DEV__) {
      console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    }
    return response;
  },
  (error) => {
    if (env.ENABLE_DEBUG_LOGS && __DEV__) {
      console.log(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data);
    }
    
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Token expired or invalid
      console.log('🔐 Authentication error - token may be expired');
    }
    
    return Promise.reject(error);
  }
);

export class AuthService {
  /**
   * Login with username/password - matches FastAPI OAuth2PasswordRequestForm
   */
  static async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      // Our backend expects form data for OAuth2PasswordRequestForm
      const formData = new FormData();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response: AxiosResponse<LoginResponse> = await api.post('/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      return response.data;
    } catch (error: any) {
      console.error('Login failed:', error.response?.data || error.message);
      throw new Error(
        error.response?.data?.detail || 
        'Login failed. Please check your credentials.'
      );
    }
  }

  /**
   * Register new user
   */
  static async register(credentials: RegisterCredentials): Promise<User> {
    try {
      const response: AxiosResponse<User> = await api.post('/user', credentials);
      return response.data;
    } catch (error: any) {
      console.error('Registration failed:', error.response?.data || error.message);
      
      // Handle validation errors
      if (error.response?.data?.detail && Array.isArray(error.response.data.detail)) {
        const validationErrors = error.response.data.detail
          .map((err: any) => err.msg)
          .join(', ');
        throw new Error(`Registration failed: ${validationErrors}`);
      }
      
      throw new Error(
        error.response?.data?.detail || 
        'Registration failed. Please try again.'
      );
    }
  }

  /**
   * Get current user profile using token
   */
  static async getCurrentUser(): Promise<User> {
    try {
      const response: AxiosResponse<User> = await api.get('/users/me');
      return response.data;
    } catch (error: any) {
      console.error('Get current user failed:', error.response?.data || error.message);
      throw new Error('Failed to get user profile');
    }
  }

  /**
   * Set authorization token for future requests
   */
  static setAuthToken(token: string): void {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  /**
   * Remove authorization token
   */
  static removeAuthToken(): void {
    delete api.defaults.headers.common['Authorization'];
  }

  /**
   * Test API connection
   */
  static async testConnection(): Promise<boolean> {
    try {
      await api.get('/sentences');
      return true;
    } catch (error) {
      console.error('API connection test failed:', error);
      return false;
    }
  }
}

export default api;