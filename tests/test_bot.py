from unittest.mock import patch, MagicMock
from agents.crew import run_ceo_crew


@patch("agents.crew.get_ritu_tools", return_value=[])
def test_run_ceo_crew_returns_string(mock_ritu_tools):
    fake_result = MagicMock()
    fake_result.raw = "This is a fake research summary."

    with patch("agents.crew.Crew.kickoff", return_value=fake_result):
        output = run_ceo_crew("test topic")

    assert isinstance(output, str)
    assert len(output) > 0


@patch("agents.crew.get_ritu_tools", return_value=[])
def test_run_ceo_crew_handles_empty_topic(mock_ritu_tools):
    fake_result = MagicMock()
    fake_result.raw = "Summary even for vague input."

    with patch("agents.crew.Crew.kickoff", return_value=fake_result):
        output = run_ceo_crew("")

    assert isinstance(output, str)
