"""
Manually maintained model catalog.

Add models here as needed. Each model defines its capabilities,
API type, and any special handling (e.g., vision fallback model).
"""
# TODO: should use something like https://github.com/anomalyco/models.dev in future

import asyncio
import os
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any

import httpx

DEFAULT_MAX_TOKENS = 16384
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


class ApiType(Enum):
    OPENAI_COMPLETIONS = "openai-completions"
    OPENAI_RESPONSES = "openai-responses"
    OPENAI_CODEX_RESPONSES = "openai-codex-responses"
    ANTHROPIC_COPILOT = "anthropic-copilot"
    AZURE_AI_FOUNDRY = "azure-ai-foundry"
    GITHUB_COPILOT = "github-copilot"
    GITHUB_COPILOT_RESPONSES = "github-copilot-responses"
    OPENROUTER = "openrouter"


@dataclass
class Model:
    id: str  # Model ID (e.g., "glm-5.1", "claude-opus-4.6")
    provider: str  # "openai", "zhipu", "github-copilot", "openai-codex"
    api: ApiType  # Which API format to use
    base_url: str  # API endpoint
    max_tokens: int  # Max output tokens
    supports_images: bool  # Native vision support
    supports_thinking: bool  # Reasoning/thinking support
    context_window: int | None = None  # Max context (None = use config default)
    vision_model: str | None = None  # Fallback vision model if no native support


MODELS: dict[str, Model] = {
    # ZhiPu models
    "glm-5.1": Model(
        id="glm-5.1",
        provider="zhipu",
        api=ApiType.OPENAI_COMPLETIONS,
        base_url="https://api.z.ai/api/coding/paas/v4",
        max_tokens=8192,
        supports_images=True,
        supports_thinking=True,
    ),
    "glm-5.2": Model(
        id="glm-5.2",
        provider="zhipu",
        api=ApiType.OPENAI_COMPLETIONS,
        base_url="https://api.z.ai/api/coding/paas/v4",
        max_tokens=65536,
        supports_images=True,
        supports_thinking=True,
        context_window=131072,
    ),
    # DeepSeek models (OpenAI-compatible Chat Completions API)
    "deepseek-v4-flash": Model(
        id="deepseek-v4-flash",
        provider="deepseek",
        api=ApiType.OPENAI_COMPLETIONS,
        base_url="https://api.deepseek.com",
        max_tokens=8192,
        supports_images=False,
        supports_thinking=True,
    ),
    "deepseek-v4-pro": Model(
        id="deepseek-v4-pro",
        provider="deepseek",
        api=ApiType.OPENAI_COMPLETIONS,
        base_url="https://api.deepseek.com",
        max_tokens=8192,
        supports_images=False,
        supports_thinking=True,
    ),
    # GitHub Copilot models - Claude (uses Anthropic Messages API for thinking support)
    "claude-sonnet-4.6-copilot": Model(
        id="claude-sonnet-4.6",
        provider="github-copilot",
        api=ApiType.ANTHROPIC_COPILOT,
        base_url="https://api.individual.githubcopilot.com",
        max_tokens=8192 * 2,
        supports_images=True,
        supports_thinking=True,
    ),
    "claude-opus-4.6-copilot": Model(
        id="claude-opus-4.6",
        provider="github-copilot",
        api=ApiType.ANTHROPIC_COPILOT,
        base_url="https://api.individual.githubcopilot.com",
        max_tokens=8192 * 2,
        supports_images=True,
        supports_thinking=True,
    ),
    # GitHub Copilot models - GPT/Codex (uses OpenAI Responses API)
    "gpt-5.5-copilot": Model(
        id="gpt-5.5",
        provider="github-copilot",
        api=ApiType.GITHUB_COPILOT_RESPONSES,
        base_url="https://api.individual.githubcopilot.com",
        max_tokens=8192 * 2,
        supports_images=True,
        supports_thinking=True,
    ),
    # OpenAI Codex OAuth models (ChatGPT Plus/Pro subscription)
    "gpt-5.5": Model(
        id="gpt-5.5",
        provider="openai-codex",
        api=ApiType.OPENAI_CODEX_RESPONSES,
        base_url="https://chatgpt.com/backend-api",
        max_tokens=8192 * 2,
        supports_images=True,
        supports_thinking=True,
    ),
    # Azure AI Foundry models (Anthropic via Azure)
    "claude-sonnet-4.6-azure": Model(
        id="claude-sonnet-4.6",
        provider="azure-ai-foundry",
        api=ApiType.AZURE_AI_FOUNDRY,
        base_url="",  # resolved from AZURE_AI_FOUNDRY_BASE_URL env var
        max_tokens=8192 * 2,
        supports_images=True,
        supports_thinking=True,
    ),
    "claude-opus-4.6-azure": Model(
        id="claude-opus-4.6",
        provider="azure-ai-foundry",
        api=ApiType.AZURE_AI_FOUNDRY,
        base_url="",  # resolved from AZURE_AI_FOUNDRY_BASE_URL env var
        max_tokens=8192 * 2,
        supports_images=True,
        supports_thinking=True,
    ),
    # Azure AI Foundry - Opus 4.7
    "claude-opus-4.7-azure": Model(
        id="claude-opus-4.7",
        provider="azure-ai-foundry",
        api=ApiType.AZURE_AI_FOUNDRY,
        base_url="",  # resolved from AZURE_AI_FOUNDRY_BASE_URL env var
        max_tokens=8192 * 2,
        supports_images=True,
        supports_thinking=True,
    ),
    # OpenRouter models
    "openrouter/anthropic/claude-3-7-sonnet:beta": Model(
        id="claude-3-7-sonnet",
        provider="openrouter",
        api=ApiType.OPENROUTER,
        base_url="https://openrouter.ai/api/v1",
        max_tokens=8192,
        supports_images=True,
        supports_thinking=True,
        context_window=200000,
    ),
    "openrouter/anthropic/claude-3-5-sonnet:beta": Model(
        id="claude-3-5-sonnet",
        provider="openrouter",
        api=ApiType.OPENROUTER,
        base_url="https://openrouter.ai/api/v1",
        max_tokens=8192,
        supports_images=True,
        supports_thinking=True,
        context_window=200000,
    ),
    "openrouter/openai/gpt-4o": Model(
        id="gpt-4o",
        provider="openrouter",
        api=ApiType.OPENROUTER,
        base_url="https://openrouter.ai/api/v1",
        max_tokens=8192,
        supports_images=True,
        supports_thinking=True,
        context_window=128000,
    ),
    "openrouter/meta-llama/llama-3.1-405b": Model(
        id="llama-3.1-405b",
        provider="openrouter",
        api=ApiType.OPENROUTER,
        base_url="https://openrouter.ai/api/v1",
        max_tokens=8192,
        supports_images=False,
        supports_thinking=True,
        context_window=131072,
    ),
}


# =============================================================================
# OpenRouter Dynamic Model Fetching
# =============================================================================

# Cache for dynamically fetched OpenRouter models
_OPENROUTER_DYNAMIC_MODELS: dict[str, Model] | None = None


async def _fetch_openrouter_models(api_key: str | None = None) -> dict[str, Model]:
    """Fetch all available OpenRouter models from the API."""
    headers: dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(OPENROUTER_MODELS_URL, headers=headers)
            response.raise_for_status()
            data = response.json()
    except Exception:
        # If fetching fails, return empty dict (will use static models)
        return {}

    models: dict[str, Model] = {}
    for model_data in data.get("data", []):
        model_id = model_data.get("id")
        if not model_id:
            continue

        full_id = f"openrouter/{model_id}"

        # Determine capabilities from model metadata
        architecture = model_data.get("architecture", {})
        input_modalities = architecture.get("input_modalities", [])
        supports_images = "image" in input_modalities

        supported_params = model_data.get("supported_parameters", [])
        supports_thinking = "reasoning_effort" in supported_params

        context_length = model_data.get("context_length")

        models[full_id] = Model(
            id=model_id,
            provider="openrouter",
            api=ApiType.OPENROUTER,
            base_url="https://openrouter.ai/api/v1",
            max_tokens=min(context_length or 8192, 8192),  # Conservative default
            supports_images=supports_images,
            supports_thinking=supports_thinking,
            context_window=context_length,
        )

    return models


def _ensure_openrouter_models() -> dict[str, Model]:
    """Ensure OpenRouter models are fetched and cached. Returns dynamic models."""
    global _OPENROUTER_DYNAMIC_MODELS

    if _OPENROUTER_DYNAMIC_MODELS is not None:
        return _OPENROUTER_DYNAMIC_MODELS

    try:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        _OPENROUTER_DYNAMIC_MODELS = asyncio.run(_fetch_openrouter_models(api_key))
    except Exception:
        _OPENROUTER_DYNAMIC_MODELS = {}

    return _OPENROUTER_DYNAMIC_MODELS


def _get_openrouter_static_models() -> dict[str, Model]:
    """Get statically defined OpenRouter models."""
    return {k: v for k, v in MODELS.items() if v.provider == "openrouter"}


def get_all_models() -> list[Model]:
    """Get all models including dynamically fetched OpenRouter models."""
    models = list(MODELS.values())

    # Add dynamically fetched OpenRouter models (if not already in static list)
    dynamic_models = _ensure_openrouter_models()
    static_openrouter_ids = _get_openrouter_static_models().keys()

    for model_id, model in dynamic_models.items():
        if model_id not in MODELS and model_id not in static_openrouter_ids:
            models.append(model)

    return models


def get_models_by_provider(provider: str) -> list[Model]:
    """Get models by provider, including dynamic OpenRouter models."""
    if provider == "openrouter":
        # Get static OpenRouter models
        models = [m for m in MODELS.values() if m.provider == provider]
        # Add dynamic OpenRouter models
        dynamic_models = _ensure_openrouter_models()
        models.extend(dynamic_models.values())
        return models

    return [m for m in MODELS.values() if m.provider == provider]


def get_model(model_id: str, provider: str | None = None) -> Model | None:
    if provider:
        for model in MODELS.values():
            if model.id == model_id and model.provider == provider:
                return model

    direct = MODELS.get(model_id)
    if direct:
        return direct

    for model in MODELS.values():
        if model.id == model_id:
            return model

    return None


def get_all_models() -> list[Model]:
    return list(MODELS.values())


def get_models_by_provider(provider: str) -> list[Model]:
    return [m for m in MODELS.values() if m.provider == provider]


def get_max_tokens(model_id: str) -> int:
    model = MODELS.get(model_id)
    return model.max_tokens if model else DEFAULT_MAX_TOKENS
