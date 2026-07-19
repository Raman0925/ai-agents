import atexit
import json
import logging
import os
import urllib.error
import urllib.request

from crewai_tools import MCPServerAdapter

from .connections import (
    GITHUB_SERVER,
    FILESYSTEM_SERVER,
    POSTGRES_SERVER,
    SENTRY_SERVER,
    LINEAR_SERVER,
    NOTION_SERVER,
    FIGMA_SERVER,
    SLACK_SERVER,
)

logger = logging.getLogger(__name__)

# Cached adapters, one per server. Kept open for the lifetime of the process.
#
# IMPORTANT: do NOT use `with MCPServerAdapter(...) as tools: return list(tools)`.
# The `with` block closes the MCP connection on exit, so the returned tools
# point at a dead connection and every tool call fails/hangs silently.
_adapters: dict[str, MCPServerAdapter] = {}


def _tools_for(name: str, server) -> list:
    adapter = _adapters.get(name)
    if adapter is None:
        logger.info("Connecting MCP server: %s", name)
        try:
            # Newer crewai-tools: fail after 60s instead of hanging forever.
            adapter = MCPServerAdapter(server, connect_timeout=60)
        except TypeError:  # older version without the param
            adapter = MCPServerAdapter(server)
        _adapters[name] = adapter
    return list(adapter.tools)


_github_token_validated = False


def _validate_github_token() -> None:
    """Fail fast with a clear error instead of hanging on a bad token."""
    global _github_token_validated
    if _github_token_validated:
        return
    token = (os.getenv("GITHUB_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("GITHUB_TOKEN is missing/empty in .env")
    req = urllib.request.Request(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {token}", "User-Agent": "agentsteam-bot"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            login = json.load(resp).get("login")
            logger.info("GitHub token OK (authenticated as %s)", login)
    except urllib.error.HTTPError as e:
        raise RuntimeError(
            f"GitHub rejected GITHUB_TOKEN ({e.code}). Fix the token in .env "
            f"and restart. Run `python check_token.py` to verify."
        ) from e
    _github_token_validated = True


def _shutdown_adapters() -> None:
    for name, adapter in _adapters.items():
        try:
            adapter.stop()
        except Exception:
            logger.warning("Failed to stop MCP adapter %s", name, exc_info=True)
    _adapters.clear()


atexit.register(_shutdown_adapters)


def get_github_tools():
    return _tools_for("github", GITHUB_SERVER)


def get_filesystem_tools():
    return _tools_for("filesystem", FILESYSTEM_SERVER)


def get_postgres_tools():
    return _tools_for("postgres", POSTGRES_SERVER)


def get_sentry_tools():
    return _tools_for("sentry", SENTRY_SERVER)


def get_linear_tools():
    return _tools_for("linear", LINEAR_SERVER)


def get_notion_tools():
    return _tools_for("notion", NOTION_SERVER)


def get_figma_tools():
    return _tools_for("figma", FIGMA_SERVER)


def get_slack_tools():
    return _tools_for("slack", SLACK_SERVER)


def get_turing_tools():
    return (
        get_github_tools()
        + get_filesystem_tools()
        + get_postgres_tools()
        + get_sentry_tools()
        + get_linear_tools()
        + get_notion_tools()
        + get_slack_tools()
    )


def get_max_tools():
    return get_figma_tools() + get_notion_tools() + get_slack_tools()


def get_iris_tools():
    return get_figma_tools() + get_slack_tools()


def get_athena_tools():
    return get_notion_tools() + get_postgres_tools() + get_slack_tools()


RITU_ALLOWED_TOOLS = {
    "get_pull_request",
    "get_pull_request_diff",
    "get_pull_request_files",
    "get_file_contents",
    "list_pull_requests",
    "create_pull_request_review_comment",
    "add_comment_to_pending_review",
}


def get_ritu_tools():
    _validate_github_token()
    available = [t for t in get_github_tools() if t.name in RITU_ALLOWED_TOOLS]
    logger.info("Ritu's tools: %s", [t.name for t in available])
    return available
