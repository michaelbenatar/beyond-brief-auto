#!/usr/bin/env python3
"""
Notion Poster - Posts newsletter content to a Notion database.

This module handles creating new pages in a Notion database with
the generated newsletter content.
"""

import os
import requests
from datetime import datetime


def post_to_notion(newsletter: dict, html_content: str, dry_run: bool = False) -> dict:
    """
    Post newsletter content to Notion database.

    Args:
        newsletter: The newsletter data with sections
        html_content: The HTML content (for reference)
        dry_run: If True, skip posting

    Returns:
        API response or dry run indicator
    """
    if dry_run:
        print("  → DRY RUN: Skipping Notion post")
        return {"dry_run": True}

    api_key = os.environ.get("NOTION_API_KEY")
    database_id = os.environ.get("NOTION_DATABASE_ID")

    if not api_key or not database_id:
        raise ValueError("NOTION_API_KEY and NOTION_DATABASE_ID required")

    today = datetime.now()
    title = f"Beyond Brief - {today.strftime('%B %d, %Y')}"

    # Build the page content from newsletter sections
    children = []

    # The newsletter format has sections as a dict: {"greeting": "...", "top_story": "..."}
    sections_data = newsletter.get('sections', {})

    # Define section order and their display names
    section_order = [
        ('greeting', '👋 Welcome'),
        ('top_story', '🔥 Top Story'),
        ('in_the_news', '📰 In The News'),
        ('ai_watch', '🤖 AI Watch'),
        ('tool_of_day', '🛠️ Tool of the Day'),
        ('quick_hits', '⚡ Quick Hits'),
        ('founder_insight', '💡 Founder Insight'),
    ]

    # Add each section as Notion blocks
    for section_type, header_text in section_order:
        content = sections_data.get(section_type, '')
        if not content:
            continue

        # Section header
        children.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": header_text}}]
                }
            })

        # Skip the greeting header but keep content
        if section_type == 'greeting':
            children.pop()  # Remove the header we just added

        # Section content - split into paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # Check if it's a bullet point
            if para.startswith('- ') or para.startswith('• '):
                # Add as bulleted list
                items = [line.strip()[2:] for line in para.split('\n') if line.strip().startswith(('- ', '• '))]
                for item in items:
                    children.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": item[:2000]}}]
                        }
                    })
            else:
                # Regular paragraph - Notion has 2000 char limit per block
                if len(para) > 2000:
                    # Split long paragraphs
                    for i in range(0, len(para), 2000):
                        children.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": para[i:i+2000]}}]
                            }
                        })
                else:
                    children.append({
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"type": "text", "text": {"content": para}}]
                        }
                    })

        # Add divider between sections
        children.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })

    # Create the page
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # Build properties - only use title (required)
    # The title property name varies by database (often "Name" or "Title")
    # We'll try to create with minimal properties and let Notion handle defaults
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        },
        "children": children[:100]  # Notion limit: 100 blocks per request
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        error_msg = response.json().get('message', response.text)
        raise Exception(f"Notion API error: {response.status_code} - {error_msg}")

    result = response.json()
    page_id = result.get('id', 'unknown')
    page_url = result.get('url', '')

    print(f"  → Created Notion page: {page_id}")
    print(f"  → View at: {page_url}")

    # If we have more than 100 blocks, append them
    if len(children) > 100:
        append_blocks(api_key, page_id, children[100:])

    return result


def append_blocks(api_key: str, page_id: str, blocks: list):
    """Append additional blocks to a page (for content > 100 blocks)."""
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # Append in batches of 100
    for i in range(0, len(blocks), 100):
        batch = blocks[i:i+100]
        payload = {"children": batch}
        response = requests.patch(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"  ⚠ Warning: Failed to append some blocks: {response.status_code}")


def get_section_header(section_type: str) -> str:
    """Get the display header for a section type."""
    headers = {
        'top_story': '🔥 Top Story',
        'news': '📰 In The News',
        'ai_watch': '🤖 AI Watch',
        'tool': '🛠️ Tool of the Day',
        'quick_hits': '⚡ Quick Hits',
        'insight': '💡 Founder Insight',
        'outro': '👋 Until Tomorrow'
    }
    return headers.get(section_type, '')
