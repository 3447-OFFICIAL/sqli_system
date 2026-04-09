import requests
import json
import time

BASE_URL = "http://localhost:8000"

# --- QA SUITE DATASET ---
# Format: (Payload, Expected_Is_Malicious)
QA_CASES = [
    # True Negatives (Legitimate App Queries) -> Tests False Positives
    ("SELECT username, email FROM users WHERE active = 1 AND role = 'user'", False),
    ("SELECT * FROM products WHERE id = '8f12a-3b9c-4d5e'", False),
    ("UPDATE profile SET bio = 'Hello, this is my bio! I love SQL.' WHERE id = 12", False),
    ("SELECT SUM(price) FROM orders WHERE status = 'shipped' GROUP BY date", False),
    
    # True Positives (Advanced SQLi) -> Tests False Negatives
    ("1' UNION SELECT NULL, NULL, database()--", True),
    ("admin' AND (SELECT 1 FROM (SELECT(SLEEP(5)))a)--", True), # Time-blind
    ("1; DROP TABLE users;--", True),

    # Mixed Queries (Legit prefix + Malicious suffix)
    ("SELECT * FROM items WHERE id = 1; UPDATE users SET role='admin' WHERE id=1;--", True),
    ("SELECT name FROM catalog WHERE category = 'books' UNION SELECT user, pass FROM admin--", True),

    # Encoded/Obfuscated Payloads
    ("S%45LECT * F%52OM users", True), # URL Encoded keywords
    ("SELECT/**/1/**/FROM/**/dual", True), # Inline comments
    ("1' OR '1'='1' /* bypassing waf */", True), # Tautology with trailing comment
]

def run_qa_suite():
    print("="*60)
    print("      AEGIS SENTINEL: QA & ACCURACY SUITE")
    print("="*60)
    
    try:
        token_res = requests.post(f"{BASE_URL}/token", data={"username": "admin", "password": "admin123"})
        token = token_res.json().get("access_token")
    except Exception as e:
        print(f"Failed to get token: {e}")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    metrics = {
        "TP": 0, "TN": 0, "FP": 0, "FN": 0,
        "Total": len(QA_CASES)
    }

    for idx, (payload, expected_malicious) in enumerate(QA_CASES):
        data = {
            "query": payload,
            "source_ip": f"10.QA.0.{idx}",
            "endpoint": "/qa/"
        }
        
        try:
            res = requests.post(f"{BASE_URL}/predict", json=data, headers=headers)
            if res.status_code == 200:
                pred_data = res.json()
                is_predicted_malicious = pred_data['prediction'] == 1
                
                if expected_malicious and is_predicted_malicious:
                    metrics["TP"] += 1
                    status = "✅ TP"
                elif not expected_malicious and not is_predicted_malicious:
                    metrics["TN"] += 1
                    status = "✅ TN"
                elif not expected_malicious and is_predicted_malicious:
                    metrics["FP"] += 1
                    status = "❌ FP (False Positive)"
                elif expected_malicious and not is_predicted_malicious:
                    metrics["FN"] += 1
                    status = "❌ FN (False Negative)"
                    
                print(f"[{status}] payload: {payload[:30]}... | Risk: {pred_data['risk_level']}")
            else:
                print(f"[!] Request failed: Status {res.status_code}")
        except Exception as e:
             print(f"[!] Error on payload: {e}")
             
        time.sleep(0.1) # Small delay to avoid triggering local rate limt (with varying IP it should be fine, but just in case)
        
    print("\n" + "="*60)
    print("                QA METRICS SUMMARY")
    print("="*60)
    accuracy = (metrics["TP"] + metrics["TN"]) / metrics["Total"] * 100
    print(f"Total Tests run:  {metrics['Total']}")
    print(f"True Positives:   {metrics['TP']}")
    print(f"True Negatives:   {metrics['TN']}")
    print(f"False Positives:  {metrics['FP']}  (Legitimate blocked)")
    print(f"False Negatives:  {metrics['FN']}  (Attacks missed)")
    print(f"Accuracy Rate:    {accuracy:.2f}%")
    
    # Save results to a json file to be read by the agent
    with open('qa_results.json', 'w') as f:
        json.dump(metrics, f)

if __name__ == "__main__":
    run_qa_suite()
