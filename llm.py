#!/usr/bin/env python3
"""Minimal client for the Anthropic Messages API (standard library only), used by disambig.py.

ask(prompt, model, provider, key) -> (text, input_tokens, output_tokens, error)
The key is read by the caller from the ANTHROPIC_API_KEY environment variable; it is never printed.
"""
import json, time, urllib.error, urllib.request

URL = "https://api.anthropic.com/v1/messages"


def ask(prompt, model, provider="anthropic", key=None, retries=4, max_tokens=2000):
    if provider != "anthropic":
        raise ValueError("only the Anthropic API is supported")
    body = json.dumps({"model": model, "max_tokens": max_tokens,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    hdr = {"content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01"}
    for a in range(retries):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(URL, data=body, headers=hdr), timeout=120))
            out = "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text").strip()
            u = d.get("usage", {})
            return out, u.get("input_tokens", 0), u.get("output_tokens", 0), None
        except urllib.error.HTTPError as e:
            if e.code in (400, 401, 403, 404):          # request or key problem: retrying does not help
                return None, 0, 0, f"HTTP{e.code}"
            if a == retries - 1:
                return None, 0, 0, f"HTTP{e.code}"
        except Exception as e:                          # network errors, timeouts
            if a == retries - 1:
                return None, 0, 0, type(e).__name__
        time.sleep(2 ** a * 3)
    return None, 0, 0, "retries"
