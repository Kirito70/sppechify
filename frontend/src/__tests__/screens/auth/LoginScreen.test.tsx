import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import LoginScreen from '../../../screens/auth/LoginScreen';
import { useAuth } from '../../../contexts/AuthContext';

// Mock the useAuth hook
jest.mock('../../../contexts/AuthContext');
const mockedUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

// Mock Alert
jest.spyOn(Alert, 'alert').mockImplementation(() => {});

// Mock navigation
const mockNavigation = {
  navigate: jest.fn(),
};

describe('LoginScreen', () => {
  const mockLogin = jest.fn();
  const mockClearError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseAuth.mockReturnValue({
      state: {
        user: null,
        isLoading: false,
        error: null,
      },
      login: mockLogin,
      register: jest.fn(),
      logout: jest.fn(),
      clearError: mockClearError,
    });
  });

  it('renders login form correctly', () => {
    render(<LoginScreen navigation={mockNavigation} />);
    
    expect(screen.getByText('Welcome Back')).toBeOnTheScreen();
    expect(screen.getByPlaceholderText('Enter your username')).toBeOnTheScreen();
    expect(screen.getByPlaceholderText('Enter your password')).toBeOnTheScreen();
    expect(screen.getByText('Sign In')).toBeOnTheScreen();
    expect(screen.getByText("Don't have an account?  Sign Up")).toBeOnTheScreen();
  });

  it('validates form inputs correctly', async () => {
    render(<LoginScreen navigation={mockNavigation} />);
    
    const loginButton = screen.getByText('Sign In');
    fireEvent.press(loginButton);
    
    await waitFor(() => {
      expect(screen.getByText('Username is required')).toBeOnTheScreen();
      expect(screen.getByText('Password is required')).toBeOnTheScreen();
    });
    
    expect(mockLogin).not.toHaveBeenCalled();
  });

  it('validates username length', async () => {
    render(<LoginScreen navigation={mockNavigation} />);
    
    const usernameInput = screen.getByPlaceholderText('Enter your username');
    const loginButton = screen.getByText('Sign In');
    
    fireEvent.changeText(usernameInput, 'a');
    fireEvent.press(loginButton);
    
    await waitFor(() => {
      expect(screen.getByText('Username must be at least 2 characters')).toBeOnTheScreen();
    });
  });

  it('validates password length', async () => {
    render(<LoginScreen navigation={mockNavigation} />);
    
    const usernameInput = screen.getByPlaceholderText('Enter your username');
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const loginButton = screen.getByText('Sign In');
    
    fireEvent.changeText(usernameInput, 'validuser');
    fireEvent.changeText(passwordInput, '123');
    fireEvent.press(loginButton);
    
    await waitFor(() => {
      expect(screen.getByText('Password must be at least 8 characters')).toBeOnTheScreen();
    });
  });

  it('submits valid form data', async () => {
    render(<LoginScreen navigation={mockNavigation} />);
    
    const usernameInput = screen.getByPlaceholderText('Enter your username');
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const loginButton = screen.getByText('Sign In');
    
    fireEvent.changeText(usernameInput, 'testuser');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.press(loginButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123',
      });
    });
  });

  it('trims and lowercases username', async () => {
    render(<LoginScreen navigation={mockNavigation} />);
    
    const usernameInput = screen.getByPlaceholderText('Enter your username');
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const loginButton = screen.getByText('Sign In');
    
    fireEvent.changeText(usernameInput, '  TestUser  ');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.press(loginButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123',
      });
    });
  });

  it('shows loading state during login', () => {
    mockedUseAuth.mockReturnValue({
      state: {
        user: null,
        isLoading: true,
        error: null,
      },
      login: mockLogin,
      register: jest.fn(),
      logout: jest.fn(),
      clearError: mockClearError,
    });

    render(<LoginScreen navigation={mockNavigation} />);
    
    const usernameInput = screen.getByPlaceholderText('Enter your username');
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    
    expect(usernameInput.props.editable).toBe(false);
    expect(passwordInput.props.editable).toBe(false);
  });

  it('displays error message when login fails', () => {
    mockedUseAuth.mockReturnValue({
      state: {
        user: null,
        isLoading: false,
        error: 'Invalid credentials',
      },
      login: mockLogin,
      register: jest.fn(),
      logout: jest.fn(),
      clearError: mockClearError,
    });

    render(<LoginScreen navigation={mockNavigation} />);
    
    expect(screen.getByText('Invalid credentials')).toBeOnTheScreen();
  });

  it('clears field errors when user starts typing', async () => {
    render(<LoginScreen navigation={mockNavigation} />);
    
    const usernameInput = screen.getByPlaceholderText('Enter your username');
    const loginButton = screen.getByText('Sign In');
    
    // Trigger validation error
    fireEvent.press(loginButton);
    await waitFor(() => {
      expect(screen.getByText('Username is required')).toBeOnTheScreen();
    });
    
    // Start typing to clear error
    fireEvent.changeText(usernameInput, 'test');
    
    await waitFor(() => {
      expect(screen.queryByText('Username is required')).not.toBeOnTheScreen();
    });
  });

  it('clears auth error when user starts typing', () => {
    mockedUseAuth.mockReturnValue({
      state: {
        user: null,
        isLoading: false,
        error: 'Invalid credentials',
      },
      login: mockLogin,
      register: jest.fn(),
      logout: jest.fn(),
      clearError: mockClearError,
    });

    render(<LoginScreen navigation={mockNavigation} />);
    
    const usernameInput = screen.getByPlaceholderText('Enter your username');
    fireEvent.changeText(usernameInput, 'test');
    
    expect(mockClearError).toHaveBeenCalled();
  });

  it('toggles password visibility', () => {
    render(<LoginScreen navigation={mockNavigation} />);
    
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const toggleButton = screen.getByText('🙈');
    
    expect(passwordInput.props.secureTextEntry).toBe(true);
    
    fireEvent.press(toggleButton);
    
    expect(passwordInput.props.secureTextEntry).toBe(false);
    expect(screen.getByText('👁️')).toBeOnTheScreen();
  });

  it('navigates to register screen', () => {
    render(<LoginScreen navigation={mockNavigation} />);
    
    const registerLink = screen.getByText("Don't have an account?  Sign Up");
    fireEvent.press(registerLink);
    
    expect(mockNavigation.navigate).toHaveBeenCalledWith('Register');
  });

  it('navigates to forgot password screen', () => {
    render(<LoginScreen navigation={mockNavigation} />);
    
    const forgotPasswordLink = screen.getByText('Forgot Password?');
    fireEvent.press(forgotPasswordLink);
    
    expect(mockNavigation.navigate).toHaveBeenCalledWith('ForgotPassword');
  });

  it('shows success alert on successful login', async () => {
    render(<LoginScreen navigation={mockNavigation} />);
    
    const usernameInput = screen.getByPlaceholderText('Enter your username');
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const loginButton = screen.getByText('Sign In');
    
    fireEvent.changeText(usernameInput, 'testuser');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.press(loginButton);
    
    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith('Success', 'Login successful!');
    });
  });

  it('clears error on component mount', () => {
    render(<LoginScreen navigation={mockNavigation} />);
    
    expect(mockClearError).toHaveBeenCalled();
  });
});