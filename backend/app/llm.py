import httpx

from .config import settings


class LLMError(Exception):
    pass


async def embed(text: str) -> list[float]:
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                f"{settings.ollama_base_url}/api/embeddings",
                json={
                    "model": settings.embedding_model,
                    "prompt": text,
                },
            )

            r.raise_for_status()

            return r.json()["embedding"]

    except Exception as e:
        raise LLMError(
            f"Embedding service unavailable: {e}"
        )


async def generate_with_agent_sdk(
    prompt: str,
    system: str = "",
) -> str:
    """
    Generate a response using Anthropic's Claude Agent SDK.

    The Agent SDK is used only for the cloud/Anthropic provider.
    Local development and the required Ollama demo continue to use
    the Ollama path below.
    """

    if not settings.anthropic_api_key:
        raise LLMError(
            "Anthropic provider selected but "
            "ANTHROPIC_API_KEY is missing."
        )

    try:
        from claude_agent_sdk import (
            AssistantMessage,
            ClaudeAgentOptions,
            TextBlock,
            query,
        )

        options = ClaudeAgentOptions(
            model=settings.anthropic_model,
            system_prompt=system,
            allowed_tools=[],
            max_turns=1,
        )

        text_parts = []

        async for message in query(
            prompt=prompt,
            options=options,
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        text_parts.append(block.text)

        result = "".join(text_parts).strip()

        if not result:
            raise LLMError(
                "Claude Agent SDK returned an empty response."
            )

        return result

    except LLMError:
        raise

    except Exception as e:
        raise LLMError(
            f"Claude Agent SDK unavailable: {e}"
        )


async def generate_with_ollama(
    prompt: str,
    system: str = "",
) -> str:
    """
    Generate a response using the local Ollama model.
    This is the required local/offline demo path.
    """

    try:
        async with httpx.AsyncClient(timeout=600) as client:
            r = await client.post(
                f"{settings.ollama_base_url}/api/chat",
                json={
                    "model": settings.ollama_model,
                    "stream": False,
                    "options": {
                        "num_predict": 1800,
                    },
                    "messages": [
                        {
                            "role": "system",
                            "content": system,
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                },
            )

            r.raise_for_status()

            return r.json()["message"]["content"]

    except Exception as e:
        raise LLMError(
            f"Ollama unavailable: {e}"
        )


async def generate(
    prompt: str,
    system: str = "",
    provider: str = "ollama",
) -> str:
    """
    Main LLM entry point.

    provider:
        ollama     -> local Ollama
        anthropic  -> Claude Agent SDK
    """

    if provider == "anthropic":
        return await generate_with_agent_sdk(
            prompt,
            system,
        )

    return await generate_with_ollama(
        prompt,
        system,
    )