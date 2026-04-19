"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "="*70)
    print("🎵  TOP MUSIC RECOMMENDATIONS")
    print("="*70 + "\n")
    
    for i, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        max_score = 4.5
        
        # Format output with clean alignment
        print(f"#{i} | {song['title']}")
        print(f"    Artist: {song['artist']}")
        print(f"    Score: {score:.2f} / {max_score:.2f}")
        print(f"    Reasons: {explanation}")
        print()


if __name__ == "__main__":
    main()
