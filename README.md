# Day 43 — ReAct Agent from Scratch

A simple ReAct (Reason + Act) agent built with Python and a locally running Ollama model. This project demonstrates how an LLM can request a tool, observe its result, and decide what to do next — without using LangChain, LangGraph, or CrewAI.

## Project Overview

Most LLM applications follow a simple pattern: send a prompt and receive an answer.

A ReAct agent adds a decision loop. It can request a tool, receive the tool's output, and use that observation to decide its next action.

In this project, the agent uses a calculator tool to solve a small real-world problem:

> Calculate the total cost of 3 notebooks at ₹45 each and 2 pens at ₹10 each.

Expected result: **₹155**

## How It Works

The agent follows this workflow:

1. Receive the user's task.
2. Build a prompt containing the task and previous events.
3. Ask the LLM to choose a tool call or return a final answer.
4. Parse and validate the model's JSON response.
5. Execute the requested tool if it is registered.
6. Store the tool result or error as an observation.
7. Send the updated context to the LLM for its next decision.
8. Stop when the LLM returns a final answer or the maximum number of steps is reached.

### Example ReAct Cycle

**Task:** Calculate `3 * 45 + 2 * 10`.

**Action:** The LLM requests the `calculate` tool.

**Observation:** The calculator returns `155`.

**Final answer:** The LLM responds with the total.

The loop is limited to five iterations by default. This is a maximum, not a requirement: the agent can finish earlier.

## Architecture

```text
User Task
    |
    v
main.py
    |
    v
ReActAgent
    |
    +---- Build prompt using task + memory
    |
    v
Local Ollama LLM
    |
    v
JSON Parser
    |
    +---- Final answer ---> Return result
    |
    v
Registered Tool
    |
    v
Calculator Result / Error
    |
    v
Agent Memory
    |
    +---- Updated context ---> Next iteration
```

## Project Structure

```text
Day 43/
├── src/
│   ├── __init__.py
│   ├── agent.py
│   ├── memory.py
│   ├── parser.py
│   └── tools.py
├── tests/
│   ├── test_agent.py
│   ├── test_parser.py
│   └── test_tools.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Component Responsibilities

| Component | Responsibility |
|---|---|
| `main.py` | Starts the agent and displays the answer |
| `src/agent.py` | Implements the ReAct decision loop |
| `src/memory.py` | Stores the task, actions, observations, and final event |
| `src/parser.py` | Parses and validates structured JSON responses |
| `src/tools.py` | Implements the calculator and registered-tool execution |
| `tests/` | Tests the tools, parser, memory, agent loop, and error handling |

## Technologies Used

- Python
- Ollama
- `qwen2.5:1.5b` local model
- `pytest`
- Python AST for restricted arithmetic expression evaluation

## Setup and Installation

### Prerequisites

- Python 3.12 or a compatible Python version
- [Ollama](https://ollama.com/)
- Git

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <YOUR_REPOSITORY_FOLDER>
```

Replace the placeholders with your actual public repository URL and folder name.

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Download the model

Make sure Ollama is installed and available, then run:

```powershell
ollama pull qwen2.5:1.5b
```

### 5. Run the agent

From the project root:

```powershell
python main.py
```

Expected output:

```text
Final Answer:
155
```

The exact wording may differ if the model generates a more descriptive answer.

## Running the Tests

Run the complete test suite from the project root:

```powershell
python -m pytest -v
```

The current test suite contains 22 tests covering:

- Arithmetic calculations
- Unsupported expressions and invalid tool arguments
- JSON parsing and response validation
- Memory event recording and clearing
- Tool execution followed by a final answer
- Immediate final answers
- Unknown tools
- Ollama failures
- Malformed JSON and unexpected response structures

The tests mock the LLM when testing agent behaviour, making those tests predictable without repeated model calls.

## Safety and Error Handling

This project includes several basic safeguards:

- **Registered tools only:** the agent cannot execute arbitrary tool names.
- **Restricted arithmetic:** the calculator evaluates a limited set of AST nodes instead of using Python's `eval()`.
- **Input length limit:** arithmetic expressions longer than 100 characters are rejected.
- **Structured response validation:** the parser checks the response type and required fields.
- **Tool error observations:** execution errors are recorded and passed back into the agent's context.
- **LLM failure handling:** communication failures, unexpected response structures, and invalid model responses return readable error messages.

These safeguards reduce some risks, but this is an educational implementation, not a production-hardened agent.

## Design Decisions

### Why build a ReAct loop from scratch?

Building the loop directly makes the responsibilities visible: prompting, parsing, tool execution, observations, and stopping conditions. It also makes it easier to understand what agent frameworks automate.

### Why use JSON responses?

A structured response lets the program distinguish between a tool request and a final answer without relying on free-form text conventions.

### Why use AST instead of `eval()`?

`eval()` can execute arbitrary Python expressions. This calculator instead accepts only explicitly supported numeric constants, arithmetic operations, and unary signs.

### Why keep memory?

The LLM does not automatically retain the results of previous independent calls. The agent stores events and includes them in subsequent prompts so the model can use previous observations.

## Current Limitations

- Memory exists only for one agent run; it is not persistent across runs.
- Only a calculator tool is implemented.
- The calculator supports addition, subtraction, multiplication, division, and unary positive/negative operators.
- The model may still choose an inappropriate action or produce an incorrect answer.
- A five-step limit prevents an unbounded decision loop, but it does not guarantee that every task will finish.
- Error handling is basic and does not include retries or recovery strategies.

