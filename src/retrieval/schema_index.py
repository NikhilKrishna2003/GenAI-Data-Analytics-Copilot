from sentence_transformers import SentenceTransformer
import numpy as np


class SchemaRetriever:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.column_docs = []
        self.embeddings = None

    def build_index(self, profile: dict):
        self.column_docs = []

        for col in profile["columns"]:
            doc = (
                f"Column name: {col['name']}. "
                f"Data type: {col['dtype']}. "
                f"Null count: {col['null_count']}. "
                f"Sample values: {', '.join(col['sample_values'])}"
            )
            self.column_docs.append({
                "column_name": col["name"],
                "text": doc
            })

        texts = [doc["text"] for doc in self.column_docs]
        self.embeddings = self.model.encode(texts, convert_to_numpy=True)

    def retrieve(self, question: str, top_k: int = 5):
        if self.embeddings is None or len(self.column_docs) == 0:
            return []

        q_emb = self.model.encode([question], convert_to_numpy=True)[0]

        scores = []
        for i, emb in enumerate(self.embeddings):
            sim = self.cosine_similarity(q_emb, emb)
            scores.append((sim, self.column_docs[i]))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scores[:top_k]]

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        denom = (np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)