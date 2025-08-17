import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import {
  ResponsiveLayout,
  ResponsiveCard,
  ResponsiveHeader,
  ResponsiveInput,
  ResponsiveButton,
  ResponsiveDivider,
  ResponsiveLink,
} from '../../components/ResponsiveLayout';

interface LoginScreenProps {
  navigation: any;
}

interface FormData {
  email: string;
  password: string;
}

interface FormErrors {
  email?: string;
  password?: string;
}

const LoginScreen: React.FC<LoginScreenProps> = ({ navigation }) => {
  const { t } = useTranslation('common');
  const { state, login, clearError } = useAuth();
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [showPassword, setShowPassword] = useState(false);

  // Clear auth error when component mounts or when user starts typing
  useEffect(() => {
    clearError();
  }, [clearError]);

  // Email validation regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  // Form validation
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = t('auth.errors.emailRequired');
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = t('auth.errors.emailInvalid');
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = t('auth.errors.passwordRequired');
    } else if (formData.password.length < 6) {
      newErrors.password = t('auth.errors.passwordTooShort');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle input changes
  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear field error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
    // Clear auth error when user starts typing
    if (state.error) {
      clearError();
    }
  };

  // Handle form submission
  const handleLogin = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      await login(formData);
      // Success is handled by the AuthContext and navigation will be handled by App.tsx
      Alert.alert(t('auth.success'), t('auth.loginSuccess'));
    } catch (error) {
      // Error is handled by the AuthContext
      console.error('Login failed:', error);
    }
  };

  // Navigate to register screen
  const handleGoToRegister = () => {
    navigation.navigate('Register');
  };

  // Navigate to forgot password screen
  const handleForgotPassword = () => {
    navigation.navigate('ForgotPassword');
  };

  return (
    <ResponsiveLayout
      gradientColors={['#667eea', '#764ba2']}
    >
      <ResponsiveCard>
        <ResponsiveHeader
          icon="📚"
          iconBackgroundColor="#667eea"
          title={t('auth.login.title')}
          subtitle={t('auth.login.subtitle')}
        />

        {/* Login Form */}
        <>
          {/* Email Input */}
          <ResponsiveInput
            label={t('auth.email')}
            value={formData.email}
            onChangeText={(value) => handleInputChange('email', value)}
            placeholder={t('auth.emailPlaceholder')}
            keyboardType="email-address"
            autoCapitalize="none"
            autoCorrect={false}
            editable={!state.isLoading}
            error={errors.email}
          />

          {/* Password Input */}
          <ResponsiveInput
            label={t('auth.password')}
            value={formData.password}
            onChangeText={(value) => handleInputChange('password', value)}
            placeholder={t('auth.passwordPlaceholder')}
            secureTextEntry={!showPassword}
            autoCapitalize="none"
            autoCorrect={false}
            editable={!state.isLoading}
            error={errors.password}
            rightElement={
              <TouchableOpacity
                onPress={() => setShowPassword(!showPassword)}
                style={{ padding: 4 }}
              >
                <Text style={{ fontSize: 18 }}>
                  {showPassword ? '👁️' : '🙈'}
                </Text>
              </TouchableOpacity>
            }
          />

          {/* Auth Error Message */}
          {state.error && (
            <View style={{ 
              marginBottom: 20,
              padding: 12,
              backgroundColor: '#fef2f2',
              borderRadius: 10,
              borderWidth: 1,
              borderColor: '#fecaca'
            }}>
              <Text style={{ 
                color: '#dc2626', 
                fontSize: 13,
                fontWeight: '500',
                textAlign: 'center'
              }}>
                {state.error}
              </Text>
            </View>
          )}

          {/* Login Button */}
          <ResponsiveButton
            title={t('auth.login.button')}
            onPress={handleLogin}
            backgroundColor="#667eea"
            disabled={state.isLoading}
            loading={state.isLoading}
            style={{ marginBottom: 16 }}
          />

          {/* Forgot Password Link */}
          <TouchableOpacity
            style={{ 
              alignItems: 'center', 
              marginBottom: 20,
              padding: 8,
            }}
            onPress={handleForgotPassword}
          >
            <Text style={{ 
              color: '#667eea', 
              fontSize: 14,
              fontWeight: '600'
            }}>
              {t('auth.forgotPassword')}
            </Text>
          </TouchableOpacity>

          {/* Divider */}
          <ResponsiveDivider />

          {/* Register Link */}
          <ResponsiveLink
            text={`${t('auth.noAccount')} `}
            linkText={t('auth.register.title')}
            onPress={handleGoToRegister}
            linkColor="#667eea"
          />
        </>
      </ResponsiveCard>
    </ResponsiveLayout>
  );
};

export default LoginScreen;