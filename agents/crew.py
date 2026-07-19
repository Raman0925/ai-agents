from crewai import Agent, Task, Crew, Process
from agents.registry import AGENTS
from tools import search_tool
from mcp_servers.toolsets import get_ritu_tools


def build_agent(name, tools=None):
    config = AGENTS[name]
    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        llm=config["llm"],
        tools=tools or [],
        allow_delegation=False,
        verbose=True,
    )


def build_ritu():
    return Agent(
        role=AGENTS["ritu"]["role"],
        goal=AGENTS["ritu"]["goal"],
        backstory=AGENTS["ritu"]["backstory"],
        llm=AGENTS["ritu"]["llm"],
        tools=get_ritu_tools(),
        allow_delegation=False,
        verbose=True,
    )


def build_ritu_review_task(ritu, repo: str, pr_number: int):
    return Task(
        description=(
            f"Fetch and review pull request #{pr_number} in repo '{repo}'. "
            f"Read the actual diff and changed files. For each real issue "
            f"you find (bugs, missing error handling, security concerns, "
            f"meaningful style/consistency problems), post a specific "
            f"review comment on the PR citing the exact file and line. "
            f"Do not post generic or filler comments -- only comment where "
            f"you have something specific and useful to say. If the PR "
            f"looks clean, post ONE summary comment saying so rather than "
            f"inventing issues to comment on. Never attempt to approve, "
            f"merge, or close the PR -- you do not have that capability "
            f"and should not try."
        ),
        expected_output=(
            "Confirmation of which comments were posted, with a summary "
            "of what was found and where."
        ),
        agent=ritu,
    )


def run_ceo_crew(prompt: str) -> str:
    researcher = build_agent("researcher", tools=[search_tool])
    marketing_expert = build_agent("marketing_expert")
    ritu = build_ritu()

    task = Task(
        description=(
            f"You are the CEO of Kumar Enterprises, a software company that builds products and does ML and automotive research and development. "
            f"Your job is to understand what the user wants and delegate the work "
            f"to the right specialist(s) or handle it yourself."
            f"The user said: '{prompt}'. Determine what they need "
            f"and delegate to the right specialist(s):\n"
            f"- Code review, PR review, 'check this code' -> delegate to "
            f"Ritu. She needs the repo name and PR number -- if the user "
            f"didn't give both, ask for them instead of guessing. Ritu "
            f"will post her findings as real comments on the PR, so "
            f"confirm with the user first if this is their intent, unless "
            f"they already said something like 'review and comment.'\n"
            f"- Market research, competitor analysis -> delegate to the "
            f"Domain Researcher\n"
            f"- Marketing copy, positioning -> delegate to the Marketing "
            f"Expert\n"
            f"Only delegate to Ritu for genuine code review requests."
        ),
        expected_output="The completed work from whichever specialist(s) handled it, or a clarifying question if info is missing.",
    )

    crew = Crew(
        agents=[researcher, marketing_expert, ritu],
        tasks=[task],
        process=Process.hierarchical,
        manager_llm="gpt-4o",
        verbose=True,
    )

    result = crew.kickoff()
    return result.raw or ""
