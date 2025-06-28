import os

def get_api_keys() -> dict[str, str]:
    """Retrieve API keys from environment variables."""
    api_keys = {
        "openai": os.getenv("OPENAI_API_KEY"),
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    }
    if not all(api_keys.values()):
        raise ValueError("Missing one or more API keys in environment variables")
    return api_keys # type: ignore