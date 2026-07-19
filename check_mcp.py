"""Test the GitHub MCP endpoint directly, bypassing crewai-tools.

Run:  python check_mcp.py
"""
import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv()

token = (os.getenv("GITHUB_TOKEN") or "").strip()
if not token:
    print("FAIL: GITHUB_TOKEN missing in .env")
    raise SystemExit(1)

body = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {},
        "clientInfo": {"name": "check-mcp", "version": "1.0"},
    },
}).encode()

req = urllib.request.Request(
    "https://api.githubcopilot.com/mcp/",
    data=body,
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": "check-mcp",
    },
)

try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        print(f"OK: MCP server answered with HTTP {resp.status}")
        print(resp.read(500).decode(errors="replace"))
except urllib.error.HTTPError as e:
    print(f"FAIL: MCP server returned HTTP {e.code}")
    print(e.read(500).decode(errors="replace"))
except Exception as e:
    print(f"FAIL: could not reach MCP server: {type(e).__name__}: {e}")
