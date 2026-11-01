#!/usr/bin/env python3
"""
Tantric AI Agent — intent classifier trainer (Tier 4, offline).

Trains a tiny mixed Bengali+English intent classifier and writes it to
models/intent_clf.joblib. The runtime loader is scripts/intent_classifier.py.

Pipeline:
  TF-IDF (char 2-5 grams + word 1-2 grams)  ->  LogisticRegression (multinomial)

Char n-grams make a single mixed-language model work without language
detection: they capture Bengali conjuncts/morphology and tolerate typos,
while word n-grams catch English keywords.

Nothing here generates text. The model only predicts WHICH deterministic
responder consultation_engine should call; the answer content still comes
from Swiss Ephemeris, the seeded tables, and the C++ engine.

Usage:
  python3 scripts/train_intent_classifier.py            # train + save
  python3 scripts/train_intent_classifier.py --report   # also print metrics
  python3 scripts/train_intent_classifier.py --data path/to.jsonl
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DATA = os.path.join(ROOT, "data", "intent_dataset.jsonl")
MODEL_DIR = os.path.join(ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "intent_clf.joblib")


def load_dataset(path):
    """Read a JSONL file of {"text": ..., "label": ...} records."""
    texts, labels = [], []
    with open(path, "r", encoding="utf-8") as f:
        for ln, raw in enumerate(f, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError as e:
                print(f"[WARN] skipping malformed line {ln}: {e}",
                      file=sys.stderr)
                continue
            text = (rec.get("text") or "").strip()
            label = (rec.get("label") or "").strip()
            if not text or not label:
                print(f"[WARN] skipping incomplete line {ln}", file=sys.stderr)
                continue
            texts.append(text)
            labels.append(label)
    return texts, labels


def build_pipeline():
    """TF-IDF (char + word) union -> LogisticRegression."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.pipeline import FeatureUnion, Pipeline
    from sklearn.linear_model import LogisticRegression

    # lowercase=False: Bengali has no case, and lowercasing only helps the
    # Latin side — the word analyzer handles English case via strip_accents.
    char_vec = TfidfVectorizer(
        analyzer="char_wb", ngram_range=(2, 5), min_df=1,
        lowercase=True, sublinear_tf=True)
    word_vec = TfidfVectorizer(
        analyzer="word", ngram_range=(1, 2), min_df=1,
        lowercase=True, sublinear_tf=True, token_pattern=r"(?u)\b\w+\b")

    features = FeatureUnion([("char", char_vec), ("word", word_vec)])
    # sklearn >= 1.7 dropped the `multi_class` arg; LogisticRegression is
    # multinomial by default for the lbfgs solver.
    clf = LogisticRegression(
        max_iter=2000, C=4.0, class_weight="balanced", solver="lbfgs")
    return Pipeline([("features", features), ("clf", clf)])


def main():
    ap = argparse.ArgumentParser(description="Train the intent classifier")
    ap.add_argument("--data", default=DEFAULT_DATA, help="JSONL dataset path")
    ap.add_argument("--out", default=MODEL_PATH, help="output model path")
    ap.add_argument("--report", action="store_true",
                    help="print a held-out classification report")
    args = ap.parse_args()

    if not os.path.exists(args.data):
        print(f"[FATAL] dataset not found: {args.data}", file=sys.stderr)
        return 1

    texts, labels = load_dataset(args.data)
    n = len(texts)
    classes = sorted(set(labels))
    print(f"[*] loaded {n} examples across {len(classes)} intents: "
          f"{', '.join(classes)}")
    if n < len(classes) * 3:
        print("[WARN] very small dataset — accuracy numbers will be noisy",
              file=sys.stderr)

    import joblib

    if args.report:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report, accuracy_score
        # stratify needs >=2 per class; fall back if any class is too small
        from collections import Counter
        min_count = min(Counter(labels).values())
        strat = labels if min_count >= 2 else None
        Xtr, Xte, ytr, yte = train_test_split(
            texts, labels, test_size=0.25, random_state=42, stratify=strat)
        pipe = build_pipeline()
        pipe.fit(Xtr, ytr)
        pred = pipe.predict(Xte)
        print(f"\n[=] held-out accuracy: {accuracy_score(yte, pred):.3f}\n")
        print(classification_report(yte, pred, zero_division=0))

    # Final model is trained on ALL data (the report split was only for metrics)
    pipe = build_pipeline()
    pipe.fit(texts, labels)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    joblib.dump({"pipeline": pipe, "classes": classes, "version": 1}, args.out)
    size_kb = os.path.getsize(args.out) / 1024.0
    print(f"[\u2713] saved model -> {args.out} ({size_kb:.1f} KB)")

    # quick smoke test so a bad model is caught at train time
    probe = [
        ("নমস্কার", "GREETING"),
        ("বিয়ে কবে হবে", "TOPIC_MARRIAGE"),
        ("who are you", "IDENTITY"),
        ("who was gorakhnath", "LINEAGE_Q"),
        ("sade sati", "TOPIC_SADESATI"),
    ]
    print("\n[*] smoke test:")
    import numpy as np
    for text, want in probe:
        proba = pipe.predict_proba([text])[0]
        idx = int(np.argmax(proba))
        got = pipe.classes_[idx]
        conf = float(proba[idx])
        flag = "ok " if got == want else "DIFF"
        print(f"    [{flag}] {text!r:40s} -> {got} ({conf:.2f}) "
              f"[expected {want}]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
