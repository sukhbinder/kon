import pytest
from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import Label

from kon.ui.blocks import ToolBlock
from kon.ui.chat import ChatLog
from kon.ui.tool_output import format_expand_hint, truncate_tool_output_text


class ToolExpansionTestApp(App):
    def compose(self) -> ComposeResult:
        yield ChatLog(id="chat-log")


def test_format_expand_hint_styles_ctrl_o_differently():
    hint = format_expand_hint(3)

    assert hint.plain == "... (3 lines hidden • ctrl+o to expand)"
    assert len(hint.spans) == 3
    assert hint.spans[1].start == hint.plain.index("ctrl+o")
    assert hint.spans[1].end == hint.spans[1].start + len("ctrl+o")
    assert hint.spans[1].style != hint.spans[0].style


def test_truncate_tool_output_text_adds_expand_hint():
    collapsed, full = truncate_tool_output_text("\n".join(str(i) for i in range(7)), max_lines=5)

    assert full is True
    assert Text.from_markup(collapsed).plain.splitlines() == [
        "0",
        "1",
        "2",
        "3",
        "4",
        "... (2 lines hidden • ctrl+o to expand)",
    ]


def test_chat_log_toggles_all_tool_blocks(monkeypatch):
    chat = ChatLog()
    block_a = ToolBlock(name="bash")
    block_b = ToolBlock(name="read")
    chat._tool_blocks = {"a": block_a, "b": block_b}
    seen: dict[str, bool] = {}
    monkeypatch.setattr(block_a, "set_expanded", lambda expanded: seen.update(a=expanded))
    monkeypatch.setattr(block_b, "set_expanded", lambda expanded: seen.update(b=expanded))
    monkeypatch.setattr(chat, "_scroll_if_anchored", lambda animate=False: None)

    assert chat.toggle_tool_output_expanded() is True
    assert seen == {"a": True, "b": True}

    assert chat.toggle_tool_output_expanded() is False
    assert seen == {"a": False, "b": False}


@pytest.mark.asyncio
async def test_start_tool_uses_expanded_state_before_mount():
    async with ToolExpansionTestApp().run_test() as pilot:
        chat = pilot.app.query_one("#chat-log", ChatLog)
        chat.set_tool_output_expanded(True)

        block = chat.start_tool("bash", "tool-1")
        await pilot.pause()

        assert block._expanded is True
        assert block.query_one("#tool-output", Label)
