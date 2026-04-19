from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    
    Reads CSV and converts numerical fields (id, energy, tempo_bpm, valence, 
    danceability, acousticness) to floats/ints for mathematical operations.
    """
    songs = []
    print(f"Loading songs from {csv_path}...")
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert numerical fields
            song = {
                'id': int(row['id']),
                'title': row['title'],
                'artist': row['artist'],
                'genre': row['genre'],
                'mood': row['mood'],
                'energy': float(row['energy']),
                'tempo_bpm': float(row['tempo_bpm']),
                'valence': float(row['valence']),
                'danceability': float(row['danceability']),
                'acousticness': float(row['acousticness'])
            }
            songs.append(song)
    
    print(f"Loaded {len(songs)} songs.")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song by comparing its attributes to user preferences; return (score, reasons)."""
    score = 0.0
    reasons = []
    
    # 1. Genre Match: +2.0 points
    if song['genre'].lower() == user_prefs.get('genre', '').lower():
        score += 2.0
        reasons.append("genre match (+2.0)")
    
    # 2. Mood Match: +1.0 points
    if song['mood'].lower() == user_prefs.get('mood', '').lower():
        score += 1.0
        reasons.append("mood match (+1.0)")
    
    # 3. Energy Similarity: 0.0–1.0 points
    target_energy = user_prefs.get('energy', 0.5)
    energy_diff = abs(song['energy'] - target_energy)
    energy_score = max(0.0, 1.0 - (energy_diff / 0.5))
    if energy_score > 0.0:
        score += energy_score
        reasons.append(f"energy proximity (+{energy_score:.2f})")
    
    # 4. Acousticness Match: +0.5 points
    likes_acoustic = user_prefs.get('likes_acoustic', False)
    song_is_acoustic = song['acousticness'] > 0.6
    
    if (likes_acoustic and song_is_acoustic) or (not likes_acoustic and not song_is_acoustic):
        score += 0.5
        reasons.append("acousticness match (+0.5)")
    
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score and rank all songs; return top k recommendations with scores and explanations."""
    def score_with_explanation(song):
        """Helper: scores a song and formats the explanation."""
        score, reasons = score_song(user_prefs, song)
        explanation = " + ".join(reasons) if reasons else "no matches"
        return (song, score, explanation)
    
    # Pythonic approach: map + sorted + slice
    return sorted(
        map(score_with_explanation, songs),
        key=lambda x: x[1],
        reverse=True
    )[:k]
