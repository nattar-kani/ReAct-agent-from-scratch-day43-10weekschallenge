
import pytest

from src.tools import calculate, execute_tool


def test_addition():
    assert calculate("45 + 10") == "55"


def test_multiplication():
    assert calculate("3 * 45") == "135"


def test_combined_expression():
    assert calculate("3 * 45 + 2 * 10") == "155"


def test_unknown_tool():
    with pytest.raises(ValueError):
        execute_tool("delete_files", {})


def test_unsupported_expression():
    with pytest.raises(ValueError):
        calculate("__import__('os')")


def test_invalid_arguments():
    with pytest.raises(ValueError):
        execute_tool("calculate", {"wrong": "45 + 10"})
