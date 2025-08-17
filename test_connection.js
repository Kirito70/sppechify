#!/usr/bin/env node

// Simple test script to verify frontend-backend connectivity
const http = require('http');

const testEndpoints = [
  '/api/v1/sentences',
  '/docs',
  '/openapi.json'
];

async function testConnection() {
  console.log('🚀 Testing Backend Connectivity...\n');

  for (const endpoint of testEndpoints) {
    console.log(`Testing: http://localhost:8001${endpoint}`);
    
    try {
      const options = {
        hostname: 'localhost',
        port: 8001,
        path: endpoint,
        method: 'GET',
        headers: {
          'Origin': 'http://localhost:19000',
          'Accept': 'application/json'
        }
      };

      await new Promise((resolve, reject) => {
        const req = http.request(options, (res) => {
          console.log(`  ✅ Status: ${res.statusCode}`);
          console.log(`  🔗 CORS Origin: ${res.headers['access-control-allow-origin']}`);
          console.log(`  📋 Content-Type: ${res.headers['content-type']}\n`);
          resolve();
        });

        req.on('error', (e) => {
          console.log(`  ❌ Error: ${e.message}\n`);
          reject(e);
        });

        req.end();
      });

    } catch (error) {
      console.log(`  ❌ Failed to test ${endpoint}: ${error.message}\n`);
    }
  }
  
  console.log('✅ Backend connectivity test completed!');
}

testConnection().catch(console.error);