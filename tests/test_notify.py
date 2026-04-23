from pathlib import Path

import kon.notify as mod
from kon.notify import notify


def test_notify_plays_macos_sound(monkeypatch):
    commands: list[list[str]] = []

    monkeypatch.setattr(mod, "_platform", lambda: "darwin")
    monkeypatch.setattr(mod, "_sound_path", lambda event: Path(f"/sounds/{event}.mp3"))
    monkeypatch.setattr(mod, "_run", commands.append)

    notify("completion")

    assert commands == [["afplay", "/sounds/completion.mp3"]]


def test_notify_plays_linux_sound_with_cached_player(monkeypatch):
    commands: list[list[str]] = []

    monkeypatch.setattr(mod, "_platform", lambda: "linux")
    monkeypatch.setattr(mod, "_sound_path", lambda event: Path(f"/sounds/{event}.mp3"))
    monkeypatch.setattr(mod, "_linux_player", lambda: "mpv")
    monkeypatch.setattr(mod, "_run", commands.append)

    notify("permission")

    assert commands == [
        [
            "mpv",
            "--no-video",
            "--no-terminal",
            "--script-opts=autoload-disabled=yes",
            "/sounds/permission.mp3",
        ]
    ]


def test_notify_ignores_unsupported_platform(monkeypatch):
    commands: list[list[str]] = []

    monkeypatch.setattr(mod, "_platform", lambda: "windows")
    monkeypatch.setattr(mod, "_sound_path", lambda event: Path(f"/sounds/{event}.mp3"))
    monkeypatch.setattr(mod, "_run", commands.append)

    notify("error")

    assert commands == []


def test_linux_player_prefers_paplay(monkeypatch):
    mod._linux_player.cache_clear()
    monkeypatch.setattr(
        mod.shutil, "which", lambda command: command if command == "paplay" else None
    )

    assert mod._linux_player() == "paplay"

    mod._linux_player.cache_clear()


def test_linux_player_falls_back_to_aplay(monkeypatch):
    mod._linux_player.cache_clear()
    monkeypatch.setattr(
        mod.shutil, "which", lambda command: command if command == "aplay" else None
    )

    assert mod._linux_player() == "aplay"

    mod._linux_player.cache_clear()
