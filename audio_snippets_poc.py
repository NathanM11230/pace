#!/usr/bin/env python3
"""
Audio Snippets POC - Runner's Content App
Demonstrates the full pipeline: Fetch -> Summarize -> Audio Generation
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

# Configuration
NEWS_API_KEY = "demo"  # Using demo key for POC - you'll need a real key from newsapi.org
ELEVENLABS_API_KEY = "your_elevenlabs_key_here"  # Get free trial from elevenlabs.io
OUTPUT_DIR = Path("/home/claude/audio_snippets")

# Interest categories and their search queries
CATEGORIES = {
    "tech": ["artificial intelligence", "technology startups", "new gadgets"],
    "nba": ["NBA basketball", "Cleveland Cavaliers"],
    "space": ["space exploration", "NASA", "SpaceX"],
    "health": ["fitness", "health research", "nutrition"],
    "ai": ["machine learning", "ChatGPT", "AI"]
}


def fetch_articles(category, query, max_articles=2):
    """Fetch recent articles from NewsAPI"""
    print(f"\n📰 Fetching articles for '{query}'...")
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_articles
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "ok":
            articles = data.get("articles", [])
            print(f"   ✓ Found {len(articles)} articles")
            return articles
        else:
            print(f"   ✗ API Error: {data.get('message', 'Unknown error')}")
            return []
    except Exception as e:
        print(f"   ✗ Error fetching articles: {e}")
        return []


def summarize_with_claude(article):
    """Summarize article using Claude API"""
    title = article.get("title", "")
    description = article.get("description", "")
    content = article.get("content", "")
    
    # Combine available content
    full_text = f"{title}. {description} {content}"
    
    print(f"\n🤖 Summarizing: {title[:60]}...")
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    prompt = f"""Summarize this news article as a 60-second audio snippet for someone running. 

Requirements:
- Conversational, energetic tone
- Around 150-180 words (reads in ~60 seconds)
- Start with a hook, then key details
- No intro like "Here's a story about..." - jump right in
- Write it like you're telling a friend

Article:
{full_text[:1000]}

Write ONLY the audio script, nothing else:"""

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract text from response
        summary = data["content"][0]["text"].strip()
        print(f"   ✓ Generated {len(summary.split())} word summary")
        return summary
    except Exception as e:
        print(f"   ✗ Error summarizing: {e}")
        return None


def generate_audio(text, filename):
    """Generate audio using ElevenLabs API"""
    print(f"\n🎙️  Generating audio: {filename}...")
    
    # Check if we have a valid API key
    if ELEVENLABS_API_KEY == "your_elevenlabs_key_here":
        print("   ⚠️  No ElevenLabs API key - saving text only")
        # Save the text script instead
        text_file = OUTPUT_DIR / f"{filename}.txt"
        text_file.write_text(text)
        print(f"   ✓ Saved script to {text_file}")
        return str(text_file)
    
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Default voice
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save audio file
        audio_file = OUTPUT_DIR / f"{filename}.mp3"
        audio_file.write_bytes(response.content)
        print(f"   ✓ Saved audio to {audio_file}")
        return str(audio_file)
    except Exception as e:
        print(f"   ✗ Error generating audio: {e}")
        # Still save the text
        text_file = OUTPUT_DIR / f"{filename}.txt"
        text_file.write_text(text)
        print(f"   ✓ Saved script to {text_file}")
        return str(text_file)


def create_snippet(article, category, index):
    """Create a complete snippet from article"""
    snippet = {
        "category": category,
        "title": article.get("title", ""),
        "source": article.get("source", {}).get("name", "Unknown"),
        "url": article.get("url", ""),
        "published": article.get("publishedAt", ""),
        "timestamp": datetime.now().isoformat()
    }
    
    # Generate summary
    summary = summarize_with_claude(article)
    if not summary:
        return None
    
    snippet["script"] = summary
    snippet["word_count"] = len(summary.split())
    
    # Generate audio filename
    safe_title = "".join(c for c in article.get("title", "")[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '_')
    filename = f"{category}_{index}_{safe_title}"
    
    # Generate audio
    audio_path = generate_audio(summary, filename)
    snippet["audio_file"] = audio_path
    
    return snippet


def main():
    """Run the POC pipeline"""
    print("=" * 70)
    print("🏃 AUDIO SNIPPETS POC - Content Generation Pipeline")
    print("=" * 70)
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    all_snippets = []
    
    # Process each category
    for category, queries in CATEGORIES.items():
        print(f"\n{'=' * 70}")
        print(f"📂 Category: {category.upper()}")
        print(f"{'=' * 70}")
        
        # Pick first query for POC
        query = queries[0]
        
        # Fetch articles
        articles = fetch_articles(category, query, max_articles=2)
        
        # Create snippets
        for i, article in enumerate(articles, 1):
            snippet = create_snippet(article, category, i)
            if snippet:
                all_snippets.append(snippet)
            
            # Rate limiting - be nice to APIs
            time.sleep(1)
    
    # Save manifest
    manifest_file = OUTPUT_DIR / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(all_snippets, f, indent=2)
    
    # Print summary
    print(f"\n{'=' * 70}")
    print("✅ POC COMPLETE!")
    print(f"{'=' * 70}")
    print(f"\nGenerated {len(all_snippets)} snippets")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Manifest file: {manifest_file}")
    
    # Show snippet breakdown
    print("\n📊 Snippet Breakdown:")
    for snippet in all_snippets:
        print(f"   • {snippet['category'].upper()}: {snippet['title'][:50]}...")
        print(f"     Words: {snippet['word_count']} | Source: {snippet['source']}")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Sign up for NewsAPI at newsapi.org (free tier: 100 requests/day)")
    print(f"   2. Get ElevenLabs trial at elevenlabs.io (10,000 chars free)")
    print(f"   3. Update API keys in this script")
    print(f"   4. Run again to generate actual audio files")
    print(f"   5. Listen and evaluate quality!")
    
    return all_snippets


if __name__ == "__main__":
    snippets = main()
