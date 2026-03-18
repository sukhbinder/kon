from __future__ import annotations

from pydantic import BaseModel


class ToolBgConfig(BaseModel):
    pending: str
    success: str
    error: str


class BadgeColorConfig(BaseModel):
    bg: str
    label: str


class ColorsConfig(BaseModel):
    dim: str
    muted: str
    title: str
    spinner: str
    accent: str
    info: str
    markdown_heading: str
    markdown_code: str
    selected: str
    error: str
    notice: str
    diff_added: str
    diff_removed: str
    tool_bg: ToolBgConfig
    badge: BadgeColorConfig
    running: str
    success: str
    failed: str
    bg: str
    fg: str
    panel: str
    panel_alt: str
    panel_user: str
    border: str


class ThemeConfig(BaseModel):
    id: str
    label: str
    colors: ColorsConfig


_THEMES: dict[str, ThemeConfig] = {
    "gruvbox-dark": ThemeConfig(
        id="gruvbox-dark",
        label="Gruvbox Dark",
        colors=ColorsConfig(
            bg="#282828",
            fg="#ebdbb2",
            dim="#7c6f64",
            muted="#a89984",
            title="#fabd2f",
            spinner="#83a598",
            accent="#83a598",
            info="#fabd2f",
            markdown_heading="#fabd2f",
            markdown_code="#8ec07c",
            selected="#8ec07c",
            error="#fb4934",
            notice="#fe8019",
            diff_added="#b8bb26",
            diff_removed="#fb4934",
            tool_bg=ToolBgConfig(pending="#32302f", success="#3c3836", error="#3c2f2f"),
            badge=BadgeColorConfig(bg="#3c3836", label="#d3869b"),
            running="#458588",
            success="#98971a",
            failed="#cc241d",
            panel="#3c3836",
            panel_alt="#32302f",
            panel_user="#504945",
            border="#504945",
        ),
    ),
    "gruvbox-light": ThemeConfig(
        id="gruvbox-light",
        label="Gruvbox Light",
        colors=ColorsConfig(
            bg="#fbf1c7",
            fg="#3c3836",
            dim="#a89984",
            muted="#7c6f64",
            title="#b57614",
            spinner="#076678",
            accent="#076678",
            info="#b57614",
            markdown_heading="#b57614",
            markdown_code="#427b58",
            selected="#427b58",
            error="#9d0006",
            notice="#af3a03",
            diff_added="#79740e",
            diff_removed="#9d0006",
            tool_bg=ToolBgConfig(pending="#f2e5bc", success="#ebdbb2", error="#f3d9d4"),
            badge=BadgeColorConfig(bg="#ebdbb2", label="#b16286"),
            running="#458588",
            success="#79740e",
            failed="#9d0006",
            panel="#ebdbb2",
            panel_alt="#f2e5bc",
            panel_user="#d5c4a1",
            border="#d5c4a1",
        ),
    ),
    "catppuccin-mocha": ThemeConfig(
        id="catppuccin-mocha",
        label="Catppuccin Mocha",
        colors=ColorsConfig(
            bg="#1e1e2e",
            fg="#cdd6f4",
            dim="#6c7086",
            muted="#a6adc8",
            title="#f5e0dc",
            spinner="#89b4fa",
            accent="#89b4fa",
            info="#f9e2af",
            markdown_heading="#f9e2af",
            markdown_code="#94e2d5",
            selected="#a6e3a1",
            error="#f38ba8",
            notice="#fab387",
            diff_added="#a6e3a1",
            diff_removed="#f38ba8",
            tool_bg=ToolBgConfig(pending="#313244", success="#2b3a33", error="#3d2f38"),
            badge=BadgeColorConfig(bg="#313244", label="#cba6f7"),
            running="#89b4fa",
            success="#a6e3a1",
            failed="#f38ba8",
            panel="#313244",
            panel_alt="#45475a",
            panel_user="#3b3f57",
            border="#45475a",
        ),
    ),
    "catppuccin-latte": ThemeConfig(
        id="catppuccin-latte",
        label="Catppuccin Latte",
        colors=ColorsConfig(
            bg="#eff1f5",
            fg="#4c4f69",
            dim="#9ca0b0",
            muted="#7c7f93",
            title="#dc8a78",
            spinner="#1e66f5",
            accent="#1e66f5",
            info="#df8e1d",
            markdown_heading="#df8e1d",
            markdown_code="#179299",
            selected="#40a02b",
            error="#d20f39",
            notice="#fe640b",
            diff_added="#40a02b",
            diff_removed="#d20f39",
            tool_bg=ToolBgConfig(pending="#e6e9ef", success="#dfe8dc", error="#f2d8dd"),
            badge=BadgeColorConfig(bg="#e6e9ef", label="#8839ef"),
            running="#1e66f5",
            success="#40a02b",
            failed="#d20f39",
            panel="#e6e9ef",
            panel_alt="#dce0e8",
            panel_user="#ccd0da",
            border="#ccd0da",
        ),
    ),
    "tokyo-night": ThemeConfig(
        id="tokyo-night",
        label="Tokyo Night",
        colors=ColorsConfig(
            bg="#1a1b26",
            fg="#c0caf5",
            dim="#565f89",
            muted="#a9b1d6",
            title="#bb9af7",
            spinner="#7aa2f7",
            accent="#7aa2f7",
            info="#e0af68",
            markdown_heading="#e0af68",
            markdown_code="#73daca",
            selected="#9ece6a",
            error="#f7768e",
            notice="#ff9e64",
            diff_added="#9ece6a",
            diff_removed="#f7768e",
            tool_bg=ToolBgConfig(pending="#24283b", success="#243638", error="#3a2734"),
            badge=BadgeColorConfig(bg="#24283b", label="#bb9af7"),
            running="#7aa2f7",
            success="#9ece6a",
            failed="#f7768e",
            panel="#24283b",
            panel_alt="#2f354d",
            panel_user="#313a5f",
            border="#3b4261",
        ),
    ),
    "tokyo-day": ThemeConfig(
        id="tokyo-day",
        label="Tokyo Day",
        colors=ColorsConfig(
            bg="#d5d6db",
            fg="#3760bf",
            dim="#848cb5",
            muted="#6172b0",
            title="#7847bd",
            spinner="#2e7de9",
            accent="#2e7de9",
            info="#8c6c3e",
            markdown_heading="#8c6c3e",
            markdown_code="#007197",
            selected="#587539",
            error="#f52a65",
            notice="#b15c00",
            diff_added="#587539",
            diff_removed="#f52a65",
            tool_bg=ToolBgConfig(pending="#cbccd1", success="#c7d8cb", error="#dec7cf"),
            badge=BadgeColorConfig(bg="#cbccd1", label="#9854f1"),
            running="#2e7de9",
            success="#587539",
            failed="#f52a65",
            panel="#cbccd1",
            panel_alt="#c4c8da",
            panel_user="#b7c5e3",
            border="#b4b5b9",
        ),
    ),
    "one-dark": ThemeConfig(
        id="one-dark",
        label="One Dark",
        colors=ColorsConfig(
            bg="#282c34",
            fg="#abb2bf",
            dim="#5c6370",
            muted="#7f848e",
            title="#c678dd",
            spinner="#61afef",
            accent="#61afef",
            info="#e5c07b",
            markdown_heading="#e5c07b",
            markdown_code="#56b6c2",
            selected="#98c379",
            error="#e06c75",
            notice="#d19a66",
            diff_added="#98c379",
            diff_removed="#e06c75",
            tool_bg=ToolBgConfig(pending="#353b45", success="#33403b", error="#442f36"),
            badge=BadgeColorConfig(bg="#353b45", label="#c678dd"),
            running="#61afef",
            success="#98c379",
            failed="#e06c75",
            panel="#353b45",
            panel_alt="#3e4451",
            panel_user="#404754",
            border="#4b5263",
        ),
    ),
    "one-light": ThemeConfig(
        id="one-light",
        label="One Light",
        colors=ColorsConfig(
            bg="#fafafa",
            fg="#383a42",
            dim="#9ca0a4",
            muted="#696c77",
            title="#a626a4",
            spinner="#4078f2",
            accent="#4078f2",
            info="#c18401",
            markdown_heading="#c18401",
            markdown_code="#0184bc",
            selected="#50a14f",
            error="#e45649",
            notice="#986801",
            diff_added="#50a14f",
            diff_removed="#e45649",
            tool_bg=ToolBgConfig(pending="#f0f0f1", success="#e6f1e6", error="#f5e3e1"),
            badge=BadgeColorConfig(bg="#f0f0f1", label="#a626a4"),
            running="#4078f2",
            success="#50a14f",
            failed="#e45649",
            panel="#f0f0f1",
            panel_alt="#e5e5e6",
            panel_user="#dfe1e6",
            border="#d0d0d2",
        ),
    ),
}

THEME_ORDER = [
    "gruvbox-dark",
    "gruvbox-light",
    "catppuccin-mocha",
    "catppuccin-latte",
    "tokyo-night",
    "tokyo-day",
    "one-dark",
    "one-light",
]


def get_theme_ids() -> list[str]:
    return list(THEME_ORDER)


def get_theme_options() -> list[tuple[str, str]]:
    return [(theme_id, _THEMES[theme_id].label) for theme_id in THEME_ORDER]


def get_theme(theme_id: str) -> ThemeConfig:
    theme = _THEMES.get(theme_id)
    if theme is None:
        raise ValueError(f"Unknown theme: {theme_id}")
    return theme.model_copy(deep=True)
