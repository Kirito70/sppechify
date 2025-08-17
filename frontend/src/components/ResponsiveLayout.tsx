import React from 'react';
import {
  View,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ViewStyle,
  ScrollViewProps,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Text,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { getLayoutStyles, responsive } from '../utils/responsive';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  backgroundColor?: string;
  gradientColors?: string[];
  showScrollIndicator?: boolean;
  keyboardAvoidBehavior?: 'height' | 'position' | 'padding';
  contentContainerStyle?: ViewStyle;
  scrollViewProps?: Partial<ScrollViewProps>;
  safeAreaStyle?: ViewStyle;
}

export const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({
  children,
  backgroundColor = '#f8fafc',
  gradientColors,
  showScrollIndicator = false,
  keyboardAvoidBehavior = Platform.OS === 'ios' ? 'padding' : 'height',
  contentContainerStyle = {},
  scrollViewProps = {},
  safeAreaStyle = {},
}) => {
  const layoutStyles = getLayoutStyles();

  return (
    <View style={{ 
      flex: 1,
      backgroundColor: gradientColors ? gradientColors[0] : backgroundColor,
    }}>
      {/* Gradient Background */}
      {gradientColors && gradientColors[1] && (
        <View style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: gradientColors[1],
          opacity: 0.8,
        }} />
      )}

      <SafeAreaView style={[{ flex: 1 }, safeAreaStyle]}>
        <KeyboardAvoidingView 
          style={{ flex: 1 }}
          behavior={keyboardAvoidBehavior}
        >
          <ScrollView 
            style={{ flex: 1 }}
            contentContainerStyle={[
              {
                padding: responsive.spacing.md,
                paddingTop: responsive.spacing.xl,
                paddingBottom: responsive.spacing.xl,
                minHeight: '100%',
                justifyContent: 'center',
              },
              contentContainerStyle,
            ]}
            keyboardShouldPersistTaps="handled"
            showsVerticalScrollIndicator={showScrollIndicator}
            scrollEnabled={true}
            bounces={Platform.OS === 'ios'}
            {...scrollViewProps}
          >
            {children}
          </ScrollView>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </View>
  );
};

interface ResponsiveCardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  maxWidth?: number | string;
}

export const ResponsiveCard: React.FC<ResponsiveCardProps> = ({
  children,
  style = {},
  maxWidth,
}) => {
  const layoutStyles = getLayoutStyles();

  return (
    <View style={[
      layoutStyles.card,
      maxWidth && { maxWidth },
      style,
    ]}>
      {children}
    </View>
  );
};

interface ResponsiveHeaderProps {
  icon?: string;
  iconBackgroundColor?: string;
  title: string;
  subtitle?: string;
  style?: ViewStyle;
}

export const ResponsiveHeader: React.FC<ResponsiveHeaderProps> = ({
  icon = '📚',
  iconBackgroundColor = '#667eea',
  title,
  subtitle,
  style = {},
}) => {
  const layoutStyles = getLayoutStyles();

  return (
    <View style={[layoutStyles.header, style]}>
      <View style={[
        layoutStyles.icon,
        { backgroundColor: iconBackgroundColor, shadowColor: iconBackgroundColor },
      ]}>
        <Text style={{ 
          fontSize: responsive.icon.medium * 0.4, 
          color: 'white' 
        }}>
          {icon}
        </Text>
      </View>
      <Text style={layoutStyles.title}>
        {title}
      </Text>
      {subtitle && (
        <Text style={layoutStyles.subtitle}>
          {subtitle}
        </Text>
      )}
    </View>
  );
};

interface ResponsiveInputProps {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  secureTextEntry?: boolean;
  keyboardType?: 'default' | 'email-address' | 'numeric' | 'phone-pad';
  autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';
  autoCorrect?: boolean;
  editable?: boolean;
  error?: string;
  rightElement?: React.ReactNode;
  style?: ViewStyle;
}

export const ResponsiveInput: React.FC<ResponsiveInputProps> = ({
  label,
  value,
  onChangeText,
  placeholder,
  secureTextEntry = false,
  keyboardType = 'default',
  autoCapitalize = 'sentences',
  autoCorrect = true,
  editable = true,
  error,
  rightElement,
  style = {},
}) => {
  const layoutStyles = getLayoutStyles();

  return (
    <View style={[layoutStyles.formGroup, style]}>
      <Text style={layoutStyles.label}>
        {label}
      </Text>
      <View style={[
        layoutStyles.inputContainer,
        { borderColor: error ? '#ef4444' : '#e2e8f0' },
      ]}>
        <TextInput
          style={[
            layoutStyles.input,
            rightElement && { paddingRight: responsive.spacing.xxl },
          ]}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor="#94a3b8"
          secureTextEntry={secureTextEntry}
          keyboardType={keyboardType}
          autoCapitalize={autoCapitalize}
          autoCorrect={autoCorrect}
          editable={editable}
        />
        {rightElement && (
          <View style={{
            position: 'absolute',
            right: responsive.spacing.sm,
            top: responsive.spacing.sm,
          }}>
            {rightElement}
          </View>
        )}
      </View>
      {error && (
        <Text style={layoutStyles.errorText}>
          {error}
        </Text>
      )}
    </View>
  );
};

interface ResponsiveButtonProps {
  title: string;
  onPress: () => void;
  backgroundColor?: string;
  disabled?: boolean;
  loading?: boolean;
  style?: ViewStyle;
  textStyle?: ViewStyle;
}

export const ResponsiveButton: React.FC<ResponsiveButtonProps> = ({
  title,
  onPress,
  backgroundColor = '#667eea',
  disabled = false,
  loading = false,
  style = {},
  textStyle = {},
}) => {
  const layoutStyles = getLayoutStyles();

  return (
    <TouchableOpacity
      style={[
        layoutStyles.button,
        {
          backgroundColor: disabled || loading ? '#94a3b8' : backgroundColor,
          shadowColor: backgroundColor,
          shadowOpacity: disabled || loading ? 0 : 0.3,
          elevation: disabled || loading ? 0 : 6,
        },
        style,
      ]}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.8}
    >
      {loading ? (
        <ActivityIndicator color="white" size="small" />
      ) : (
        <Text style={[layoutStyles.buttonText, textStyle]}>
          {title}
        </Text>
      )}
    </TouchableOpacity>
  );
};

interface ResponsiveDividerProps {
  text?: string;
  style?: ViewStyle;
}

export const ResponsiveDivider: React.FC<ResponsiveDividerProps> = ({
  text = 'or',
  style = {},
}) => {
  const layoutStyles = getLayoutStyles();

  return (
    <View style={[layoutStyles.divider, style]}>
      <View style={layoutStyles.dividerLine} />
      <Text style={layoutStyles.dividerText}>
        {text}
      </Text>
      <View style={layoutStyles.dividerLine} />
    </View>
  );
};

interface ResponsiveLinkProps {
  text: string;
  linkText: string;
  onPress: () => void;
  linkColor?: string;
  style?: ViewStyle;
}

export const ResponsiveLink: React.FC<ResponsiveLinkProps> = ({
  text,
  linkText,
  onPress,
  linkColor = '#667eea',
  style = {},
}) => {
  const layoutStyles = getLayoutStyles();

  return (
    <TouchableOpacity 
      style={[layoutStyles.linkContainer, style]}
      onPress={onPress}
    >
      <Text style={{ 
        color: '#64748b', 
        fontSize: responsive.text.body,
        marginRight: responsive.spacing.xs,
      }}>
        {text}
      </Text>
      <Text style={{ 
        color: linkColor, 
        fontSize: responsive.text.body, 
        fontWeight: '700'
      }}>
        {linkText}
      </Text>
    </TouchableOpacity>
  );
};