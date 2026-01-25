#!/usr/bin/env python3
"""
Beyond Brief - AI Content Writer

Uses Claude API to transform raw news into punchy, Morning Brew-style newsletter content.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import anthropic


# ============================================================
# PROMPTS
# ============================================================

SYSTEM_PROMPT = """You are the head writer for "Beyond Brief," a daily newsletter for founders, entrepreneurs, and tech professionals. Your writing style is:

TONE:
- Punchy and direct like Sam Parr (The Hustle) and Morning Brew
- Conversational but smart - you're talking to busy, intelligent people
- Use short sentences. Punch. Impact. Move on.
- Inject personality and occasional humor, but never at the expense of clarity
- No corporate speak. No fluff. No filler words.

STRUCTURE:
- Lead with the most interesting angle, not the obvious one
- Include specific numbers and facts (they build credibility)
- End sections with a "so what" - why should the reader care?
- Use analogies to explain complex topics

RULES:
- Never start with "In today's newsletter..." or similar
- Avoid clichés like "game-changer," "revolutionary," "disrupting"
- Don't use emojis excessively (1-2 per section max)
- Always attribute sources with clean anchor text like "Source Name → Read more"
- Keep paragraphs to 2-3 sentences max

FORMAT for each story:
**Headline** (bold, attention-grabbing)
2-3 paragraphs of content with the story + analysis + why it matters
Source attribution at the end"""


TOP_STORY_PROMPT = """Write the TOP STORY section for today's newsletter.

Here are the top news items to choose from (pick the BEST one):
{news_items}

Write a compelling 150-200 word piece on the most important/interesting story. Include:
1. A punchy headline (not the original - make it better)
2. The key facts (who, what, how much, etc.)
3. Context - why this matters to founders/entrepreneurs
4. A "so what" takeaway

End with the source attribution in this exact format:
[Source Name](URL) → Read more

Output ONLY the formatted content, no preamble."""


NEWS_SECTION_PROMPT = """Write the "IN THE NEWS" section with 2-3 quick hit stories.

Available stories:
{news_items}

For each story, write:
- Bold headline
- 2-3 sentences max
- Source link

Keep it punchy. These are quick hits, not deep dives.
Output ONLY the formatted content."""


AI_WATCH_PROMPT = """Write the "AI WATCH" section about the latest in AI/ML.

Available AI stories:
{news_items}

Pick the most interesting AI story and write 100-150 words covering:
- What happened
- Why it's significant for people building products/companies
- What to watch for next

End with source attribution.
Output ONLY the formatted content."""


TOOL_PROMPT = """Write the "TOOL OF THE DAY" section.

Available tool/product stories:
{news_items}

Pick ONE interesting tool and write 80-100 words:
- What it does
- Who it's for
- Why it's worth checking out

Be specific about features/pricing if available.
Output ONLY the formatted content."""


QUICK_HITS_PROMPT = """Write the "QUICK HITS" section - 5 bullet points of trending stories.

Available stories:
{news_items}

Write exactly 5 bullet points. Each should be:
- One sentence
- Include a hyperlink to the source
- Format: "• [Story summary with key fact](URL)"

Output ONLY the 5 bullet points."""


FOUNDER_INSIGHT_PROMPT = """Write the "FOUNDER INSIGHT" section - a tactical takeaway for entrepreneurs.

Based on today's news themes:
{themes}

Write 80-100 words with:
- A specific, actionable insight or framework
- Something the reader can apply TODAY
- Make it practical, not philosophical

Output ONLY the formatted content."""


GREETING_PROMPT = """Write a 2-sentence opening greeting for today's newsletter.

Today is {day_of_week}, {date}.

Key themes from today's news:
{themes}

Write a punchy, Morning Brew-style opener that:
- Hooks the reader immediately
- References something topical
- Sets up what's coming in the newsletter

Keep it under 40 words total. No "Good morning" - be more creative.
Output ONLY the greeting text."""


# ============================================================
# CLAUDE API CLIENT
# ============================================================

class AIWriter:
    """Generates newsletter content using Claude API."""

    def __init__(self, api_key: str = None):
        """
        Initialize the AI writer.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY env var.")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Fast and capable

    def _call_claude(self, user_prompt: str, max_tokens: int = 1000) -> str:
        """Make a call to Claude API."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Claude API error: {e}")
            raise

    def _format_news_for_prompt(self, items: List[Dict], max_items: int = 5) -> str:
        """Format news items for inclusion in prompts."""
        formatted = []
        for i, item in enumerate(items[:max_items], 1):
            formatted.append(f"""
{i}. **{item.get('title', 'Untitled')}**
   Source: {item.get('source', 'Unknown')}
   URL: {item.get('url', '')}
   Summary: {item.get('summary', '')[:300]}
""")
        return "\n".join(formatted)

    def write_greeting(self, themes: List[str]) -> str:
        """Generate the opening greeting."""
        now = datetime.now()
        prompt = GREETING_PROMPT.format(
            day_of_week=now.strftime("%A"),
            date=now.strftime("%B %d, %Y"),
            themes=", ".join(themes[:5])
        )
        return self._call_claude(prompt, max_tokens=150)

    def write_top_story(self, news_items: List[Dict]) -> str:
        """Generate the top story section."""
        prompt = TOP_STORY_PROMPT.format(
            news_items=self._format_news_for_prompt(news_items, 5)
        )
        return self._call_claude(prompt, max_tokens=500)

    def write_news_section(self, news_items: List[Dict]) -> str:
        """Generate the In The News section."""
        prompt = NEWS_SECTION_PROMPT.format(
            news_items=self._format_news_for_prompt(news_items, 6)
        )
        return self._call_claude(prompt, max_tokens=600)

    def write_ai_watch(self, ai_items: List[Dict]) -> str:
        """Generate the AI Watch section."""
        prompt = AI_WATCH_PROMPT.format(
            news_items=self._format_news_for_prompt(ai_items, 5)
        )
        return self._call_claude(prompt, max_tokens=400)

    def write_tool_of_day(self, tool_items: List[Dict]) -> str:
        """Generate the Tool of the Day section."""
        prompt = TOOL_PROMPT.format(
            news_items=self._format_news_for_prompt(tool_items, 5)
        )
        return self._call_claude(prompt, max_tokens=300)

    def write_quick_hits(self, all_items: List[Dict]) -> str:
        """Generate the Quick Hits section."""
        prompt = QUICK_HITS_PROMPT.format(
            news_items=self._format_news_for_prompt(all_items, 10)
        )
        return self._call_claude(prompt, max_tokens=400)

    def write_founder_insight(self, themes: List[str]) -> str:
        """Generate the Founder Insight section."""
        prompt = FOUNDER_INSIGHT_PROMPT.format(
            themes=", ".join(themes)
        )
        return self._call_claude(prompt, max_tokens=300)


def generate_full_newsletter(news_data: Dict, api_key: str = None) -> Dict:
    """
    Generate a complete newsletter from fetched news data.

    Args:
        news_data: Output from news_fetcher.fetch_all_news()
        api_key: Anthropic API key

    Returns:
        Dictionary with all newsletter sections
    """
    writer = AIWriter(api_key)
    categories = news_data.get("categories", {})

    # Extract themes from top stories
    themes = []
    for item in categories.get("top_stories", [])[:3]:
        title = item.get("title", "")
        # Extract key themes
        if "ai" in title.lower() or "gpt" in title.lower():
            themes.append("AI advancements")
        if "funding" in title.lower() or "raised" in title.lower():
            themes.append("startup funding")
        if "apple" in title.lower() or "google" in title.lower() or "microsoft" in title.lower():
            themes.append("big tech moves")

    if not themes:
        themes = ["tech innovation", "startup ecosystem", "AI development"]

    print("Generating newsletter content with Claude...")

    # Generate each section
    print("  → Writing greeting...")
    greeting = writer.write_greeting(themes)

    print("  → Writing top story...")
    top_story = writer.write_top_story(
        categories.get("top_stories", []) + categories.get("business", [])
    )

    print("  → Writing news section...")
    news_section = writer.write_news_section(
        categories.get("business", []) + categories.get("startup", [])
    )

    print("  → Writing AI watch...")
    ai_watch = writer.write_ai_watch(
        categories.get("ai", []) + categories.get("tech", [])
    )

    print("  → Writing tool of the day...")
    tool_section = writer.write_tool_of_day(
        categories.get("tool", []) + categories.get("startup", [])
    )

    print("  → Writing quick hits...")
    quick_hits = writer.write_quick_hits(
        categories.get("top_stories", []) +
        categories.get("tech", []) +
        categories.get("ai", [])
    )

    print("  → Writing founder insight...")
    founder_insight = writer.write_founder_insight(themes)

    # Compile newsletter
    newsletter = {
        "generated_at": datetime.now().isoformat(),
        "sections": {
            "greeting": greeting,
            "top_story": top_story,
            "in_the_news": news_section,
            "ai_watch": ai_watch,
            "tool_of_day": tool_section,
            "quick_hits": quick_hits,
            "founder_insight": founder_insight
        },
        "metadata": {
            "themes": themes,
            "source_count": news_data.get("total_items", 0)
        }
    }

    return newsletter


def save_newsletter_content(newsletter: Dict, filepath: str):
    """Save generated newsletter to JSON."""
    with open(filepath, 'w') as f:
        json.dump(newsletter, f, indent=2)
    print(f"Saved newsletter content to {filepath}")


# Example usage
if __name__ == "__main__":
    import sys

    # Load news data
    if len(sys.argv) > 1:
        news_file = sys.argv[1]
        with open(news_file, 'r') as f:
            news_data = json.load(f)
    else:
        # Sample data for testing
        news_data = {
            "categories": {
                "top_stories": [
                    {
                        "title": "xAI Raises $20B in Largest AI Funding Round Ever",
                        "source": "TechCrunch",
                        "url": "https://techcrunch.com/xai-funding",
                        "summary": "Elon Musk's AI company xAI has closed a $20 billion funding round, valuing the company at over $120 billion."
                    }
                ],
                "ai": [],
                "business": [],
                "startup": [],
                "tool": [],
                "tech": []
            },
            "total_items": 1
        }

    newsletter = generate_full_newsletter(news_data)

    print("\n" + "=" * 60)
    print("GENERATED NEWSLETTER")
    print("=" * 60)

    for section, content in newsletter["sections"].items():
        print(f"\n--- {section.upper()} ---")
        print(content[:500] + "..." if len(content) > 500 else content)

    # Save if output path provided
    if len(sys.argv) > 2:
        save_newsletter_content(newsletter, sys.argv[2])
