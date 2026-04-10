import pytest
from kon.ui.input import InputBox

def test_input_box_shell_command_detection():
    input_box = InputBox()

    # Test single !
    cmd, history = input_box._detect_shell_command("!ls -la")
    assert cmd == "ls -la"
    assert history is False

def test_input_box_shell_command_history_detection():
    input_box = InputBox()

    # Test double !!
    cmd, history = input_box._detect_shell_command("!!git status")
    assert cmd == "git status"
    assert history is True

def test_input_box_no_shell_command():
    input_box = InputBox()

    # Test no prefix
    cmd, history = input_box._detect_shell_command("ls -la")
    assert cmd is None
    assert history is False

    # Test single ! not at start (should not be detected by _detect_shell_command as it expects startswith)
    cmd, history = input_box._detect_shell_command("echo !hello")
    assert cmd is None
