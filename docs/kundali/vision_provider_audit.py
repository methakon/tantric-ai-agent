"""
vision_provider_audit.py — which configured vision providers actually work?

Reports ONLY: provider, configured?, credential present?, auth test, result.
Never prints a key, token, secret or authorization header. Credentials are read
from the environment as Hermes already resolves them; this file never logs them
and never sends them anywhere except the provider's own API endpoint.

Run: venv/bin/python docs/kundali/vision_provider_audit.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

# A 1x1 transparent PNG - the smallest possible non-destructive vision payload.
TINY_PNG = ("data:image/png;base64,"
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQ"
            "AAAABJRU5ErkJggg==")

results = []


def load_env_keys():
    """Read credential NAMES and values into memory only (never printed)."""
    env_path = os.path.expanduser("~/.hermes/.env")
    vals = {}
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if "=" in line and not line.strip().startswith("#"):
                    k, _, v = line.rstrip().partition("=")
                    vals[k.strip()] = v.strip()
    return vals


def post_json(url, headers, payload, timeout=45):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read()[:400].decode("utf-8", "replace")


def probe(name, configured, cred_name, cred_value, url, model, payload_fn):
    entry = {"provider": name, "configured": configured,
             "credential_env_var": cred_name,
             "credential_present": bool(cred_value),
             "auth_test": "not attempted", "vision_model": model,
             "result": ""}
    if not cred_value:
        entry["result"] = "skipped - no credential"
        results.append(entry)
        return entry
    try:
        status, body = payload_fn(url, {"Authorization": f"Bearer {cred_value}",
                                        "Content-Type": "application/json"},
                                  model)
        entry["auth_test"] = f"HTTP {status}"
        entry["result"] = "AUTHENTICATED" if status == 200 else f"HTTP {status}"
        if status != 200:
            try:
                err = json.loads(body)
                entry["result"] += " - " + str(err.get("error", {}).get("code", ""))[:60]
            except Exception:
                pass
    except urllib.error.HTTPError as e:
        entry["auth_test"] = f"HTTP {e.code}"
        entry["result"] = f"HTTP {e.code} (rejected)"
    except Exception as e:
        entry["auth_test"] = "network/other error"
        entry["result"] = f"{type(e).__name__}"
    results.append(entry)
    return entry


def openai_style(url, headers, model):
    payload = {"model": model,
               "messages": [{"role": "user", "content": [
                   {"type": "image_url", "image_url": {"url": TINY_PNG}},
                   {"type": "text", "text": "reply with the single word OK"}]}],
               "max_tokens": 8}
    return post_json(url, headers, payload)


def gemini_style(url, headers, model):
    key = headers["x-goog-api-key"]
    payload = {"contents": [{"parts": [
        {"inline_data": {"mime_type": "image/png",
                         "data": TINY_PNG.split(",", 1)[1]}},
        {"text": "reply with the single word OK"}]}]}
    url2 = f"{url.rstrip('/')}/models/{model}:generateContent?key={key}"
    hdr = {"Content-Type": "application/json"}
    return post_json(url2, hdr, payload)


def main():
    keys = load_env_keys()
    env = dict(os.environ)
    keys.update({k: v for k, v in env.items() if v})

    probe("bailian / DashScope (currently configured)",
          True, "DASHSCOPE_API_KEY", keys.get("DASHSCOPE_API_KEY"),
          "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
          "qwen-vl-max", openai_style)
    probe("OpenAI-compatible (OPENAI_API_KEY)",
          True, "OPENAI_API_KEY", keys.get("OPENAI_API_KEY"),
          "https://api.openai.com/v1/chat/completions", "gpt-4o-mini", openai_style)
    probe("Nous inference", True, "HERMES_API_KEY", keys.get("HERMES_API_KEY"),
          "https://inference-api.nousresearch.com/v1/chat/completions",
          "Hermes-4-14B", openai_style)
    probe("Gemini", True, "GEMINI_API_KEY", keys.get("GEMINI_API_KEY"),
          "https://generativelanguage.googleapis.com/v1beta",
          "gemini-2.0-flash", gemini_style)
    probe("OpenRouter", True, "OPENROUTER_API_KEY", keys.get("OPENROUTER_API_KEY"),
          "https://openrouter.ai/api/v1/chat/completions",
          "google/gemini-2.0-flash-exp:free", openai_style)
    probe("Fireworks", True, "FIREWORKS_API_KEY", keys.get("FIREWORKS_API_KEY"),
          "https://api.fireworks.ai/inference/v1/chat/completions",
          "accounts/fireworks/models/llama-v3p2-90b-vision-instruct",
          openai_style)
    probe("NVIDIA", True, "NVIDIA_API_KEY", keys.get("NVIDIA_API_KEY"),
          "https://integrate.api.nvidia.com/v1/chat/completions",
          "nvidia/llama-3.2-90b-vision-instruct", openai_style)

    print("=" * 96)
    print(f"{'PROVIDER':<44} {'CRED':<6} {'AUTH':<12} {'RESULT'}")
    print("=" * 96)
    ok = []
    for r in results:
        print(f"{r['provider'][:43]:<44} "
              f"{('yes' if r['credential_present'] else 'NO'):<6} "
              f"{r['auth_test'][:11]:<12} {r['result']}")
        if r["result"].startswith("AUTHENTICATED"):
            ok.append(r)
    print("=" * 96)
    if ok:
        print("Providers that AUTHENTICATE with a vision request:")
        for r in ok:
            print(f"  - {r['provider']}  (model {r['vision_model']})")
    else:
        print("NO configured provider authenticated a vision request.")
    print("\nNote: no credential value was printed by this script.")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out",
                       "vision_provider_audit.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"providers": results,
                   "any_working": bool(ok),
                   "working_providers": [r["provider"] for r in ok]}, fh, indent=2)
    print(f"Wrote {out}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())