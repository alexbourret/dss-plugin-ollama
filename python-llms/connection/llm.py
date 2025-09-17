# This file is the implementation of custom LLM connection
from dataiku.llm.python import BaseLLM


class OllamaLLM(BaseLLM):
    def __init__(self):
        pass

    def set_config(self, config: dict, plugin_config: dict) -> None:
        pass

    def process(self, query, settings, trace):
        prompt = query["messages"][0]["content"]

        # Add code here, for LLM completion, tool execution, etc...

        return {
            "text": "the custom LLM answer",
            "promptTokens": 46, # Optional
            "completionTokens": 10, # Optional
            "estimatedCost": 0.13, # Optional
            "toolCalls": [],
        }
