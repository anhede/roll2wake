from abc import ABC, abstractmethod
from openai import OpenAI
from prompts import STORYTELLER_SYSTEM_PROMPT
import anthropic


class LLM(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Sends the two prompts to whatever backend and returns the raw string output.
        """
        pass


class OpenAILLM(LLM):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            #response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("No content from OpenAI")
        return content
    
    def __repr__(self):
        return f"OpenAI ({self.model})"


class ClaudeLLM(LLM):
    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 1500,
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        if not response.content or len(response.content) == 0:
            raise ValueError("No content from Claude")

        # Claude returns a list of content blocks, get the text from the first one
        content_block = response.content[0]
        if hasattr(content_block, "text"):
            return content_block.text  # type: ignore
        else:
            raise ValueError("Unexpected content format from Claude")
        
    def __repr__(self):
        return f"Anthropic ({self.model})"


if __name__ == "__main__":
    import os

    # Get API keys from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    # Models
    llm_gpt = OpenAILLM(api_key=openai_api_key, model="gpt-4o-mini")
    llm_claude = ClaudeLLM(api_key=anthropic_api_key, model="claude-3-5-sonnet-20240620")

    # Test
    for llm in [llm_gpt, llm_claude]:
        print(f"Testing {llm}...")
        try:
            user_prompt = "Themes: Sci-fi Horror Escape\n\nGenerate a single beat and up to 8 choices following the format above."
            response = llm.generate(STORYTELLER_SYSTEM_PROMPT, user_prompt)
            print("LLM Response:", response)
        except Exception as e:
            print("Error:", e)
