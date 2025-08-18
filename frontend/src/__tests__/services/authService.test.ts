import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthService } from '../../services/authService';

// Mock axios and AsyncStorage
jest.mock('axios');
jest.mock('@react-native-async-storage/async-storage');

const mockedAxios = axios as jest.Mocked<typeof axios>;
const mockedAsyncStorage = AsyncStorage as jest.Mocked<typeof AsyncStorage>;

// Mock API responses
const mockLoginResponse = {
  data: {
    access_token: 'mock-jwt-token',
    token_type: 'bearer',
  }
};

const mockUserResponse = {
  data: {
    id: 1,
    name: 'Test User',
    email: 'test@example.com',
    username: 'testuser',
    profile_image_url: 'https://example.com/avatar.jpg',
    is_superuser: false,
    tier_id: null,
    native_language: 'English',
    current_jlpt_level: 'N5',
    target_jlpt_level: 'N3',
    daily_study_goal: 10,
    study_streak: 5,
    best_streak: 15,
    total_sentences_learned: 50,
    total_study_time_minutes: 300,
    preferred_study_time: '18:00',
    study_reminders_enabled: true,
    audio_enabled: true,
    furigana_enabled: true,
    romaji_enabled: false,
    difficulty_preference: 'mixed',
    last_study_date: '2023-01-01'
  }
};

const mockRegisterResponse = {
  data: mockUserResponse.data
};

describe('AuthService', () => {
  // Mock the axios instance that AuthService uses
  const mockAxiosInstance = {
    post: jest.fn(),
    get: jest.fn(),
    defaults: {
      headers: {
        common: {}
      }
    }
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Setup axios create mock to return our mock instance
    mockedAxios.create.mockReturnValue(mockAxiosInstance as any);
  });

  describe('login', () => {
    it('should login successfully with valid credentials', async () => {
      mockAxiosInstance.post.mockResolvedValueOnce(mockLoginResponse);
      
      const result = await AuthService.login({
        username: 'test@example.com',
        password: 'password123'
      });
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/login', expect.any(FormData), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      expect(result).toEqual(mockLoginResponse.data);
    });

    it('should throw error on login failure', async () => {
      const errorResponse = {
        response: {
          status: 401,
          data: { detail: 'Invalid credentials' }
        }
      };
      
      mockAxiosInstance.post.mockRejectedValueOnce(errorResponse);
      
      await expect(AuthService.login({
        username: 'wrong@email.com',
        password: 'wrongpassword'
      })).rejects.toThrow('Invalid credentials');
    });

    it('should handle network errors', async () => {
      const networkError = new Error('Network Error');
      mockAxiosInstance.post.mockRejectedValueOnce(networkError);
      
      await expect(AuthService.login({
        username: 'test@example.com',
        password: 'password123'
      })).rejects.toThrow();
    });
  });

  describe('register', () => {
    it('should register successfully with valid data', async () => {
      mockAxiosInstance.post.mockResolvedValueOnce(mockRegisterResponse);
      
      const result = await AuthService.register({
        name: 'Test User',
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123'
      });
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/user', {
        name: 'Test User',
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123'
      });
      
      expect(result).toEqual(mockRegisterResponse.data);
    });

    it('should throw error on registration failure', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: { detail: 'Email already exists' }
        }
      };
      
      mockAxiosInstance.post.mockRejectedValueOnce(errorResponse);
      
      await expect(AuthService.register({
        name: 'Test User',
        email: 'existing@email.com',
        username: 'testuser',
        password: 'password123'
      })).rejects.toThrow('Email already exists');
    });
  });

  describe('getCurrentUser', () => {
    it('should fetch current user successfully', async () => {
      mockAxiosInstance.get.mockResolvedValueOnce(mockUserResponse);
      
      const result = await AuthService.getCurrentUser();
      
      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/user/me/');
      expect(result).toEqual(mockUserResponse.data);
    });

    it('should throw error when user not found', async () => {
      const errorResponse = {
        response: {
          status: 404,
          data: { detail: 'User not found' }
        }
      };
      
      mockAxiosInstance.get.mockRejectedValueOnce(errorResponse);
      
      await expect(AuthService.getCurrentUser())
        .rejects.toThrow('Failed to get user profile');
    });

    it('should throw error on invalid token', async () => {
      const errorResponse = {
        response: {
          status: 401,
          data: { detail: 'Invalid token' }
        }
      };
      
      mockAxiosInstance.get.mockRejectedValueOnce(errorResponse);
      
      await expect(AuthService.getCurrentUser())
        .rejects.toThrow('Failed to get user profile');
    });
  });

  describe('setAuthToken', () => {
    it('should set authorization header when token is provided', () => {
      const token = 'test-token-123';
      
      AuthService.setAuthToken(token);
      
      expect(mockAxiosInstance.defaults.headers.common['Authorization']).toBe(`Bearer ${token}`);
    });
  });

  describe('removeAuthToken', () => {
    it('should remove authorization header', () => {
      // First set a token
      mockAxiosInstance.defaults.headers.common['Authorization'] = 'Bearer test-token';
      
      AuthService.removeAuthToken();
      
      expect(mockAxiosInstance.defaults.headers.common['Authorization']).toBeUndefined();
    });
  });

  describe('error handling', () => {
    it('should handle server errors gracefully', async () => {
      const serverError = {
        response: {
          status: 500,
          data: { detail: 'Internal server error' }
        }
      };
      
      mockAxiosInstance.post.mockRejectedValueOnce(serverError);
      
      await expect(AuthService.login({
        username: 'test@example.com',
        password: 'password123'
      })).rejects.toThrow('Internal server error');
    });

    it('should handle malformed responses', async () => {
      const malformedError = {
        response: {
          status: 400,
          data: 'Not a JSON object'
        }
      };
      
      mockAxiosInstance.post.mockRejectedValueOnce(malformedError);
      
      await expect(AuthService.login({
        username: 'test@example.com',
        password: 'password123'
      })).rejects.toThrow();
    });

    it('should handle missing error details', async () => {
      const errorWithoutDetail = {
        response: {
          status: 400,
          data: {}
        }
      };
      
      mockAxiosInstance.post.mockRejectedValueOnce(errorWithoutDetail);
      
      await expect(AuthService.login({
        username: 'test@example.com',
        password: 'password123'
      })).rejects.toThrow();
    });
  });
});