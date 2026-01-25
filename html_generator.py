#!/usr/bin/env python3
"""
Beyond Brief - HTML Newsletter Generator

Converts newsletter content into beautiful, email-ready HTML.
"""

import re
from datetime import datetime
from typing import Dict
import markdown


def markdown_to_html(text: str) -> str:
    """Convert markdown text to HTML."""
    # Convert markdown
    html = markdown.markdown(text, extensions=['extra'])

    # Fix links to open in new tab
    html = re.sub(
        r'<a href="([^"]+)">',
        r'<a href="\1" target="_blank" style="color: #2563eb; text-decoration: underline;">',
        html
    )

    return html


def generate_html(newsletter: Dict) -> str:
    """
    Generate full HTML email from newsletter content.

    Args:
        newsletter: Output from ai_writer.generate_full_newsletter()

    Returns:
        Complete HTML string
    """
    sections = newsletter.get("sections", {})
    today = datetime.now()

    # Convert each section from markdown to HTML
    greeting_html = markdown_to_html(sections.get("greeting", ""))
    top_story_html = markdown_to_html(sections.get("top_story", ""))
    news_html = markdown_to_html(sections.get("in_the_news", ""))
    ai_watch_html = markdown_to_html(sections.get("ai_watch", ""))
    tool_html = markdown_to_html(sections.get("tool_of_day", ""))
    quick_hits_html = markdown_to_html(sections.get("quick_hits", ""))
    founder_html = markdown_to_html(sections.get("founder_insight", ""))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Beyond Brief - {today.strftime("%B %d, %Y")}</title>
    <style>
        /* Reset */
        body, html {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #1a1a1a;
            background-color: #f5f5f5;
        }}

        /* Container */
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
        }}

        /* Header */
        .header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
            color: white;
            padding: 30px 40px;
            text-align: center;
        }}

        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}

        .header .date {{
            margin-top: 8px;
            font-size: 14px;
            opacity: 0.9;
        }}

        /* Content */
        .content {{
            padding: 30px 40px;
        }}

        /* Greeting */
        .greeting {{
            font-size: 17px;
            color: #333;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}

        /* Section */
        .section {{
            margin-bottom: 35px;
        }}

        .section-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}

        .section-emoji {{
            font-size: 20px;
            margin-right: 10px;
        }}

        .section-title {{
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #666;
        }}

        /* Story content */
        .story-content {{
            font-size: 16px;
            color: #333;
        }}

        .story-content p {{
            margin: 0 0 15px 0;
        }}

        .story-content strong {{
            color: #1a1a1a;
        }}

        .story-content a {{
            color: #2563eb;
            text-decoration: underline;
        }}

        /* Quick hits */
        .quick-hits ul {{
            padding-left: 0;
            list-style: none;
        }}

        .quick-hits li {{
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
            font-size: 15px;
        }}

        .quick-hits li:last-child {{
            border-bottom: none;
        }}

        .quick-hits li::before {{
            content: "→ ";
            color: #2563eb;
            font-weight: bold;
        }}

        /* Divider */
        .divider {{
            height: 1px;
            background: linear-gradient(90deg, transparent, #ddd, transparent);
            margin: 30px 0;
        }}

        /* Footer */
        .footer {{
            background-color: #f8f9fa;
            padding: 30px 40px;
            text-align: center;
            font-size: 13px;
            color: #666;
        }}

        .footer a {{
            color: #2563eb;
        }}

        .social-links {{
            margin: 15px 0;
        }}

        .social-links a {{
            display: inline-block;
            margin: 0 10px;
            color: #666;
            text-decoration: none;
        }}

        /* Responsive */
        @media (max-width: 640px) {{
            .header, .content, .footer {{
                padding: 20px;
            }}

            .header h1 {{
                font-size: 24px;
            }}

            .story-content {{
                font-size: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Beyond Brief</h1>
            <div class="date">{today.strftime("%A, %B %d, %Y")}</div>
        </div>

        <!-- Content -->
        <div class="content">
            <!-- Greeting -->
            <div class="greeting">
                {greeting_html}
            </div>

            <!-- Top Story -->
            <div class="section">
                <div class="section-header">
                    <span class="section-emoji">🔥</span>
                    <span class="section-title">Top Story</span>
                </div>
                <div class="story-content">
                    {top_story_html}
                </div>
            </div>

            <div class="divider"></div>

            <!-- In The News -->
            <div class="section">
                <div class="section-header">
                    <span class="section-emoji">📰</span>
                    <span class="section-title">In The News</span>
                </div>
                <div class="story-content">
                    {news_html}
                </div>
            </div>

            <div class="divider"></div>

            <!-- AI Watch -->
            <div class="section">
                <div class="section-header">
                    <span class="section-emoji">🤖</span>
                    <span class="section-title">AI Watch</span>
                </div>
                <div class="story-content">
                    {ai_watch_html}
                </div>
            </div>

            <div class="divider"></div>

            <!-- Tool of the Day -->
            <div class="section">
                <div class="section-header">
                    <span class="section-emoji">🛠️</span>
                    <span class="section-title">Tool of the Day</span>
                </div>
                <div class="story-content">
                    {tool_html}
                </div>
            </div>

            <div class="divider"></div>

            <!-- Quick Hits -->
            <div class="section quick-hits">
                <div class="section-header">
                    <span class="section-emoji">⚡</span>
                    <span class="section-title">Quick Hits</span>
                </div>
                <div class="story-content">
                    {quick_hits_html}
                </div>
            </div>

            <div class="divider"></div>

            <!-- Founder Insight -->
            <div class="section">
                <div class="section-header">
                    <span class="section-emoji">💡</span>
                    <span class="section-title">Founder Insight</span>
                </div>
                <div class="story-content">
                    {founder_html}
                </div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p><strong>Beyond Brief</strong> - Your daily dose of what matters</p>
            <p>
                <a href="{{{{unsubscribe_url}}}}">Unsubscribe</a> •
                <a href="{{{{preferences_url}}}}">Update preferences</a>
            </p>
            <p style="margin-top: 20px; font-size: 11px; color: #999;">
                © {today.year} Beyond Brief. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>"""

    return html


def save_html(html: str, filepath: str):
    """Save HTML to file."""
    with open(filepath, 'w') as f:
        f.write(html)
    print(f"Saved HTML to {filepath}")


# Example usage
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            newsletter = json.load(f)

        html = generate_html(newsletter)

        if len(sys.argv) > 2:
            save_html(html, sys.argv[2])
        else:
            print(html)
    else:
        print("Usage: python html_generator.py <newsletter.json> [output.html]")
