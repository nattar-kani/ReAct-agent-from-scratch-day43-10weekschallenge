
import pytest

from src.parser import parse_response


def test_parse_tool_call():
    response = (
        '{"type": "tool_call", "tool": "calculate", '
        '"arguments": {"expression": "3 * 45 + 2 * 10"}}'
    )

    result = parse_response(response)

    assert result["type"] == "tool_call"
    assert result["tool"] == "calculate"
    assert result["arguments"]["expression"] == "3 * 45 + 2 * 10"


def test_parse_final_answer():
    response = '{"type": "final", "answer": "The total is 155."}'

    result = parse_response(response)

    assert result["type"] == "final"
    assert result["answer"] == "The total is 155."


def test_invalid_json():
    with pytest.raises(ValueError):
        parse_response("This is not JSON")


def test_unknown_response_type():
    with pytest.raises(ValueError):
        parse_response('{"type": "unknown"}')


def test_tool_call_missing_arguments():
    response = '{"type": "tool_call", "tool": "calculate"}'

    with pytest.raises(ValueError):
        parse_response(response)


def test_arguments_must_be_an_object():
    response = (
        '{"type": "tool_call", "tool": "calculate", '
        '"arguments": "3 * 45"}'
    )

    with pytest.raises(ValueError):
        parse_response(response)
