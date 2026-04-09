import http from 'k6/http';
import { check, sleep } from 'k6';

// k6 Load Test Configuration 
export const options = {
  stages: [
    { duration: '5s', target: 10 }, // Ramp up to 10 VUs
    { duration: '15s', target: 50 }, // Plateau at 50 VUs
    { duration: '5s', target: 0 },  // Ramp down
  ],
  thresholds: {
    // We expect the 95th percentile response time to be under 200ms
    http_req_duration: ['p(95)<200'],
    // We expect fewer than 1% of requests to fail
    http_req_failed: ['rate<0.01'], 
  },
};

const BASE_URL = 'http://localhost:8000';

// Global setup to get the JWT token
export function setup() {
  const loginRes = http.post(`${BASE_URL}/token`, {
    username: 'admin',
    password: 'admin123',
  });
  
  if (loginRes.status !== 200) {
      console.error("Login failed!", loginRes.body);
  }
  return { token: loginRes.json('access_token') };
}

export default function (data) {
  const token = data.token;

  const payloads = [
    "SELECT * FROM products WHERE category = 'electronics'", // Normal
    "1' OR '1'='1", // SQLi Option
    "SELECT/**/pass/**/FROM/**/users", // Obfuscated
    "admin'; WAITFOR DELAY '0:0:5'--", // Blind
    "SELECT email FROM users WHERE id=" + Math.floor(Math.random() * 1000) // Dynamic Legitimate
  ];

  const payload = payloads[Math.floor(Math.random() * payloads.length)];
  
  // Spoof IP to bypass the 1 request/sec rate limiter for load testing
  const randomIp = `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`;

  const body = JSON.stringify({
    query: payload,
    source_ip: randomIp,
    endpoint: "/api/search"
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
  };

  const res = http.post(`${BASE_URL}/predict`, body, params);

  // Checks
  check(res, {
    'status is 200 (Processed) or 413 (Oversized)': (r) => r.status === 200 || r.status === 413,
    'rate limit successfully bypassed': (r) => r.status !== 429,
  });

  sleep(0.1); // Small think time
}
