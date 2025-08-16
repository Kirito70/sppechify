import React from 'react';
import { View, Text, TouchableOpacity, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useTranslation } from 'react-i18next';
import env from '../config/env';

export default function HomeScreen() {
  const { t } = useTranslation('common');

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#f8fafc' }}>
      <ScrollView style={{ flex: 1 }}>
        {/* Header */}
        <View style={{ 
          padding: 20, 
          backgroundColor: '#3b82f6',
          borderBottomLeftRadius: 20,
          borderBottomRightRadius: 20
        }}>
          <Text style={{ 
            fontSize: 24, 
            fontWeight: 'bold', 
            color: 'white',
            marginBottom: 8 
          }}>
            {t('home.title')}
          </Text>
          <Text style={{ fontSize: 16, color: '#e0e7ff' }}>
            {t('home.welcomeMessage')}
          </Text>
          {env.ENABLE_DEBUG_LOGS && __DEV__ && (
            <Text style={{ fontSize: 12, color: '#e0e7ff', marginTop: 8 }}>
              🔧 API: {env.API_BASE_URL}
            </Text>
          )}
        </View>

        {/* Daily Progress */}
        <View style={{ 
          margin: 20, 
          padding: 16, 
          backgroundColor: 'white',
          borderRadius: 12,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: 2 },
          shadowOpacity: 0.1,
          shadowRadius: 4,
          elevation: 3
        }}>
          <Text style={{ fontSize: 18, fontWeight: '600', marginBottom: 12 }}>
            {t('home.todayProgress')}
          </Text>
          
          <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
            <View style={{ alignItems: 'center' }}>
              <Text style={{ fontSize: 24, fontWeight: 'bold', color: '#22c55e' }}>
                0
              </Text>
              <Text style={{ fontSize: 12, color: '#6b7280' }}>
                {t('home.wordsLearned')}
              </Text>
            </View>
            <View style={{ alignItems: 'center' }}>
              <Text style={{ fontSize: 24, fontWeight: 'bold', color: '#3b82f6' }}>
                0
              </Text>
              <Text style={{ fontSize: 12, color: '#6b7280' }}>
                {t('home.minutes')}
              </Text>
            </View>
            <View style={{ alignItems: 'center' }}>
              <Text style={{ fontSize: 24, fontWeight: 'bold', color: '#f59e0b' }}>
                0
              </Text>
              <Text style={{ fontSize: 12, color: '#6b7280' }}>
                {t('home.days')}
              </Text>
            </View>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={{ paddingHorizontal: 20 }}>
          <Text style={{ 
            fontSize: 18, 
            fontWeight: '600', 
            marginBottom: 16,
            color: '#1f2937'
          }}>
            {t('home.quickActions')}
          </Text>
          
          <TouchableOpacity 
            style={{ 
              backgroundColor: '#22c55e',
              padding: 16,
              borderRadius: 12,
              marginBottom: 12,
              alignItems: 'center'
            }}
            onPress={() => {
              if (env.ENABLE_DEBUG_LOGS) {
                console.log('Start Learning pressed');
              }
            }}
          >
            <Text style={{ 
              color: 'white', 
              fontSize: 16, 
              fontWeight: '600' 
            }}>
              📚 {t('home.startLearning')}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={{ 
              backgroundColor: '#3b82f6',
              padding: 16,
              borderRadius: 12,
              marginBottom: 12,
              alignItems: 'center'
            }}
            onPress={() => {
              if (env.ENABLE_DEBUG_LOGS) {
                console.log('Take Photo pressed - API Base URL:', env.API_BASE_URL);
              }
            }}
          >
            <Text style={{ 
              color: 'white', 
              fontSize: 16, 
              fontWeight: '600' 
            }}>
              📸 {t('home.takePhoto')}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={{ 
              backgroundColor: '#f59e0b',
              padding: 16,
              borderRadius: 12,
              marginBottom: 12,
              alignItems: 'center'
            }}
            onPress={() => {
              if (env.ENABLE_DEBUG_LOGS) {
                console.log('Review Cards pressed');
              }
            }}
          >
            <Text style={{ 
              color: 'white', 
              fontSize: 16, 
              fontWeight: '600' 
            }}>
              🔄 {t('home.reviewCards')}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Recent Activity */}
        <View style={{ 
          margin: 20, 
          padding: 16, 
          backgroundColor: 'white',
          borderRadius: 12,
          shadowColor: '#000',
          shadowOffset: { width: 0, height: 2 },
          shadowOpacity: 0.1,
          shadowRadius: 4,
          elevation: 3
        }}>
          <Text style={{ fontSize: 18, fontWeight: '600', marginBottom: 12 }}>
            Recent Activity
          </Text>
          <Text style={{ color: '#6b7280', textAlign: 'center', padding: 20 }}>
            No activity yet. Start learning to see your progress here!
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}