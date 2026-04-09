import requests
import json
import logging
import pandas as pd
import time
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DatasetScraper:
    def __init__(self):
        self.malicious_urls = [
            # PayloadsAllTheThings High-Value Injection Arrays
            "https://raw.githubusercontent.com/swisskyrepo/PayloadsAllTheThings/master/SQL%20Injection/Intruder/Auth_Bypass.txt",
            "https://raw.githubusercontent.com/swisskyrepo/PayloadsAllTheThings/master/SQL%20Injection/Intruder/Generic_SQLI.txt",
            "https://raw.githubusercontent.com/fuzzdb-project/fuzzdb/master/attack/sqli/sqli-auth-bypass-libinjection.txt"
        ]
        
    def fetch_github_payloads(self) -> list:
        """Pulls sophisticated obfuscated injection paths from raw GitHub repositories."""
        logging.info("Initializing payload extraction from external repositories...")
        payloads = []
        for url in self.malicious_urls:
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    lines = res.text.split("\n")
                    cleaned = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
                    payloads.extend(cleaned)
                    logging.info(f"Successfully digested {len(cleaned)} payloads from {url.split('/')[-1]}")
                time.sleep(1) # Be polite to GitHub servers
            except Exception as e:
                logging.error(f"Failed to fetch {url}: {str(e)}")
                
        return list(set(payloads))

    def generate_synthetic_benign(self, num_samples=100) -> list:
        """
        Placeholder logic. In production, this connects to the StackExchange API 
        or parses WikiSQL sets. Returning a tiny subset for scaffolding.
        """
        logging.info(f"Synthesizing {num_samples} complex, nested benign queries...")
        benign_templates = [
            "SELECT id, username, email FROM users WHERE status = 'active' AND last_login > '2023-01-01';",
            "SELECT u.name, p.title FROM users u INNER JOIN posts p ON u.id = p.author_id WHERE p.published = TRUE GROUP BY u.name HAVING COUNT(p.id) > 5;",
            "UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 4920 AND target_region = 'EU';",
            "WITH regional_sales AS (SELECT region, SUM(amount) AS total_sales FROM orders GROUP BY region) SELECT region FROM regional_sales WHERE total_sales > (SELECT SUM(amount)/10 FROM orders);"
        ]
        
        # Simulating a much larger fetch by multiplying templates (in reality, loop through distinct datasets)
        return benign_templates * (num_samples // len(benign_templates))
        
    def compile_master_dataset(self, output_path="../dataset/next_gen_sqli.csv"):
        """Compiles scraped malicious payloads and complex benign queries into a single DataFrame."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        malicious = self.fetch_github_payloads()
        benign = self.generate_synthetic_benign(len(malicious)) # Attempting to balance the load
        
        df = pd.DataFrame({
            "Query": malicious + benign,
            "Label": [1] * len(malicious) + [0] * len(benign)
        })
        
        df = df.sample(frac=1).reset_index(drop=True) # Shuffle
        df.to_csv(output_path, index=False)
        logging.info(f"Master Dataset compiled. Saved {len(df)} samples to [ {output_path} ]")
        logging.info("Next Step: Ensure SentenceTransformers parses these queries for embedding generation.")

if __name__ == "__main__":
    scraper = DatasetScraper()
    scraper.compile_master_dataset("dataset/next_gen_sqli.csv")

