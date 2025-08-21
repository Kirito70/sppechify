// Test script to verify frontend authService connects to our backend
import { AuthService } from '../src/services/authService';

// Mock the environment config to use our backend URL
jest.mock('../src/config/env', () => ({
  env: {
    API_URL: 'http://localhost:55073',
    API_BASE_URL: 'http://localhost:55073/api/v1',
    ENABLE_DEBUG_LOGS: true,
  }
}));

describe('Frontend-Backend End-to-End Connection', () => {
  test('should connect to actual backend', async () => {
    // This test verifies the frontend service can talk to our running backend
    const result = await AuthService.testConnection();
    expect(result).toBe(true);
  });

  test('should handle registration flow', async () => {
    try {
      const user = await AuthService.register({
        name: 'E2E Test User',
        username: 'e2etest',
        email: 'e2e@test.com',
        password: 'testpass123'
      });
      expect(user.name).toBe('E2E Test User');
    } catch (error) {
      // User may already exist, which is fine for this test
      expect(error.message).toContain('already registered');
    }
  });
});