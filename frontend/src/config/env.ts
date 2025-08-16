import Constants from 'expo-constants';

interface EnvConfig {
  API_URL: string;
  API_VERSION: string;
  API_BASE_URL: string;
  WS_URL: string;
  APP_NAME: string;
  APP_VERSION: string;
  NODE_ENV: string;
  ENABLE_DEBUG_LOGS: boolean;
  ENABLE_OFFLINE_MODE: boolean;
  ENABLE_ANALYTICS: boolean;
}

const getEnvVar = (name: string, defaultValue: string = ''): string => {
  // Try to get from Expo config first
  const value = Constants.expoConfig?.extra?.[name] || 
                Constants.manifest?.extra?.[name] ||
                Constants.manifest2?.extra?.[name];
  
  if (value !== undefined) {
    return value;
  }
  
  // Fallback to default values for development
  const envDefaults: Record<string, string> = {
    API_URL: 'http://localhost:8000',
    API_VERSION: 'v1',
    WS_URL: 'ws://localhost:8000',
    APP_NAME: 'Language Learning',
    APP_VERSION: '1.0.0',
    NODE_ENV: 'development',
    ENABLE_DEBUG_LOGS: 'true',
    ENABLE_OFFLINE_MODE: 'true',
    ENABLE_ANALYTICS: 'false'
  };
  
  return envDefaults[name] || defaultValue;
};

const parseBoolean = (value: string): boolean => {
  return value.toLowerCase() === 'true';
};

export const env: EnvConfig = {
  API_URL: getEnvVar('API_URL'),
  API_VERSION: getEnvVar('API_VERSION'),
  API_BASE_URL: `${getEnvVar('API_URL')}/api/${getEnvVar('API_VERSION')}`,
  WS_URL: getEnvVar('WS_URL'),
  APP_NAME: getEnvVar('APP_NAME'),
  APP_VERSION: getEnvVar('APP_VERSION'),
  NODE_ENV: getEnvVar('NODE_ENV'),
  ENABLE_DEBUG_LOGS: parseBoolean(getEnvVar('ENABLE_DEBUG_LOGS')),
  ENABLE_OFFLINE_MODE: parseBoolean(getEnvVar('ENABLE_OFFLINE_MODE')),
  ENABLE_ANALYTICS: parseBoolean(getEnvVar('ENABLE_ANALYTICS'))
};

// Debug logging
if (env.ENABLE_DEBUG_LOGS && __DEV__) {
  console.log('🔧 Environment Configuration:', {
    ...env,
    // Don't log sensitive information in production builds
    NODE_ENV: env.NODE_ENV,
    API_BASE_URL: env.API_BASE_URL
  });
}

export default env;