"""A provider profile's get_max_tokens() fills max_output_tokens on the Responses wire."""

import pytest

from agent.transports import get_transport


@pytest.mark.parametrize(("model", "params", "expected"), [
    ("anthropic/claude-sonnet-4-6", {}, 64_000),
    ("openai/gpt-5.5", {}, None),
    ("anthropic/claude-sonnet-4-6", {"max_tokens": 1000}, 1000),
])
def test_perplexity_profile_max_tokens(model, params, expected):
    import agent.transports.codex
    kw = get_transport("codex_responses").build_kwargs(
        model=model, messages=[{"role": "user", "content": "Hi"}], tools=[],
        base_url="https://api.perplexity.ai/v1", provider="perplexity", **params,
    )
    assert kw.get("max_output_tokens") == expected
