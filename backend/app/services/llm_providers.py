import logging
from abc import ABC, abstractmethod
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract interface for LLM generation providers."""

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate response text given system and user prompts.

        Args:
            system_prompt: System instruction directing model behavior and constraints.
            user_prompt: User query and grounding context.
            temperature: Sampling temperature (0.0 to 1.0).
            max_tokens: Maximum output tokens to generate.

        Returns:
            Generated text string.

        Raises:
            RuntimeError: If provider API call fails.
        """
        pass


class GroqProvider(LLMProvider):
    """Groq LLM provider adapter using AsyncGroq client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key if api_key is not None else settings.groq_api_key
        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "GROQ_API_KEY is not configured. Set GROQ_API_KEY in .env or provide it directly."
            )
        self.model = model or settings.groq_model

        from groq import AsyncGroq

        self.client = AsyncGroq(api_key=self.api_key)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        temp = temperature if temperature is not None else settings.llm_temperature
        tokens = max_tokens if max_tokens is not None else settings.llm_max_tokens

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temp,
                max_tokens=tokens,
            )
            choice = response.choices[0] if response.choices else None
            return choice.message.content.strip() if choice and choice.message.content else ""
        except Exception as err:
            logger.error("Groq API call failed: %s", type(err).__name__)
            raise RuntimeError(f"Groq generation failed: {err}") from err


class GeminiProvider(LLMProvider):
    """Google Gemini provider adapter using google.genai Client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key if api_key is not None else settings.gemini_api_key
        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "GEMINI_API_KEY is not configured. Set GEMINI_API_KEY in .env or provide it directly."
            )
        self.model = model or settings.gemini_model

        from google import genai

        self.client = genai.Client(api_key=self.api_key)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        from google.genai import types

        temp = temperature if temperature is not None else settings.llm_temperature
        tokens = max_tokens if max_tokens is not None else settings.llm_max_tokens

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temp,
            max_output_tokens=tokens,
        )

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config,
            )
            return response.text.strip() if response.text else ""
        except Exception as err:
            logger.error("Gemini API call failed: %s", type(err).__name__)
            raise RuntimeError(f"Gemini generation failed: {err}") from err


class OpenAIProvider(LLMProvider):
    """OpenAI provider adapter using AsyncOpenAI client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key if api_key is not None else settings.openai_api_key
        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "OPENAI_API_KEY is not configured. Set OPENAI_API_KEY in .env or provide it directly."
            )
        self.model = model or settings.openai_model

        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        temp = temperature if temperature is not None else settings.llm_temperature
        tokens = max_tokens if max_tokens is not None else settings.llm_max_tokens

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temp,
                max_tokens=tokens,
            )
            choice = response.choices[0] if response.choices else None
            return choice.message.content.strip() if choice and choice.message.content else ""
        except Exception as err:
            logger.error("OpenAI API call failed: %s", type(err).__name__)
            raise RuntimeError(f"OpenAI generation failed: {err}") from err


def get_llm_provider(provider_name: Optional[str] = None) -> LLMProvider:
    """Factory to instantiate the configured LLM provider.

    Args:
        provider_name: Optional provider override ('groq', 'gemini', 'openai').
                       Defaults to settings.llm_provider.

    Returns:
        Configured LLMProvider instance.

    Raises:
        ValueError: If provider is unknown or required API key is missing.
    """
    provider = (provider_name or settings.llm_provider).lower().strip()

    if provider == "groq":
        return GroqProvider()
    elif provider == "gemini":
        return GeminiProvider()
    elif provider == "openai":
        return OpenAIProvider()
    else:
        raise ValueError(
            f"Unsupported LLM provider '{provider}'. "
            f"Supported providers are: 'groq', 'gemini', 'openai'."
        )
