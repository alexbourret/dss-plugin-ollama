import requests
from dataiku.llm.python import BaseLLM
from ollama_common import (
    get_configuration,
)
import dataiku


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
        print("OllamaLLM:process")
        # print("query={}, settings={}".format(query, settings))
        available_tools = get_tools_definitions(settings)
        print("Found {} tools for this agent".formta(len(available_tools)))
        messages = query.get("messages", [])

        done = False
        last_run_tools_replies = []
        while not done:
            done = True
            if last_run_tools_replies:
                print("There are {} tool messages to process".format(len(last_run_tools_replies)))
            messages += last_run_tools_replies
            data = {
                "model": "{}".format(self.model_name),
                "messages": messages,
                "stream": False
            }
            # if image:
            #     data["images"] = [image]
            if self.output_format:
                data["format"] = self.output_format
            if available_tools:
                data["tools"] = available_tools
            try:
                print("Sending request")
                response = requests.post(url="{}/api/chat".format(self.server_url), json=data)
            except Exception as error:
                if response:
                    print("Error {}, dumping response: {}".format(
                        error,
                        response.content
                    ))
                raise Exception("Connection error: {}".format(error))
            """
            {
                "model": "mistral",
                "created_at": "2025-09-23T11:39:17.284636Z",
                "message": {
                    "role": "assistant",
                    "content": "ello! How can I help you today? If you have any questions or need assistance with something, feel free to ask.\\n\\nHere are some things that I can do for you:\\n1. Answer general knowledge questions\\n2. Help you solve problems and puzzles\\n3. Provide explanations for complex concepts\\n4. Generate ideas and suggestions\\n5. Tell jokes and stories\\n6. Keep you company and chat with you\\n7. Much more! Just ask, and I\'ll do my best to help.\\n\\nWhat would you like me to do for you today?"
                },
                "done_reason": "stop",
                "done": true,
                "total_duration": 2516315041,
                "load_duration": 13009250,
                "prompt_eval_count": 40,
                "prompt_eval_duration": 97205584,
                "eval_count": 122,
                "eval_duration": 2405588333
            }
            """
            json_response = response.json()
            message = json_response.get("message", {})
            tool_calls = message.get("tool_calls", [])
            if tool_calls:
                for tool_call in tool_calls:
                    function = tool_call.get("function", {})
                    function_name = function.get("name")
                    function_name = " ".join(function_name.split("_")[:-1])
                    function_arguments = function.get("arguments", {})
                    list_tools = dataiku.api_client().get_default_project().list_agent_tools()
                    tool_id = None
                    for list_tool in list_tools:
                        if list_tool.get("name") == function_name:
                            tool_id = list_tool.get("id")
                    if tool_id:
                        print("Calling tool {}".format(tool_id))
                        tool = dataiku.api_client().get_default_project().get_agent_tool(tool_id)
                        output = tool.run(function_arguments)
                        if output:
                            done = False
                            last_run_tools_replies.append({"role": "tool", "content": output.get("output")})
            answer = message.get("content")
            """ run a tool
            tool = dataiku.api_client().get_default_project().get_agent_tool("my-tool-1")

            output = tool.run({
                "filter" : {
                    "operator": "EQUALS",
                    "column": "company_name",
                    "value": "Dataiku"
                }
            })

            # Matched rows are in
            output["output"]["rows"]
            """
            """ request for tooling
            {
                "model": "mistral-small",
                "created_at": "2025-09-23T12:05:52.9735Z",
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [{
                        "function": {
                            "name": "Create_Servicenow_Issue_sAih26",
                            "arguments": {
                                "description": "The user is getting an error message saying \'user does not exist\' when trying to log in.",
                                "summary": "User does not exist error"
                            }
                        }
                    }]
                },
                "done_reason": "stop",
                "done": true,
                "total_duration": 17854819542,
                "load_duration": 7190488459,
                "prompt_eval_count": 533,
                "prompt_eval_duration": 5826685708,
                "eval_count": 58,
                "eval_duration": 4833721833
            }
            """
        return {
            "text": answer,
            # "promptTokens": 46, # Optional
            # "completionTokens": 10, # Optional
            # "estimatedCost": 0.13, # Optional
            "toolCalls": [],
        }


def get_tools_definitions(settings):
    """
    {
        'type': 'function',
        'function': {
            'name': 'Lookup_incident_EPnC2e',
            'description': "This tool can be used to search for a incident on this ServiceNow instance. The input to this tool is a dictionary containing at least one known detail about the incident to lookup, e.g. '{'email':'john.doe@example.com'}' or '{'user_name':'john.doe'}'",
            'parameters': {
                '$schema': 'https://json-schema.org/draft/2020-12/schema',
                '$id': 'https://dataiku.com/agents/tools/search/input',
                'type': 'object',
                'properties': {
                    'description_contains': {
                        'type': 'string'
                    },
                    'number': {
                        'type': 'string'
                    }
                }
            }
        }
    }
    """
    # https://www.postman.com/postman-student-programs/ollama-api/request/uprcxdn/chat-completion-with-tools
    tools_definitions = settings.get("tools", [{}])
    return tools_definitions
