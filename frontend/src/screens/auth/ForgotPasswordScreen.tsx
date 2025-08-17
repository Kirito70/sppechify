import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useTranslation } from 'react-i18next';
import {
  ResponsiveLayout,
  ResponsiveCard,
  ResponsiveHeader,
  ResponsiveInput,
  ResponsiveButton,
  ResponsiveDivider,
  ResponsiveLink,
} from '../../components/ResponsiveLayout';

interface ForgotPasswordScreenProps {
  navigation: any;
}

interface FormErrors {
  email?: string;
}

const ForgotPasswordScreen: React.FC<ForgotPasswordScreenProps> = ({ navigation }) => {
  const { t } = useTranslation('common');
  const [email, setEmail] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);

  // Email validation regex
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  // Form validation
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Email validation
    if (!email.trim()) {
      newErrors.email = t('auth.errors.emailRequired');
    } else if (!emailRegex.test(email)) {
      newErrors.email = t('auth.errors.emailInvalid');
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle input changes
  const handleEmailChange = (value: string) => {
    setEmail(value);
    // Clear field error when user starts typing
    if (errors.email) {
      setErrors(prev => ({ ...prev, email: undefined }));
    }
  };

  // Handle form submission
  const handleResetPassword = async () => {
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // TODO: Implement actual forgot password API call
      // For now, just simulate the request
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      Alert.alert(
        t('auth.success'),
        'Password reset instructions have been sent to your email address.',
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error) {
      console.error('Forgot password error:', error);
      Alert.alert(
        t('auth.error'),
        'Failed to send reset instructions. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Navigate back to login screen
  const handleGoToLogin = () => {
    navigation.navigate('Login');
  };

  return (
    <ResponsiveLayout
      gradientColors={['#ec4899', '#be185d']}
    >
      <ResponsiveCard>
        <ResponsiveHeader
          icon="🔐"
          iconBackgroundColor="#ec4899"
          title="Reset Password"
          subtitle="Enter your email address and we'll send you instructions to reset your password."
        />

        {/* Reset Password Form */}
        <>
          {/* Email Input */}
          <ResponsiveInput
            label={t('auth.email')}
            value={email}
            onChangeText={handleEmailChange}
            placeholder={t('auth.emailPlaceholder')}
            keyboardType="email-address"
            autoCapitalize="none"
            autoCorrect={false}
            editable={!isLoading}
            error={errors.email}
          />

          {/* Reset Password Button */}
          <ResponsiveButton
            title="Send Reset Instructions"
            onPress={handleResetPassword}
            backgroundColor="#ec4899"
            disabled={isLoading}
            loading={isLoading}
            style={{ marginBottom: 20 }}
          />

          {/* Divider */}
          <ResponsiveDivider />

          {/* Back to Login Link */}
          <ResponsiveLink
            text="Remember your password? "
            linkText="Sign In"
            onPress={handleGoToLogin}
            linkColor="#ec4899"
          />
        </>
      </ResponsiveCard>
    </ResponsiveLayout>
  );
};

export default ForgotPasswordScreen;