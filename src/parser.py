import json

def parse_response(response:str)-> dict:
    try:
        data = json.loads(response)

    except json.JSONDecodeError as exc:
        raise ValueError("Model returned invalid JSON") from exc

    if not isinstance(data,dict):
        raise ValueError("Model response must be a JSON object")

    response_type = data.get("type")

    if response_type == "tool_call":
        required_keys = {"type","tool","arguments"}

        if set(data.keys()) != required_keys:
            raise ValueError("Invalid tool call structure")

        if not isinstance(data["tool"],str) or not data["tool"]:
            raise ValueError("Tool name must be a non-empty string")

        if not isinstance(data["arguments"],dict):
            raise ValueError("Tool arguments must be a JSON object")

        return data

    if response_type == "final":
        required_keys = {"type","answer"}

        if set(data.keys()) != required_keys:
            raise ValueError("Invalid final-answer structure")

        if not isinstance(data["answer"], str):
            raise ValueError("Final answer must be a string")

        return data

    raise ValueError("Unknown response type")


    
