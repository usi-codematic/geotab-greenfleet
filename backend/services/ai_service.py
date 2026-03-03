"""
AI service for generating sustainability reports using Claude API.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def get_client():
    """Get Anthropic client."""
    import anthropic
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment")
    return anthropic.Anthropic(api_key=api_key)


def generate_narrative(prompt, max_tokens=1500):
    """Generate a narrative using Claude."""
    client = get_client()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
