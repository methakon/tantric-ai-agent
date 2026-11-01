#!/usr/bin/env python3
"""
Tantric AI Agent — intent classifier runtime loader (Tier 4).

Loads models/intent_clf.joblib once and exposes classify(text) -> (label, conf).
Train the model with scripts/train_intent_classifier.py.

Graceful degradation: if the model file is missing or fails to load,
classify() returns (None, 0.0) and callers fall back to their existing
rule-based routing — the same pattern used when the C++ engine binary is
absent. This module therefore NEVER raises on a missing model.
"""
import os
import sys
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(ROOT, "models", "intent_clf.joblib")

# Confidence below this is treated as "unsure" -> caller uses rule fallback.
CONFIDENCE_THRESHOLD = 0.55

_lock = threading.Lock()
_loaded = False
_bundle = None  # {"pipeline", "classes", "version"}


def _ensure_loaded():
    """Load the model once, thread-safe. Never raises; sets _bundle=None on fail."""
    global _loaded, _bundle
    if _loaded:
        return
    with _lock:
        if _loaded:
            return
        _loaded = True
        if not os.path.exists(MODEL_PATH):
            print(f"[intent] no model at {MODEL_PATH} — using rule fallback",
                  file=sys.stderr)
            _bundle = None
            return
        try:
            import joblib
            _bundle = joblib.load(MODEL_PATH)
            n = len(_bundle.get("classes", []))
            print(f"[intent] loaded model ({n} intents)", file=sys.stderr)
        except Exception as e:  # noqa: BLE001 - must not break the bridge
            print(f"[intent] load failed ({e}) — using rule fallback",
                  file=sys.stderr)
            _bundle = None


def is_available() -> bool:
    """True if a usable model is loaded."""
    _ensure_loaded()
    return _bundle is not None


def classify(text: str):
    """Return (label, confidence). (None, 0.0) if no model or empty text.

    confidence is the top-class probability in [0, 1]. Callers should
    compare it against CONFIDENCE_THRESHOLD and fall back to rules when
    it is lower.
    """
    _ensure_loaded()
    if _bundle is None:
        return None, 0.0
    text = (text or "").strip()
    if not text:
        return None, 0.0
    try:
        pipe = _bundle["pipeline"]
        proba = pipe.predict_proba([text])[0]
        # argmax without importing numpy at module top (keeps import light)
        best_idx = max(range(len(proba)), key=lambda i: proba[i])
        label = pipe.classes_[best_idx]
        return str(label), float(proba[best_idx])
    except Exception as e:  # noqa: BLE001
        print(f"[intent] classify failed ({e}) — rule fallback", file=sys.stderr)
        return None, 0.0


def classify_confident(text: str, threshold: float = CONFIDENCE_THRESHOLD):
    """Return label only when confidence >= threshold, else None."""
    label, conf = classify(text)
    if label is not None and conf >= threshold:
        return label
    return None


if __name__ == "__main__":
    # Manual probe: python3 scripts/intent_classifier.py "কেমন আছো"
    import json
    if not is_available():
        print("no model loaded — train it first with "
              "scripts/train_intent_classifier.py", file=sys.stderr)
        sys.exit(1)
    queries = sys.argv[1:] or [
        "নমস্কার", "কেমন আছো", "ধন্যবাদ", "who are you",
        "বিয়ে কবে হবে", "will i get a job", "সাড়ে সাতী",
        "who was gorakhnath", "tell me more",
    ]
    for q in queries:
        label, conf = classify(q)
        chosen = classify_confident(q)
        print(json.dumps({
            "text": q, "label": label, "confidence": round(conf, 3),
            "routed": chosen or "FALLBACK",
        }, ensure_ascii=False))
