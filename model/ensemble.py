import os
import joblib
import numpy as np
from scipy.sparse import hstack, csr_matrix
try:
    import tensorflow as tf
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    
from .preprocessing import extract_features_batch, clean_query, analyze_payload

MAX_LEN = 200

class SQLiEnsemblePredictor:
    def __init__(self, model_dir=None):
        if model_dir is None:
            # Point to relative saved_models directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_dir = os.path.join(current_dir, "../saved_models")
            
        self.model_dir = model_dir
        self.models = {}
        self.dl_model = None
        self.tfidf = None
        self.tokenizer = None
        self._load_models()
        self.weights = {
            "logisticregression": 0.1,
            "decisiontree": 0.1,
            "randomforest": 0.2,
            "linearsvc": 0.1,
            "xgboost": 0.2,
            "lightgbm": 0.1,
            "lstm": 0.2
        }

    def _load_models(self):
        try:
            self.tfidf = joblib.load(os.path.join(self.model_dir, 'tfidf_vectorizer.joblib'))
            self.tokenizer = joblib.load(os.path.join(self.model_dir, 'dl_tokenizer.joblib'))
            
            ml_model_names = ['logisticregression', 'decisiontree', 'randomforest', 'linearsvc', 'xgboost', 'lightgbm']
            for name in ml_model_names:
                model_path = os.path.join(self.model_dir, f'{name}_model.joblib')
                if os.path.exists(model_path):
                    self.models[name] = joblib.load(model_path)
            
            dl_path = os.path.join(self.model_dir, 'lstm_model.keras')
            if HAS_TENSORFLOW and os.path.exists(dl_path):
                self.dl_model = tf.keras.models.load_model(dl_path)
        except Exception as e:
            print(f"Warning: Could not load some models. Run training first. Error: {e}")

    def predict(self, raw_query: str):
        cleaned = clean_query(raw_query)
        
        # Prepare ML features
        hc_feats = csr_matrix(extract_features_batch([cleaned]))
        tfidf_feats = self.tfidf.transform([cleaned])
        X_ml = hstack([tfidf_feats, hc_feats])
        
        # Prepare DL features
        X_dl = None
        if HAS_TENSORFLOW and self.tokenizer:
            seq = self.tokenizer.texts_to_sequences([cleaned])
            X_dl = pad_sequences(seq, maxlen=MAX_LEN)
        
        preds = {}
        weighted_sum = 0.0
        total_weight = 0.0
        
        for name, model in self.models.items():
            if name == 'linearsvc':
                score = model.decision_function(X_ml)[0]
                prob = 1.0 / (1.0 + np.exp(-score))
            elif hasattr(model, "predict_proba"):
                prob = model.predict_proba(X_ml)[0][1]
            else:
                prob = float(model.predict(X_ml)[0])
                
            preds[name] = prob
            w = self.weights.get(name, 1.0)
            weighted_sum += prob * w
            total_weight += w
            
        if HAS_TENSORFLOW and self.dl_model and X_dl is not None:
            dl_prob = float(self.dl_model.predict(X_dl, verbose=0)[0][0])
            preds['lstm'] = dl_prob
            w = self.weights.get('lstm', 1.0)
            weighted_sum += dl_prob * w
            total_weight += w
            
        ensemble_prob = weighted_sum / total_weight if total_weight > 0 else 0.5
        is_sqli = int(ensemble_prob > 0.5)
        
        # XAI Layer via heuristics
        attack_type = "Safe / Standard Query"
        keywords = []
        if is_sqli:
            attack_type, keywords = analyze_payload(raw_query)
        
        # Fallback if no models are loaded but the system is running
        if not preds and not HAS_TENSORFLOW:
            preds = {"Heuristic_Engine": 0.5}

        return {
            "prediction": is_sqli,
            "confidence": ensemble_prob if is_sqli else 1 - ensemble_prob,
            "individual_probabilities": preds,
            "risk_level": "High" if ensemble_prob > 0.8 else "Medium" if ensemble_prob > 0.5 else "Low",
            "attack_type": attack_type,
            "keywords": keywords
        }

if __name__ == "__main__":
    predictor = SQLiEnsemblePredictor()
    res = predictor.predict("1; DROP TABLE users; --")
    print(res)
