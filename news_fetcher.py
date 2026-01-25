#!/usr/bin/env python3
"""
Beyond Brief - Multi-Source News Fetcher

Fetches news from multiple sources:
1. RSS feeds (TechCrunch, The Verge, Hacker News, etc.)
2. NewsAPI (requires free API key)
3. Web search via DuckDuckGo (no API key needed)

Returns structured news items ready for AI processing.
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Optional
import feedparser
import requests
from urllib.parse import quote_plus


@dataclass
class NewsItem:
    """A single news item from any source."""
    title: str
    summary: str
    url: str
    source: str
    published: str
    category: str  # tech, ai, business, startup, tool
    relevance_score: float = 0.0

    def to_dict(self):
        return asdict(self)

    @property
    def id(self) -> str:
        """Generate unique ID for deduplication."""
        return hashlib.md5(f"{self.title}{self.url}".encode()).hexdigest()[:12]


# ============================================================
# RSS FEED SOURCES
# ============================================================

RSS_FEEDS = {
    # Tech News
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "Wired": "https://www.wired.com/feed/rss",

    # AI Specific
    "MIT Tech Review AI": "https://www.technologyreview.com/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",

    # Startups & Business
    "Hacker News": "https://hnrss.org/frontpage",
    "Product Hunt": "https://www.producthunt.com/feed",
    "SaaStr": "https://www.saastr.com/feed/",

    # Founder/Productivity
    "First Round Review": "https://review.firstround.com/feed.xml",
    "a]6z": "https://a16z.com/feed/",
}

# Keywords to prioritize
PRIORITY_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "llm", "gpt", "claude",
    "startup", "funding", "raised", "valuation", "ipo", "acquisition",
    "founder", "ceo", "entrepreneur",
    "saas", "arr", "revenue", "growth",
    "productivity", "tool", "app", "launch",
    "openai", "anthropic", "google", "microsoft", "apple", "meta",
]


def fetch_rss_feeds(max_age_hours: int = 24) -> List[NewsItem]:
    """
    Fetch news from all configured RSS feeds.

    Args:
        max_age_hours: Only include items from the last N hours

    Returns:
        List of NewsItem objects
    """
    items = []
    cutoff = datetime.now() - timedelta(hours=max_age_hours)

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:  # Limit per source
                # Parse published date
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                else:
                    published = datetime.now()

                # Skip old items
                if published < cutoff:
                    continue

                # Get summary
                summary = ""
                if hasattr(entry, 'summary'):
                    summary = entry.summary[:500]  # Truncate
                elif hasattr(entry, 'description'):
                    summary = entry.description[:500]

                # Clean HTML from summary
                import re
                summary = re.sub(r'<[^>]+>', '', summary)
                summary = summary.strip()

                # Calculate relevance score
                title_lower = entry.title.lower()
                score = sum(1 for kw in PRIORITY_KEYWORDS if kw in title_lower)

                # Determine category
                category = "tech"
                if any(kw in title_lower for kw in ["ai", "gpt", "llm", "claude", "machine learning"]):
                    category = "ai"
                elif any(kw in title_lower for kw in ["funding", "raised", "valuation", "ipo"]):
                    category = "business"
                elif any(kw in title_lower for kw in ["startup", "founder", "launch"]):
                    category = "startup"
                elif any(kw in title_lower for kw in ["tool", "app", "product"]):
                    category = "tool"

                item = NewsItem(
                    title=entry.title,
                    summary=summary,
                    url=entry.link,
                    source=source_name,
                    published=published.isoformat(),
                    category=category,
                    relevance_score=score
                )
                items.append(item)

        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
            continue

    return items


# ============================================================
# NEWS API
# ============================================================

def fetch_newsapi(api_key: str, query: str = "AI OR startup OR tech", max_results: int = 20) -> List[NewsItem]:
    """
    Fetch news from NewsAPI.org

    Get a free API key at: https://newsapi.org/register

    Args:
        api_key: NewsAPI API key
        query: Search query
        max_results: Maximum results to return

    Returns:
        List of NewsItem objects
    """
    if not api_key:
        print("NewsAPI key not provided, skipping...")
        return []

    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "pageSize": max_results,
            "language": "en",
            "apiKey": api_key
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        items = []
        for article in data.get("articles", []):
            # Calculate relevance
            title_lower = article.get("title", "").lower()
            score = sum(1 for kw in PRIORITY_KEYWORDS if kw in title_lower)

            # Determine category
            category = "tech"
            if any(kw in title_lower for kw in ["ai", "gpt", "llm", "claude"]):
                category = "ai"
            elif any(kw in title_lower for kw in ["funding", "raised", "valuation"]):
                category = "business"

            item = NewsItem(
                title=article.get("title", ""),
                summary=article.get("description", "")[:500] if article.get("description") else "",
                url=article.get("url", ""),
                source=article.get("source", {}).get("name", "NewsAPI"),
                published=article.get("publishedAt", datetime.now().isoformat()),
                category=category,
                relevance_score=score
            )
            items.append(item)

        return items

    except Exception as e:
        print(f"Error fetching NewsAPI: {e}")
        return []


# ============================================================
# DUCKDUCKGO SEARCH (No API key needed)
# ============================================================

def fetch_duckduckgo(query: str = "AI news today", max_results: int = 10) -> List[NewsItem]:
    """
    Fetch news via DuckDuckGo Instant Answer API.
    Free, no API key required.

    Args:
        query: Search query
        max_results: Maximum results

    Returns:
        List of NewsItem objects
    """
    try:
        # Use DuckDuckGo's instant answer API
        url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1"

        response = requests.get(url, timeout=10, headers={
            "User-Agent": "BeyondBrief/1.0 (Newsletter Automation)"
        })
        response.raise_for_status()
        data = response.json()

        items = []

        # Get related topics
        for topic in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(topic, dict) and "Text" in topic:
                title = topic.get("Text", "")[:100]
                url = topic.get("FirstURL", "")

                if title and url:
                    item = NewsItem(
                        title=title,
                        summary="",
                        url=url,
                        source="DuckDuckGo",
                        published=datetime.now().isoformat(),
                        category="tech",
                        relevance_score=1
                    )
                    items.append(item)

        return items

    except Exception as e:
        print(f"Error fetching DuckDuckGo: {e}")
        return []


# ============================================================
# MAIN AGGREGATOR
# ============================================================

def fetch_all_news(
    newsapi_key: str = None,
    max_age_hours: int = 24,
    deduplicate: bool = True
) -> dict:
    """
    Fetch news from all sources and aggregate.

    Args:
        newsapi_key: Optional NewsAPI key for additional sources
        max_age_hours: Only include items from last N hours
        deduplicate: Remove duplicate stories

    Returns:
        Dictionary with categorized news items
    """
    print("Fetching news from multiple sources...")

    all_items = []

    # 1. RSS Feeds (primary source, free)
    print("  → RSS feeds...")
    rss_items = fetch_rss_feeds(max_age_hours)
    print(f"    Found {len(rss_items)} items")
    all_items.extend(rss_items)

    # 2. NewsAPI (if key provided)
    if newsapi_key:
        print("  → NewsAPI...")
        newsapi_items = fetch_newsapi(newsapi_key, "AI startup funding tech")
        print(f"    Found {len(newsapi_items)} items")
        all_items.extend(newsapi_items)

    # 3. DuckDuckGo (backup, free)
    print("  → DuckDuckGo...")
    ddg_items = fetch_duckduckgo("AI technology startup news today")
    print(f"    Found {len(ddg_items)} items")
    all_items.extend(ddg_items)

    # Deduplicate by title similarity
    if deduplicate:
        seen_ids = set()
        unique_items = []
        for item in all_items:
            if item.id not in seen_ids:
                seen_ids.add(item.id)
                unique_items.append(item)
        all_items = unique_items
        print(f"  → After deduplication: {len(all_items)} items")

    # Sort by relevance score
    all_items.sort(key=lambda x: x.relevance_score, reverse=True)

    # Categorize
    categorized = {
        "top_stories": [],  # Highest relevance
        "ai": [],
        "business": [],
        "startup": [],
        "tool": [],
        "tech": [],
    }

    for item in all_items:
        # Top stories are the highest relevance regardless of category
        if item.relevance_score >= 2 and len(categorized["top_stories"]) < 3:
            categorized["top_stories"].append(item.to_dict())
        else:
            cat = item.category
            if cat in categorized and len(categorized[cat]) < 10:
                categorized[cat].append(item.to_dict())

    # Add metadata
    result = {
        "fetched_at": datetime.now().isoformat(),
        "total_items": len(all_items),
        "categories": categorized
    }

    return result


def save_news_to_file(news_data: dict, filepath: str):
    """Save fetched news to JSON file."""
    with open(filepath, 'w') as f:
        json.dump(news_data, f, indent=2)
    print(f"Saved news to {filepath}")


# Example usage
if __name__ == "__main__":
    import sys

    newsapi_key = os.environ.get("NEWSAPI_KEY", "")

    news = fetch_all_news(
        newsapi_key=newsapi_key,
        max_age_hours=24
    )

    print(f"\nFetched {news['total_items']} total news items")
    print(f"Top stories: {len(news['categories']['top_stories'])}")
    print(f"AI news: {len(news['categories']['ai'])}")
    print(f"Business: {len(news['categories']['business'])}")
    print(f"Startup: {len(news['categories']['startup'])}")
    print(f"Tools: {len(news['categories']['tool'])}")

    # Save to file
    if len(sys.argv) > 1:
        save_news_to_file(news, sys.argv[1])
    else:
        # Print sample
        print("\n--- TOP STORIES ---")
        for item in news['categories']['top_stories'][:3]:
            print(f"• {item['title'][:80]}...")
            print(f"  {item['source']} | {item['url'][:50]}...")
            print()
