import requests
import json
import time

API_URL = "http://localhost:8000"

def get_auth_token():
    print("[*] Authenticating with WAF API...")
    try:
        res = requests.post(f"{API_URL}/token", data={"username": "admin", "password": "admin123"})
        if res.status_code == 200:
            return res.json()["access_token"]
        print("[!] Authentication failed.")
    except Exception as e:
        print(f"[!] Target API unreachable: {e}")
    return None

def waf_intercept(query: str, token: str):
    print(f"\n[WAF Proxy] Intercepting request containing SQL: '{query}'")
    headers = {"Authorization": f"Bearer {token}"}
    
    start_time = time.time()
    try:
        res = requests.post(f"{API_URL}/predict", json={"query": query}, headers=headers)
        elapsed = time.time() - start_time
        
        if res.status_code == 200:
            data = res.json()
            if data["prediction"] == 1:
                print(f"[❌] BLOCKED: Malicious intent detected! (Confidence: {data['confidence']:.2%})")
                print(f"     Risk Level: {data['risk_level']}")
                return False
            else:
                print(f"[✅] ALLOWED: Query is safe. (Confidence: {data['confidence']:.2%})")
                return True
        else:
            print(f"[?] WAF API Error: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[!] WAF Error: {e}")
        
    print(f"[WAF Proxy] Latency: {elapsed*1000:.2f} ms")
    return False

if __name__ == "__main__":
    token = get_auth_token()
    if not token:
        exit(1)
        
    sample_queries = [
        "SELECT * FROM product WHERE user_uuid = '123-abc-456'",
        "admin' OR 1=1 --",
        "SELECT email FROM users WHERE id = 12",
        "1; DROP TABLE auth_users; --",
        "john_doe",
        "admin' UNION SELECT username, password FROM admin --"
    ]
    
    print("\n--- Starting Real-Time WAF Simulation ---")
    for q in sample_queries:
        waf_intercept(q, token)
        time.sleep(1.0)
