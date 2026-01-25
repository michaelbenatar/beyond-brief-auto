# Beyond Brief - Automated Newsletter

A fully automated daily newsletter system that fetches news, writes content using Claude AI, and posts to Beehiiv.

## How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   News Fetch    │────▶│  Claude AI      │────▶│  HTML Generate  │────▶│  Beehiiv Post   │
│  (RSS + APIs)   │     │  (Content)      │     │  (Email Ready)  │     │  (Draft)        │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

Every morning at 6 AM:
1. **Fetches** latest news from RSS feeds, NewsAPI, and web sources
2. **Generates** punchy, Morning Brew-style content using Claude
3. **Creates** beautiful HTML email template
4. **Posts** draft to Beehiiv for your review

## Quick Setup (5 minutes)

### 1. Fork this repo

Click "Fork" in the top right of this GitHub page.

### 2. Add your API keys as GitHub Secrets

Go to your repo → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Required | Get it from |
|-------------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ Yes | [console.anthropic.com](https://console.anthropic.com/) |
| `BEEHIIV_API_KEY` | ✅ Yes | Beehiiv → Settings → API |
| `BEEHIIV_PUBLICATION_ID` | ✅ Yes | Beehiiv URL: `app.beehiiv.com/publications/pub_xxx` |
| `NEWSAPI_KEY` | Optional | [newsapi.org](https://newsapi.org/) (free tier) |

### 3. Enable GitHub Actions

Go to Actions tab → Click "I understand my workflows, go ahead and enable them"

### 4. Test it!

Actions → Daily Newsletter → Run workflow → Run workflow

Done! Check Beehiiv for your draft.

## Configuration

### Change the schedule

Edit `.github/workflows/daily-newsletter.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'  # 6 AM UTC daily
```

Common schedules:
- `0 6 * * 1-5` - Weekdays only at 6 AM
- `0 14 * * *` - 2 PM UTC (6 AM PST)
- `0 11 * * *` - 11 AM UTC (6 AM EST)

### Customize the writing style

Edit `ai_writer.py` → `SYSTEM_PROMPT` to change the tone and style.

### Add/remove news sources

Edit `news_fetcher.py` → `RSS_FEEDS` dictionary.

## Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/beyond-brief-auto
cd beyond-brief-auto

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="your-key"
export BEEHIIV_API_KEY="your-key"
export BEEHIIV_PUBLICATION_ID="pub_xxx"

# Run (dry run - no Beehiiv post)
python main.py --dry-run

# Run for real
python main.py
```

## Files

```
beyond-brief-auto/
├── main.py              # Entry point - orchestrates everything
├── news_fetcher.py      # Fetches from RSS, NewsAPI, DuckDuckGo
├── ai_writer.py         # Claude API content generation
├── html_generator.py    # Converts to email-ready HTML
├── requirements.txt     # Python dependencies
├── README.md            # You are here
└── .github/
    └── workflows/
        └── daily-newsletter.yml  # GitHub Actions automation
```

## Cost Estimate

| Service | Cost |
|---------|------|
| Claude API | ~$0.10-0.30 per newsletter |
| GitHub Actions | Free (2000 min/month) |
| NewsAPI | Free tier (100 req/day) |
| **Total** | **~$3-9/month** |

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
Make sure you added the secret in GitHub → Settings → Secrets → Actions

### "Beehiiv 401 error"
Check your Beehiiv API key is correct. Note: Some features require Enterprise plan.

### "No news items found"
RSS feeds might be temporarily unavailable. The workflow will retry next day.

### Workflow not running
Go to Actions tab and ensure workflows are enabled for your fork.

## License

MIT - Do whatever you want with it.

---

Built with Claude AI 🤖
