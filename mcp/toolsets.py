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


def get_github_tools():
    with MCPServerAdapter(GITHUB_SERVER) as tools:
        return list(tools)


def get_filesystem_tools():
    with MCPServerAdapter(FILESYSTEM_SERVER) as tools:
        return list(tools)


def get_postgres_tools():
    with MCPServerAdapter(POSTGRES_SERVER) as tools:
        return list(tools)


def get_sentry_tools():
    with MCPServerAdapter(SENTRY_SERVER) as tools:
        return list(tools)


def get_linear_tools():
    with MCPServerAdapter(LINEAR_SERVER) as tools:
        return list(tools)


def get_notion_tools():
    with MCPServerAdapter(NOTION_SERVER) as tools:
        return list(tools)


def get_figma_tools():
    with MCPServerAdapter(FIGMA_SERVER) as tools:
        return list(tools)


def get_slack_tools():
    with MCPServerAdapter(SLACK_SERVER) as tools:
        return list(tools)


def get_turing_tools():
    tools = []
    tools.extend(get_github_tools())
    tools.extend(get_filesystem_tools())
    tools.extend(get_postgres_tools())
    tools.extend(get_sentry_tools())
    tools.extend(get_linear_tools())
    tools.extend(get_notion_tools())
    tools.extend(get_slack_tools())
    return tools


def get_max_tools():
    tools = []
    tools.extend(get_figma_tools())
    tools.extend(get_notion_tools())
    tools.extend(get_slack_tools())
    return tools


def get_iris_tools():
    tools = []
    tools.extend(get_figma_tools())
    tools.extend(get_slack_tools())
    return tools


def get_athena_tools():
    tools = []
    tools.extend(get_notion_tools())
    tools.extend(get_postgres_tools())
    tools.extend(get_slack_tools())
    return tools


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
    with MCPServerAdapter(GITHUB_SERVER) as all_tools:
        available = [t for t in all_tools if t.name in RITU_ALLOWED_TOOLS]
        print(f"Ritu's tools: {[t.name for t in available]}")
        return available
