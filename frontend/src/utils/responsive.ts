import { Dimensions, Platform } from 'react-native';

// Get device dimensions
const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

// Breakpoints based on common device sizes
export const breakpoints = {
  xs: 320,   // Small phones
  sm: 375,   // iPhone SE, etc.
  md: 414,   // iPhone 11 Pro, etc.
  lg: 768,   // Tablets
  xl: 1024,  // Large tablets
  xxl: 1200, // Desktop
};

// Screen type detection
export const getScreenType = () => {
  if (screenWidth < breakpoints.sm) return 'xs';
  if (screenWidth < breakpoints.md) return 'sm';
  if (screenWidth < breakpoints.lg) return 'md';
  if (screenWidth < breakpoints.xl) return 'lg';
  if (screenWidth < breakpoints.xxl) return 'xl';
  return 'xxl';
};

// Device type detection
export const isPhone = screenWidth < breakpoints.lg;
export const isTablet = screenWidth >= breakpoints.lg && screenWidth < breakpoints.xxl;
export const isDesktop = screenWidth >= breakpoints.xxl;
export const isSmallScreen = screenHeight < 600;
export const isMediumScreen = screenHeight >= 600 && screenHeight < 800;
export const isLargeScreen = screenHeight >= 800;

// Responsive values based on screen width
export const responsive = {
  // Padding and margins
  padding: {
    xs: 12,
    sm: 16,
    md: 20,
    lg: 24,
    xl: 32,
  },
  
  // Card dimensions
  card: {
    maxWidth: isDesktop ? 400 : isTablet ? 350 : '100%',
    padding: isPhone ? (isSmallScreen ? 16 : 20) : 24,
    margin: isPhone ? (isSmallScreen ? 8 : 12) : 16,
    borderRadius: isPhone ? 16 : 20,
  },
  
  // Typography
  text: {
    title: isPhone ? (isSmallScreen ? 20 : 24) : 28,
    subtitle: isPhone ? (isSmallScreen ? 13 : 14) : 16,
    label: isPhone ? 12 : 13,
    body: 14,
    caption: 12,
  },
  
  // Icon sizes
  icon: {
    small: isPhone ? 40 : 48,
    medium: isPhone ? (isSmallScreen ? 48 : 56) : 64,
    large: isPhone ? 64 : 80,
  },
  
  // Input dimensions
  input: {
    height: isPhone ? (isSmallScreen ? 44 : 48) : 52,
    padding: isPhone ? (isSmallScreen ? 12 : 14) : 16,
    fontSize: isPhone ? 15 : 16,
    borderRadius: isPhone ? 8 : 12,
  },
  
  // Button dimensions
  button: {
    height: isPhone ? (isSmallScreen ? 44 : 48) : 52,
    padding: isPhone ? (isSmallScreen ? 12 : 16) : 18,
    fontSize: isPhone ? 15 : 16,
    borderRadius: isPhone ? 8 : 12,
  },
  
  // Spacing
  spacing: {
    xs: isPhone ? (isSmallScreen ? 4 : 6) : 8,
    sm: isPhone ? (isSmallScreen ? 8 : 10) : 12,
    md: isPhone ? (isSmallScreen ? 12 : 16) : 20,
    lg: isPhone ? (isSmallScreen ? 16 : 20) : 24,
    xl: isPhone ? (isSmallScreen ? 20 : 24) : 32,
    xxl: isPhone ? (isSmallScreen ? 24 : 32) : 40,
  },
};

// Responsive style generator
export const createResponsiveStyle = (styles: {
  xs?: any;
  sm?: any;
  md?: any;
  lg?: any;
  xl?: any;
  xxl?: any;
}) => {
  const screenType = getScreenType();
  return styles[screenType] || styles.md || {};
};

// Platform-specific responsive adjustments
export const platformResponsive = {
  web: {
    // Web-specific responsive adjustments
    cardShadow: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.15,
      shadowRadius: 20,
      // CSS fallback for web
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
    },
    
    // Better scrolling on web
    scrollView: {
      scrollbarWidth: 'none' as any,
      msOverflowStyle: 'none' as any,
      '&::-webkit-scrollbar': {
        display: 'none',
      },
    },
  },
  
  native: {
    // Native-specific responsive adjustments
    cardShadow: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.15,
      shadowRadius: 20,
      elevation: 12,
    },
  },
};

// Get current platform responsive styles
export const getPlatformStyles = () => {
  return Platform.OS === 'web' ? platformResponsive.web : platformResponsive.native;
};

// Responsive layout helpers
export const getLayoutStyles = () => ({
  card: {
    backgroundColor: 'white',
    borderRadius: responsive.card.borderRadius,
    padding: responsive.card.padding,
    marginHorizontal: responsive.card.margin,
    maxWidth: responsive.card.maxWidth,
    alignSelf: 'center' as const,
    width: '100%',
    ...getPlatformStyles().cardShadow,
  },
  
  header: {
    alignItems: 'center' as const,
    marginBottom: responsive.spacing.lg,
  },
  
  icon: {
    width: responsive.icon.medium,
    height: responsive.icon.medium,
    borderRadius: responsive.icon.medium * 0.25,
    justifyContent: 'center' as const,
    alignItems: 'center' as const,
    marginBottom: responsive.spacing.sm,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  
  title: {
    fontSize: responsive.text.title,
    fontWeight: '700' as const,
    color: '#1a202c',
    marginBottom: responsive.spacing.xs,
    letterSpacing: -0.5,
    textAlign: 'center' as const,
  },
  
  subtitle: {
    fontSize: responsive.text.subtitle,
    color: '#718096',
    textAlign: 'center' as const,
    lineHeight: responsive.text.subtitle * 1.4,
  },
  
  formGroup: {
    marginBottom: responsive.spacing.md,
  },
  
  label: {
    fontSize: responsive.text.label,
    fontWeight: '600' as const,
    color: '#374151',
    marginBottom: responsive.spacing.xs,
    textTransform: 'uppercase' as const,
    letterSpacing: 0.5,
  },
  
  inputContainer: {
    borderWidth: 2,
    borderRadius: responsive.input.borderRadius,
    backgroundColor: '#f8fafc',
    overflow: 'hidden' as const,
  },
  
  input: {
    padding: responsive.input.padding,
    fontSize: responsive.input.fontSize,
    color: '#1a202c',
    fontWeight: '500' as const,
    minHeight: responsive.input.height,
  },
  
  button: {
    padding: responsive.button.padding,
    borderRadius: responsive.button.borderRadius,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    minHeight: responsive.button.height,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
  
  buttonText: {
    color: 'white',
    fontSize: responsive.button.fontSize,
    fontWeight: '700' as const,
    letterSpacing: 0.5,
  },
  
  errorText: {
    color: '#ef4444',
    fontSize: responsive.text.caption,
    marginTop: responsive.spacing.xs,
    fontWeight: '500' as const,
  },
  
  divider: {
    flexDirection: 'row' as const,
    alignItems: 'center' as const,
    marginVertical: responsive.spacing.md,
  },
  
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#e2e8f0',
  },
  
  dividerText: {
    marginHorizontal: responsive.spacing.sm,
    color: '#94a3b8',
    fontSize: responsive.text.caption,
    fontWeight: '500' as const,
  },
  
  linkContainer: {
    flexDirection: 'row' as const,
    justifyContent: 'center' as const,
    alignItems: 'center' as const,
    backgroundColor: '#f8fafc',
    padding: responsive.spacing.sm,
    borderRadius: responsive.input.borderRadius - 2,
    minHeight: responsive.button.height - 6,
  },
});

export default responsive;