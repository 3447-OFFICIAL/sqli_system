import os
import pandas as pd
from sklearn.model_selection import train_test_split
from .preprocessing import clean_query

def load_data(filepath: str = None):
    """Load the dataset from CSV and clean queries."""
    if filepath is None:
        # Try to find it relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # SQL_Dataset.csv is in the parent of the sqli_system folder
        # model/dataset.py -> model -> sqli_system -> (parent)
        filepath = os.path.join(current_dir, "../../SQL_Dataset.csv")
    
    if not os.path.exists(filepath):
        # Fallback for Docker environment where it might be in /app/SQL_Dataset.csv
        filepath = "/app/SQL_Dataset.csv" if os.path.exists("/app/SQL_Dataset.csv") else filepath

    df = pd.read_csv(filepath)
    # Ensure columns are named 'Query' and 'Label' (as per the file inspection)
    if 'Query' not in df.columns or 'Label' not in df.columns:
        raise ValueError("Dataset must contain 'Query' and 'Label' columns.")
    
    # Process queries
    df['cleaned_query'] = df['Query'].apply(clean_query)
    # Drop empty queries
    df = df[df['cleaned_query'].str.len() > 0].reset_index(drop=True)
    return df

def get_train_test_split(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """Split data into training and testing sets."""
    X = df['cleaned_query'].to_numpy()
    y = df['Label'].to_numpy()
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test
