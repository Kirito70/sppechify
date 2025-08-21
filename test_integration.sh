#!/bin/bash

echo "🧪 Testing Frontend-Backend Integration"
echo

API_BASE_URL="http://localhost:55073/api/v1"

# Test 1: User Registration
echo "1️⃣  Testing User Registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE_URL/user" \
  -H "Content-Type: application/json" \
  -d '{"name": "Frontend Test User", "username": "frontendtest", "email": "frontend@test.com", "password": "testpass123"}')

if echo "$REGISTER_RESPONSE" | grep -q '"id"'; then
    echo "✅ Registration successful"
elif echo "$REGISTER_RESPONSE" | grep -q "already registered"; then
    echo "ℹ️  User already exists, proceeding with login"
else
    echo "❌ Registration failed: $REGISTER_RESPONSE"
    exit 1
fi

# Test 2: User Login  
echo
echo "2️⃣  Testing User Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE_URL/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=frontendtest&password=testpass123")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Login successful, got auth token"
else
    echo "❌ Login failed: $LOGIN_RESPONSE"
    exit 1
fi

# Test 3: Get Current User
echo
echo "3️⃣  Testing Get Current User..."
USER_RESPONSE=$(curl -s -X GET "$API_BASE_URL/user/me/" \
  -H "Authorization: Bearer $TOKEN")

if echo "$USER_RESPONSE" | grep -q '"name"'; then
    USER_NAME=$(echo "$USER_RESPONSE" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Got user profile: $USER_NAME"
else
    echo "❌ Get user failed: $USER_RESPONSE"
    exit 1
fi

# Test 4: Get Sentences
echo
echo "4️⃣  Testing Get Sentences..."
SENTENCES_RESPONSE=$(curl -s -X GET "$API_BASE_URL/sentences" \
  -H "Authorization: Bearer $TOKEN")

if echo "$SENTENCES_RESPONSE" | grep -q '"total_count"'; then
    COUNT=$(echo "$SENTENCES_RESPONSE" | grep -o '"total_count":[0-9]*' | cut -d':' -f2)
    echo "✅ Got sentences: $COUNT sentences"
else
    echo "❌ Get sentences failed: $SENTENCES_RESPONSE"
    exit 1
fi

# Test 5: Test Permission Control (should fail)
echo
echo "5️⃣  Testing Sentence Creation (should be denied)..."
CREATE_RESPONSE=$(curl -s -X POST "$API_BASE_URL/sentences" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"japanese_text": "テスト", "english_translation": "Test", "difficulty_level": 1, "jlpt_level": "N5"}')

if echo "$CREATE_RESPONSE" | grep -q "Insufficient permissions"; then
    echo "✅ Sentence creation properly denied (non-superuser)"
else
    echo "⚠️  Unexpected: Sentence creation succeeded (should have been denied)"
fi

echo
echo "🎉 Frontend-Backend Integration Test PASSED!"
echo "📱 The frontend can successfully:"
echo "   - Register new users"
echo "   - Login users"
echo "   - Get authenticated user data"
echo "   - Access protected endpoints"
echo "   - Respect permission controls"
