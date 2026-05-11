# 🏃 Audio Snippets POC - Runner's Content App

A proof-of-concept for an app that delivers personalized audio content snippets to runners in a "For You" feed format.

## 🎯 What This Does

This POC demonstrates the complete content pipeline:
1. **Fetch** - Get articles from news sources
2. **Summarize** - Convert articles into 60-second audio scripts using Claude
3. **Generate** - Turn scripts into high-quality audio with text-to-speech
4. **Personalize** - Build custom playlists based on user interests

## 📁 Files Included

- **`audio_snippets_demo.py`** - Ready-to-run demo with mock data (NO API KEYS NEEDED)
- **`audio_snippets_poc.py`** - Full production version (requires API keys)
- **`/audio_snippets_demo/`** - Demo output with 5 sample snippets

## 🚀 Quick Start (Demo Version)

The demo works immediately without any setup:

```bash
python3 audio_snippets_demo.py
```

This generates:
- 5 sample snippets across Tech, NBA, Space, Health categories
- Text scripts you can read to evaluate quality
- A sample "For You" playlist
- Metadata JSON files showing the data structure

**Read the generated scripts out loud** to test pacing and tone!

## 🔧 Full Setup (Production Version)

To run the real pipeline with live data:

### 1. Get API Keys (Free Tiers Available)

**NewsAPI** (News articles)
- Sign up: https://newsapi.org/register
- Free tier: 100 requests/day
- Copy your API key

**Anthropic Claude API** (Summarization)
- Get key from: https://console.anthropic.com/
- You already have access if using Claude
- Pricing: ~$0.01-0.03 per snippet

**ElevenLabs** (Text-to-speech)
- Sign up: https://elevenlabs.io/
- Free trial: 10,000 characters (~70 snippets)
- Pricing after: ~$0.27 per snippet

### 2. Update API Keys

Edit `audio_snippets_poc.py`:

```python
NEWS_API_KEY = "your_newsapi_key_here"
ELEVENLABS_API_KEY = "your_elevenlabs_key_here"
```

Note: Claude API key is already configured (no update needed)

### 3. Install Dependencies

```bash
pip install requests --break-system-packages
```

### 4. Run the POC

```bash
python3 audio_snippets_poc.py
```

This will:
- Fetch 10 real articles across 5 categories
- Summarize each with Claude API
- Generate audio files with ElevenLabs
- Create a complete content library

## 📊 Output Structure

```
audio_snippets/
├── manifest.json              # Full catalog of all snippets
├── tech_1_article_title.mp3   # Audio files
├── tech_1_article_title.txt   # Script backups
├── nba_1_game_recap.mp3
└── ...
```

**manifest.json** contains:
```json
{
  "category": "tech",
  "title": "Article Title",
  "source": "TechCrunch",
  "script": "Full 60-second script...",
  "word_count": 155,
  "audio_file": "path/to/file.mp3",
  "timestamp": "2026-04-01T10:30:00"
}
```

## 💰 Cost Breakdown

For a daily batch of 200 snippets (supporting ~1000 users):

| Service | Usage | Cost/Day | Cost/Month |
|---------|-------|----------|------------|
| NewsAPI | 200 articles | Free | $0 |
| Claude API | 200 summaries | $2-6 | $60-180 |
| ElevenLabs | 200 audio files | $54 | $1,620 |
| **Total** | | **~$60** | **~$1,680** |

**With caching** (80% reuse rate):
- Month 1: ~$1,680
- Month 2: ~$400 (only new snippets)
- Month 3: ~$200 (high cache hit rate)

## 🎨 Customization

### Add New Categories

Edit `CATEGORIES` dict in the script:

```python
CATEGORIES = {
    "your_category": ["search query 1", "search query 2"],
    "finance": ["stock market", "crypto news"],
    "gaming": ["video game releases", "esports"]
}
```

### Adjust Script Length

Modify the Claude prompt:

```python
# For 45-second snippets
"Around 120-150 words (reads in ~45 seconds)"

# For 90-second snippets  
"Around 200-250 words (reads in ~90 seconds)"
```

### Change Voice

ElevenLabs voice options:

```python
# Energetic male voice
voice_id = "21m00Tcm4TlvDq8ikWAM"

# Calm female voice
voice_id = "EXAVITQu4vr4xnSDxMaL"

# Professional newscaster
voice_id = "pNInz6obpgDQGcFmaJgB"
```

Browse more at: https://elevenlabs.io/voice-library

## 📱 Next Steps: Building the App

Once you validate the content quality:

1. **Backend** - Flask/FastAPI server
   - Runs daily batch job (this POC script)
   - Stores snippets in S3/CloudFlare R2
   - Serves personalized playlists via API

2. **Mobile App** - React Native
   - User onboarding: interest selection
   - Audio player with auto-advance
   - Offline downloads
   - Skip/replay controls

3. **Personalization** - Simple matching algorithm
   - User selects 5-10 interests
   - Daily feed = 15-20 snippets weighted toward their picks
   - Track skips to improve recommendations

## 🎯 Quality Validation Checklist

Before building the full app, validate:

- [ ] Read 10 scripts out loud - do they sound natural?
- [ ] Time yourself - are they actually ~60 seconds?
- [ ] Play them while running - can you follow along?
- [ ] Check variety - do snippets feel repetitive?
- [ ] Test skipping behavior - are some instantly skippable?
- [ ] Get feedback from 5 runners

## 🐛 Troubleshooting

**"API Error: Unauthorized"**
- Double-check your API keys are correct
- Ensure no extra spaces when copy-pasting

**"Rate limit exceeded"**
- NewsAPI free tier: max 100 requests/day
- Add delays between requests: `time.sleep(2)`

**"Audio sounds robotic"**
- Try different ElevenLabs voices
- Adjust voice settings (stability, similarity_boost)
- Ensure scripts use conversational language

**"Snippets too long/short"**
- Adjust word count target in Claude prompt
- Test reading speed: ~150 words/minute average

## 📈 Scaling Plan

**Month 1** - Validate concept
- Run POC daily, listen to output
- Get 10 beta testers
- Track: completion rate, skips, feedback

**Month 2** - Build MVP  
- Simple mobile app (React Native)
- "For You" feed only
- 100 beta users

**Month 3** - Add features
- Prompt mode ("30 mins of tech news")
- Voice options
- Offline downloads

**Month 4** - Launch
- App Store + Google Play
- Freemium model
- Scale backend infrastructure

## 💡 Ideas for Differentiation

- **Running-specific features**: Auto-pause when heart rate spikes
- **Social**: Share favorite snippets with friends
- **Gamification**: Badges for listening streaks
- **Voice control**: "Hey Claude, skip to space news"
- **Context-aware**: Longer snippets for long runs, shorter for intervals

## 📞 Support

Questions? Feedback? Found a bug?

This is a POC/demo - customize it for your needs!

## 📄 License

MIT License - feel free to use and modify
