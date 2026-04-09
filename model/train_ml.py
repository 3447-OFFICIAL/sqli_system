import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
import xgboost as xgb
import lightgbm as lgb
from scipy.sparse import hstack, csr_matrix
from .dataset import load_data, get_train_test_split
from .preprocessing import extract_features_batch
import time

def train_and_save_ml_models():
    print("Loading data...")
    df = load_data()
    X_train_text, X_test_text, y_train, y_test = get_train_test_split(df)
    
    print("Extracting handcrafted features...")
    hc_train = csr_matrix(extract_features_batch(X_train_text))
    hc_test = csr_matrix(extract_features_batch(X_test_text))
    
    print("Fitting TF-IDF vectorizer...")
    tfidf = TfidfVectorizer(
        analyzer='char_wb',
        ngram_range=(2, 4),
        max_features=5000,
        sublinear_tf=True
    )
    tfidf_train = tfidf.fit_transform(X_train_text)
    tfidf_test = tfidf.transform(X_test_text)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(current_dir, "../saved_models")
    os.makedirs(model_dir, exist_ok=True)
    
    joblib.dump(tfidf, os.path.join(model_dir, 'tfidf_vectorizer.joblib'))
    
    print("Combining features...")
    X_train = hstack([tfidf_train, hc_train])
    X_test = hstack([tfidf_test, hc_test])
    
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "DecisionTree": DecisionTreeClassifier(max_depth=20, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        "LinearSVC": LinearSVC(C=1.0, max_iter=2000, random_state=42),
        "XGBoost": xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42, n_jobs=-1),
        "LightGBM": lgb.LGBMClassifier(random_state=42, n_jobs=-1)
    }
    
    metrics = {}
    for name, model in models.items():
        print(f"Training {name}...")
        start = time.time()
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        print(f"{name} trained in {time.time()-start:.2f}s, Accuracy: {score:.4f}")
        joblib.dump(model, os.path.join(model_dir, f'{name.lower()}_model.joblib'))
        metrics[name] = score

    print("All ML models trained and saved to saved_models directory.")
    return metrics

if __name__ == "__main__":
    train_and_save_ml_models()
