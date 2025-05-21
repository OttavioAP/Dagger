import json
import re
from openai import AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion
from google import genai
from google.genai import types
from google.genai.client import AsyncClient
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.config import app_settings
from app.schema.llm.message import Message, ToolMessage
from app.core.exceptions import LLMException
from app.core.logger import logger
from typing import Dict, Any, Optional
from app.schema.llm.tool import AbstractTool, ToolCall


def collect_tools() -> Dict[str, Dict[str, Any]]:
    """
    Collects all AbstractTool subclasses and their schemas/functions.
    Returns a dictionary mapping tool names to their details.
    """
    tools = {}

    # Get all subclasses of AbstractTool
    for tool_class in AbstractTool.__subclasses__():
        try:
            # Get the tool name from the schema
            tool_name = tool_class.__name__

            # Store the class, schema, and function
            # Note: tool_class.function() returns the actual implementation function
            tools[tool_name] = {
                "class": tool_class,
                "schema": tool_class.tool_schema,
                "function": tool_class.tool_function(),  # This already returns the implementation function
            }

            logger.debug(f"Collected tool: {tool_name}")
        except Exception as e:
            logger.error(f"Failed to collect tool {tool_class.__name__}: {str(e)}")
            continue

    return tools


def clean_json_response(response: str) -> dict:
    try:
        match = re.search(r"```(?:json)?(.*?)```", response, re.DOTALL)
        if match is None:
            return json.loads(response)
        json_content = match.group(1).strip()
        return json.loads(json_content)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}\n\nResponse: {response}")
        raise LLMException(
            f"Failed to parse JSON response: {e}\n\nResponse: {response}"
        ) from e


class LLMService:
    def __init__(
        self,
        base_url: str = app_settings.LLM_API_BASE_URL,
        api_key: str = app_settings.LLM_API_KEY,
        model_name: str = app_settings.LLM_MODEL_NAME,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name

        # Dictionary mapping tool names to their class, schema, and function
        self.tools: Dict[str, Dict[str, Any]] = collect_tools()
        logger.debug(f"Initialized LLMService with {len(self.tools)} tools")

    def _client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    async def query_llm(
        self,
        messages: Message | list[Message],
        json_response: bool = False,
        tools: Optional[str | list[str]] = None,
        **kwargs,
    ) -> Message:
        client = self._client()

        if isinstance(messages, Message):
            messages = [messages]

        if isinstance(tools, str):
            tools = [tools]

        tools_to_call = None
        if tools:
            tools_to_call = []
            for tool in tools:
                if tool not in self.tools:
                    raise ValueError(f"Unknown tool: {tool}")
                # Get the schema instance and convert it to dict for JSON serialization
                tools_to_call.append(
                    self.tools[tool]["schema"].model_dump(exclude_none=True)
                )
                logger.debug(f"schema added: {self.tools[tool]['schema']}")
        try:
            logger.debug(f"Querying LLM with latest message: {messages[-1]}")
            completion: ChatCompletion = await client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tools_to_call,
                response_format={"type": "json_object"} if json_response else None,
                **kwargs,
            )

            if completion.choices[0].message.tool_calls:
                logger.debug(
                    f"tool calls produced are {completion.choices[0].message.tool_calls} created from tools {tools_to_call} and completion {completion}"
                )
                tool_results = None
                """
                if tool calls are present, we need to make the calls, and then query the LLM again with the tool results, which leads to a new completion
                """
                tool_results = await self.handle_tool_calls(
                    completion.choices[0].message.tool_calls
                )
                logger.debug(f"tool_results: {tool_results}")

                full_messages = (
                    messages + [completion.choices[0].message] + tool_results
                )
                completion = await client.chat.completions.create(
                    model=self.model_name,
                    messages=full_messages,
                    response_format={"type": "json_object"} if json_response else None,
                    **kwargs,
                )
                logger.debug(f"LLM response after tool calls: {completion}")

            return (
                json.loads(completion.choices[0].message.content)
                if json_response
                else completion.choices[0].message
            )
        except json.JSONDecodeError as e:
            error_message = f"Failed to parse JSON response: {e}\n\nResponse: {completion.choices[0].message.content}"
            logger.error(error_message)
            raise LLMException(error_message) from e
        except Exception as e:
            error_message = f"Failed to query LLM: {e}"
            logger.error(error_message)
            raise LLMException(error_message) from e

    async def handle_tool_calls(self, tool_calls: list[ToolCall]) -> list[ToolMessage]:
        """
        Handle tool calls from the LLM response.

        Args:
            tool_calls: List of ToolCall objects from the LLM response

        Returns:
            List of ToolMessage objects with the results of tool execution
        """
        if not tool_calls:
            return []

        results = []
        for call in tool_calls:
            try:
                name = call.function.name
                args = json.loads(call.function.arguments)
                tool_call_id = call.id

                if name in self.tools:
                    tool_function = self.tools[name]["function"]
                    logger.debug(f"function {name} called with args {args}")
                    result = await tool_function(**args)

                    # Create a ToolMessage instance with JSON content
                    tool_message = ToolMessage(
                        role="tool",
                        tool_call_id=tool_call_id,
                        name=name,
                        content=result.json(),
                    )

                    results.append(tool_message)
                else:
                    logger.warning(f"Tool '{name}' not found in available tools")
            except Exception as e:
                logger.error(f"Error running tool {name}: {e}")
                # Create error message as a ToolMessage with JSON content
                error_message = ToolMessage(
                    role="tool",
                    tool_call_id=call.id if hasattr(call, "id") else "unknown",
                    name=call.function.name if hasattr(call, "function") else "unknown",
                    content={"error": str(e)},  # JSON object, not a string
                )
                results.append(error_message)

        return results


class GoogleGeminiService:
    def __init__(
        self,
        model_name: str = app_settings.GEMINI_MODEL_NAME,
        api_key: str = app_settings.GEMINI_API_KEY,
    ):
        self.model_name = model_name
        self.api_key = api_key

    def _client(self) -> genai.Client:
        return genai.Client(api_key=self.api_key)

    @staticmethod
    def get_content_from_messages(messages: list[Message]):
        return [
            types.Content(
                role=message.role,
                parts=[types.Part.from_text(text=message.content)],
            )
            for message in messages
        ]

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15)
    )
    async def query_llm(
        self,
        messages: list[Message],
        search_enabled=True,
        json_response=True,
        **kwargs,
    ) -> Message:
        try:
            client = self._client()
            contents = self.get_content_from_messages(messages)
            tool = (
                types.Tool(google_search=types.GoogleSearch())
                if search_enabled
                else None
            )
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="application/json"
                if json_response and not search_enabled
                else "text/plain",
                tools=[tool] if tool else None,
                **kwargs,
            )
            response = await client.aio.models.generate_content(
                model=self.model_name, contents=contents, config=generate_content_config
            )
            return (
                {
                    "response": clean_json_response(response.text),
                    "grounding_chunks": response.candidates[
                        0
                    ].grounding_metadata.grounding_chunks,
                }
                if search_enabled and json_response
                else response
            )
        except Exception as e:
            logger.error(f"Error querying LLM: {e}")
            raise LLMException(f"Error querying LLM: {e}") from e
