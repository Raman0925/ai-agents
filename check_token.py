"""Verify the GITHUB_TOKEN in .env works, exactly as the bot loads it.

Run:  python check_token.py
"""
import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv()

token = os.getenv("GITHUB_TOKEN")

if not token:
    print("FAIL: GITHUB_TOKEN is missing/empty in .env")
    raise SystemExit(1)

print(f"Token loaded from .env: {token[:8]}... (length {len(token)})")

if token != token.strip() or token.startswith(('"', "'")):
    print("WARNING: token has surrounding whitespace or quotes in .env -- remove them!")

req = urllib.request.Request(
    "https://api.github.com/user",
    headers={"Authorization": f"Bearer {token.strip()}", "User-Agent": "token-check"},
)
try:
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
        print(f"OK: authenticated as '{data['login']}'")
        scopes = resp.headers.get("x-oauth-scopes")
        if scopes is not None:
            print(f"Classic token scopes: {scopes or '(none!)'}")
        else:
            print("Fine-grained token (no scope header) -- make sure it has "
                  "Pull requests: Read/write and Contents: Read on your repo.")
except urllib.error.HTTPError as e:
    print(f"FAIL: GitHub returned {e.code} -- the token itself is invalid/expired.")
    raise SystemExit(1)
