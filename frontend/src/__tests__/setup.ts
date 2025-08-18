import 'react-native-gesture-handler/jestSetup';

// Mock React Native
jest.mock('react-native', () => {
  return {
    Platform: {
      OS: 'ios',
      select: jest.fn((options) => options.ios),
    },
    Dimensions: {
      get: jest.fn(() => ({ width: 375, height: 812 })),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    },
    StyleSheet: {
      create: jest.fn((styles) => styles),
      flatten: jest.fn((style) => style || {}),
    },
    View: 'View',
    Text: 'Text',
    ScrollView: 'ScrollView',
    TouchableOpacity: 'TouchableOpacity',
    TextInput: 'TextInput',
    SafeAreaView: 'SafeAreaView',
    KeyboardAvoidingView: 'KeyboardAvoidingView',
    ActivityIndicator: 'ActivityIndicator',
    NativeModules: {
      SettingsManager: {
        settings: {},
      },
    },
    Alert: {
      alert: jest.fn(),
    },
    Linking: {
      openURL: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
    },
  };
});

// Mock React Native Safe Area Context
jest.mock('react-native-safe-area-context', () => ({
  SafeAreaProvider: ({ children }: any) => children,
  SafeAreaView: ({ children }: any) => children,
  useSafeAreaInsets: () => ({ top: 0, bottom: 0, left: 0, right: 0 }),
  useSafeAreaFrame: () => ({ x: 0, y: 0, width: 375, height: 812 }),
}));

// Mock ResponsiveLayout components
jest.mock('../components/ResponsiveLayout', () => {
  const React = require('react');
  const { View, Text, TextInput, TouchableOpacity } = require('react-native');
  
  return {
    ResponsiveLayout: ({ children }: any) => React.createElement(View, { testID: 'responsive-layout' }, children),
    ResponsiveCard: ({ children }: any) => React.createElement(View, { testID: 'responsive-card' }, children),
    ResponsiveHeader: ({ title }: any) => React.createElement(Text, { testID: 'responsive-header' }, title),
    ResponsiveInput: ({ label, placeholder, value, onChangeText, testID, editable = true, secureTextEntry = false, error, rightElement }: any) => 
      React.createElement(View, null, [
        label ? React.createElement(Text, { key: `${testID}-label` }, label) : null,
        React.createElement(TextInput, { 
          key: `${testID}-input`,
          testID,
          placeholder,
          value,
          onChangeText,
          editable,
          secureTextEntry
        }),
        rightElement ? React.createElement(View, { key: `${testID}-right` }, rightElement) : null,
        error ? React.createElement(Text, { key: `${testID}-error`, testID: 'input-error' }, error) : null
      ].filter(Boolean)),
    ResponsiveButton: ({ title, onPress, testID, disabled = false }: any) => 
      React.createElement(TouchableOpacity, { onPress, testID, disabled }, 
        React.createElement(Text, null, title)
      ),
    ResponsiveDivider: ({ text }: any) => React.createElement(Text, { testID: 'responsive-divider' }, text || ''),
    ResponsiveLink: ({ text, linkText, onPress }: any) => 
      React.createElement(TouchableOpacity, { onPress },
        React.createElement(Text, null, `${text || ''}${linkText || ''}`)
      ),
  };
});

// Mock utils/responsive
jest.mock('../utils/responsive', () => ({
  getLayoutStyles: jest.fn(() => ({
    container: {},
    card: {},
    header: {},
    title: {},
    subtitle: {},
    formGroup: {},
    label: {},
    input: {},
    inputContainer: {},
    button: {},
    buttonText: {},
    errorText: {},
    divider: {},
    dividerLine: {},
    dividerText: {},
    linkContainer: {},
    icon: {},
  })),
  responsive: {
    spacing: {
      xs: 4,
      sm: 8,
      md: 16,
      lg: 24,
      xl: 32,
      xxl: 48,
    },
    text: {
      body: 16,
      heading: 24,
    },
    icon: {
      medium: 48,
    },
  },
}));

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn().mockResolvedValue(null),
  setItem: jest.fn().mockResolvedValue(null),
  removeItem: jest.fn().mockResolvedValue(null),
  clear: jest.fn().mockResolvedValue(null),
  getAllKeys: jest.fn().mockResolvedValue([]),
  multiGet: jest.fn().mockResolvedValue([]),
  multiSet: jest.fn().mockResolvedValue(null),
  multiRemove: jest.fn().mockResolvedValue(null),
}));

// Mock React Navigation
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: jest.fn(),
    goBack: jest.fn(),
    reset: jest.fn(),
    setParams: jest.fn(),
    dispatch: jest.fn(),
    canGoBack: jest.fn(() => true),
    isFocused: jest.fn(() => true),
    addListener: jest.fn(),
    removeListener: jest.fn(),
  }),
  useRoute: () => ({
    key: 'test-route',
    name: 'TestScreen',
    params: {},
  }),
  useFocusEffect: jest.fn(),
  NavigationContainer: ({ children }: any) => children,
  CommonActions: {
    navigate: jest.fn(),
    reset: jest.fn(),
  },
}));

jest.mock('@react-navigation/stack', () => ({
  createStackNavigator: () => ({
    Navigator: ({ children }: any) => children,
    Screen: ({ children }: any) => children,
  }),
  CardStyleInterpolators: {
    forHorizontalIOS: {},
  },
  TransitionPresets: {
    SlideFromRightIOS: {},
  },
}));

jest.mock('@react-navigation/bottom-tabs', () => ({
  createBottomTabNavigator: () => ({
    Navigator: ({ children }: any) => children,
    Screen: ({ children }: any) => children,
  }),
}));

// Create a shared mock instance for all axios usage
const mockAxiosInstance = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
  defaults: {
    headers: {
      common: {},
    },
  },
  interceptors: {
    request: {
      use: jest.fn(),
      eject: jest.fn(),
    },
    response: {
      use: jest.fn(),
      eject: jest.fn(),
    },
  },
};

// Mock Axios
jest.mock('axios', () => ({
  create: jest.fn(() => mockAxiosInstance),
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
  defaults: {
    headers: {
      common: {},
    },
  },
}));

// Export mockAxiosInstance for use in tests
global.mockAxiosInstance = mockAxiosInstance;

// Mock AuthService as a proper class (only for specific tests that need it mocked)
// The simple test will use the real AuthService
const shouldMockAuthService = process.env.JEST_MOCK_AUTH_SERVICE === 'true';

if (shouldMockAuthService) {
  jest.mock('../services/authService', () => {
    const mockAuthService = {
      login: jest.fn(),
      register: jest.fn(),
      getCurrentUser: jest.fn(),
      setAuthToken: jest.fn(),
    };
    
    return {
      __esModule: true,
      default: mockAuthService,
      AuthService: jest.fn().mockImplementation(() => mockAuthService),
    };
  });
}

// Mock i18next with proper translations
const translations = {
  'auth.login.title': 'Welcome Back',
  'auth.login.button': 'Sign In',
  'auth.register.title': 'Sign Up',
  'auth.register.button': 'Create Account',
  'auth.username': 'Username',
  'auth.password': 'Password',
  'auth.name': 'Full Name',
  'auth.email': 'Email Address',
  'auth.confirmPassword': 'Confirm Password',
  'auth.usernameLoginPlaceholder': 'Enter your username',
  'auth.passwordPlaceholder': 'Enter your password',
  'auth.namePlaceholder': 'Enter your name',
  'auth.usernamePlaceholder': 'Choose a username',
  'auth.emailPlaceholder': 'Enter your email address',
  'auth.forgotPassword': 'Forgot Password?',
  'auth.noAccount': "Don't have an account? ",
  'auth.haveAccount': 'Already have an account? ',
  'auth.success': 'Success',
  'auth.loginSuccess': 'Login successful!',
  'auth.errors.usernameRequired': 'Username is required',
  'auth.errors.usernameTooShort': 'Username must be at least 2 characters',
  'auth.errors.passwordRequired': 'Password is required',
  'auth.errors.passwordTooShort': 'Password must be at least 8 characters',
  'auth.errors.nameRequired': 'Name is required',
  'auth.errors.nameTooShort': 'Name must be at least 2 characters',
  'auth.errors.emailRequired': 'Email address is required',
  'auth.errors.emailInvalid': 'Please enter a valid email address',
  'auth.errors.confirmPasswordRequired': 'Please confirm your password',
  'auth.errors.passwordsDoNotMatch': 'Passwords do not match',
  'auth.errors.usernameInvalid': 'Username can only contain lowercase letters and numbers',
  'common.loading': 'Loading...',
};

jest.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => translations[key] || key,
    i18n: {
      changeLanguage: jest.fn(),
      language: 'en',
    },
  }),
  initReactI18next: {
    type: '3rdParty',
    init: jest.fn(),
  },
}));

jest.mock('i18next', () => ({
  use: jest.fn().mockReturnThis(),
  init: jest.fn().mockResolvedValue({}),
  t: (key: string) => translations[key] || key,
  changeLanguage: jest.fn(),
  language: 'en',
}));

// Mock Expo modules
jest.mock('expo-constants', () => ({
  default: {
    expoConfig: {
      extra: {
        API_URL: 'http://localhost:8000',
        API_VERSION: 'v1',
        WS_URL: 'ws://localhost:8000',
        APP_NAME: 'Language Learning',
        APP_VERSION: '1.0.0',
        NODE_ENV: 'development',
        ENABLE_DEBUG_LOGS: 'true',
        ENABLE_OFFLINE_MODE: 'true',
        ENABLE_ANALYTICS: 'false',
      },
    },
  },
}));

jest.mock('expo-font', () => ({
  loadAsync: jest.fn(),
  isLoaded: jest.fn(() => true),
}));

jest.mock('expo-asset', () => ({
  Asset: {
    loadAsync: jest.fn(),
  },
}));

// Global variable for React Native
global.__DEV__ = true;

// Polyfill for requestAnimationFrame
global.requestAnimationFrame = (cb) => {
  setTimeout(cb, 0);
};

global.cancelAnimationFrame = (id) => {
  clearTimeout(id);
};

// Silence specific warnings
const originalError = console.error;
const originalWarn = console.warn;

console.error = (...args: any[]) => {
  if (
    typeof args[0] === 'string' &&
    (args[0].includes('Warning: ReactDOM.render is deprecated') ||
     args[0].includes('Warning: `react-test-renderer` is deprecated') ||
     args[0].includes('react-test-renderer is deprecated') ||
     args[0].includes('act(...) is not supported') ||
     args[0].includes('An update to') ||
     args[0].includes('not wrapped in act'))
  ) {
    return;
  }
  originalError.call(console, ...args);
};

console.warn = (...args: any[]) => {
  if (
    typeof args[0] === 'string' &&
    (args[0].includes('Warning: ReactDOM.render is deprecated') ||
     args[0].includes('componentWillReceiveProps has been renamed'))
  ) {
    return;
  }
  originalWarn.call(console, ...args);
};