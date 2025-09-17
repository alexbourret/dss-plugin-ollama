from dataiku.llm.python import BaseLLM


class OllamaLLM(BaseLLM):
    def __init__(self):
        print("ALX:OllamaLLM init")

    def set_config(self, config: dict, plugin_config: dict) -> None:
        print("ALX:OllamaLLM set_config")

    def process(self, query, settings, trace):
        print("ALX:query={}, settings={}".format(query, settings))
        prompt = query["messages"][0]["content"]

        # Add code here, for LLM completion, tool execution, etc...
        # data = {
        #   "model": "{}".format(model_name),
        #   "prompt": "{}".format(prompt)
        #  }
        # if image:
        #     data["images"] = [image]
        # if output_format:
        #     data["format"] = output_format
        # try:
        #     response = requests.post(url="{}/api/generate".format(server_url), json=data)
        # except Exception as error:
        #     raise Exception("Connection error: {}".format(error))

        return {
            "text": "the custom LLM answer",
            "promptTokens": 46, # Optional
            "completionTokens": 10, # Optional
            "estimatedCost": 0.13, # Optional
            "toolCalls": [],
        }
