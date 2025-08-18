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

interface RegisterScreenProps {
  navigation: any;
}

interface FormData {
  name: string;          // Changed from fullName
  username: string;      // Added username field
  email: string;
  password: string;
  confirmPassword: string;
}

interface FormErrors {
  name?: string;         // Changed from fullName
  username?: string;     // Added username field
  email?: string;
  password?: string;
  confirmPassword?: string;
}

const RegisterScreen: React.FC<RegisterScreenProps> = ({ navigation }) => {
  const { t } = useTranslation('common');
  const { state, register, clearError } = useAuth();
  const [formData, setFormData] = useState<FormData>({
    name: '',        // Changed from fullName
    username: '',    // Added username field
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Clear auth error when component mounts or when user starts typing
  useEffect(() => {
    clearError();
  }, [clearError]);

  // Email validation regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  // Form validation
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Name validation (changed from fullName)
    if (!formData.name.trim()) {
      newErrors.name = t('auth.errors.nameRequired');
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    // Username validation (new field)
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.trim().length < 2) {
      newErrors.username = 'Username must be at least 2 characters';
    } else if (!/^[a-z0-9]+$/.test(formData.username.trim())) {
      newErrors.username = 'Username can only contain lowercase letters and numbers';
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = t('auth.errors.emailRequired');
    } else if (!emailRegex.test(formData.email.trim())) {
      newErrors.email = t('auth.errors.emailInvalid');
    }

    // Password validation - Updated to match backend requirements (8 chars minimum)
    if (!formData.password) {
      newErrors.password = t('auth.errors.passwordRequired');
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = t('auth.errors.confirmPasswordRequired');
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = t('auth.errors.passwordsDoNotMatch');
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
  const handleRegister = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      // Extract confirmPassword since it's not needed for the API
      const { confirmPassword, ...registrationData } = formData;
      
      // Trim and normalize data
      const normalizedData = {
        ...registrationData,
        email: registrationData.email.trim().toLowerCase(),
        username: registrationData.username.trim().toLowerCase(),
        name: registrationData.name.trim(),
      };
      
      // Pass data matching our backend API format
      await register(normalizedData);
      // Success is handled by the AuthContext and navigation will be handled by App.tsx
      Alert.alert(t('auth.success'), 'Registration successful!');
    } catch (error) {
      // Error is handled by the AuthContext
      console.error('Registration failed:', error);
    }
  };

  // Navigate to login screen
  const handleGoToLogin = () => {
    navigation.navigate('Login');
  };

  return (
    <ResponsiveLayout
      gradientColors={['#22c55e', '#059669']}
    >
      <ResponsiveCard>
        <ResponsiveHeader
          icon="📚"
          iconBackgroundColor="#22c55e"
          title={t('auth.register.title')}
          subtitle={t('auth.register.subtitle')}
        />

        {/* Registration Form */}
        <>
          {/* Name Input (changed from Full Name) */}
          <ResponsiveInput
            label={t('auth.name')}
            value={formData.name}
            onChangeText={(value) => handleInputChange('name', value)}
            placeholder={t('auth.namePlaceholder')}
            autoCapitalize="words"
            autoCorrect={false}
            editable={!state.isLoading}
            error={errors.name}
          />

          {/* Username Input (new field) */}
          <ResponsiveInput
            label="Username"
            value={formData.username}
            onChangeText={(value) => handleInputChange('username', value.toLowerCase())}
            placeholder="Choose a username"
            autoCapitalize="none"
            autoCorrect={false}
            editable={!state.isLoading}
            error={errors.username}
          />

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

          {/* Confirm Password Input */}
          <ResponsiveInput
            label={t('auth.confirmPassword')}
            value={formData.confirmPassword}
            onChangeText={(value) => handleInputChange('confirmPassword', value)}
            placeholder="Confirm your password"
            secureTextEntry={!showConfirmPassword}
            autoCapitalize="none"
            autoCorrect={false}
            editable={!state.isLoading}
            error={errors.confirmPassword}
            rightElement={
              <TouchableOpacity
                onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                style={{ padding: 4 }}
              >
                <Text style={{ fontSize: 18 }}>
                  {showConfirmPassword ? '👁️' : '🙈'}
                </Text>
              </TouchableOpacity>
            }
          />

          {/* Auth Error Message */}
          {state.error && (
            <View style={{ 
              marginBottom: 18,
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

          {/* Register Button */}
          <ResponsiveButton
            title={t('auth.register.button')}
            onPress={handleRegister}
            backgroundColor="#22c55e"
            disabled={state.isLoading}
            loading={state.isLoading}
            style={{ marginBottom: 20 }}
          />

          {/* Divider */}
          <ResponsiveDivider />

          {/* Login Link */}
          <ResponsiveLink
            text={`${t('auth.haveAccount')} `}
            linkText={t('auth.login.title')}
            onPress={handleGoToLogin}
            linkColor="#22c55e"
          />
        </>
      </ResponsiveCard>
    </ResponsiveLayout>
  );
};

export default RegisterScreen;