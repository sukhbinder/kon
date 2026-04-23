from __future__ import annotations

import platform
import shutil
import subprocess
from functools import cache
from importlib import resources
from pathlib import Path
from typing import Literal

NotificationEvent = Literal["completion", "permission", "error"]

_SOUND_FILES: dict[NotificationEvent, str] = {
    "completion": "completion.wav",
    "permission": "permission.wav",
    "error": "error.wav",
}


@cache
def _platform() -> str:
    return platform.system().lower()


@cache
def _sound_path(event: NotificationEvent) -> Path:
    return Path(str(resources.files("kon.sounds").joinpath(_SOUND_FILES[event])))


@cache
def _linux_player() -> str | None:
    for player in ("paplay", "aplay", "mpv", "ffplay"):
        if shutil.which(player):
            return player
    return None


def _run(command: list[str]) -> None:
    subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _play_macos(sound_path: Path) -> None:
    _run(["afplay", str(sound_path)])


def _play_linux(sound_path: Path) -> None:
    player = _linux_player()
    if player is None:
        return

    sound = str(sound_path)
    match player:
        case "paplay":
            _run(["paplay", sound])
        case "aplay":
            _run(["aplay", sound])
        case "mpv":
            _run(
                [
                    "mpv",
                    "--no-video",
                    "--no-terminal",
                    "--script-opts=autoload-disabled=yes",
                    sound,
                ]
            )
        case "ffplay":
            _run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", sound])


def notify(event: NotificationEvent) -> None:
    sound_path = _sound_path(event)
    os_name = _platform()

    try:
        if os_name == "darwin":
            _play_macos(sound_path)
        elif os_name == "linux":
            _play_linux(sound_path)
    except Exception:
        return
