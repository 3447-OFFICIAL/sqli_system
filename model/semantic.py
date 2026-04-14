import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np
from scipy.spatial.distance import cosine

class CodeBERTSemanticEncoder:
    """
    Tier 1: Semantic Intent Encoder using CodeBERT.
    Captures the underlying 'intent' of the SQL query rather than tokens.
    """
    def __init__(self, model_name="microsoft/codebert-base"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device).eval()

    def get_embedding(self, query: str) -> np.ndarray:
        """Generates a 768-dimensional embedding vector for a query."""
        inputs = self.tokenizer(query, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use mean pooling of the last hidden state
            embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
        return embedding

class IntentMismatchDetector:
    """
    Compares query embeddings against a baseline of 'safe' application intents.
    Anomalies (high distance) trigger alerts regardless of token presence.
    """
    def __init__(self, threshold=0.3):
        self.threshold = threshold
        # Default 'safe' centroids (learned from common SELECT/UPDATE patterns)
        # In a real system, these are trained on application logs.
        self.safe_centroids = [] 

    def update_centroids(self, embeddings: list[np.ndarray]):
        """Update the baseline safe intent vectors."""
        self.safe_centroids = embeddings

    def compute_anomaly_score(self, embedding: np.ndarray) -> float:
        """
        Calculates the minimum cosine distance to safe centroids.
        Distance > Threshold indicates 'Intent Mismatch'.
        """
        if not self.safe_centroids:
            return 0.5 # Default middle-ground if no baseline exists
            
        distances = [cosine(embedding, centroid) for centroid in self.safe_centroids]
        return min(distances)

    def is_anomaly(self, score: float) -> bool:
        return score > self.threshold
