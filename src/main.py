"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs, get_strategy, STRATEGIES
from adversarial_profiles import ADVERSARIAL_PROFILES

# Try to import tabulate for nice tables, fall back to ASCII if not available
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False
    # Simple fallback ASCII table builder
    def tabulate(data, headers=None, tablefmt="simple"):
        if not data:
            return ""
        if headers:
            rows = [headers] + data
        else:
            rows = data
        
        # Calculate column widths
        col_widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]
        
        # Build table
        lines = []
        for i, row in enumerate(rows):
            cells = [str(cell).ljust(width) for cell, width in zip(row, col_widths)]
            lines.append(" | ".join(cells))
            if i == 0 and headers:
                lines.append("-" * len(lines[0]))
        return "\n".join(lines)


# ============================================================================
# TABLE FORMATTING FUNCTIONS
# ============================================================================

def format_reasons_short(explanation, max_length=40):
    """Truncate reasons to fit in table."""
    if len(explanation) <= max_length:
        return explanation
    return explanation[:max_length-3] + "..."


def display_recommendations_table(recommendations, title="Recommendations", 
                                 show_max_score=True, show_reasons=True):
    """
    Display recommendations in a formatted table.
    
    Args:
        recommendations: List of (song, score, explanation) tuples
        title: Table title
        show_max_score: Show "Score/MaxScore" column
        show_reasons: Show reasons/explanation column
    """
    if not recommendations:
        print("No recommendations found.")
        return
    
    print("\n" + "="*100)
    print(title.center(100))
    print("="*100 + "\n")
    
    # Prepare table data
    table_data = []
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        row = []
        row.append(f"#{rank}")
        row.append(song['title'][:30])
        row.append(song['artist'][:20])
        row.append(song['genre'][:12])
        row.append(f"{score:.2f}")
        
        if show_reasons:
            # Truncate explanation to fit nicely
            short_reason = format_reasons_short(explanation, 50)
            row.append(short_reason)
        
        table_data.append(row)
    
    # Build headers
    headers = ["Rank", "Song", "Artist", "Genre", "Score"]
    if show_reasons:
        headers.append("Reasons (Top Factors)")
    
    # Display table
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print()


def display_recommendations_detailed(recommendations, title="Recommendations"):
    """
    Display recommendations in a detailed format with full explanations.
    
    Args:
        recommendations: List of (song, score, explanation) tuples
    """
    if not recommendations:
        print("No recommendations found.")
        return
    
    print("\n" + "="*100)
    print(title.center(100))
    print("="*100 + "\n")
    
    for rank, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"{rank:2d}. {song['title']:<30} by {song['artist']:<20} (Score: {score:.2f})")
        print(f"    Genre: {song['genre']:<15} | Decade: {song.get('release_decade', 'N/A'):<10} | "
              f"Energy: {song.get('energy', 'N/A'):.2f if song.get('energy') is not None else 'N/A'}")
        print(f"    Reasons: {explanation}")
        print()


def display_recommendations_comparison(recommendations_list, strategy_names, title="Strategy Comparison"):
    """
    Compare recommendations from different strategies side-by-side.
    
    Args:
        recommendations_list: List of recommendation lists
        strategy_names: List of strategy names
        title: Comparison title
    """
    print("\n" + "="*120)
    print(title.center(120))
    print("="*120 + "\n")
    
    # Show top 5 from each strategy
    k = 5
    
    for strategy_idx, (strategy_name, recs) in enumerate(zip(strategy_names, recommendations_list)):
        print(f"\n{strategy_idx + 1}. {strategy_name.upper()}")
        print("-" * 100)
        
        table_data = []
        for rank, (song, score, _) in enumerate(recs[:k], 1):
            table_data.append([
                f"#{rank}",
                song['title'][:25],
                song['artist'][:18],
                f"{score:.2f}"
            ])
        
        print(tabulate(table_data, headers=["Rank", "Song", "Artist", "Score"], tablefmt="plain"))


def display_diversity_summary(recommendations, title="Diversity Analysis"):
    """
    Display summary of artist and genre diversity.
    
    Args:
        recommendations: List of (song, score, explanation) tuples
    """
    if not recommendations:
        print("No recommendations to analyze.")
        return
    
    print("\n" + "="*80)
    print(title.center(80))
    print("="*80 + "\n")
    
    artists = [song['artist'] for song, _, _ in recommendations]
    genres = [song['genre'] for song, _, _ in recommendations]
    
    unique_artists = set(artists)
    unique_genres = set(genres)
    
    # Build artist distribution table
    artist_counts = {}
    for artist in artists:
        artist_counts[artist] = artist_counts.get(artist, 0) + 1
    
    genre_counts = {}
    for genre in genres:
        genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    # Summary stats
    summary_data = [
        ["Total Recommendations", len(recommendations)],
        ["Unique Artists", len(unique_artists)],
        ["Unique Genres", len(unique_genres)],
        ["Artist Diversity %", f"{(len(unique_artists) / len(recommendations) * 100):.1f}%"],
        ["Genre Diversity %", f"{(len(unique_genres) / len(recommendations) * 100):.1f}%"],
    ]
    
    print(tabulate(summary_data, headers=["Metric", "Value"], tablefmt="grid"))
    
    # Artist distribution
    print(f"\n{'Artist Distribution':<30}")
    print("-" * 50)
    artist_data = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)
    for artist, count in artist_data:
        bar = "█" * count
        print(f"  {artist:<25} {bar} ({count})")
    
    # Genre distribution
    print(f"\n{'Genre Distribution':<30}")
    print("-" * 50)
    genre_data = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    for genre, count in genre_data:
        bar = "█" * count
        print(f"  {genre:<25} {bar} ({count})")
    
    print()


def display_score_analysis(recommendations, title="Score Analysis"):
    """
    Display statistical analysis of recommendation scores.
    
    Args:
        recommendations: List of (song, score, explanation) tuples
    """
    if not recommendations:
        print("No recommendations to analyze.")
        return
    
    scores = [score for _, score, _ in recommendations]
    
    min_score = min(scores)
    max_score = max(scores)
    avg_score = sum(scores) / len(scores)
    
    print("\n" + "="*60)
    print(title.center(60))
    print("="*60 + "\n")
    
    stats_data = [
        ["Minimum Score", f"{min_score:.2f}"],
        ["Maximum Score", f"{max_score:.2f}"],
        ["Average Score", f"{avg_score:.2f}"],
        ["Range", f"{max_score - min_score:.2f}"],
        ["Total Recommendations", len(recommendations)],
    ]
    
    print(tabulate(stats_data, headers=["Statistic", "Value"], tablefmt="grid"))
    print()


def display_penalties_summary(recommendations, title="Penalty Analysis"):
    """
    Display summary of penalties applied (if any).
    
    Args:
        recommendations: List of (song, score, explanation) tuples
    """
    penalized_songs = []
    penalty_types = {"artist": 0, "genre": 0, "both": 0}
    
    for song, score, explanation in recommendations:
        has_artist_penalty = "artist penalty" in explanation.lower()
        has_genre_penalty = "genre penalty" in explanation.lower()
        
        if has_artist_penalty or has_genre_penalty:
            penalty_type = "both" if (has_artist_penalty and has_genre_penalty) else (
                "artist" if has_artist_penalty else "genre"
            )
            penalty_types[penalty_type] += 1
            penalized_songs.append((song['title'], penalty_type, explanation))
    
    if not penalized_songs:
        print(f"\n[No penalties applied to {len(recommendations)} recommendations]")
        return
    
    print("\n" + "="*100)
    print(title.center(100))
    print("="*100 + "\n")
    
    # Summary
    summary_data = [
        ["Total Penalized", len(penalized_songs)],
        ["Artist Penalties", penalty_types["artist"]],
        ["Genre Penalties", penalty_types["genre"]],
        ["Combined Penalties", penalty_types["both"]],
    ]
    
    print(tabulate(summary_data, headers=["Category", "Count"], tablefmt="grid"))
    
    # Detailed penalties
    print(f"\n{'Penalized Recommendations':<50}")
    print("-" * 100)
    
    penalty_data = []
    for title_str, penalty_type, explanation in penalized_songs:
        short_reason = format_reasons_short(explanation, 60)
        penalty_data.append([title_str[:30], penalty_type.upper(), short_reason])
    
    print(tabulate(penalty_data, headers=["Song", "Type", "Explanation (Summary)"], tablefmt="plain"))
    print()


# ============================================================================


USER_PROFILES = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.4,
        "likes_acoustic": True
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "likes_acoustic": False
    }
}


def test_single_profile(user_prefs, songs, profile_name="User Profile", k=5):
    """Test a single user profile and display results."""
    recommendations = recommend_songs(user_prefs, songs, k=k)

    print("\n" + "="*80)
    print(f"PROFILE: {profile_name}")
    print("="*80)
    print(f"Description: {user_prefs.get('description', 'No description')}")
    print(f"Genre: {user_prefs.get('favorite_genre', 'OPEN')} | Mood: {user_prefs.get('favorite_mood', 'OPEN')}")
    print(f"Energy: {user_prefs.get('target_energy', user_prefs.get('energy', '?')):.2f} | "
          f"Acousticness: {user_prefs.get('target_acousticness', user_prefs.get('likes_acoustic', '?'))}")
    print("-"*80 + "\n")
    
    # Display using new table format
    display_recommendations_table(recommendations, title=f"Top {k} Recommendations for {profile_name}")
    display_score_analysis(recommendations)


def test_adversarial_profiles(songs):
    """Test all adversarial profiles to find edge cases and scoring issues."""
    print("\n\n")
    print("="*80)
    print("ADVERSARIAL & EDGE CASE PROFILE TESTING".center(80))
    print("(Designed to expose scoring logic weaknesses)".center(80))
    print("="*80)
    
    for profile_name, profile_data in ADVERSARIAL_PROFILES.items():
        test_single_profile(profile_data, songs, profile_name=profile_name)


def test_expanded_attributes(songs):
    """Demonstrate the 5 new attributes with example profiles."""
    print("\n\n")
    print("="*80)
    print("EXPANDED ATTRIBUTE SCORING DEMONSTRATION".center(80))
    print("(Popularity, Decade, Mood Tags, Instrumentation, Lyrical Depth)".center(80))
    print("="*80)
    
    # Profile 1: Popularity + Recent Decade + Mood Tags
    profile_1 = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.85,
        "likes_acoustic": False,
        "popularity_preference": 85,
        "preferred_decade": "2020s",
        "preferred_mood_tags": ["uplifting", "euphoric"],
    }
    print("\n" + "="*80)
    print("PROFILE 1: Modern Chart-Topper (with Popularity, Decade, Mood Tags)")
    print("="*80)
    print("Prefers: Pop music from 2020s, popularity ~85, uplifting/euphoric moods")
    print("-"*80)
    recommendations = recommend_songs(profile_1, songs, k=5)
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"\n#{i} | {song['title']:30} (Score: {score:.2f}/6.20)")
        print(f"     Artist: {song['artist']}")
        print(f"     Popularity: {song['popularity']}/100 | Decade: {song['release_decade']} | Tags: {', '.join(song['mood_tags'])}")
        print(f"     Instrumentation: {song['instrumentation']} | Lyrical Depth: {song['lyrical_depth']:.2f}")
        print(f"     Reasons: {explanation}")
    
    # Profile 2: Instrumental + Deep Lyrics + Retro Vibes
    profile_2 = {
        "favorite_genre": "jazz",
        "favorite_mood": "relaxed",
        "target_energy": 0.35,
        "likes_acoustic": True,
        "popularity_preference": 55,
        "preferred_decades": ["1980s", "1990s", "2000s"],
        "preferred_instrumentation": ["instrumental", "vocal"],
        "lyrical_depth_preference": 0.7,
    }
    print("\n\n" + "="*80)
    print("PROFILE 2: Retro Jazz Enthusiast (with Decade, Instrumentation, Lyrical Depth)")
    print("="*80)
    print("Prefers: Jazz/acoustic, 1980s-2000s era, deeper lyrics, lower mainstream popularity")
    print("-"*80)
    recommendations = recommend_songs(profile_2, songs, k=5)
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"\n#{i} | {song['title']:30} (Score: {score:.2f}/6.20)")
        print(f"     Artist: {song['artist']}")
        print(f"     Popularity: {song['popularity']}/100 | Decade: {song['release_decade']} | Tags: {', '.join(song['mood_tags'])}")
        print(f"     Instrumentation: {song['instrumentation']} | Lyrical Depth: {song['lyrical_depth']:.2f}")
        print(f"     Reasons: {explanation}")
    
    # Profile 3: Synthesized Sound + Energetic + Modern
    profile_3 = {
        "favorite_genre": "electronic",
        "favorite_mood": "energetic",
        "target_energy": 0.88,
        "likes_acoustic": False,
        "preferred_mood_tags": ["energetic", "euphoric", "powerful"],
        "preferred_instrumentation": ["synthesized", "hybrid"],
        "preferred_decade": "2010s",
        "popularity_preference": 80,
    }
    print("\n\n" + "="*80)
    print("PROFILE 3: Electronic Music Lover (Mood Tags + Instrumentation + Decade)")
    print("="*80)
    print("Prefers: Electronic/synth, energetic/euphoric moods, 2010s+, high energy")
    print("-"*80)
    recommendations = recommend_songs(profile_3, songs, k=5)
    for i, (song, score, explanation) in enumerate(recommendations, 1):
        print(f"\n#{i} | {song['title']:30} (Score: {score:.2f}/6.20)")
        print(f"     Artist: {song['artist']}")
        print(f"     Popularity: {song['popularity']}/100 | Decade: {song['release_decade']} | Tags: {', '.join(song['mood_tags'])}")
        print(f"     Instrumentation: {song['instrumentation']} | Lyrical Depth: {song['lyrical_depth']:.2f}")
        print(f"     Reasons: {explanation}")
    
    print("\n" + "="*80)
    print("SUCCESS: All 5 New Attributes Integrated!")
    print("  - Popularity: Distance-based scoring preference matching")
    print("  - Release Decade: Flexible decade-list filtering")
    print("  - Mood Tags: Refined emotional preference matching")
    print("  - Instrumentation: Production style filtering")
    print("  - Lyrical Depth: Continuous preference support")
    print("="*80)


def test_strategy_comparison(songs):
    """Compare different ranking strategies on the same profile."""
    print("\n\n")
    print("="*80)
    print("RANKING STRATEGY COMPARISON".center(80))
    print("(See how different strategies rank the same profile differently)".center(80))
    print("="*80)
    
    # Test profile: Someone who likes pop but wants energetic music
    test_profile = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.85,
        "likes_acoustic": False,
        "popularity_preference": 80,
        "preferred_decade": "2020s",
    }
    
    print(f"\nTest Profile: Pop fan, happy mood, high energy (0.85), prefers 2020s, moderate popularity")
    print("-"*80)
    
    # Compare all strategies
    for strategy_name in STRATEGIES.keys():
        print(f"\n>>> {strategy_name.upper()} STRATEGY")
        print("-"*40)
        
        strategy = get_strategy(strategy_name)
        recommendations = recommend_songs(test_profile, songs, k=3, strategy=strategy)
        
        for i, (song, score, explanation) in enumerate(recommendations, 1):
            max_score = strategy.max_possible_score()
            print(f"  #{i} | {song['title']:25} [{score:5.2f}/{max_score:5.2f}] {explanation[:60]}")
    
    print("\n" + "="*80)
    print("KEY OBSERVATIONS:")
    print("  - Genre-First: Prioritizes exact genre match")
    print("  - Mood-First: Emphasizes emotional vibe and mood tags")
    print("  - Energy-Focused: All scores driven by energy level matching")
    print("  - Balanced: Even distribution across all criteria")
    print("  - Popularity-Aware: Favors mainstream, trending music")
    print("  - Niche-Seeker: Rewards lesser-known songs")
    print("="*80)


def test_strategy_switching():
    """Demonstrate easy strategy switching in code."""
    print("\n\n")
    print("="*80)
    print("STRATEGY SWITCHING EXAMPLE (Code Pattern)".center(80))
    print("="*80)
    
    example_code = """
# Easy way to switch strategies in your code:

from recommender import load_songs, recommend_songs, get_strategy

songs = load_songs("data/songs.csv")
profile = {"favorite_genre": "rock", ...}

# Method 1: Use strategy by name
strategy_name = 'energy-focused'
recommendations = recommend_songs(profile, songs, strategy=get_strategy(strategy_name))

# Method 2: Get all available strategies
for strategy_name in ['genre-first', 'mood-first', 'energy-focused', 'balanced']:
    strategy = get_strategy(strategy_name)
    results = recommend_songs(profile, songs, k=5, strategy=strategy)
    print(f"Using {strategy_name}:")
    for song, score, reason in results:
        print(f"  {song['title']}: {score:.2f}")

# Method 3: Default to balanced (if no strategy specified)
results = recommend_songs(profile, songs)  # Uses BalancedStrategy
    """
    
    print(example_code)
    print("="*80)


def test_diversity_penalty(songs):
    """Demonstrate the Diversity Penalty feature preventing artist/genre repetition."""
    print("\n\n")
    print("="*100)
    print("DIVERSITY PENALTY DEMONSTRATION".center(100))
    print("(Prevents too many songs from the same artist or genre)".center(100))
    print("="*100)
    
    # Test Profile: Someone who likes pop
    test_profile = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.80,
        "likes_acoustic": False,
    }
    
    print("\n" + "="*100)
    print("SCENARIO 1: HIGH DIVERSITY (Recommended)")
    print("="*100)
    print("Profile: Pop fan, happy mood, high energy (0.80)")
    print("Diversity Settings: max 1 song per artist, max 2 per genre\n")
    
    diversity_config = {
        'enabled': True,
        'artist_penalty': 0.15,
        'genre_penalty': 0.10,
        'max_same_artist': 1,
        'max_same_genre': 2
    }
    
    recommendations = recommend_songs(test_profile, songs, k=10, 
                                     strategy=get_strategy("balanced"),
                                     diversity_penalty=diversity_config)
    
    display_recommendations_table(recommendations, title="Scenario 1: With Diversity Penalty")
    display_diversity_summary(recommendations)
    
    # Show comparison without diversity penalty
    print("\n" + "="*100)
    print("SCENARIO 2: NO DIVERSITY ENFORCEMENT (No Penalty)")
    print("="*100)
    print("Same profile, but with diversity penalty DISABLED\n")
    
    no_diversity_config = {'enabled': False}
    
    recommendations_no_div = recommend_songs(test_profile, songs, k=10,
                                            strategy=get_strategy("balanced"),
                                            diversity_penalty=no_diversity_config)
    
    display_recommendations_table(recommendations_no_div, title="Scenario 2: Without Diversity Penalty")
    display_diversity_summary(recommendations_no_div)
    
    # SCENARIO 3: More aggressive diversity settings
    print("\n" + "="*100)
    print("SCENARIO 3: STRICT DIVERSITY ENFORCEMENT (max_same_artist=0)")
    print("="*100)
    print("Forcing absolute no-repeat policy on artists\n")
    
    strict_diversity_config = {
        'enabled': True,
        'artist_penalty': 0.25,
        'genre_penalty': 0.15,
        'max_same_artist': 0,
        'max_same_genre': 1
    }
    
    recommendations_strict = recommend_songs(test_profile, songs, k=10,
                                            strategy=get_strategy("balanced"),
                                            diversity_penalty=strict_diversity_config)
    
    display_recommendations_table(recommendations_strict, title="Scenario 3: Strict Diversity (No Artist Repeats)")
    display_diversity_summary(recommendations_strict)
    display_penalties_summary(recommendations_strict, title="Penalty Details - Strict Mode")
    
    # Show all three scenarios side-by-side comparison
    print("\n" + "="*100)
    print("COMPARISON: DIVERSITY SETTINGS IMPACT")
    print("="*100 + "\n")
    print("""HOW IT WORKS:
  1. Recommendations built iteratively (one song at a time)
  2. After each selection:
     - Track how many songs from that artist/genre are selected
     - When building next batch of candidates, penalize songs that would exceed limits
  
  3. ARTIST PENALTY:
     - 1st song from Artist X: No penalty (always allowed)
     - 2nd song from Artist X: -15% score penalty (if max_same_artist=1)
     - 3rd song from Artist X: -30% score penalty (if max_same_artist=1)
     - Pattern: penalty = artist_penalty × (count - max_same_artist)
  
  4. GENRE PENALTY:
     - Up to max_same_genre: No penalty
     - (max_same_genre + 1)th song: -10% score penalty
     - (max_same_genre + 2)th song: -20% score penalty
     - Pattern: penalty = genre_penalty × (count - max_same_genre)
  
CONFIGURATION OPTIONS:
  diversity_penalty = {
      'enabled': True/False,              # Turn feature on/off
      'artist_penalty': 0.15,             # Penalty multiplier per artist violation
      'genre_penalty': 0.10,              # Penalty multiplier per genre violation
      'max_same_artist': 1,               # Max songs from single artist
      'max_same_genre': 2                 # Max songs from single genre
  }
  
BENEFITS:
  [+] More varied listening experience
  [+] Discover different artists/genres
  [+] Prevents playlist dominated by one artist
  [+] Maintains recommendation quality while enforcing diversity
  [+] Penalties are "soft" - high-scoring songs still rank high
""")
    print("="*80)


def main() -> None:
    songs = load_songs("data/songs.csv")
    
    # Option 1: Test standard profiles
    print("\n" + "="*80)
    print("STANDARD PROFILE TESTING".center(80))
    print("="*80)
    
    for profile_name, profile_data in USER_PROFILES.items():
        test_single_profile(profile_data, songs, profile_name=profile_name)
    
    # Option 2: Test adversarial profiles
    test_adversarial_profiles(songs)
    
    # Option 3: Demonstrate expanded attributes
    test_expanded_attributes(songs)
    
    # Option 4: Strategy comparison and switching
    test_strategy_comparison(songs)
    test_strategy_switching()
    
    # Option 5: NEW - Diversity Penalty demonstration
    test_diversity_penalty(songs)


if __name__ == "__main__":
    main()
