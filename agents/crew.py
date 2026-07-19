from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from tools import search_tool


def run_ceo_crew(prompt: str) -> str:
    # Use gpt-4o for the manager and agents
    llm = ChatOpenAI(model="gpt-4o")

    researcher = Agent(
        role="Domain Researcher",
        goal="Find current, credible information on the given topic and summarize it clearly",
        backstory="You are an expert researcher who gives concise, well-sourced summaries.",
        llm=llm,
        tools=[search_tool],
        allow_delegation=False,
    )

    marketing_expert = Agent(
        role="Marketing Expert",
        goal="Create compelling marketing strategies, copies, and analyze market trends",
        backstory="You are a seasoned marketing executive who knows how to sell products and build brands.",
        llm=llm,
        allow_delegation=False,
    )

    # We create a generic task that the CEO (Manager) will break down and assign
    task = Task(
        description=f"Fulfill the following request from the user:\n\n{prompt}\n\nDelegate tasks to the appropriate agents to accomplish this. If it's a simple conversation, you can answer directly.",
        expected_output="A complete, well-formatted response addressing the user's request, synthesized from the agents' work.",
    )

    crew = Crew(
        agents=[researcher, marketing_expert],
        tasks=[task],
        process=Process.hierarchical,
        manager_llm=llm,
    )

    result = crew.kickoff()
    return result.raw
