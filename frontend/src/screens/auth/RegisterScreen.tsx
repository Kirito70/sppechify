import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  ScrollView,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';

interface RegisterScreenProps {
  navigation?: any; // Will be properly typed when we add navigation
}

interface FormData {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
}

interface FormErrors {
  fullName?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}

const RegisterScreen: React.FC<RegisterScreenProps> = ({ navigation }) => {
  const { t } = useTranslation('common');
  const { state, register, clearError } = useAuth();
  const [formData, setFormData] = useState<FormData>({
    fullName: '',
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

    // Full name validation
    if (!formData.fullName.trim()) {
      newErrors.fullName = t('auth.errors.nameRequired');
    } else if (formData.fullName.trim().length < 2) {
      newErrors.fullName = 'Full name must be at least 2 characters';
    }

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
      await register(registrationData);
      // Success is handled by the AuthContext and navigation will be handled by App.tsx
      Alert.alert(t('auth.success'), 'Registration successful!');
    } catch (error) {
      // Error is handled by the AuthContext
      console.error('Registration failed:', error);
    }
  };

  // Navigate to login screen
  const handleGoToLogin = () => {
    // TODO: Navigate to login screen
    console.log('Navigate to login');
    // navigation?.navigate('Login');
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#f8fafc' }}>
      <KeyboardAvoidingView 
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView 
          style={{ flex: 1 }}
          contentContainerStyle={{ flexGrow: 1 }}
          keyboardShouldPersistTaps="handled"
        >
          <View style={{ flex: 1, padding: 20, justifyContent: 'center' }}>
            {/* Header */}
            <View style={{ alignItems: 'center', marginBottom: 40 }}>
              <Text style={{ 
                fontSize: 32, 
                fontWeight: 'bold', 
                color: '#1f2937',
                marginBottom: 8 
              }}>
                {t('auth.register.title')}
              </Text>
              <Text style={{ 
                fontSize: 16, 
                color: '#6b7280',
                textAlign: 'center' 
              }}>
                {t('auth.register.subtitle')}
              </Text>
            </View>

            {/* Registration Form */}
            <View>
              {/* Full Name Input */}
              <View style={{ marginBottom: 20 }}>
                <Text style={{ 
                  fontSize: 16, 
                  fontWeight: '600', 
                  color: '#374151',
                  marginBottom: 8 
                }}>
                  {t('auth.fullName')}
                </Text>
                <TextInput
                  style={{
                    borderWidth: 1,
                    borderColor: errors.fullName ? '#ef4444' : '#d1d5db',
                    borderRadius: 8,
                    padding: 12,
                    fontSize: 16,
                    backgroundColor: 'white',
                  }}
                  value={formData.fullName}
                  onChangeText={(value) => handleInputChange('fullName', value)}
                  placeholder={t('auth.namePlaceholder')}
                  autoCapitalize="words"
                  autoCorrect={false}
                  editable={!state.isLoading}
                />
                {errors.fullName && (
                  <Text style={{ color: '#ef4444', fontSize: 14, marginTop: 4 }}>
                    {errors.fullName}
                  </Text>
                )}
              </View>

              {/* Email Input */}
              <View style={{ marginBottom: 20 }}>
                <Text style={{ 
                  fontSize: 16, 
                  fontWeight: '600', 
                  color: '#374151',
                  marginBottom: 8 
                }}>
                  {t('auth.email')}
                </Text>
                <TextInput
                  style={{
                    borderWidth: 1,
                    borderColor: errors.email ? '#ef4444' : '#d1d5db',
                    borderRadius: 8,
                    padding: 12,
                    fontSize: 16,
                    backgroundColor: 'white',
                  }}
                  value={formData.email}
                  onChangeText={(value) => handleInputChange('email', value)}
                  placeholder={t('auth.emailPlaceholder')}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  autoCorrect={false}
                  editable={!state.isLoading}
                />
                {errors.email && (
                  <Text style={{ color: '#ef4444', fontSize: 14, marginTop: 4 }}>
                    {errors.email}
                  </Text>
                )}
              </View>

              {/* Password Input */}
              <View style={{ marginBottom: 20 }}>
                <Text style={{ 
                  fontSize: 16, 
                  fontWeight: '600', 
                  color: '#374151',
                  marginBottom: 8 
                }}>
                  {t('auth.password')}
                </Text>
                <View style={{ position: 'relative' }}>
                  <TextInput
                    style={{
                      borderWidth: 1,
                      borderColor: errors.password ? '#ef4444' : '#d1d5db',
                      borderRadius: 8,
                      padding: 12,
                      fontSize: 16,
                      backgroundColor: 'white',
                      paddingRight: 50,
                    }}
                    value={formData.password}
                    onChangeText={(value) => handleInputChange('password', value)}
                    placeholder={t('auth.passwordPlaceholder')}
                    secureTextEntry={!showPassword}
                    autoCapitalize="none"
                    autoCorrect={false}
                    editable={!state.isLoading}
                  />
                  <TouchableOpacity
                    style={{
                      position: 'absolute',
                      right: 12,
                      top: 12,
                      padding: 4,
                    }}
                    onPress={() => setShowPassword(!showPassword)}
                  >
                    <Text style={{ color: '#6b7280' }}>
                      {showPassword ? '👁️' : '🙈'}
                    </Text>
                  </TouchableOpacity>
                </View>
                {errors.password && (
                  <Text style={{ color: '#ef4444', fontSize: 14, marginTop: 4 }}>
                    {errors.password}
                  </Text>
                )}
              </View>

              {/* Confirm Password Input */}
              <View style={{ marginBottom: 20 }}>
                <Text style={{ 
                  fontSize: 16, 
                  fontWeight: '600', 
                  color: '#374151',
                  marginBottom: 8 
                }}>
                  {t('auth.confirmPassword')}
                </Text>
                <View style={{ position: 'relative' }}>
                  <TextInput
                    style={{
                      borderWidth: 1,
                      borderColor: errors.confirmPassword ? '#ef4444' : '#d1d5db',
                      borderRadius: 8,
                      padding: 12,
                      fontSize: 16,
                      backgroundColor: 'white',
                      paddingRight: 50,
                    }}
                    value={formData.confirmPassword}
                    onChangeText={(value) => handleInputChange('confirmPassword', value)}
                    placeholder="Confirm your password"
                    secureTextEntry={!showConfirmPassword}
                    autoCapitalize="none"
                    autoCorrect={false}
                    editable={!state.isLoading}
                  />
                  <TouchableOpacity
                    style={{
                      position: 'absolute',
                      right: 12,
                      top: 12,
                      padding: 4,
                    }}
                    onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                  >
                    <Text style={{ color: '#6b7280' }}>
                      {showConfirmPassword ? '👁️' : '🙈'}
                    </Text>
                  </TouchableOpacity>
                </View>
                {errors.confirmPassword && (
                  <Text style={{ color: '#ef4444', fontSize: 14, marginTop: 4 }}>
                    {errors.confirmPassword}
                  </Text>
                )}
              </View>

              {/* Auth Error Message */}
              {state.error && (
                <View style={{ 
                  marginBottom: 20,
                  padding: 12,
                  backgroundColor: '#fef2f2',
                  borderRadius: 8,
                  borderWidth: 1,
                  borderColor: '#fecaca'
                }}>
                  <Text style={{ color: '#dc2626', fontSize: 14 }}>
                    {state.error}
                  </Text>
                </View>
              )}

              {/* Register Button */}
              <TouchableOpacity
                style={{
                  backgroundColor: state.isLoading ? '#9ca3af' : '#22c55e',
                  padding: 16,
                  borderRadius: 8,
                  alignItems: 'center',
                  marginBottom: 24,
                }}
                onPress={handleRegister}
                disabled={state.isLoading}
              >
                {state.isLoading ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <Text style={{ 
                    color: 'white', 
                    fontSize: 16, 
                    fontWeight: '600' 
                  }}>
                    {t('auth.register.button')}
                  </Text>
                )}
              </TouchableOpacity>

              {/* Login Link */}
              <View style={{ 
                flexDirection: 'row', 
                justifyContent: 'center',
                alignItems: 'center' 
              }}>
                <Text style={{ color: '#6b7280', fontSize: 14 }}>
                  {t('auth.haveAccount')} 
                </Text>
                <TouchableOpacity onPress={handleGoToLogin}>
                  <Text style={{ color: '#3b82f6', fontSize: 14, fontWeight: '600' }}>
                    {t('auth.login.title')}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

export default RegisterScreen;