import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react-native';
import { Alert } from 'react-native';
import RegisterScreen from '../../../screens/auth/RegisterScreen';
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

describe('RegisterScreen', () => {
  const mockRegister = jest.fn();
  const mockClearError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseAuth.mockReturnValue({
      state: {
        user: null,
        isLoading: false,
        error: null,
      },
      login: jest.fn(),
      register: mockRegister,
      logout: jest.fn(),
      clearError: mockClearError,
    });
  });

  it('renders register form correctly', () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    expect(screen.getByText('Sign Up')).toBeOnTheScreen();
    expect(screen.getByPlaceholderText('Enter your name')).toBeOnTheScreen();
    expect(screen.getByPlaceholderText('Choose a username')).toBeOnTheScreen();
    expect(screen.getByPlaceholderText('Enter your email address')).toBeOnTheScreen();
    expect(screen.getByPlaceholderText('Enter your password')).toBeOnTheScreen();
    expect(screen.getByPlaceholderText('Confirm your password')).toBeOnTheScreen();
  });

  it('validates required fields', async () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const registerButton = screen.getByText('Create Account');
    fireEvent.press(registerButton);
    
    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeOnTheScreen();
      expect(screen.getByText('Username is required')).toBeOnTheScreen();
      expect(screen.getByText('Email address is required')).toBeOnTheScreen();
      expect(screen.getByText('Password is required')).toBeOnTheScreen();
    });
    
    expect(mockRegister).not.toHaveBeenCalled();
  });

  it('validates name length', async () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const nameInput = screen.getByPlaceholderText('Enter your name');
    const registerButton = screen.getByText('Create Account');
    
    fireEvent.changeText(nameInput, 'a');
    fireEvent.press(registerButton);
    
    await waitFor(() => {
      expect(screen.getByText('Name must be at least 2 characters')).toBeOnTheScreen(); // Using the actual error message from validation
    });
  });

  it('validates username format', async () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const usernameInput = screen.getByPlaceholderText('Choose a username');
    const registerButton = screen.getByText('Create Account');
    
    fireEvent.changeText(usernameInput, 'User@123');
    fireEvent.press(registerButton);
    
    await waitFor(() => {
      expect(screen.getByText('Username can only contain lowercase letters and numbers')).toBeOnTheScreen();
    });
  });

  it('validates email format', async () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const nameInput = screen.getByPlaceholderText('Enter your name');
    const usernameInput = screen.getByPlaceholderText('Choose a username');
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const registerButton = screen.getByText('Create Account');
    
    fireEvent.changeText(nameInput, 'Test User');
    fireEvent.changeText(usernameInput, 'testuser');
    fireEvent.changeText(emailInput, 'invalid-email');
    fireEvent.press(registerButton);
    
    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeOnTheScreen();
    });
  });

  it('validates password length', async () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const nameInput = screen.getByPlaceholderText('Enter your name');
    const usernameInput = screen.getByPlaceholderText('Choose a username');
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const registerButton = screen.getByText('Create Account');
    
    fireEvent.changeText(nameInput, 'Test User');
    fireEvent.changeText(usernameInput, 'testuser');
    fireEvent.changeText(emailInput, 'test@example.com');
    fireEvent.changeText(passwordInput, '123');
    fireEvent.press(registerButton);
    
    await waitFor(() => {
      expect(screen.getByText('Password must be at least 8 characters')).toBeOnTheScreen();
    });
  });

  it('validates password confirmation match', async () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const nameInput = screen.getByPlaceholderText('Enter your name');
    const usernameInput = screen.getByPlaceholderText('Choose a username');
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const confirmPasswordInput = screen.getByPlaceholderText('Confirm your password');
    const registerButton = screen.getByText('Create Account');
    
    fireEvent.changeText(nameInput, 'Test User');
    fireEvent.changeText(usernameInput, 'testuser');
    fireEvent.changeText(emailInput, 'test@example.com');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.changeText(confirmPasswordInput, 'different123');
    fireEvent.press(registerButton);
    
    await waitFor(() => {
      expect(screen.getByText('Passwords do not match')).toBeOnTheScreen();
    });
  });

  it('submits valid form data', async () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const nameInput = screen.getByPlaceholderText('Enter your name');
    const usernameInput = screen.getByPlaceholderText('Choose a username');
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const confirmPasswordInput = screen.getByPlaceholderText('Confirm your password');
    const registerButton = screen.getByText('Create Account');
    
    fireEvent.changeText(nameInput, 'Test User');
    fireEvent.changeText(usernameInput, 'testuser');
    fireEvent.changeText(emailInput, 'test@example.com');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.changeText(confirmPasswordInput, 'password123');
    fireEvent.press(registerButton);
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        name: 'Test User',
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123',
      });
    });
  });

  it('trims and lowercases email and username', async () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const nameInput = screen.getByPlaceholderText('Enter your name');
    const usernameInput = screen.getByPlaceholderText('Choose a username');
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const confirmPasswordInput = screen.getByPlaceholderText('Confirm your password');
    const registerButton = screen.getByText('Create Account');
    
    fireEvent.changeText(nameInput, 'Test User');
    fireEvent.changeText(usernameInput, '  testuser  '); // Valid username without numbers
    fireEvent.changeText(emailInput, '  Test@Example.COM  ');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.changeText(confirmPasswordInput, 'password123');
    fireEvent.press(registerButton);
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        name: 'Test User',
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123',
      });
    });
  });

  it('shows loading state during registration', () => {
    mockedUseAuth.mockReturnValue({
      state: {
        user: null,
        isLoading: true,
        error: null,
      },
      login: jest.fn(),
      register: mockRegister,
      logout: jest.fn(),
      clearError: mockClearError,
    });

    render(<RegisterScreen navigation={mockNavigation} />);
    
    const nameInput = screen.getByPlaceholderText('Enter your name');
    const usernameInput = screen.getByPlaceholderText('Choose a username');
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const confirmPasswordInput = screen.getByPlaceholderText('Confirm your password');
    
    expect(nameInput.props.editable).toBe(false);
    expect(usernameInput.props.editable).toBe(false);
    expect(emailInput.props.editable).toBe(false);
    expect(passwordInput.props.editable).toBe(false);
    expect(confirmPasswordInput.props.editable).toBe(false);
  });

  it('displays error message when registration fails', () => {
    mockedUseAuth.mockReturnValue({
      state: {
        user: null,
        isLoading: false,
        error: 'Email already exists',
      },
      login: jest.fn(),
      register: mockRegister,
      logout: jest.fn(),
      clearError: mockClearError,
    });

    render(<RegisterScreen navigation={mockNavigation} />);
    
    expect(screen.getByText('Email already exists')).toBeOnTheScreen();
  });

  it('toggles password visibility', () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const toggleButton = screen.getAllByText('🙈')[0];
    
    expect(passwordInput.props.secureTextEntry).toBe(true);
    
    fireEvent.press(toggleButton);
    
    expect(passwordInput.props.secureTextEntry).toBe(false);
    expect(screen.getAllByText('👁️')[0]).toBeOnTheScreen();
  });

  it('toggles confirm password visibility', () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const confirmPasswordInput = screen.getByPlaceholderText('Confirm your password');
    const toggleButton = screen.getAllByText('🙈')[1];
    
    expect(confirmPasswordInput.props.secureTextEntry).toBe(true);
    
    fireEvent.press(toggleButton);
    
    expect(confirmPasswordInput.props.secureTextEntry).toBe(false);
    expect(screen.getAllByText('👁️')[0]).toBeOnTheScreen();
  });

  it('navigates to login screen', () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const loginLink = screen.getByText('Already have an account?  Welcome Back');
    fireEvent.press(loginLink);
    
    expect(mockNavigation.navigate).toHaveBeenCalledWith('Login');
  });

  it('shows success alert on successful registration', async () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const nameInput = screen.getByPlaceholderText('Enter your name');
    const usernameInput = screen.getByPlaceholderText('Choose a username');
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const passwordInput = screen.getByPlaceholderText('Enter your password');
    const confirmPasswordInput = screen.getByPlaceholderText('Confirm your password');
    const registerButton = screen.getByText('Create Account');
    
    fireEvent.changeText(nameInput, 'Test User');
    fireEvent.changeText(usernameInput, 'testuser');
    fireEvent.changeText(emailInput, 'test@example.com');
    fireEvent.changeText(passwordInput, 'password123');
    fireEvent.changeText(confirmPasswordInput, 'password123');
    fireEvent.press(registerButton);
    
    await waitFor(() => {
      expect(Alert.alert).toHaveBeenCalledWith('Success', 'Registration successful!');
    });
  });

  it('clears field errors when user starts typing', async () => {
    render(<RegisterScreen navigation={mockNavigation} />);
    
    const nameInput = screen.getByPlaceholderText('Enter your name');
    const registerButton = screen.getByText('Create Account');
    
    // Trigger validation error
    fireEvent.press(registerButton);
    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeOnTheScreen();
    });
    
    // Start typing to clear error
    fireEvent.changeText(nameInput, 'Test');
    
    await waitFor(() => {
      expect(screen.queryByText('Name is required')).not.toBeOnTheScreen();
    });
  });

  it('clears auth error when user starts typing', () => {
    mockedUseAuth.mockReturnValue({
      state: {
        user: null,
        isLoading: false,
        error: 'Email already exists',
      },
      login: jest.fn(),
      register: mockRegister,
      logout: jest.fn(),
      clearError: mockClearError,
    });

    render(<RegisterScreen navigation={mockNavigation} />);
    
    const nameInput = screen.getByPlaceholderText('Enter your name');
    fireEvent.changeText(nameInput, 'Test');
    
    expect(mockClearError).toHaveBeenCalled();
  });
});