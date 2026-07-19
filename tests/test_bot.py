from unittest.mock import patch, MagicMock
from agents.researcher import run_researcher


def test_run_researcher_returns_string():
    fake_result = MagicMock()
    fake_result.raw = "This is a fake research summary."

    with patch("agents.researcher.Crew.kickoff", return_value=fake_result):
        output = run_researcher("test topic")

    assert isinstance(output, str)
    assert len(output) > 0


def test_run_researcher_handles_empty_topic():
    fake_result = MagicMock()
    fake_result.raw = "Summary even for vague input."

    with patch("agents.researcher.Crew.kickoff", return_value=fake_result):
        output = run_researcher("")

    assert isinstance(output, str)
