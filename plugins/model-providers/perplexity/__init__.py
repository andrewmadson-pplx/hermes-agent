"""Perplexity Agent API provider profile (Responses API at api.perplexity.ai/v1).

``PERPLEXITY_API_KEY`` is also the Search API web backend key, so ``ambient_credentials`` keeps a
web-search-only key from auto-selecting Perplexity for inference or auxiliary tasks. Agent API model
ids are vendor-prefixed (``perplexity/sonar``); the picker reads the live ``GET /v1/models``.
"""

from agent.anthropic_adapter import _get_anthropic_max_output
from hermes_cli.version_info import hermes_user_agent
from providers import register_provider
from providers.base import LazyHeaders, ProviderProfile


class PerplexityProfile(ProviderProfile):
    """The Agent API 400s on ``anthropic/*`` models without ``max_output_tokens``."""

    def get_max_tokens(self, model: str | None) -> int | None:
        if model and model.startswith("anthropic/"):
            return _get_anthropic_max_output(model.removeprefix("anthropic/"))
        return self.default_max_tokens


perplexity = PerplexityProfile(
    name="perplexity", aliases=("pplx",), display_name="Perplexity", description="Perplexity (Agent API)",
    signup_url="https://www.perplexity.ai/account/api", api_mode="codex_responses",
    env_vars=("PERPLEXITY_API_KEY",), base_url="https://api.perplexity.ai/v1", auth_type="api_key",
    ambient_credentials=True, models_dev_id="perplexity-agent",
    default_headers=LazyHeaders({
        "User-Agent": lambda: hermes_user_agent("Hermes-Agent"), "X-Pplx-Integration": "hermes-agent",
    }),
    fallback_models=("openai/gpt-5.5", "anthropic/claude-sonnet-4-6", "perplexity/sonar"),
    default_aux_model="openai/gpt-5-mini",
)

register_provider(perplexity)
