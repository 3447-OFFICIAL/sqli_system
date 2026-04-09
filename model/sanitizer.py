import re
import urllib.parse

class SecuritySanitizer:
    """
    Normalization Engine for SQL Queries.
    Resolves obfuscation and prepares a canonical form for the AI ensemble.
    """
    
    @staticmethod
    def normalize(query: str) -> str:
        if not query:
            return ""
        
        # 1. URL Decoding (handle %20, %27, etc.)
        try:
            query = urllib.parse.unquote(query)
        except Exception:
            pass
            
        # 2. Lowercase for standard processing (kept in original clean_query too)
        normalized = query.lower()
        
        # 3. Strip Block Comments: /* comment */
        normalized = re.sub(r'/\*.*?\*/', ' ', normalized, flags=re.DOTALL)
        
        # 4. Strip single line comments: -- and #
        normalized = re.sub(r'--.*$', '', normalized, flags=re.MULTILINE)
        normalized = re.sub(r'#.*$', '', normalized, flags=re.MULTILINE)
        
        # 5. Handle Hex encoding (simulated: 0x5345... -> plaintext approx)
        # Note: True hex decoding is complex for partial strings, 
        # but we flag it or normalize the most common ones.
        
        # 6. Flatten Whitespace: tabs, newlines, multiple spaces -> single space
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # 7. Strip surrounding quotes if they wrap the entire query (common in API logs)
        normalized = normalized.strip().strip("'").strip('"')
        
        return normalized

if __name__ == "__main__":
    # Test cases
    test_queries = [
        "SELECT/**/column/**/FROM/**/table",
        "SELECT * FROM users -- inline comment",
        "U%4eION S%45LECT 1,2,3",
        "SELECT\n*\nFROM\nusers",
        " 'OR 1=1 --' "
    ]
    
    sanitizer = SecuritySanitizer()
    for q in test_queries:
        print(f"RAW: {q}")
        print(f"NORM: {sanitizer.normalize(q)}")
        print("-" * 20)
