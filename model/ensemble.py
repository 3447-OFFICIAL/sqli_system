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
    
from .preprocessing import extract_features_batch, clean_query, analyze_payload, extract_features
from .semantic import CodeBERTSemanticEncoder, IntentMismatchDetector

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
        
        # Tier 1 Semantic Layer (CodeBERT + IMD)
        self.semantic_encoder = None
        self.imd = None
        
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
                try:
                    model_path = os.path.join(self.model_dir, f'{name}_model.joblib')
                    if os.path.exists(model_path):
                        self.models[name] = joblib.load(model_path)
                except Exception as e:
                    print(f"⚠️ [AEGIS] Failed to load ML model {name}: {e}")
            
            # Load DL Model
            try:
                dl_path = os.path.join(self.model_dir, 'lstm_model.keras')
                if HAS_TENSORFLOW and os.path.exists(dl_path):
                    self.dl_model = tf.keras.models.load_model(dl_path)
            except Exception as e:
                print(f"⚠️ [AEGIS] Failed to load DL model (LSTM): {e}")
                
            # Initialize Semantic Tier
            try:
                self.semantic_encoder = CodeBERTSemanticEncoder()
                self.imd = IntentMismatchDetector()
                print("✅ [AEGIS] Semantic Layer: LOADED")
            except Exception as e:
                print(f"⚠️ [AEGIS] Semantic Layer: FAILED ({e})")
                
            print(f"🎯 [AEGIS] Neural Stats: {len(self.models)} ML loaded, DL {'Ready' if self.dl_model else 'Offline'}")
            
        except Exception as e:
            print(f"❌ [AEGIS] ERROR: Critical failure during model load: {e}")

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
        
        # Tier 1: Semantic Intent Analysis
        semantic_score = 0.5
        semantic_anomaly = False
        if self.semantic_encoder and self.imd:
            embedding = self.semantic_encoder.get_embedding(cleaned)
            semantic_score = self.imd.compute_anomaly_score(embedding)
            semantic_anomaly = self.imd.is_anomaly(semantic_score)

        preds = {}
        weighted_sum = 0.0
        total_weight = 0.0
        
        # Integrate Semantic Signal into prediction
        # If IMD identifies a mismatch, provide a baseline probability of 0.8
        if semantic_anomaly:
            preds["semantic_imd"] = 0.85
            weighted_sum += 0.85 * 0.4  # High weight for semantic layer
            total_weight += 0.4
        
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
        
        # XAI Layer via heuristics + Semantic feedback
        attack_type = "Safe / Standard Query"
        keywords = []
        if is_sqli:
            attack_type, keywords = analyze_payload(raw_query)
            if semantic_anomaly:
                attack_type = f"Intent Mismatch: {attack_type}"
                keywords.append("Semantic Deviation")
        
        # Fallback if no models are loaded but the system is running
        if not preds and not HAS_TENSORFLOW:
            preds = {"Heuristic_Engine": 0.5}

        # Generate Consensus Data for Radar Chart (Hyper-Sensitive)
        features = extract_features(raw_query)
        consensus_data = {
            "semantic": float(semantic_score * 100),
            "time": float(max(features[10], features[11]) * 100),
            "union": float(max(features[12], features[13]) * 100),
            "boolean": float(max(features[14], features[15], features[16], features[43] if len(features)>43 else 0) * 100),
            "tautology": float(max(features[14], features[15]) * 100),
            "obf": float(max(features[9], features[22], features[23], features[24]) * 100)
        }
        
        # Binary Spike: If attack_type matches a category, force that axis to at least 80%
        at = attack_type.lower()
        if "boolean" in at: consensus_data["boolean"] = 95
        if "union" in at: consensus_data["union"] = 95
        if "time" in at: consensus_data["time"] = 95
        if "obfuscation" in at: consensus_data["obf"] = 95
        if "tautology" in at: consensus_data["tautology"] = 95

        return {
            "prediction": is_sqli,
            "confidence": float(ensemble_prob if is_sqli else 1 - ensemble_prob),
            "individual_probabilities": preds,
            "consensus_data": consensus_data,
            "risk_level": "Critical" if (ensemble_prob > 0.9 or (ensemble_prob > 0.7 and semantic_anomaly)) else "High" if ensemble_prob > 0.8 else "Medium" if ensemble_prob > 0.5 else "Low",
            "attack_type": attack_type,
            "keywords": keywords,
            "semantic_anomaly": semantic_anomaly
        }

if __name__ == "__main__":
    predictor = SQLiEnsemblePredictor()
    res = predictor.predict("1; DROP TABLE users; --")
    print(res)
