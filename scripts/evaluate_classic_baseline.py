"""Entrena y reporta una línea base clásica con partición estratificada fija."""

import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

from src.core.category_taxonomy import canonicalize_category
from src.infrastructure.ml.classic_ticket_classifier import ClassicTicketClassifier

ROOT = Path(__file__).resolve().parent.parent
TICKETS_PATH = ROOT / "data" / "processed" / "tickets_limpios.csv"
REPORT_PATH = ROOT / "tmp" / "stage5_classic_baseline.json"


def evaluate_baseline() -> dict:
    tickets = pd.read_csv(TICKETS_PATH)
    tickets["label"] = tickets["categoria"].map(canonicalize_category)
    tickets = tickets[tickets["label"] != "Sin Clasificar"].copy()
    train, test = train_test_split(
        tickets, test_size=0.20, random_state=42, stratify=tickets["label"]
    )
    classifier = ClassicTicketClassifier()
    classifier.fit(train)
    texts = (test["asunto"].fillna("") + " " + test["descripcion"].fillna("")).tolist()
    predicted, latencies = classifier.predict(texts)
    labels = sorted(test["label"].unique())
    matrix = confusion_matrix(test["label"], predicted, labels=labels).tolist()
    report = {
        "train_size": len(train),
        "test_size": len(test),
        "macro_f1": round(float(f1_score(test["label"], predicted, average="macro")), 4),
        "p95_latency_ms": round(float(pd.Series(latencies).quantile(0.95)), 4),
        "labels": labels,
        "confusion_matrix": matrix,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(json.dumps(evaluate_baseline(), ensure_ascii=False, indent=2))
