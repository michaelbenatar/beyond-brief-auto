# Beyond Brief - Automated Newsletter

Automated daily newsletter that fetches news, writes with Claude AI, and posts to Beehiiv.

## Quick Setup

1. Add secrets in Settings → Secrets → Actions:
2.    - `ANTHROPIC_API_KEY`
      -    - `BEEHIIV_API_KEY`
           -    - `BEEHIIV_PUBLICATION_ID`
            
                - 2. Go to Actions tab and run "Daily Newsletter"
                 
                  3. ## How It Works
                 
                  4. Every day at 6 AM:
                  5. 1. Fetches news from RSS feeds and APIs
                     2. 2. Claude writes Morning Brew-style content
                        3. 3. Creates HTML email
                           4. 4. Posts draft to Beehiiv
                             
                              5. Cost: ~$0.10-0.30 per newsletter
