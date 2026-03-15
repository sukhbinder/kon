from typing import Any, cast

import pytest
from anthropic.types import ThinkingConfigEnabledParam

from kon.core.types import AssistantMessage, TextContent, ThinkingContent, ToolCall, UserMessage
from kon.llm.base import ProviderConfig
from kon.llm.providers.anthropic import AnthropicProvider, supports_adaptive_thinking


@pytest.fixture
def anthropic_provider() -> AnthropicProvider:
    # Avoid constructing the real SDK client; conversion helpers don't need it.
    return AnthropicProvider.__new__(AnthropicProvider)


def test_convert_assistant_message_drops_unsigned_thinking(anthropic_provider: AnthropicProvider):
    messages = [
        UserMessage(content="hi"),
        AssistantMessage(content=[ThinkingContent(thinking="partial reasoning", signature=None)]),
        UserMessage(content="next"),
    ]

    converted = anthropic_provider._convert_messages(messages)

    # Assistant message with only unsigned thinking should be dropped entirely.
    assert len(converted) == 2
    assert converted[0]["role"] == "user"
    assert converted[1]["role"] == "user"


def test_convert_assistant_message_keeps_signed_thinking(anthropic_provider: AnthropicProvider):
    messages = [
        UserMessage(content="hi"),
        AssistantMessage(
            content=[
                ThinkingContent(thinking="valid reasoning", signature="sig_123"),
                TextContent(text="result"),
                ToolCall(id="tool_1", name="read", arguments={"path": "a.txt"}),
            ]
        ),
    ]

    converted = anthropic_provider._convert_messages(messages)

    assert len(converted) == 2
    assert converted[1]["role"] == "assistant"
    assistant_content = converted[1]["content"]
    assert isinstance(assistant_content, list)

    assert assistant_content[0] == {
        "type": "thinking",
        "thinking": "valid reasoning",
        "signature": "sig_123",
    }
    assert assistant_content[1] == {"type": "text", "text": "result"}
    assert assistant_content[2] == {
        "type": "tool_use",
        "id": "tool_1",
        "name": "read",
        "input": {"path": "a.txt"},
    }


def test_supports_adaptive_thinking_detection():
    assert supports_adaptive_thinking("claude-opus-4.6")
    assert supports_adaptive_thinking("claude-opus-4-6")
    assert supports_adaptive_thinking("claude-sonnet-4.6")
    assert supports_adaptive_thinking("claude-sonnet-4-6")
    assert not supports_adaptive_thinking("claude-3-7-sonnet")


class _EmptyAsyncIterator:
    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration


class _DummyStreamContext:
    async def __aenter__(self):
        return _EmptyAsyncIterator()


class _DummyMessages:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        return _DummyStreamContext()


@pytest.mark.asyncio
async def test_stream_uses_adaptive_thinking_for_claude_4_6():
    provider = AnthropicProvider.__new__(AnthropicProvider)
    provider.config = ProviderConfig(model="claude-sonnet-4.6", thinking_level="xhigh")
    dummy_messages = _DummyMessages()
    provider._client = cast(Any, type("DummyClient", (), {"messages": dummy_messages})())

    stream = await provider._stream_impl(messages=[])
    async for _ in stream:
        pass

    kwargs = dummy_messages.calls[0]
    assert kwargs["thinking"] == {"type": "adaptive"}
    assert kwargs["output_config"] == {"effort": "max"}
    assert "temperature" not in kwargs


@pytest.mark.asyncio
async def test_stream_uses_budget_thinking_for_non_adaptive_models():
    provider = AnthropicProvider.__new__(AnthropicProvider)
    provider.config = ProviderConfig(model="claude-3-7-sonnet", thinking_level="high")
    dummy_messages = _DummyMessages()
    provider._client = cast(Any, type("DummyClient", (), {"messages": dummy_messages})())

    stream = await provider._stream_impl(messages=[])
    async for _ in stream:
        pass

    kwargs = dummy_messages.calls[0]
    assert kwargs["thinking"] == ThinkingConfigEnabledParam(type="enabled", budget_tokens=8192)
