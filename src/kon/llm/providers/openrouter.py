"""OpenRouter provider implementation."""

from collections.abc import AsyncIterator
from typing import Any

from openai import APIConnectionError, APIStatusError, AsyncOpenAI, RateLimitError

from kon import config as kon_config

from ...core.errors import format_error
from ...core.types import (
    AssistantMessage,
    ImageContent,
    Message,
    StopReason,
    StreamDone,
    StreamError,
    StreamPart,
    TextContent,
    TextPart,
    ThinkingContent,
    ThinkPart,
    ToolCall,
    ToolCallDelta,
    ToolCallStart,
    ToolDefinition,
    ToolResultMessage,
    Usage,
    UserMessage,
)
from ..base import (
    BaseProvider,
    LLMStream,
    ProviderConfig,
    make_http_client,
    resolve_api_key,
)
from .sanitize import sanitize_surrogates


# OpenRouter-specific headers
OPENROUTER_HEADERS = {
    "HTTP-Referer": "https://github.com/kon-sh/kon",
    "X-Title": "Kon",
}


class OpenRouterProvider(BaseProvider):
    name = "openrouter"
    thinking_levels: list[str] = ["none", "minimal", "low", "medium", "high", "xhigh"]

    def __init__(self, config: ProviderConfig):
        super().__init__(config)

        api_key = resolve_api_key(
            config.api_key,
            env_vars=("OPENROUTER_API_KEY",),
            base_url=config.base_url,
            auth_mode=config.openai_compat_auth_mode,
        )
        if not api_key:
            raise ValueError(
                "No API key found for openrouter. "
                "Set OPENROUTER_API_KEY environment variable."
            )

        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=config.base_url or "https://openrouter.ai/api/v1",
            timeout=kon_config.llm.request_timeout_seconds,
            http_client=make_http_client(),
            default_headers=OPENROUTER_HEADERS,
        )

    async def _stream_impl(
        self,
        messages: list[Message],
        *,
        system_prompt: str | None = None,
        tools: list[ToolDefinition] | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMStream:
        openai_messages = self._convert_messages(messages, system_prompt)
        openai_tools = self._convert_tools(tools) if tools else None

        temp = temperature if temperature is not None else self.config.temperature
        max_tok = max_tokens if max_tokens is not None else self.config.max_tokens

        create_kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": openai_messages,
            "stream": True,
            "stream_options": {"include_usage": True},
        }

        if temp is not None:
            create_kwargs["temperature"] = temp

        if max_tok is not None:
            create_kwargs["max_tokens"] = max_tok

        if openai_tools:
            create_kwargs["tools"] = openai_tools

        # Add reasoning effort for thinking support
        thinking_level = self.config.thinking_level
        if thinking_level and thinking_level != "none":
            create_kwargs["reasoning_effort"] = thinking_level

        response = await self._client.chat.completions.create(**create_kwargs)

        llm_stream = LLMStream()
        llm_stream.set_iterator(self._process_stream(response, llm_stream))
        return llm_stream

    async def _process_stream(
        self, response: AsyncIterator, llm_stream: LLMStream
    ) -> AsyncIterator[StreamPart]:
        stop_reason: StopReason = StopReason.STOP

        try:
            async for chunk in response:
                if chunk.usage:
                    prompt_details = getattr(chunk.usage, "prompt_tokens_details", None)
                    cached = getattr(prompt_details, "cached_tokens", 0) or 0
                    cache_write = (
                        getattr(prompt_details, "cache_write_tokens", 0)
                        or getattr(prompt_details, "cache_creation_tokens", 0)
                        or getattr(chunk.usage, "cache_write_tokens", 0)
                        or 0
                    )
                    prompt_tokens = chunk.usage.prompt_tokens or 0
                    non_cached_input = max(prompt_tokens - cached, 0)
                    llm_stream._usage = Usage(
                        input_tokens=non_cached_input,
                        output_tokens=chunk.usage.completion_tokens or 0,
                        cache_read_tokens=cached,
                        cache_write_tokens=cache_write,
                    )

                if chunk.id:
                    llm_stream._id = chunk.id

                if not chunk.choices:
                    continue

                choice = chunk.choices[0]
                delta = choice.delta

                if choice.finish_reason:
                    stop_reason = self._map_finish_reason(choice.finish_reason)

                # Handle reasoning content
                for field_name in ("reasoning_content", "reasoning", "reasoning_text"):
                    reasoning = getattr(delta, field_name, None)
                    if reasoning:
                        yield ThinkPart(think=reasoning, signature=field_name)
                        break

                if delta.content:
                    yield TextPart(text=delta.content)

                if delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        if tool_call.index is None:
                            continue

                        if tool_call.function and tool_call.function.name:
                            yield ToolCallStart(
                                id=tool_call.id or "",
                                name=tool_call.function.name,
                                index=tool_call.index,
                            )

                        if tool_call.function and tool_call.function.arguments:
                            yield ToolCallDelta(
                                index=tool_call.index, arguments_delta=tool_call.function.arguments
                            )

            yield StreamDone(stop_reason=stop_reason)

        except Exception as e:
            yield StreamError(error=format_error(e))

    def _convert_messages(
        self, messages: list[Message], system_prompt: str | None
    ) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []

        if system_prompt:
            result.append({"role": "system", "content": sanitize_surrogates(system_prompt)})

        pending_images: list[ImageContent] = []

        for msg in messages:
            if isinstance(msg, UserMessage):
                if pending_images:
                    result.append(self._create_image_user_message(pending_images))
                    pending_images = []
                result.append(self._convert_user_message(msg))
            elif isinstance(msg, AssistantMessage):
                if pending_images:
                    result.append(self._create_image_user_message(pending_images))
                    pending_images = []
                result.append(self._convert_assistant_message(msg))
            elif isinstance(msg, ToolResultMessage):
                result.append(self._convert_tool_result(msg))
                for item in msg.content:
                    if isinstance(item, ImageContent):
                        pending_images.append(item)

        if pending_images:
            result.append(self._create_image_user_message(pending_images))

        return result

    def _create_image_user_message(self, images: list[ImageContent]) -> dict[str, Any]:
        parts: list[dict[str, Any]] = [
            {"type": "text", "text": "Attached image(s) from tool result:"}
        ]
        for img in images:
            parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{img.mime_type};base64,{img.data}"},
                }
            )
        return {"role": "user", "content": parts}

    def _convert_user_message(self, msg: UserMessage) -> dict[str, Any]:
        if isinstance(msg.content, str):
            return {"role": "user", "content": sanitize_surrogates(msg.content)}

        parts: list[dict[str, Any]] = []
        for item in msg.content:
            if isinstance(item, TextContent):
                parts.append({"type": "text", "text": sanitize_surrogates(item.text)})
            elif isinstance(item, ImageContent):
                parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{item.mime_type};base64,{item.data}"},
                    }
                )

        return {"role": "user", "content": parts}

    def _convert_assistant_message(self, msg: AssistantMessage) -> dict[str, Any]:
        content_parts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        thinking_by_field: dict[str, list[str]] = {}

        for item in msg.content:
            if isinstance(item, TextContent):
                if item.text.strip():
                    content_parts.append(sanitize_surrogates(item.text))
            elif isinstance(item, ThinkingContent):
                if item.thinking.strip():
                    field = item.signature or "reasoning_content"
                    if field not in thinking_by_field:
                        thinking_by_field[field] = []
                    thinking_by_field[field].append(item.thinking)
            elif isinstance(item, ToolCall):
                tool_calls.append(
                    {
                        "id": item.id,
                        "type": "function",
                        "function": {"name": item.name, "arguments": item.arguments},
                    }
                )

        content: Any = "".join(content_parts) if content_parts else None

        result: dict[str, Any] = {"role": "assistant", "content": content}

        for field, thinking_list in thinking_by_field.items():
            result[field] = "\n".join(thinking_list)

        if tool_calls:
            result["tool_calls"] = tool_calls

        if not content and not tool_calls:
            return {"role": "assistant", "content": ""}

        return result

    def _convert_tool_result(self, msg: ToolResultMessage) -> dict[str, Any]:
        text_parts = [item.text for item in msg.content if isinstance(item, TextContent)]
        has_images = any(isinstance(item, ImageContent) for item in msg.content)

        if text_parts:
            content = "\n".join(text_parts)
        elif has_images:
            content = "(see attached image)"
        else:
            content = "(no output)"

        return {"role": "tool", "tool_call_id": msg.tool_call_id, "content": content}

    def _convert_tools(self, tools: list[ToolDefinition]) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in tools
        ]

    def _map_finish_reason(self, reason: str) -> StopReason:
        match reason:
            case "stop":
                return StopReason.STOP
            case "length":
                return StopReason.LENGTH
            case "tool_calls":
                return StopReason.TOOL_USE
            case _:
                return StopReason.STOP

    def should_retry_for_error(self, error: Exception) -> bool:
        if isinstance(error, RateLimitError):
            return True
        if isinstance(error, APIConnectionError):
            return True
        if isinstance(error, APIStatusError):
            return error.status_code >= 500
        return False
