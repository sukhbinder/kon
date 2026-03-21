import json

from kon import CONFIG_DIR_NAME
from kon.metrics import append_run_metric, get_turn_metrics_path


def test_get_turn_metrics_path(monkeypatch, tmp_path):
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    assert get_turn_metrics_path() == tmp_path / CONFIG_DIR_NAME / "turn-metrics.jsonl"


def test_append_run_metric_appends_jsonl(monkeypatch, tmp_path):
    path = tmp_path / "turn-metrics.jsonl"
    monkeypatch.setattr("kon.metrics.get_turn_metrics_path", lambda: path)

    append_run_metric(
        session_id="session-1",
        provider="openai",
        model="gpt-5",
        turn_metrics=[(45, 1.5), (30, 2.256)],
        tool_call_count=2,
        stop_reason="tool_use",
    )
    append_run_metric(
        session_id="session-2",
        provider="anthropic",
        model="claude",
        turn_metrics=[(78, 3.333)],
        tool_call_count=0,
        stop_reason="stop",
    )

    lines = path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2

    first = json.loads(lines[0])
    second = json.loads(lines[1])

    assert first["session_id"] == "session-1"
    assert first["provider"] == "openai"
    assert first["model"] == "gpt-5"
    assert first["turn_metrics"] == [[45, 1.5], [30, 2.26]]
    assert first["tool_call_count"] == 2
    assert first["stop_reason"] == "tool_use"
    assert first["timestamp"].endswith("Z")
    assert len(first["timestamp"]) == 17

    assert second["session_id"] == "session-2"
    assert second["turn_metrics"] == [[78, 3.33]]
    assert second["stop_reason"] == "stop"
