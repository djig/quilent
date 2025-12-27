from typing import Any, Optional

from anthropic import Anthropic

from app.config import settings

client = None


def get_client():
    global client
    if client is None and settings.ANTHROPIC_API_KEY:
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    return client


async def generate_summary(
    content: str, prompt_template: str, max_tokens: int = 500
) -> str:
    """Generate AI summary using Claude"""
    ai_client = get_client()
    if not ai_client:
        return "AI summarization not available. Please configure ANTHROPIC_API_KEY."

    prompt = prompt_template.replace("{{content}}", content)

    message = ai_client.messages.create(
        model="claude-3-haiku-20240307",  # Fast & cheap for summaries
        max_tokens=max_tokens,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


async def analyze_contract(
    content: str, prompt_template: str, user_profile: Optional[dict[str, Any]] = None
) -> str:
    """Deep analysis using Claude Sonnet"""
    ai_client = get_client()
    if not ai_client:
        return "AI analysis not available. Please configure ANTHROPIC_API_KEY."

    prompt = prompt_template.replace("{{content}}", content)
    if user_profile:
        prompt = prompt.replace("{{profile}}", str(user_profile))

    message = ai_client.messages.create(
        model="claude-3-5-sonnet-20241022",  # Better for analysis
        max_tokens=1000,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


async def answer_question(context: str, question: str) -> str:
    """Answer question about a contract"""
    ai_client = get_client()
    if not ai_client:
        return "AI Q&A not available. Please configure ANTHROPIC_API_KEY."

    prompt = f"""Based on this government contract information:

{context}

Answer this question: {question}

Provide a clear, concise answer based only on the information provided."""

    message = ai_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=500,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text


# Product-specific prompts
PROMPTS = {
    "gov": {
        "summarize": """Summarize this government contract opportunity in 2-3 sentences.
Focus on: what the government needs, key requirements, and who should apply.

Contract details: {{content}}""",
        "analyze": """Analyze this government contract for a small business. Highlight:
1) Key requirements
2) Potential challenges
3) Estimated effort to bid
4) Red flags to watch for

Contract: {{content}}""",
        "match": """Given this business profile: {{profile}}

Rate how well this contract matches on a scale of 1-100 and explain why.

Contract: {{content}}""",
    },
    "sec": {
        "summarize": """Summarize this SEC filing in 2-3 sentences.
Focus on: key financial changes, significant disclosures, and potential impact on investors.

Filing details: {{content}}""",
        "analyze": """Analyze this SEC filing for retail investors. Highlight:
1) Key financial metrics and changes
2) Risk factors
3) Management commentary insights
4) Red flags to watch

Filing: {{content}}""",
    },
}
