import os
from dotenv import load_dotenv
from mcp import StdioServerParameters

load_dotenv()

GITHUB_SERVER = {
    "url": "https://api.githubcopilot.com/mcp/",
    "transport": "streamable-http",
    "headers": {
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
        "X-MCP-Toolsets": "repos,pull_requests",
    },
}

FILESYSTEM_SERVER = StdioServerParameters(
    command="npx",
    args=[
        "-y",
        "@modelcontextprotocol/server-filesystem",
        os.getenv("FILESYSTEM_ROOT", "."),
    ],
    env=dict(os.environ),
)

POSTGRES_SERVER = StdioServerParameters(
    command="npx",
    args=[
        "-y",
        "@modelcontextprotocol/server-postgres",
        os.getenv("POSTGRES_CONNECTION_STRING", ""),
    ],
    env=dict(os.environ),
)

SENTRY_SERVER = StdioServerParameters(
    command="npx",
    args=["-y", "@sentry/mcp-server"],
    env={
        **dict(os.environ),
        "SENTRY_AUTH_TOKEN": os.getenv("SENTRY_AUTH_TOKEN", ""),
        "SENTRY_ORG": os.getenv("SENTRY_ORG", ""),
    },
)

LINEAR_SERVER = StdioServerParameters(
    command="npx",
    args=["-y", "mcp-linear"],
    env={
        **dict(os.environ),
        "LINEAR_API_KEY": os.getenv("LINEAR_API_KEY", ""),
    },
)

NOTION_SERVER = StdioServerParameters(
    command="npx",
    args=["-y", "@notionhq/notion-mcp-server"],
    env={
        **dict(os.environ),
        "OPENAPI_MCP_HEADERS": (
            '{"Authorization": "Bearer '
            + os.getenv("NOTION_API_TOKEN", "")
            + '", "Notion-Version": "2022-06-28"}'
        ),
    },
)

FIGMA_SERVER = {
    "url": "https://mcp.figma.com/mcp",
    "transport": "streamable-http",
    "headers": {"Authorization": f"Bearer {os.getenv('FIGMA_API_TOKEN')}"},
}

SLACK_SERVER = StdioServerParameters(
    command="npx",
    args=["-y", "@anthropic/mcp-server-slack"],
    env={
        **dict(os.environ),
        "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN", ""),
    },
)
