#!/usr/bin/env python3
"""
Beyond Brief - Main Automation Script

This is the entry point for the daily newsletter automation.
Run this script via GitHub Actions, cron, or manually.

Usage:
    python main.py                    # Full run: fetch → write → post
    python main.py --dry-run          # Generate but don't post to Beehiiv
    python main.py --skip-fetch       # Use cached news data
    python main.py --output-dir ./out # Save files to specific directory

Environment Variables Required:
    ANTHROPIC_API_KEY       - Claude API key for content generation
    BEEHIIV_API_KEY         - Beehiiv API key for posting drafts
    BEEHIIV_PUBLICATION_ID  - Your Beehiiv publication ID

Optional Environment Variables:
    NEWSAPI_KEY             - NewsAPI key for additional news sources
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Import our modules
from news_fetcher import fetch_all_news, save_news_to_file
from ai_writer import generate_full_newsletter, save_newsletter_content
from html_generator import generate_html, save_html


def post_to_beehiiv(html_content: str, dry_run: bool = False) -> dict:
    """
    Post newsletter draft to Beehiiv.

    Args:
        html_content: The newsletter HTML
        dry_run: If True, skip posting

    Returns:
        API response or dry run indicator
    """
    import requests

    if dry_run:
        print("  → DRY RUN: Skipping Beehiiv post")
        return {"dry_run": True}

    api_key = os.environ.get("BEEHIIV_API_KEY")
    pub_id = os.environ.get("BEEHIIV_PUBLICATION_ID")

    if not api_key or not pub_id:
        raise ValueError("BEEHIIV_API_KEY and BEEHIIV_PUBLICATION_ID required")

    today = datetime.now().strftime("%B %d, %Y")

    url = f"https://api.beehiiv.com/v2/publications/{pub_id}/posts"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "title": f"Beyond Brief - {today}",
        "subtitle": "Your daily briefing",
        "status": "draft",
        "content_html": html_content,
        "preview_text": "Today's top stories, trends, and tips for founders"
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    result = response.json()
    post_id = result.get("data", {}).get("id", "unknown")

    print(f"  → Created Beehiiv draft: {post_id}")
    print(f"  → Edit at: https://app.beehiiv.com/posts/{post_id}/edit")

    return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Beyond Brief Newsletter Automation")
    parser.add_argument("--dry-run", action="store_true", help="Don't post to Beehiiv")
    parser.add_argument("--skip-fetch", action="store_true", help="Use cached news data")
    parser.add_argument("--output-dir", type=str, default="./output", help="Output directory")
    parser.add_argument("--news-file", type=str, help="Use specific news JSON file")
    args = parser.parse_args()

    # Setup
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")

    print("=" * 60)
    print("BEYOND BRIEF - Automated Newsletter Generation")
    print("=" * 60)
    print(f"Date: {today.strftime('%A, %B %d, %Y at %I:%M %p')}")
    print(f"Output: {output_dir.absolute()}")
    print()

    # ========================================
    # Step 1: Fetch News
    # ========================================
    print("STEP 1: Fetching news...")

    news_file = output_dir / f"news_{date_str}.json"

    if args.news_file:
        news_file = Path(args.news_file)
        print(f"  → Using provided news file: {news_file}")
        with open(news_file, 'r') as f:
            news_data = json.load(f)
    elif args.skip_fetch and news_file.exists():
        print(f"  → Using cached news: {news_file}")
        with open(news_file, 'r') as f:
            news_data = json.load(f)
    else:
        newsapi_key = os.environ.get("NEWSAPI_KEY", "")
        news_data = fetch_all_news(newsapi_key=newsapi_key, max_age_hours=24)
        save_news_to_file(news_data, str(news_file))

    print(f"  → Total news items: {news_data.get('total_items', 0)}")
    print()

    # ========================================
    # Step 2: Generate Content with Claude
    # ========================================
    print("STEP 2: Generating content with Claude...")

    newsletter_file = output_dir / f"newsletter_{date_str}.json"

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("  ❌ ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    newsletter = generate_full_newsletter(news_data, api_key=anthropic_key)
    save_newsletter_content(newsletter, str(newsletter_file))

    print(f"  → Generated {len(newsletter['sections'])} sections")
    print()

    # ========================================
    # Step 3: Generate HTML
    # ========================================
    print("STEP 3: Generating HTML...")

    html_file = output_dir / f"newsletter_{date_str}.html"
    html_content = generate_html(newsletter)
    save_html(html_content, str(html_file))

    print(f"  → HTML size: {len(html_content):,} characters")
    print()

    # ========================================
    # Step 4: Post to Beehiiv
    # ========================================
    print("STEP 4: Posting to Beehiiv...")

    try:
        result = post_to_beehiiv(html_content, dry_run=args.dry_run)
        if not args.dry_run:
            # Save post ID for reference
            with open(output_dir / f"beehiiv_{date_str}.json", 'w') as f:
                json.dump(result, f, indent=2)
    except Exception as e:
        print(f"  ❌ Error posting to Beehiiv: {e}")
        if not args.dry_run:
            sys.exit(1)

    print()
    print("=" * 60)
    print("✅ COMPLETE!")
    print("=" * 60)

    if args.dry_run:
        print("\nDry run complete. Files saved to:")
        print(f"  • News: {news_file}")
        print(f"  • Newsletter: {newsletter_file}")
        print(f"  • HTML: {html_file}")
        print("\nTo post to Beehiiv, run without --dry-run")
    else:
        print("\nNewsletter draft created! Next steps:")
        print("  1. Go to Beehiiv and review the draft")
        print("  2. Make any final edits")
        print("  3. Schedule or send!")


if __name__ == "__main__":
    main()
