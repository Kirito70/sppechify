import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text, ActivityIndicator } from 'react-native';
import { useTranslation } from 'react-i18next';

// Import screens
import HomeScreen from '../screens/HomeScreen';
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';

// Import auth context
import { useAuth } from '../contexts/AuthContext';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Temporary placeholder screens
const PlaceholderScreen = ({ name }: { name: string }) => {
  const { t } = useTranslation('common');
  
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text style={{ fontSize: 18 }}>{name} Screen</Text>
      <Text style={{ fontSize: 14, color: '#6b7280', marginTop: 8 }}>
        Coming soon...
      </Text>
    </View>
  );
};

function MainTabs() {
  const { t } = useTranslation('common');

  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopWidth: 1,
          borderTopColor: '#e5e7eb',
          paddingBottom: 8,
          paddingTop: 8,
          height: 60,
        },
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
        tabBarActiveTintColor: '#3b82f6',
        tabBarInactiveTintColor: '#6b7280',
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          tabBarLabel: t('navigation.home'),
        }}
      />
      <Tab.Screen 
        name="Learning" 
        component={() => <PlaceholderScreen name="Learning" />}
        options={{
          tabBarLabel: t('navigation.learn'),
        }}
      />
      <Tab.Screen 
        name="Camera" 
        component={() => <PlaceholderScreen name="Camera" />}
        options={{
          tabBarLabel: t('navigation.camera'),
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={() => <PlaceholderScreen name="Profile" />}
        options={{
          tabBarLabel: t('navigation.profile'),
        }}
      />
    </Tab.Navigator>
  );
}

// Auth Stack Navigator
function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
}

export default function AppNavigation() {
  const { state } = useAuth();
  const { t } = useTranslation('common');

  // Show loading screen while checking authentication status
  if (state.isLoading) {
    return (
      <NavigationContainer>
        <View style={{ 
          flex: 1, 
          justifyContent: 'center', 
          alignItems: 'center',
          backgroundColor: '#ffffff'
        }}>
          <ActivityIndicator size="large" color="#3b82f6" />
          <Text style={{ 
            marginTop: 16, 
            fontSize: 16, 
            color: '#6b7280' 
          }}>
            {t('auth.loading')}
          </Text>
        </View>
      </NavigationContainer>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {state.isAuthenticated ? (
          // User is authenticated - show main app
          <Stack.Screen name="MainTabs" component={MainTabs} />
        ) : (
          // User is not authenticated - show auth screens
          <Stack.Screen name="Auth" component={AuthStack} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}