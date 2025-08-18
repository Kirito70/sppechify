import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthProvider, useAuth } from '../../contexts/AuthContext';
import { AuthService } from '../../services/authService';

// Enable mocking for this test file
process.env.JEST_MOCK_AUTH_SERVICE = 'true';

// Mock the AuthService
jest.mock('../../services/authService', () => ({
  AuthService: {
    login: jest.fn(),
    register: jest.fn(),
    getCurrentUser: jest.fn(),
    setAuthToken: jest.fn(),
    removeAuthToken: jest.fn(),
  },
}));

const mockedAuthService = AuthService as jest.Mocked<typeof AuthService>;

// Test component to access AuthContext
const TestComponent = () => {
  const { user, login, register, logout, loading } = useAuth();
  
  return (
    <>
      <text testID="loading">{loading ? 'loading' : 'not-loading'}</text>
      <text testID="user">{user ? user.email : 'no-user'}</text>
      <button
        testID="login-btn"
        onPress={() => login('test@example.com', 'password123')}
      />
      <button
        testID="register-btn"
        onPress={() => register('Test User', 'test@example.com', 'testuser', 'password123')}
      />
      <button testID="logout-btn" onPress={() => logout()} />
    </>
  );
};

const TestWrapper = () => (
  <AuthProvider>
    <TestComponent />
  </AuthProvider>
);

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (AsyncStorage.clear as jest.Mock).mockClear();
    (AsyncStorage.getItem as jest.Mock).mockResolvedValue(null);
    (AsyncStorage.setItem as jest.Mock).mockResolvedValue(null);
    (AsyncStorage.removeItem as jest.Mock).mockResolvedValue(null);
  });

  it('initializes with no user and not loading', async () => {
    await act(async () => {
      render(<TestWrapper />);
    });
    
    expect(screen.getByTestId('user')).toHaveTextContent('no-user');
    expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
  });

  it('handles successful login', async () => {
    const mockUser = {
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
    };
    
    const mockToken = 'mock-jwt-token';
    mockedAuthService.login.mockResolvedValueOnce({
      access_token: mockToken,
      token_type: 'bearer',
    });
    
    mockedAuthService.getCurrentUser.mockResolvedValueOnce(mockUser);

    await act(async () => {
      render(<TestWrapper />);
    });
    
    // Initially loading should be false
    expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
    
    // Trigger login
    await act(async () => {
      fireEvent.press(screen.getByTestId('login-btn'));
    });
    
    // Wait for login to complete
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
    });
    
    expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
    expect(mockedAuthService.login).toHaveBeenCalledWith({
      username: 'test@example.com',
      password: 'password123'
    });
    expect(AsyncStorage.setItem).toHaveBeenCalledWith('token', mockToken);
  });

  it('handles failed login', async () => {
    mockedAuthService.login.mockRejectedValueOnce(new Error('Invalid credentials'));

    await act(async () => {
      render(<TestWrapper />);
    });
    
    await act(async () => {
      fireEvent.press(screen.getByTestId('login-btn'));
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
    });
    
    // User should still be null after failed login
    expect(screen.getByTestId('user')).toHaveTextContent('no-user');
  });

  it('handles successful registration', async () => {
    const mockUser = {
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
      study_streak: 0,
      best_streak: 0,
      total_sentences_learned: 0,
      total_study_time_minutes: 0,
      preferred_study_time: '18:00',
      study_reminders_enabled: true,
      audio_enabled: true,
      furigana_enabled: true,
      romaji_enabled: false,
      difficulty_preference: 'mixed',
      last_study_date: null
    };
    
    mockedAuthService.register.mockResolvedValueOnce(mockUser);

    await act(async () => {
      render(<TestWrapper />);
    });
    
    await act(async () => {
      fireEvent.press(screen.getByTestId('register-btn'));
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
    });
    
    expect(mockedAuthService.register).toHaveBeenCalledWith({
      name: 'Test User',
      email: 'test@example.com',
      username: 'testuser',
      password: 'password123'
    });
  });

  it('handles logout', async () => {
    const mockUser = {
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
    };
    
    const mockToken = 'mock-jwt-token';
    mockedAuthService.login.mockResolvedValueOnce({
      access_token: mockToken,
      token_type: 'bearer',
    });
    
    mockedAuthService.getCurrentUser.mockResolvedValueOnce(mockUser);

    await act(async () => {
      render(<TestWrapper />);
    });
    
    // Login first
    await act(async () => {
      fireEvent.press(screen.getByTestId('login-btn'));
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
    });
    
    // Now logout
    await act(async () => {
      fireEvent.press(screen.getByTestId('logout-btn'));
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('no-user');
    });
    
    expect(AsyncStorage.removeItem).toHaveBeenCalledWith('token');
  });

  it('restores user from token on app start', async () => {
    const mockToken = 'stored-token';
    const mockUser = {
      id: 1,
      name: 'Stored User',
      email: 'stored@example.com',
      username: 'storeduser',
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
    };
    
    // Mock AsyncStorage to return a stored token
    (AsyncStorage.getItem as jest.Mock).mockResolvedValueOnce(mockToken);
    mockedAuthService.getCurrentUser.mockResolvedValueOnce(mockUser);

    await act(async () => {
      render(<TestWrapper />);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('stored@example.com');
    });
    
    expect(AsyncStorage.getItem).toHaveBeenCalledWith('token');
    expect(mockedAuthService.getCurrentUser).toHaveBeenCalled();
  });

  it('handles invalid stored token', async () => {
    const mockToken = 'invalid-token';
    
    // Mock AsyncStorage to return a stored token
    (AsyncStorage.getItem as jest.Mock).mockResolvedValueOnce(mockToken);
    mockedAuthService.getCurrentUser.mockRejectedValueOnce(new Error('Invalid token'));

    await act(async () => {
      render(<TestWrapper />);
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
    });
    
    // Should clear invalid token and remain logged out
    expect(screen.getByTestId('user')).toHaveTextContent('no-user');
    expect(AsyncStorage.removeItem).toHaveBeenCalledWith('token');
  });
});