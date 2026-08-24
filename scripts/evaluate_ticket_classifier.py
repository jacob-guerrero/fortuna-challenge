"""Ejecuta el baseline clásico contra el conjunto de referencia de Etapa 5."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, precision_score

from src.core.category_taxonomy import canonicalize_category
from src.infrastructure.ml.classic_ticket_classifier import ClassicTicketClassifier

ROOT = Path(__file__).resolve().parent.parent
REFERENCE_PATH = ROOT / "docs" / "n5" / "reference_set.csv"
TICKETS_PATH = ROOT / "data" / "processed" / "tickets_limpios.csv"
REPORT_PATH = ROOT / "tmp" / "stage5_evaluation_metrics.json"
MIN_MACRO_F1 = 0.75
MIN_CATEGORY_PRECISION = 0.70
MAX_P95_LATENCY_MS = 200.0


def evaluate() -> dict:
    reference = pd.read_csv(REFERENCE_PATH)
    cases = reference[reference["type"] == "classification"].copy()
    tickets = pd.read_csv(TICKETS_PATH)
    training = tickets[~tickets["id"].isin(cases["source_ticket_id"])].copy()

    classifier = ClassicTicketClassifier()
    classifier.fit(training)
    expected = cases["expected_label"].map(canonicalize_category).tolist()
    predicted, latencies = classifier.predict(cases["input"].tolist())
    labels = sorted(set(expected))
    per_category_precision = precision_score(
        expected, predicted, labels=labels, average=None, zero_division=0
    )
    metrics = {
        "classification_cases": len(cases),
        "macro_f1": round(float(f1_score(expected, predicted, average="macro")), 4),
        "p95_latency_ms": round(float(np.percentile(latencies, 95)), 4),
        "precision_by_category": {
            label: round(float(score), 4) for label, score in zip(labels, per_category_precision)
        },
        "excluded_reference_ticket_ids": sorted(cases["source_ticket_id"].dropna().tolist()),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return metrics


def assert_thresholds(metrics: dict) -> None:
    failures = []
    if metrics["macro_f1"] < MIN_MACRO_F1:
        failures.append(f"macro_f1={metrics['macro_f1']} < {MIN_MACRO_F1}")
    if metrics["p95_latency_ms"] > MAX_P95_LATENCY_MS:
        failures.append(f"p95_latency_ms={metrics['p95_latency_ms']} > {MAX_P95_LATENCY_MS}")
    for category, precision in metrics["precision_by_category"].items():
        if precision < MIN_CATEGORY_PRECISION:
            failures.append(f"precision[{category}]={precision} < {MIN_CATEGORY_PRECISION}")
    if failures:
        raise SystemExit("Evaluation thresholds failed: " + "; ".join(failures))


if __name__ == "__main__":
    result = evaluate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    assert_thresholds(result)
