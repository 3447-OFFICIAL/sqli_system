import re

class StructuralIntegrityCheck:
    """
    Heuristic-based validator to catch high-risk structural anomalies.
    Acts as a fast-fail layer before the ML ensemble.
    """
    
    @staticmethod
    def validate(query: str) -> dict:
        """
        Returns a dict with 'is_valid' and 'threat_score'.
        score > 0.7 triggers instant block.
        """
        score = 0.0
        reasons = []
        
        # 1. Check for unbalanced quotes
        if query.count("'") % 2 != 0:
            score += 0.3
            reasons.append("Unbalanced single quotes")
        
        # 2. Check for semicolon chaining (common in command injection)
        if query.count(";") > 1:
            score += 0.4
            reasons.append("Excessive semicolon chaining")
            
        # 3. Check for obvious Boolean Tautology (even after normalization)
        if re.search(r'(\d+)\s*=\s*\1', query):
            score += 0.5
            reasons.append("Tautological pattern (e.g. 1=1)")
            
        # 4. Check for nested comments (evasion attempt)
        if query.count("/*") > 1 or ( "/*" in query and "*/" in query and query.find("*/") < query.find("/*")):
            score += 0.5
            reasons.append("Potentially nested or reversed comments")

        # 5. Check for common time-based blind markers
        if any(marker in query.lower() for marker in ["pg_sleep", "waitfor delay", "benchmark"]):
            score += 0.8
            reasons.append("Exploitative time-delay function detected")

        return {
            "threat_score": min(score, 1.0),
            "is_high_risk": score >= 0.7,
            "reasons": reasons
        }

if __name__ == "__main__":
    # Test cases
    scenarios = [
        "SELECT * FROM users WHERE id=1; DROP TABLE users;",
        "1' OR 1=1 --",
        "SELECT pg_sleep(5)",
        "legitimate query with 'quote'"
    ]
    
    sic = StructuralIntegrityCheck()
    for s in scenarios:
        print(f"QUERY: {s}")
        print(f"RESULT: {sic.validate(s)}")
        print("-" * 20)
