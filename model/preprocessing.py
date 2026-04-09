import numpy as np

from .sanitizer import SecuritySanitizer

def clean_query(text: str) -> str:
    """Clean and normalize the raw query text."""
    if not isinstance(text, str):
        text = str(text)
    sanitizer = SecuritySanitizer()
    return sanitizer.normalize(text)

def extract_features(text: str) -> list[float]:
    """Extract handcrafted semantic and structural features from a SQL query."""
    t = str(text).lower()
    return [
        len(t),                                        # query length
        t.count("'"),                                  # single quote count
        t.count('"'),                                  # double quote count
        t.count(';'),                                  # semicolon count
        t.count('='),                                  # equals sign count
        t.count('--'),                                 # SQL comment --
        t.count('#'),                                  # SQL comment #
        t.count('/*'),                                 # block comment
        int('union' in t),                             # UNION keyword
        int('select' in t),                            # SELECT keyword
        int('drop' in t),                              # DROP keyword
        int('insert' in t),                            # INSERT keyword
        int('delete' in t),                            # DELETE keyword
        int('update' in t),                            # UPDATE keyword
        int('exec' in t or 'execute' in t),            # EXEC keyword
        int('sleep' in t or 'benchmark' in t),         # Time-based injection
        int('or 1=1' in t or "or '1'='1'" in t),       # Tautology
        int('and 1=1' in t or "and '1'='1'" in t),     # AND tautology
        int('xp_' in t),                               # xp_ stored procedures
        int('information_schema' in t),                # Schema enumeration
        int('pg_sleep' in t),                          # PostgreSQL time-based
        t.count('('),                                  # open parenthesis count
        sum(1 for c in t if not c.isalnum() and c != ' '), # special char count
    ]

def extract_features_batch(queries: list[str]) -> np.ndarray:
    """Extract features for a batch of queries."""
    features = [extract_features(q) for q in queries]
    return np.array(features, dtype=np.float32)

def analyze_payload(text: str):
    """Heuristic logic to identify attack type and extract keywords for explainability."""
    t = str(text).lower()
    attack_type = "Pattern Anomaly"
    keywords = []
    
    # Time-based
    if 'sleep' in t or 'benchmark' in t or 'pg_sleep' in t:
        attack_type = "Time-based Blind SQLi"
        if 'sleep' in t: keywords.append('sleep')
        if 'benchmark' in t: keywords.append('benchmark')
        if 'pg_sleep' in t: keywords.append('pg_sleep')
        
    # Boolean/Tautology
    elif 'or 1=1' in t or "or '1'='1'" in t or 'and 1=1' in t or "and '1'='1'" in t:
        attack_type = "Boolean-based SQLi"
        keywords.append('1=1 (Tautology)')
        if 'or' in t: keywords.append('OR')
        
    # Union-based
    elif 'union' in t and 'select' in t:
        attack_type = "Union-based SQLi"
        keywords.extend(['union', 'select'])
        
    # Error-based / Enumeration
    elif 'information_schema' in t or 'table_name' in t or 'column_name' in t:
        attack_type = "Schema Enumeration"
        keywords.append('information_schema')
        
    # Command Execution
    elif 'xp_' in t or 'exec' in t or 'execute' in t:
        attack_type = "Command Execution"
        if 'xp_' in t: keywords.append('xp_cmdshell')
        if 'exec' in t: keywords.append('exec')
        
    # Obfuscation
    elif '/**/' in t or 'char(' in t:
        attack_type = "Obfuscation / Evasion"
        keywords.append('inline comments / encoding')
        
    # Generic
    else:
        if 'select' in t: keywords.append('select')
        if 'drop' in t: keywords.append('drop')
        if 'insert' in t: keywords.append('insert')
        if '--' in t: keywords.append('-- (comment)')
        if '/* ' in t: keywords.append('/* (comment block)')
    
    return attack_type, list(set(keywords))

if __name__ == "__main__":
    sample = "SELECT * FROM users WHERE id=1 OR 1=1 --"
    print(extract_features(sample))
    print(analyze_payload(sample))
