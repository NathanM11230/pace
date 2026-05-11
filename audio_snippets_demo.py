#!/usr/bin/env python3
"""
Audio Snippets POC - DEMO VERSION
Works immediately without API keys using mock data
"""

import json
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("/home/claude/audio_snippets_demo")

# Mock articles for demonstration
MOCK_ARTICLES = {
    "tech": [
        {
            "title": "OpenAI Releases New GPT Model with Enhanced Reasoning",
            "description": "OpenAI announced a breakthrough in AI reasoning capabilities with their latest model update.",
            "content": "The new model shows significant improvements in complex problem-solving tasks and mathematical reasoning. Early testers report 40% better performance on coding challenges.",
            "source": {"name": "TechCrunch"},
            "url": "https://example.com/gpt-update",
            "publishedAt": "2026-04-01T08:00:00Z"
        },
        {
            "title": "Apple Vision Pro 2 Leaks Show Major Display Upgrade",
            "description": "Internal documents suggest Apple's next VR headset will feature higher resolution and lighter design.",
            "content": "The upgraded display technology promises 8K per eye resolution while reducing weight by 25%. Launch expected Q4 2026.",
            "source": {"name": "The Verge"},
            "url": "https://example.com/vision-pro-2",
            "publishedAt": "2026-04-01T07:30:00Z"
        }
    ],
    "nba": [
        {
            "title": "Cavaliers Defeat Celtics 118-112 in Overtime Thriller",
            "description": "Cleveland rallies from 15-point deficit to secure crucial playoff seeding win.",
            "content": "Donovan Mitchell scored 38 points including the game-winning three-pointer with 12 seconds remaining in overtime. The win moves Cleveland into the 3rd seed.",
            "source": {"name": "ESPN"},
            "url": "https://example.com/cavs-celtics",
            "publishedAt": "2026-03-31T23:45:00Z"
        }
    ],
    "space": [
        {
            "title": "NASA Discovers Water Ice in Unexpected Lunar Region",
            "description": "Artemis mission data reveals significant water deposits in sunlit crater areas.",
            "content": "The discovery challenges previous assumptions about lunar water distribution. Scientists believe this could support future long-term moon bases with accessible water resources.",
            "source": {"name": "NASA"},
            "url": "https://example.com/lunar-water",
            "publishedAt": "2026-04-01T10:00:00Z"
        }
    ],
    "health": [
        {
            "title": "Study: 10-Minute Workouts Show Same Benefits as Hour-Long Sessions",
            "description": "New research challenges conventional wisdom about exercise duration.",
            "content": "Harvard Medical School study of 50,000 participants found high-intensity 10-minute sessions produced equivalent cardiovascular benefits to traditional hour-long moderate workouts when done 3x daily.",
            "source": {"name": "Health Science Journal"},
            "url": "https://example.com/workout-study",
            "publishedAt": "2026-04-01T06:00:00Z"
        }
    ]
}

# Mock summaries (what Claude API would generate)
MOCK_SUMMARIES = {
    "tech_1": """OpenAI just dropped a major update that's got the tech world buzzing. Their latest GPT model now handles complex reasoning way better than before. We're talking 40 percent improvement on coding challenges. Early testers say it's like having a significantly smarter coding partner. The breakthrough is in how the model breaks down multi-step problems. Instead of jumping to conclusions, it actually works through logic step by step. This could be huge for developers using AI assistants. The update's rolling out now to API users, with the free tier getting access in a few weeks. For anyone building AI-powered apps, this might be the upgrade you've been waiting for.""",
    
    "tech_2": """Apple's worst-kept secret just got more interesting. Leaked internal docs show the Vision Pro 2 is getting a serious display upgrade. We're looking at 8K resolution per eye, which is absolutely wild. But here's the kicker: they're also cutting the weight by 25 percent. That's been the biggest complaint about the current model, that it's too heavy for long sessions. The improved displays plus lighter build could actually make this a mainstream device instead of a tech enthusiast toy. Launch is expected late this year, probably October or November. If they can hit that $2500 price point, this could be the VR headset that finally breaks through.""",
    
    "nba_1": """The Cavs just pulled off an absolute nail-biter against the Celtics. Down 15 points in the third quarter, Cleveland stormed back to force overtime, then Donovan Mitchell put on a clinic. He finished with 38 points and hit the game-winner with just 12 seconds left in OT. The final score: 118 to 112. This wasn't just any win, it bumped the Cavs up to the 3 seed with playoffs right around the corner. Mitchell's been on fire lately, averaging over 30 in his last five games. If they can keep this momentum, Cleveland's looking dangerous heading into the postseason.""",
    
    "space_1": """NASA scientists just made a discovery that could change the future of space exploration. They found water ice on the moon, but not where you'd expect it. Previous missions only found ice in permanently shadowed craters, but this new data from Artemis shows significant water deposits in areas that actually get sunlight. This is huge because it means future moon bases wouldn't need to set up shop in the freezing dark just to access water. The ice could be used for drinking water, oxygen, even rocket fuel. We're talking about making long-term lunar habitats way more practical. The discovery came from new ground-penetrating radar tech that can see beneath the surface.""",
    
    "health_1": """Here's some news that might change your workout routine. A massive Harvard study just challenged everything we thought we knew about exercise duration. Researchers tracked 50,000 people and found that three 10-minute high-intensity sessions throughout the day gave the same cardiovascular benefits as one hour-long moderate workout. Yes, you heard that right. Ten minutes, three times a day. The key is intensity. We're talking heart-pumping, slightly uncomfortable effort, not a casual stroll. For people who say they don't have time to exercise, this basically eliminates that excuse. Morning sprint session, lunchtime bodyweight circuit, evening bike ride. That's your hour, split up and actually more effective."""
}


def create_demo_snippet(article, category, index, summary_key):
    """Create a snippet from mock data"""
    print(f"\n📝 Creating snippet: {article['title'][:50]}...")
    
    snippet = {
        "category": category,
        "title": article["title"],
        "source": article["source"]["name"],
        "url": article["url"],
        "published": article["publishedAt"],
        "timestamp": datetime.now().isoformat(),
        "script": MOCK_SUMMARIES[summary_key],
        "word_count": len(MOCK_SUMMARIES[summary_key].split())
    }
    
    # Save script as text file
    safe_title = "".join(c for c in article["title"][:40] if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '_')
    filename = f"{category}_{index}_{safe_title}"
    
    text_file = OUTPUT_DIR / f"{filename}.txt"
    text_file.write_text(MOCK_SUMMARIES[summary_key])
    snippet["script_file"] = str(text_file)
    
    print(f"   ✓ Generated {snippet['word_count']}-word script")
    print(f"   ✓ Saved to {text_file.name}")
    
    return snippet


def main():
    """Run the demo pipeline"""
    print("=" * 70)
    print("🏃 AUDIO SNIPPETS POC - DEMO VERSION")
    print("=" * 70)
    print("\nThis demo uses mock articles and pre-written summaries")
    print("to show you exactly what the output would look like.\n")
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    all_snippets = []
    summary_keys = {
        "tech": ["tech_1", "tech_2"],
        "nba": ["nba_1"],
        "space": ["space_1"],
        "health": ["health_1"]
    }
    
    # Process each category
    for category, articles in MOCK_ARTICLES.items():
        print(f"\n{'=' * 70}")
        print(f"📂 Category: {category.upper()}")
        print(f"{'=' * 70}")
        
        for i, article in enumerate(articles, 1):
            summary_key = summary_keys[category][i-1]
            snippet = create_demo_snippet(article, category, i, summary_key)
            all_snippets.append(snippet)
    
    # Save manifest
    manifest_file = OUTPUT_DIR / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(all_snippets, f, indent=2)
    
    # Create a sample "For You" playlist
    playlist = {
        "user_interests": ["tech", "nba", "space"],
        "date": datetime.now().date().isoformat(),
        "snippets": [s for s in all_snippets if s["category"] in ["tech", "nba", "space"]]
    }
    
    playlist_file = OUTPUT_DIR / "for_you_playlist.json"
    with open(playlist_file, 'w') as f:
        json.dump(playlist, f, indent=2)
    
    # Print summary
    print(f"\n{'=' * 70}")
    print("✅ DEMO COMPLETE!")
    print(f"{'=' * 70}")
    print(f"\nGenerated {len(all_snippets)} sample snippets")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Show snippet breakdown
    print("\n📊 Generated Snippets:")
    total_words = 0
    for snippet in all_snippets:
        duration = snippet['word_count'] / 150 * 60  # ~150 words per minute
        total_words += snippet['word_count']
        print(f"\n   {snippet['category'].upper()}: {snippet['title'][:55]}")
        print(f"   Source: {snippet['source']} | Words: {snippet['word_count']} | ~{duration:.0f}s")
    
    avg_words = total_words / len(all_snippets)
    avg_duration = avg_words / 150 * 60
    
    print(f"\n📈 Stats:")
    print(f"   Average snippet: {avg_words:.0f} words (~{avg_duration:.0f} seconds)")
    print(f"   Total content: {total_words} words (~{total_words/150:.1f} minutes)")
    
    print(f"\n📱 Sample 'For You' Playlist:")
    print(f"   User interests: Tech, NBA, Space")
    print(f"   Snippets queued: {len(playlist['snippets'])}")
    print(f"   Total listening time: ~{sum(s['word_count'] for s in playlist['snippets'])/150:.1f} minutes")
    
    print(f"\n📄 Files Created:")
    print(f"   • {manifest_file.name} - Full snippet catalog")
    print(f"   • {playlist_file.name} - Sample personalized playlist")
    print(f"   • {len(all_snippets)} .txt files - Individual scripts")
    
    print(f"\n💡 What This Demonstrates:")
    print(f"   ✓ Content variety across categories")
    print(f"   ✓ Conversational, engaging tone")
    print(f"   ✓ 60-second snippet format (~150-180 words)")
    print(f"   ✓ Personalized playlist generation")
    print(f"   ✓ Metadata tracking (source, category, timestamp)")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Read the generated scripts in {OUTPUT_DIR}")
    print(f"   2. Read them out loud to test pacing")
    print(f"   3. Get feedback from runners on tone/content")
    print(f"   4. Once validated, set up real APIs in audio_snippets_poc.py")
    
    return all_snippets


if __name__ == "__main__":
    snippets = main()
