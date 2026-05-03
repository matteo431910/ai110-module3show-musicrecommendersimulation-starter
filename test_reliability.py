"""
Quick test of the reliability scoring implementation
"""
import sys
sys.path.insert(0, 'src')

from recommender import load_songs, recommend_songs_with_reliability, get_strategy

# Load songs
print("Loading songs...")
songs = load_songs("data/songs.csv")
print(f"✓ Loaded {len(songs)} songs\n")

# Test profile
test_profile = {
    'favorite_genre': 'pop',
    'favorite_mood': 'happy',
    'target_energy': 0.8,
    'likes_acoustic': False
}

print(f"Test Profile: {test_profile}\n")

# Get recommendations with reliability scoring
print("Getting recommendations with reliability scoring...")
recommendations, critique = recommend_songs_with_reliability(
    test_profile,
    songs,
    k=5,
    strategy=get_strategy("balanced"),
    enable_reliability=True
)

print(f"✓ Got {len(recommendations)} recommendations\n")

# Display results
print("="*100)
print("RECOMMENDATIONS WITH RELIABILITY".center(100))
print("="*100)

for rank, rec in enumerate(recommendations, 1):
    print(f"\n#{rank}. {rec.song['title']} by {rec.song['artist']}")
    print(f"   Genre: {rec.song['genre']} | Score: {rec.score:.2f}")
    print(f"   Reliability: {rec.confidence_label} ({rec.reliability:.2f})")
    print(f"   Explanation: {rec.explanation}")
    
    if rec.reliability_reasons:
        print(f"   Reliability Factors:")
        for reason in rec.reliability_reasons[:3]:  # Show first 3
            print(f"     • {reason}")

# Show critique
if critique:
    print("\n" + "="*100)
    print("SYSTEM CRITIQUE".center(100))
    print("="*100)
    print(f"\nDiversity Score: {int(critique['diversity_score']*100)}%")
    
    if critique['critique_flags']:
        print(f"\nIssues Detected:")
        for flag in critique['critique_flags']:
            print(f"  - {flag}")
    
    if critique['bias_warnings']:
        print(f"\nBias Warnings:")
        for warning in critique['bias_warnings']:
            print(f"  - {warning}")
    
    print(f"\nStrategy: {critique['strategy_alignment']}")

print("\n✓ Test completed successfully!")
