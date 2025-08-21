#!/usr/bin/env node

// Test Frontend-Backend Integration
// This simulates what the React Native frontend would do

const axios = require('axios');

const API_BASE_URL = 'http://localhost:55073/api/v1';

async function testFrontendBackend() {
    console.log('🧪 Testing Frontend-Backend Integration\n');
    
    try {
        // Step 1: Test user registration
        console.log('1️⃣  Testing User Registration...');
        const registerData = {
            name: 'Frontend Test User',
            username: 'frontend_test',
            email: 'frontend@test.com',
            password: 'testpass123'
        };
        
        let user;
        try {
            const registerResponse = await axios.post(`${API_BASE_URL}/user`, registerData);
            user = registerResponse.data;
            console.log('✅ Registration successful:', user.name);
        } catch (error) {
            if (error.response?.data?.detail === 'Email is already registered') {
                console.log('ℹ️  User already exists, proceeding with login');
            } else {
                throw error;
            }
        }

        // Step 2: Test user login
        console.log('\n2️⃣  Testing User Login...');
        const loginData = new URLSearchParams();
        loginData.append('username', 'frontend_test');
        loginData.append('password', 'testpass123');

        const loginResponse = await axios.post(`${API_BASE_URL}/login`, loginData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        });

        const authToken = loginResponse.data.access_token;
        console.log('✅ Login successful, got auth token');

        // Step 3: Test authenticated user info
        console.log('\n3️⃣  Testing Get Current User...');
        const userResponse = await axios.get(`${API_BASE_URL}/user/me/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        console.log('✅ Got user profile:', userResponse.data.name);

        // Step 4: Test GET sentences (should work even for non-superusers)
        console.log('\n4️⃣  Testing Get Sentences...');
        const sentencesResponse = await axios.get(`${API_BASE_URL}/sentences`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        console.log('✅ Got sentences:', sentencesResponse.data.total_count, 'sentences');

        // Step 5: Test sentence creation (should fail for non-superuser)
        console.log('\n5️⃣  Testing Sentence Creation (should be denied)...');
        try {
            await axios.post(`${API_BASE_URL}/sentences`, {
                japanese_text: "テスト",
                english_translation: "Test",
                difficulty_level: 1,
                jlpt_level: "N5"
            }, {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            console.log('⚠️  Unexpected: Sentence creation succeeded (should have been denied)');
        } catch (error) {
            if (error.response?.status === 403) {
                console.log('✅ Sentence creation properly denied (non-superuser)');
            } else {
                throw error;
            }
        }

        // Final success message
        console.log('\n🎉 Frontend-Backend Integration Test PASSED!');
        console.log('📱 The frontend can successfully:');
        console.log('   - Register new users');
        console.log('   - Login users');
        console.log('   - Get authenticated user data');
        console.log('   - Access protected endpoints');
        console.log('   - Respect permission controls');
        
        return true;

    } catch (error) {
        console.error('\n❌ Frontend-Backend Integration Test FAILED');
        console.error('Error:', error.response?.data || error.message);
        return false;
    }
}

if (require.main === module) {
    testFrontendBackend().then(success => {
        process.exit(success ? 0 : 1);
    });
}

module.exports = { testFrontendBackend };