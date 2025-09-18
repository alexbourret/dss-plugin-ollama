import requests
from dataiku.llm.python import BaseLLM
from ollama_common import (extract_string, get_configuration)


class OllamaLLM(BaseLLM):
    def __init__(self):
        print("OllamaLLM init")

    def set_config(self, config, plugin_config):
        print("OllamaLLM set_config:config={}, plugin_config={}".format(config, plugin_config))
        self.server_url, self.model_name, self.output_format = get_configuration(config)
        print("server_url={}, model_name_template={}, output_format={}".format(
            self.server_url, self.model_name, self.output_format
        ))

    def process(self, query, settings, trace):
        print("query={}, settings={}".format(query, settings))
        prompt = query.get("messages", [{}])[0].get("content")

        data = {
          "model": "{}".format(self.model_name),
          "prompt": "{}".format(prompt)
         }
        # if image:
        #     data["images"] = [image]
        if self.output_format:
            data["format"] = self.output_format
        try:
            response = requests.post(url="{}/api/generate".format(self.server_url), json=data)
        except Exception as error:
            raise Exception("Connection error: {}".format(error))
        answer = extract_string(response.content)
        return {
            "text": answer,
            # "promptTokens": 46, # Optional
            # "completionTokens": 10, # Optional
            # "estimatedCost": 0.13, # Optional
            "toolCalls": [],
        }
