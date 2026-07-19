from crewai import Agent, Task, Crew


def run_researcher(topic: str) -> str:
    researcher = Agent(
        role="Domain Researcher",
        goal="Find current, credible information on the given topic and summarize it clearly",
        backstory="You are an expert researcher who gives concise, well-sourced summaries.",
        llm="gpt-4o",
    )

    task = Task(
        description=f"Research this topic and produce a clear, sourced summary: {topic}",
        expected_output="A 3-5 paragraph summary with source references.",
        agent=researcher,
    )

    crew = Crew(agents=[researcher], tasks=[task])
    result = crew.kickoff()
    return result.raw
