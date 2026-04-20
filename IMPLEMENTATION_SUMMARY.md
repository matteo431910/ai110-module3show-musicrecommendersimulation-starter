# Music Recommender System - Implementation Summary

## Overview
The Music Recommender System has been enhanced with advanced features including **5 new attributes** and **6 distinct ranking strategies**. This document summarizes all implemented features.

---

## 🎵 Core System Components

### 1. **Enhanced Song Data Model**
Each song now contains the following properties:

**Original Attributes:**
- `title` - Song name
- `artist` - Artist name
- `genre` - Music genre (pop, rock, jazz, lofi, electronic)
- `mood` - Primary mood (happy, relaxed, intense, energetic)
- `energy` - Energy level (0.0 - 1.0)
- `acoustic` - Acousticness boolean

**NEW Attributes:**
1. **`popularity`** (0-100 scale)
   - Represents mainstream appeal/chart position
   - Used for distance-based matching in scoring
   - Example: 85 = very popular, 45 = niche appeal

2. **`release_decade`** (string)
   - Decade of release (e.g., "1980s", "1990s", "2000s", "2010s", "2020s")
   - Allows era-based filtering and matching
   - Supports user preferences for specific decades

3. **`mood_tags`** (list of strings)
   - Fine-grained emotional descriptors
   - Examples: ["uplifting", "euphoric", "energetic", "peaceful", "melancholic"]
   - Enables nuanced mood matching beyond primary mood

4. **`instrumentation`** (string)
   - Production style classification
   - Values: "acoustic", "hybrid", "synthesized", "vocal", "instrumental"
   - Helps match production preferences

5. **`lyrical_depth`** (0.0-1.0 scale)
   - Measure of lyrical sophistication
   - 0.0 = instrumental, 1.0 = poetic/literary lyrics
   - Continuous value for precise preference matching

---

## 📊 Scoring Strategies

The system implements **6 different ranking strategies**, each with unique weighting:

### 1. **Genre-First Strategy** (Max: 5.60)
- **Primary Focus:** Exact genre match
- **Weighting:** Genre (+2.0), Mood (+0.8), Energy (+1.4), Acousticness (+1.4)
- **Best For:** Users who know exactly what genre they want
- **Use Case:** "I want pop music, but I'm flexible on other aspects"

### 2. **Mood-First Strategy** (Max: 6.20)
- **Primary Focus:** Emotional vibe and mood tags
- **Weighting:** Mood (+2.0), Energy (+1.4), Genre (+0.8), All new attributes (+2.0)
- **Best For:** Users prioritizing emotional experience
- **Use Case:** "I want something uplifting and euphoric"

### 3. **Energy-Focused Strategy** (Max: 6.80)
- **Primary Focus:** Energy level matching
- **Weighting:** Energy (+3.0), All components balanced
- **Best For:** Activity-based recommendations
- **Use Case:** "I need high-energy workout music"

### 4. **Balanced Strategy** (Max: 6.40) - **DEFAULT**
- **Primary Focus:** Holistic approach
- **Weighting:** Even distribution across all criteria
- **Best For:** General recommendations, first-time users
- **Use Case:** "Give me well-rounded recommendations"

### 5. **Popularity-Aware Strategy** (Max: 6.20)
- **Primary Focus:** Mainstream/chart appeal
- **Weighting:** Popularity (+1.0), Trend-aligned scores
- **Best For:** Following current hits and trends
- **Use Case:** "Show me what's trending/popular right now"

### 6. **Niche-Seeker Strategy** (Max: 6.60)
- **Primary Focus:** Lesser-known gems and indie appeal
- **Weighting:** Low popularity = bonus (+0.15), discovery focus
- **Best For:** Music enthusiasts seeking hidden gems
- **Use Case:** "Find me unique and underrated songs"

---

## 🎯 User Profile Examples

### Profile 1: Modern Chart-Topper
```python
{
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.85,
    "likes_acoustic": False,
    "popularity_preference": 85,        # NEW: Wants popular/trending
    "preferred_decade": "2020s",        # NEW: Recent music
    "preferred_mood_tags": ["uplifting", "euphoric"],  # NEW: Emotional preferences
}
```
**Expected Results:** Recent, popular pop songs with uplifting vibes (Neon Echo - "Sunrise City", Max Pulse - "Gym Hero")

### Profile 2: Retro Jazz Enthusiast
```python
{
    "favorite_genre": "jazz",
    "favorite_mood": "relaxed",
    "target_energy": 0.35,
    "likes_acoustic": True,
    "popularity_preference": 55,        # NEW: Prefers niche appeal
    "preferred_decades": ["1980s", "1990s", "2000s"],  # NEW: Retro era
    "preferred_instrumentation": ["instrumental", "vocal"],  # NEW: Production style
    "lyrical_depth_preference": 0.7,    # NEW: Deep lyrics
}
```
**Expected Results:** Vintage, acoustic jazz with thoughtful lyrics (Slow Stereo - "Coffee Shop Stories", Folk Wanderers - "Sunset Fields")

### Profile 3: Electronic Music Lover
```python
{
    "favorite_genre": "electronic",
    "favorite_mood": "energetic",
    "target_energy": 0.88,
    "likes_acoustic": False,
    "preferred_mood_tags": ["energetic", "euphoric", "powerful"],  # NEW
    "preferred_instrumentation": ["synthesized", "hybrid"],  # NEW
    "preferred_decade": "2010s",        # NEW
    "popularity_preference": 80,        # NEW
}
```
**Expected Results:** Modern, synth-heavy dance/electronic tracks (Synth Pulse - "Neon Dreams", Electro Masters - "Bass Drop")

---

## 💻 Code Usage Examples

### Basic Usage (Automatic Strategy)
```python
from recommender import load_songs, recommend_songs

songs = load_songs("data/songs.csv")
profile = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.85}

# Uses BalancedStrategy by default
recommendations = recommend_songs(profile, songs, k=5)
for song, score, explanation in recommendations:
    print(f"{song['title']}: {score:.2f}")
```

### Using Specific Strategy
```python
from recommender import load_songs, recommend_songs, get_strategy

songs = load_songs("data/songs.csv")
profile = {"favorite_genre": "pop", ...}
strategy = get_strategy("energy-focused")

recommendations = recommend_songs(profile, songs, k=5, strategy=strategy)
```

### Comparing All Strategies
```python
from recommender import load_songs, recommend_songs, STRATEGIES

songs = load_songs("data/songs.csv")
profile = {"favorite_genre": "jazz", "favorite_mood": "relaxed", ...}

for strategy_name in STRATEGIES.keys():
    strategy = STRATEGIES[strategy_name]
    results = recommend_songs(profile, songs, k=3, strategy=strategy)
    print(f"\n{strategy_name}:")
    for song, score, reason in results:
        print(f"  {song['title']}: {score:.2f}")
```

---

## 📈 Scoring Breakdown Example

**Song:** "Sunrise City" by Neon Echo

**Profile:** Modern Chart-Topper (Popular, Recent, Uplifting)

**Scoring with Balanced Strategy:**
```
Base Components:
  - Genre Match (pop):              +1.0/1.0
  - Mood Match (happy):             +1.0/1.0
  - Energy Proximity (0.85):         +1.88/2.0
  - Acousticness Match (needs no):   +0.5/0.5

New Attributes:
  - Popularity Match (85 target):    +0.50/1.0
  - Decade Match (2020s):            +0.3/0.3
  - Mood Tags Match:                 +0.4/0.4

TOTAL SCORE: 5.58/6.20 (90%)
```

---

## ✅ Testing & Validation

### Test Suites Included:

1. **Standard Profile Testing** - 3 diverse user profiles
2. **Adversarial Profile Testing** - Edge cases and contradictions
3. **Expanded Attribute Demonstration** - All 5 new attributes in action
4. **Strategy Comparison** - Same profile with different strategies
5. **Strategy Switching Examples** - Code patterns for implementation

### Running Tests:
```bash
cd ai110-module3show-musicrecommendersimulation-starter
python src/main.py
```

---

## 🎯 Key Achievements

✅ **Extended Song Model** - 5 new contextual attributes  
✅ **Multiple Strategies** - 6 different ranking philosophies  
✅ **Flexible Scoring** - Distance-based, tag-matching, decade filtering  
✅ **Comprehensive Testing** - Multiple profile types and edge cases  
✅ **Easy Strategy Switching** - Simple API for strategy selection  
✅ **Detailed Explanations** - Every recommendation includes scoring breakdown  
✅ **Scalable Design** - Easy to add more strategies or attributes  

---

## 📚 File Structure

```
ai110-module3show-musicrecommendersimulation-starter/
├── src/
│   ├── main.py                 # Demonstration and testing
│   ├── recommender.py          # Core recommendation engine
│   │   ├── Song Loading
│   │   ├── Strategy Classes
│   │   ├── Scoring Functions
│   │   └── API Functions
│   ├── user_profiles.py        # User profile definitions
│   └── adversarial_profiles.py # Edge cases and special tests
├── data/
│   └── songs.csv              # Song database with all attributes
├── tests/
│   └── test_recommender.py    # Unit tests
├── README.md                  # User guide
├── model_card.md              # Model documentation
└── requirements.txt           # Dependencies
```

---

## 🚀 Future Enhancements

Potential improvements for future iterations:
- Machine learning-based personalization
- Collaborative filtering (user similarity)
- Temporal dynamics (time-of-day recommendations)
- Playlist generation (sequential recommendations)
- User feedback loop (interactive refinement)
- Audio feature analysis (real audio processing)

---

## 📝 Notes

- All strategies maintain backward compatibility with original profiles
- Scores are normalized per-strategy for fair comparison
- Explanations are generated automatically for transparency
- The system gracefully handles missing or ambiguous data
- New strategies can be easily added by extending the `Strategy` base class

---

**Implementation Date:** 2024  
**Status:** ✅ Complete and Tested  
**Version:** 3.0 (Enhanced with Attributes & Strategies)
