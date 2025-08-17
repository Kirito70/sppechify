import React, { createContext, useContext, useReducer, useEffect, useCallback, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthService, User, LoginCredentials, RegisterCredentials } from '../services/authService';

// Re-export types for convenience
export type { User, LoginCredentials, RegisterCredentials };

export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  token: string | null;
  error: string | null;
}

// Action types
type AuthAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGOUT' }
  | { type: 'RESTORE_TOKEN'; payload: { user: User; token: string } | null };

// Initial state
const initialState: AuthState = {
  isAuthenticated: false,
  isLoading: true, // Start with loading to check for existing token
  user: null,
  token: null,
  error: null,
};

// Reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        isLoading: false,
        user: action.payload.user,
        token: action.payload.token,
        error: null,
      };
    case 'LOGOUT':
      return {
        ...state,
        isAuthenticated: false,
        isLoading: false,
        user: null,
        token: null,
        error: null,
      };
    case 'RESTORE_TOKEN':
      if (action.payload) {
        return {
          ...state,
          isAuthenticated: true,
          isLoading: false,
          user: action.payload.user,
          token: action.payload.token,
          error: null,
        };
      } else {
        return {
          ...state,
          isAuthenticated: false,
          isLoading: false,
          user: null,
          token: null,
          error: null,
        };
      }
    default:
      return state;
  }
};

// Context
interface AuthContextType {
  state: AuthState;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Storage keys
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';

// Provider component
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Restore token on app start
  useEffect(() => {
    const restoreToken = async () => {
      try {
        const token = await AsyncStorage.getItem(TOKEN_KEY);
        const userString = await AsyncStorage.getItem(USER_KEY);
        
        if (token && userString) {
          const user = JSON.parse(userString);
          
          // Set authorization header for future requests
          AuthService.setAuthToken(token);
          
          // Verify token is still valid by getting current user
          try {
            const currentUser = await AuthService.getCurrentUser();
            dispatch({ 
              type: 'RESTORE_TOKEN', 
              payload: { user: currentUser, token } 
            });
          } catch (error) {
            // Token is invalid, clear stored data
            await AsyncStorage.removeItem(TOKEN_KEY);
            await AsyncStorage.removeItem(USER_KEY);
            AuthService.removeAuthToken();
            dispatch({ type: 'RESTORE_TOKEN', payload: null });
          }
        } else {
          dispatch({ type: 'RESTORE_TOKEN', payload: null });
        }
      } catch (error) {
        console.error('Error restoring token:', error);
        dispatch({ type: 'RESTORE_TOKEN', payload: null });
      }
    };

    restoreToken();
  }, []);

  // Login function
  const login = useCallback(async (credentials: LoginCredentials) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      // Login and get token
      const loginResponse = await AuthService.login(credentials);
      const { access_token } = loginResponse;

      // Set auth token for future requests
      AuthService.setAuthToken(access_token);

      // Get user profile
      const user = await AuthService.getCurrentUser();

      // Store token and user in AsyncStorage
      await AsyncStorage.setItem(TOKEN_KEY, access_token);
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(user));

      dispatch({ 
        type: 'LOGIN_SUCCESS', 
        payload: { user, token: access_token } 
      });
    } catch (error: any) {
      console.error('Login error:', error);
      
      let errorMessage = 'Login failed. Please try again.';
      if (error.message) {
        errorMessage = error.message;
      }
      
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, []);

  // Register function
  const register = useCallback(async (credentials: RegisterCredentials) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    dispatch({ type: 'SET_ERROR', payload: null });

    try {
      // Register user
      const user = await AuthService.register(credentials);

      // After successful registration, log the user in
      await login({
        username: credentials.username,
        password: credentials.password,
      });
    } catch (error: any) {
      console.error('Registration error:', error);
      
      let errorMessage = 'Registration failed. Please try again.';
      if (error.message) {
        errorMessage = error.message;
      }
      
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      throw error;
    }
  }, [login]);

  // Logout function
  const logout = useCallback(async () => {
    dispatch({ type: 'SET_LOADING', payload: true });

    try {
      // Remove token and user from AsyncStorage
      await AsyncStorage.removeItem(TOKEN_KEY);
      await AsyncStorage.removeItem(USER_KEY);

      // Remove authorization header
      AuthService.removeAuthToken();

      dispatch({ type: 'LOGOUT' });
    } catch (error) {
      console.error('Logout error:', error);
      // Even if there's an error, we should still logout locally
      dispatch({ type: 'LOGOUT' });
    }
  }, []);

  // Clear error function
  const clearError = useCallback(() => {
    dispatch({ type: 'SET_ERROR', payload: null });
  }, []);

  const value: AuthContextType = {
    state,
    login,
    register,
    logout,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;