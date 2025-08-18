import React from 'react';
import { render, screen } from '@testing-library/react-native';
import '@testing-library/jest-native/extend-expect';
import HomeScreen from '../../screens/HomeScreen';
import { AuthProvider } from '../../contexts/AuthContext';

// Test wrapper component that provides AuthContext
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AuthProvider>
    {children}
  </AuthProvider>
);

// Mock the i18n hook
jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => {
      const translations: { [key: string]: string } = {
        'home.title': 'Language Learning',
        'home.welcomeMessage': 'Welcome to your learning journey!',
        'home.todayProgress': "Today's Progress",
        'home.wordsLearned': 'Words',
        'home.minutes': 'Minutes',
        'home.days': 'Day Streak',
        'home.quickActions': 'Quick Actions',
        'home.startLearning': 'Start Learning',
        'home.takePhoto': 'Take Photo',
        'home.reviewCards': 'Review Cards',
      };
      return translations[key] || key;
    },
  }),
}));

// Mock the env config
jest.mock('../../config/env', () => ({
  API_BASE_URL: 'http://localhost:8000/api/v1',
  ENABLE_DEBUG_LOGS: true,
}));

describe('HomeScreen', () => {
  it('renders correctly', () => {
    render(<HomeScreen />, { wrapper: TestWrapper });
    
    // Check if main elements are present
    expect(screen.getByText('Language Learning')).toBeOnTheScreen();
    expect(screen.getByText('Welcome to your learning journey!')).toBeOnTheScreen();
    expect(screen.getByText("Today's Progress")).toBeOnTheScreen();
  });

  it('displays progress counters', () => {
    render(<HomeScreen />, { wrapper: TestWrapper });
    
    // Check progress counters - they should show 0 initially
    const progressCounters = screen.getAllByText('0');
    expect(progressCounters).toHaveLength(3);
    
    // Check counter labels
    expect(screen.getByText('Words')).toBeOnTheScreen();
    expect(screen.getByText('Minutes')).toBeOnTheScreen();
    expect(screen.getByText('Day Streak')).toBeOnTheScreen();
  });

  it('displays quick action buttons', () => {
    render(<HomeScreen />, { wrapper: TestWrapper });
    
    // Check all quick action buttons are present
    expect(screen.getByText('📚 Start Learning')).toBeOnTheScreen();
    expect(screen.getByText('📸 Take Photo')).toBeOnTheScreen();
    expect(screen.getByText('🔄 Review Cards')).toBeOnTheScreen();
  });

  it('shows recent activity section', () => {
    render(<HomeScreen />, { wrapper: TestWrapper });
    
    expect(screen.getByText('Recent Activity')).toBeOnTheScreen();
    expect(screen.getByText('No activity yet. Start learning to see your progress here!')).toBeOnTheScreen();
  });

  it('displays debug info in development', () => {
    render(<HomeScreen />, { wrapper: TestWrapper });
    
    // Check if debug info is shown when ENABLE_DEBUG_LOGS is true
    expect(screen.getByText('🔧 API: http://localhost:8000/api/v1')).toBeOnTheScreen();
  });
});