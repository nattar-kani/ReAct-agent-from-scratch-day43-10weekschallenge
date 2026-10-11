from unittest.mock import patch

from src.agent import ReActAgent
from src.memory import AgentMemory


def test_memory_stores_task():
    memory = AgentMemory("Calculate 3 * 45 + 2 * 10")

    assert memory.task == "Calculate 3 * 45 + 2 * 10"
    assert memory.get_history() == []


def test_memory_records_events():
    memory = AgentMemory("Calculate the total")

    memory.add_event("action", {"tool": "calculate"})
    memory.add_event("observation", "155")

    history = memory.get_history()

    assert len(history) == 2
    assert history[0]["type"] == "action"
    assert history[1]["content"] == "155"


def test_memory_clear():
    memory = AgentMemory("Calculate the total")
    memory.add_event("observation", "155")

    memory.clear()

    assert memory.get_history() == []
    assert memory.task == "Calculate the total"


def test_history_returns_separate_list():
    memory = AgentMemory("Calculate the total")
    memory.add_event("observation", "155")

    history = memory.get_history()
    history.append({"type": "final", "content": "Changed externally"})

    assert len(memory.get_history()) == 1


@patch("src.agent.ollama.chat")
def test_agent_uses_tool_and_returns_final_answer(mock_chat):
    mock_chat.side_effect = [
        {
            "message": {
                "content": (
                    '{"type":"tool_call","tool":"calculate",'
                    '"arguments":{"expression":"3 * 45 + 2 * 10"}}'
                )
            }
        },
        {
            "message": {
                "content": (
                    '{"type":"final","answer":"The total is 155."}'
                )
            }
        },
    ]

    agent = ReActAgent()
    answer = agent.run("Calculate 3 * 45 + 2 * 10")

    assert answer == "The total is 155."
    assert mock_chat.call_count == 2

    second_call = mock_chat.call_args_list[1]
    prompt = second_call.kwargs["messages"][1]["content"]

    assert '"result": "155"' in prompt


@patch("src.agent.ollama.chat")
def test_agent_returns_immediate_final_answer(mock_chat):
    mock_chat.return_value = {
        "message": {
            "content": (
                '{"type":"final","answer":"Hello!"}'
            )
        }
    }

    agent = ReActAgent()
    answer = agent.run("Say hello")

    assert answer == "Hello!"
    assert mock_chat.call_count == 1


@patch("src.agent.ollama.chat")
def test_agent_records_invalid_tool_error(mock_chat):
    mock_chat.side_effect = [
        {
            "message": {
                "content": (
                    '{"type":"tool_call","tool":"delete_files",'
                    '"arguments":{}}'
                )
            }
        },
        {
            "message": {
                "content": (
                    '{"type":"final","answer":"I could not complete the task."}'
                )
            }
        },
    ]

    agent = ReActAgent()
    answer = agent.run("Delete some files")

    assert answer == "I could not complete the task."
    assert mock_chat.call_count == 2

    second_call = mock_chat.call_args_list[1]
    prompt = second_call.kwargs["messages"][1]["content"]

    assert "Unknown tool: delete_files" in prompt



@patch("src.agent.ollama.chat")
def test_agent_handles_ollama_failure(mock_chat):
    mock_chat.side_effect = RuntimeError("Ollama is unavailable")

    agent = ReActAgent()
    answer = agent.run("Calculate 2 + 2")

    assert answer.startswith("Agent error:")
    assert "Ollama is running" in answer
    assert "RuntimeError" in answer


@patch("src.agent.ollama.chat")
def test_agent_handles_invalid_json(mock_chat):
    mock_chat.return_value = {
        "message": {
            "content": "This is not valid JSON"
        }
    }

    agent = ReActAgent()
    answer = agent.run("Calculate 2 + 2")

    assert answer.startswith("Agent error:")
    assert "Invalid model response" in answer


@patch("src.agent.ollama.chat")
def test_agent_handles_unexpected_response_structure(mock_chat):
    mock_chat.return_value = {
        "unexpected": "response"
    }

    agent = ReActAgent()
    answer = agent.run("Calculate 2 + 2")

    assert answer.startswith("Agent error:")
    assert "unexpected response structure" in answer

