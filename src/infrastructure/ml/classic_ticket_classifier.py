from time import perf_counter

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.core.category_taxonomy import canonicalize_category


class ClassicTicketClassifier:
    """Baseline reproducible para clasificación supervisada de tickets."""

    def __init__(self) -> None:
        self._pipeline = Pipeline(
            [
                ("vectorizer", TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode")),
                ("classifier", LogisticRegression(max_iter=1_000, class_weight="balanced", random_state=42)),
            ]
        )

    def fit(self, tickets: pd.DataFrame) -> None:
        labels = tickets["categoria"].map(canonicalize_category)
        valid = labels != "Sin Clasificar"
        self._pipeline.fit(self._combine_text(tickets.loc[valid]), labels.loc[valid])

    def predict(self, texts: list[str]) -> tuple[list[str], list[float]]:
        predictions: list[str] = []
        latencies: list[float] = []
        for text in texts:
            started_at = perf_counter()
            predictions.append(self._pipeline.predict([text])[0])
            latencies.append((perf_counter() - started_at) * 1_000)
        return predictions, latencies

    @staticmethod
    def _combine_text(tickets: pd.DataFrame) -> pd.Series:
        return tickets["asunto"].fillna("").astype(str) + " " + tickets["descripcion"].fillna("").astype(str)
