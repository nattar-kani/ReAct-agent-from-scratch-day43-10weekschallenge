import json
import ollama

from src.memory import AgentMemory
from src.parser import parse_response
from src.tools import execute_tool

class ReActAgent:
    def __init__(self,model="qwen2.5:1.5b",max_steps=5):
        self.model = model
        self.max_steps = max_steps

    def run(self,task:str) -> str:
        memory = AgentMemory(task)

        for step in range(self.max_steps):
            prompt = self._build_prompt(memory)

            
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a calculator agent. "
                                "Return exactly one JSON object. "
                                'For calculations, use {"type":"tool_call",'
                                '"tool":"calculate","arguments":'
                                '{"expression":"3 * 45 + 2 * 10"}}. '
                                'When finished, use {"type":"final",'
                                '"answer":"your answer"}. '
                                "Never include Markdown fences."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    format="json",
                )
            except Exception as exc:
                return (
                    "Agent error: Could not get a response from Ollama. "
                    "Check that Ollama is running and the model is available. "
                    f"Details: {type(exc).__name__}"
                )

            try:
                raw_response = response["message"]["content"]
            except (KeyError, TypeError):
                return (
                    "Agent error: Ollama returned an unexpected "
                    "response structure."
                )

            try:
                decision = parse_response(raw_response)
            except ValueError as exc:
                return f"Agent error: Invalid model response. {exc}"


            raw_response = response["message"]["content"]
            decision = parse_response(raw_response)

            if decision["type"]=="final":
                memory.add_event("final",decision["answer"])
                return decision["answer"]

            memory.add_event("action",decision)

            try:
                result = execute_tool(
                    decision["tool"],
                    decision["arguments"]
                )
                observation = {"result":result}
            except Exception as e:
                observation={
                    "error": f"{type(e).__name__}:{e}"
                }

            memory.add_event("observation",observation)

        return "Stopped: maximum number of agent steps reached"

    def _build_prompt(self,memory:AgentMemory)->str:
        return (
            f"Task: {memory.task}\n"
            f"Previous actions and observations:\n"
            f"{json.dumps(memory.get_history(),ensure_ascii=False)}\n"
            "Decide the next action or return the final answer"
        )
            






















