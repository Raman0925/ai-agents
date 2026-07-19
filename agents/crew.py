from typing import Callable, Optional

from crewai import Agent, Task, Crew, Process

from agents.registry import AGENTS
from tools import search_tool
from mcp_servers.toolsets import get_ritu_tools


def build_agent(name: str, tools=None, allow_delegation: bool = False) -> Agent:
    config = AGENTS[name]
    return Agent(
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        llm=config["llm"],
        tools=tools or [],
        allow_delegation=allow_delegation,
        verbose=True,
    )


def build_ritu() -> Agent:
    return build_agent("ritu", tools=get_ritu_tools())


def run_ceo_crew(prompt: str, on_step: Optional[Callable[[str], None]] = None) -> str:
    """Run the hierarchical crew. `on_step` (if given) receives a short
    human-readable progress string every time an agent takes a step."""
    def report(msg: str) -> None:
        if on_step:
            on_step(msg)

    report("setting up agents...")
    researcher = build_agent("researcher", tools=[search_tool])
    marketing_expert = build_agent("marketing_expert")
    ml_researcher = build_agent("ml_researcher", tools=[search_tool])
    automotive_researcher = build_agent("automotive_researcher", tools=[search_tool])
    psychologist = build_agent("psychologist", tools=[search_tool])
    report("connecting to GitHub tools for Ritu...")
    ritu = build_ritu()
    report("agents ready -- CEO is delegating...")

    # The CEO is the manager: no tools, delegation enabled.
    ceo = build_agent("ceo", allow_delegation=True)

    task = Task(
        description=(
            f"The user said: '{prompt}'. Determine what they need and "
            f"delegate to the right specialist(s). When delegating, the "
            f"coworker name MUST be the exact role string shown in quotes "
            f"below:\n"
            f"- Code review, PR review, 'check this code' -> delegate to "
            f"'Senior Principal Engineer'. She needs the repo (owner/name) "
            f"and PR number -- extract them from the message or any GitHub "
            f"URL the user shared (e.g. github.com/OWNER/REPO/pull/NUMBER "
            f"means repo 'OWNER/REPO', PR NUMBER). If you cannot determine "
            f"both, ask the user instead of guessing. She posts real "
            f"comments on the PR, so confirm intent first unless the user "
            f"already said something like 'review and comment'.\n"
            f"- ML papers, models, training, AI concepts -> delegate to "
            f"'ML Research Scientist'.\n"
            f"- Cars, EVs, batteries, autonomous driving, automotive R&D -> "
            f"delegate to 'Automotive R&D Researcher'.\n"
            f"- Human behavior, motivation, habits, decision-making, "
            f"psychology -> delegate to 'Behavioral Psychologist'.\n"
            f"- General market research, competitor analysis -> delegate to "
            f"'Domain Researcher'.\n"
            f"- Marketing copy, positioning, branding -> delegate to "
            f"'Marketing Expert'.\n"
            f"If the request spans several areas, delegate to each relevant "
            f"specialist and synthesize their outputs into one coherent "
            f"answer. If key information is missing, return a clarifying "
            f"question instead of guessing."
        ),
        expected_output=(
            "The completed work from whichever specialist(s) handled it, "
            "synthesized into one clear answer, or a clarifying question "
            "if information is missing."
        ),
    )

    def _step_callback(step) -> None:
        if on_step is None:
            return
        try:
            # Step objects vary by crewai version; grab whatever is readable.
            text = (
                getattr(step, "thought", None)
                or getattr(step, "result", None)
                or getattr(step, "output", None)
                or str(step)
            )
            on_step(" ".join(str(text).split())[:200])
        except Exception:
            pass  # progress reporting must never break the run

    crew = Crew(
        agents=[
            researcher,
            marketing_expert,
            ml_researcher,
            automotive_researcher,
            psychologist,
            ritu,
        ],
        tasks=[task],
        process=Process.hierarchical,
        manager_agent=ceo,
        step_callback=_step_callback,
        verbose=True,
    )

    result = crew.kickoff()
    return result.raw or ""
