import { AuthService } from '../../services/authService';

describe('AuthService', () => {
  // Use the global mockAxiosInstance from setup.ts
  const mockAxiosInstance = (global as any).mockAxiosInstance;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('login', () => {
    it('should login successfully with valid credentials', async () => {
      const mockResponse = {
        data: {
          access_token: 'mock-jwt-token',
          token_type: 'bearer',
        }
      };
      
      mockAxiosInstance.post.mockResolvedValueOnce(mockResponse);
      
      const result = await AuthService.login({
        username: 'testuser',
        password: 'password123'
      });
      
      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/login', expect.any(FormData), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      
      expect(result).toEqual(mockResponse.data);
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
      })).rejects.toThrow('Login failed. Please check your credentials.');
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
      AuthService.setAuthToken('test-token');
      expect(mockAxiosInstance.defaults.headers.common['Authorization']).toBe('Bearer test-token');
      
      // Then remove it
      AuthService.removeAuthToken();
      
      expect(mockAxiosInstance.defaults.headers.common['Authorization']).toBeUndefined();
    });
  });
});