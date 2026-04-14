import numpy as np

from .sanitizer import SecuritySanitizer

def clean_query(text: str) -> str:
    """Clean and normalize the raw query text."""
    if not isinstance(text, str):
        text = str(text)
    sanitizer = SecuritySanitizer()
    return sanitizer.normalize(text)

def extract_features(text: str) -> list[float]:
    """
    Extract 28 semantic intent features.
    Each feature encodes a specific attack signal — not just character frequency.
    Matches the research-grade logic from Miniproj4_SemanticSQLi.
    """
    import re
    t = str(text).lower()
    return [
        # ─── Structural / statistical ──────────────────────────────────────────
        float(len(t)),                                                 # F01: total length
        float(t.count("'")),                                           # F02: single quotes
        float(t.count('"')),                                           # F03: double quotes
        float(t.count(';')),                                           # F04: semicolons (stacked queries)
        float(t.count('=')),                                           # F05: equals signs
        float(sum(1 for c in t if not c.isalnum() and c != ' ')),      # F06: special char density

        # ─── Comment injection ─────────────────────────────────────────────────
        float('--' in t),                                              # F07: SQL line comment (--)
        float('#' in t),                                               # F08: MySQL comment (#)
        float('/*' in t),                                              # F09: block comment (/*)
        float('/**/' in t),                                            # F10: inline bypass (/**/)

        # ─── Time-based blind injection ────────────────────────────────────────
        float(bool(re.search(r'sleep\s*\(|pg_sleep|waitfor', t))),       # F11: sleep / wait patterns
        float(bool(re.search(r'benchmark\s*\(|dbms_pipe|randomblob', t))), # F12: benchmark / pipe

        # ─── Union-based injection ─────────────────────────────────────────────
        float('union' in t and 'select' in t),                         # F13: UNION + SELECT combo
        float(bool(re.search(r'union\s+all\s+select', t))),            # F14: UNION ALL SELECT

        # ─── Boolean / tautology injection ─────────────────────────────────────
        float(bool(re.search(r'or\s+1\s*=\s*1|or\s+true|or\s+1\s*--', t))),   # F15: numeric tautology
        float(bool(re.search(r"or\s+'[a-z0-9]'\s*=\s*'[a-z0-9]'", t))),        # F16: string tautology
        float(bool(re.search(r'case\s+when|elt\s*\(', t))),               # F17: conditional blind

        # ─── Error-based injection ─────────────────────────────────────────────
        float('@@version' in t or '@@' in t),                          # F18: DB system variables
        float(bool(re.search(r'load_file|utl_inaddr|extractvalue', t))),  # F19: error trigger functions

        # ─── Schema enumeration ────────────────────────────────────────────────
        float('information_schema' in t),                               # F20: ANSI schema tables
        float('sysobjects' in t or 'syscolumns' in t or 'sysusers' in t), # F21: MSSQL system tables
        float(bool(re.search(r'all_users|dba_tables', t))),               # F22: Oracle system tables

        # ─── Encoding / obfuscation ────────────────────────────────────────────
        float(t.count('%27') + t.count('%20')),                        # F23: URL-encoded quote/space
        float(bool(re.search(r'char\s*\(|chr\s*\(', t))),                # F24: CHAR() obfuscation
        float(bool(re.search(r'0x[0-9a-f]+', t))),                       # F25: hex-encoded payload

        # ─── DDL danger ────────────────────────────────────────────────────────
        float(bool(re.search(r'\b(drop|truncate|alter)\s+table', t))),   # F26: destructive DDL
        float(bool(re.search(r'\b(insert|update|delete)\b', t))),         # F27: data manipulation

        # ─── Auth bypass ───────────────────────────────────────────────────────
        float(bool(re.search(r"'\\\s*(--|#)|admin\s*'", t))),              # F28: auth bypass pattern
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
