# Diversity Penalty - Code Examples

## Quick Start

```python
from recommender import load_songs, recommend_songs, get_strategy

# Load songs
songs = load_songs("data/songs.csv")

# Define user preferences
user_profile = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.80,
    "likes_acoustic": False
}

# Enable diversity penalty (default configuration)
diversity_config = {
    'enabled': True,
    'artist_penalty': 0.15,
    'genre_penalty': 0.10,
    'max_same_artist': 1,
    'max_same_genre': 2
}

# Get recommendations with diversity enforcement
recommendations = recommend_songs(
    user_profile, 
    songs, 
    k=10,
    strategy=get_strategy("balanced"),
    diversity_penalty=diversity_config
)

# Display results
for i, (song, score, explanation) in enumerate(recommendations, 1):
    print(f"{i}. {song['title']} by {song['artist']} ({score:.2f})")
    print(f"   {explanation}\n")
```

---

## Example 1: Playlist Generation with Diversity

**Use Case:** Create a 30-song workout playlist

```python
# Fitness playlist - want variety but high energy
fitness_profile = {
    "favorite_genre": "electronic",
    "favorite_mood": "energetic",
    "target_energy": 0.90,
    "likes_acoustic": False,
    "preferred_mood_tags": ["energetic", "powerful"]
}

# Prevent artist repetition (each artist only once)
fitness_diversity = {
    'enabled': True,
    'artist_penalty': 0.20,
    'genre_penalty': 0.10,
    'max_same_artist': 1,      # Only 1 song per artist
    'max_same_genre': 3         # OK with multiple electronic songs
}

playlist = recommend_songs(
    fitness_profile,
    songs,
    k=30,
    strategy=get_strategy("energy-focused"),
    diversity_penalty=fitness_diversity
)

print(f"Generated {len(playlist)} workout songs")
print(f"Artists: {len(set(song['artist'] for song, _, _ in playlist))}")
```

---

## Example 2: Music Discovery Mode

**Use Case:** Introduce user to new artists

```python
# Discovery mode - strict diversity
discovery_profile = {
    "favorite_genre": "indie",
    "target_energy": 0.65,
    "likes_acoustic": True
}

# Maximum diversity - force exploration
discovery_diversity = {
    'enabled': True,
    'artist_penalty': 0.30,     # Heavy penalty
    'genre_penalty': 0.20,      # Heavy penalty
    'max_same_artist': 0,       # ZERO tolerance
    'max_same_genre': 1         # Only 1 per genre
}

discovery_list = recommend_songs(
    discovery_profile,
    songs,
    k=15,
    strategy=get_strategy("niche-seeker"),
    diversity_penalty=discovery_diversity
)

print("New Artists to Discover:")
for i, (song, _, _) in enumerate(discovery_list, 1):
    print(f"{i}. {song['artist']} - {song['title']}")
```

---

## Example 3: Favorite Artist with Variety

**Use Case:** Recommend songs from favorite artist + similar artists

```python
# User loves "Neon Echo" but wants some variety
artist_fan_profile = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.80,
    "likes_acoustic": False
}

# Allow multiple songs from favorite artist, but also mix in others
fan_diversity = {
    'enabled': True,
    'artist_penalty': 0.10,     # Lenient penalty
    'genre_penalty': 0.05,
    'max_same_artist': 3,       # Allow up to 3 from same artist
    'max_same_genre': 4         # Allow many from same genre
}

recommendations = recommend_songs(
    artist_fan_profile,
    songs,
    k=20,
    strategy=get_strategy("balanced"),
    diversity_penalty=fan_diversity
)

# Count Neon Echo songs
neon_echo_count = sum(1 for song, _, _ in recommendations 
                      if song['artist'] == 'Neon Echo')
print(f"Neon Echo songs: {neon_echo_count}/20")
```

---

## Example 4: Comparing Settings

**Use Case:** Show impact of different diversity settings

```python
songs = load_songs("data/songs.csv")
profile = {
    "favorite_genre": "electronic",
    "favorite_mood": "energetic",
    "target_energy": 0.85,
    "likes_acoustic": False
}

# Test different configurations
configs = {
    "No Diversity": {
        'enabled': False
    },
    "Lenient": {
        'enabled': True,
        'artist_penalty': 0.10,
        'genre_penalty': 0.05,
        'max_same_artist': 3,
        'max_same_genre': 4
    },
    "Recommended": {
        'enabled': True,
        'artist_penalty': 0.15,
        'genre_penalty': 0.10,
        'max_same_artist': 1,
        'max_same_genre': 2
    },
    "Strict": {
        'enabled': True,
        'artist_penalty': 0.25,
        'genre_penalty': 0.15,
        'max_same_artist': 0,
        'max_same_genre': 1
    }
}

print(f"{'Config':<20} {'Artists':<12} {'Genres':<12} {'Top Artist':<20}")
print("-" * 65)

for config_name, config in configs.items():
    recs = recommend_songs(
        profile, songs, k=10,
        strategy=get_strategy("balanced"),
        diversity_penalty=config
    )
    
    artists = set(song['artist'] for song, _, _ in recs)
    genres = set(song['genre'] for song, _, _ in recs)
    top_artist = max(
        {song['artist']: sum(1 for s, _, _ in recs if s['artist'] == song['artist'])
         for song, _, _ in recs}.items(),
        key=lambda x: x[1]
    )[0]
    top_count = max(
        {song['artist']: sum(1 for s, _, _ in recs if s['artist'] == song['artist'])
         for song, _, _ in recs}.items(),
        key=lambda x: x[1]
    )[1]
    
    print(f"{config_name:<20} {len(artists):<12} {len(genres):<12} "
          f"{top_artist} ({top_count}x)")
```

---

## Example 5: Dynamic Configuration

**Use Case:** Adjust diversity based on context

```python
from recommender import load_songs, recommend_songs, get_strategy

def get_playlist(profile, context="normal", k=10):
    """
    Generate playlist with context-aware diversity settings.
    
    Contexts:
    - 'workout': High energy, maximum diversity of artists
    - 'chill': Relaxed, allow more artist repetition
    - 'discovery': New music, strict diversity
    - 'normal': Balanced approach
    """
    
    diversity_configs = {
        'workout': {
            'enabled': True,
            'artist_penalty': 0.25,
            'genre_penalty': 0.15,
            'max_same_artist': 1,
            'max_same_genre': 2
        },
        'chill': {
            'enabled': True,
            'artist_penalty': 0.10,
            'genre_penalty': 0.05,
            'max_same_artist': 3,
            'max_same_genre': 4
        },
        'discovery': {
            'enabled': True,
            'artist_penalty': 0.30,
            'genre_penalty': 0.20,
            'max_same_artist': 0,
            'max_same_genre': 1
        },
        'normal': {
            'enabled': True,
            'artist_penalty': 0.15,
            'genre_penalty': 0.10,
            'max_same_artist': 1,
            'max_same_genre': 2
        }
    }
    
    songs = load_songs("data/songs.csv")
    config = diversity_configs.get(context, diversity_configs['normal'])
    
    return recommend_songs(
        profile, songs, k=k,
        strategy=get_strategy("balanced"),
        diversity_penalty=config
    )

# Usage
workout_profile = {
    "favorite_genre": "electronic",
    "target_energy": 0.95,
    "likes_acoustic": False
}

# Get recommendations with context
workout_playlist = get_playlist(workout_profile, context="workout", k=20)
chill_playlist = get_playlist(workout_profile, context="chill", k=10)
discovery_playlist = get_playlist(workout_profile, context="discovery", k=15)

print(f"Workout: {len(set(s['artist'] for s, _, _ in workout_playlist))} artists")
print(f"Chill: {len(set(s['artist'] for s, _, _ in chill_playlist))} artists")
print(f"Discovery: {len(set(s['artist'] for s, _, _ in discovery_playlist))} artists")
```

---

## Example 6: Examining Penalty Details

**Use Case:** Debug and understand penalty application

```python
songs = load_songs("data/songs.csv")
profile = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.80,
    "likes_acoustic": False
}

# Get recommendations
recs = recommend_songs(
    profile, songs, k=20,
    diversity_penalty={
        'enabled': True,
        'artist_penalty': 0.15,
        'genre_penalty': 0.10,
        'max_same_artist': 1,
        'max_same_genre': 2
    }
)

# Analyze penalties
print("PENALTY ANALYSIS\n")
print(f"{'Rank':<5} {'Song':<25} {'Artist':<15} {'Base Score':<12} {'Penalties':<15}")
print("-" * 75)

for i, (song, final_score, explanation) in enumerate(recs, 1):
    # Extract penalty info from explanation
    has_penalty = "penalty" in explanation.lower()
    penalty_info = "None"
    
    if "artist penalty" in explanation.lower():
        penalty_info = "[Artist: -X]"
    if "genre penalty" in explanation.lower():
        if penalty_info == "None":
            penalty_info = "[Genre: -X]"
        else:
            penalty_info += " [Genre: -X]"
    
    print(f"{i:<5} {song['title']:<25} {song['artist']:<15} "
          f"{final_score:<12.2f} {penalty_info:<15}")

# Show artist distribution
print("\n\nARTIST DISTRIBUTION:")
artist_counts = {}
for song, _, _ in recs:
    artist = song['artist']
    artist_counts[artist] = artist_counts.get(artist, 0) + 1

for artist, count in sorted(artist_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {artist}: {count} song(s)")
```

---

## Example 7: Testing Different Strategies with Diversity

**Use Case:** Compare how different strategies interact with diversity penalties

```python
songs = load_songs("data/songs.csv")
profile = {
    "favorite_genre": "electronic",
    "favorite_mood": "energetic",
    "target_energy": 0.88,
    "preferred_mood_tags": ["energetic", "euphoric"]
}

diversity_config = {
    'enabled': True,
    'artist_penalty': 0.15,
    'genre_penalty': 0.10,
    'max_same_artist': 1,
    'max_same_genre': 2
}

strategies = ['genre-first', 'mood-first', 'energy-focused', 
              'balanced', 'popularity-aware', 'niche-seeker']

print(f"{'Strategy':<20} {'#Artists':<12} {'#Genres':<12} {'Avg Score':<12}")
print("-" * 57)

for strategy_name in strategies:
    recs = recommend_songs(
        profile, songs, k=10,
        strategy=get_strategy(strategy_name),
        diversity_penalty=diversity_config
    )
    
    artists = set(song['artist'] for song, _, _ in recs)
    genres = set(song['genre'] for song, _, _ in recs)
    avg_score = sum(score for _, score, _ in recs) / len(recs)
    
    print(f"{strategy_name:<20} {len(artists):<12} {len(genres):<12} {avg_score:<12.2f}")
```

---

## Example 8: Handling Edge Cases

**Use Case:** Gracefully handle limiting factors

```python
songs = load_songs("data/songs.csv")  # 20 songs in demo
profile = {
    "favorite_genre": "jazz",
    "target_energy": 0.4,
    "likes_acoustic": True
}

# Request more recommendations than unique artists available
k = 15

recs = recommend_songs(
    profile, songs, k=k,
    diversity_penalty={
        'enabled': True,
        'artist_penalty': 0.15,
        'genre_penalty': 0.10,
        'max_same_artist': 1,
        'max_same_genre': 1
    }
)

print(f"Requested: {k} songs")
print(f"Returned: {len(recs)} songs")
print(f"Unique artists: {len(set(song['artist'] for song, _, _ in recs))}")
print(f"Unique genres: {len(set(song['genre'] for song, _, _ in recs))}")

# If fewer than k songs are available that meet constraints,
# the algorithm returns all it can find
if len(recs) < k:
    print(f"\nNote: Only {len(recs)} songs available with current constraints")
    print("This is expected when dataset is small or constraints are very strict")
```

---

## Running the Tests

Execute the full demonstration:

```bash
cd ai110-module3show-musicrecommendersimulation-starter
python src/main.py
```

This runs all demo scenarios including the three diversity penalty demonstrations:
- Scenario 1: Recommended settings
- Scenario 2: No penalty (baseline)
- Scenario 3: Strict enforcement

---

## Tips & Best Practices

1. **Start with Recommended Settings**
   - `max_same_artist=1, max_same_genre=2`
   - Works well for most scenarios

2. **Monitor Explanation Strings**
   - Penalty details appear in the explanation
   - Helpful for debugging configuration

3. **Test Before Deploying**
   - Run comparisons with and without penalties
   - Ensure quality scores remain acceptable

4. **Adjust Incrementally**
   - Small changes to penalties
   - Test impact before larger changes

5. **Consider Dataset Size**
   - Smaller datasets need lenient settings
   - Larger catalogs can use strict settings

6. **Balance Quality vs. Diversity**
   - High penalties can exclude good songs
   - Find sweet spot for your use case
