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
    researcher = build_agent("researcher", tools=[search_tool])
    marketing_expert = build_agent("marketing_expert")
    ml_researcher = build_agent("ml_researcher", tools=[search_tool])
    automotive_researcher = build_agent("automotive_researcher", tools=[search_tool])
    psychologist = build_agent("psychologist", tools=[search_tool])
    ritu = build_ritu()

    # The CEO is the manager: no tools, delegation enabled.
    ceo = build_agent("ceo", allow_delegation=True)

    task = Task(
        description=(
            f"The user said: '{prompt}'. Determine what they need and "
            f"delegate to the right specialist(s):\n"
            f"- Code review, PR review, 'check this code' -> delegate to "
            f"Ritu (Senior Principal Engineer). She needs the repo name and "
            f"PR number -- if the user didn't give both, ask for them "
            f"instead of guessing. Ritu posts real comments on the PR, so "
            f"confirm intent first unless the user already said something "
            f"like 'review and comment'. Only delegate to Ritu for genuine "
            f"code review requests.\n"
            f"- ML papers, models, training, AI concepts -> delegate to the "
            f"ML Research Scientist, who explains papers and teaches "
            f"concepts with citations.\n"
            f"- Cars, EVs, batteries, autonomous driving, automotive R&D -> "
            f"delegate to the Automotive R&D Researcher.\n"
            f"- Human behavior, motivation, habits, decision-making, "
            f"psychology -> delegate to the Behavioral Psychologist.\n"
            f"- General market research, competitor analysis -> delegate to "
            f"the Domain Researcher.\n"
            f"- Marketing copy, positioning, branding -> delegate to the "
            f"Marketing Expert.\n"
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
