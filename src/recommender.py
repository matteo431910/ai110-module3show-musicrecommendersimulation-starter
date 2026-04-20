from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
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
    # NEW ATTRIBUTES
    popularity: float
    release_decade: str
    mood_tags: List[str]
    instrumentation: str
    lyrical_depth: float

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
    # NEW OPTIONAL ATTRIBUTES
    preferred_decade: Optional[str] = None
    preferred_decades: Optional[List[str]] = None
    preferred_mood_tags: Optional[List[str]] = None
    preferred_instrumentation: Optional[List[str]] = None
    popularity_preference: Optional[float] = None


# ============================================================================
# RANKING STRATEGIES (Strategy Pattern Implementation)
# ============================================================================

class RankingStrategy(ABC):
    """Abstract base class defining the interface for ranking strategies."""
    
    @abstractmethod
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Score a song based on user preferences. Return (score, reasons)."""
        pass
    
    @abstractmethod
    def max_possible_score(self) -> float:
        """Return the maximum possible score for this strategy."""
        pass
    
    def get_name(self) -> str:
        """Return strategy name."""
        return self.__class__.__name__


class GenreFirstStrategy(RankingStrategy):
    """Prioritize genre matching above all else. Good for genre-specific listeners."""
    
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        
        # Genre: 2.0 (highest weight)
        favorite_genre = user_prefs.get('favorite_genre') or user_prefs.get('genre')
        if favorite_genre and song['genre'].lower() == favorite_genre.lower():
            score += 2.0
            reasons.append("genre match (+2.0)")
        
        # Mood: 0.8
        favorite_mood = user_prefs.get('favorite_mood') or user_prefs.get('mood')
        if favorite_mood and song['mood'].lower() == favorite_mood.lower():
            score += 0.8
            reasons.append("mood match (+0.8)")
        
        # Energy: 1.5
        target_energy = user_prefs.get('target_energy') or user_prefs.get('energy', 0.5)
        energy_diff = abs(song['energy'] - target_energy)
        energy_score = max(0.0, 1.5 - (energy_diff / 0.25))
        if energy_score > 0.0:
            score += energy_score
            reasons.append(f"energy (+{energy_score:.2f})")
        
        # Acousticness: 0.3
        if 'target_acousticness' in user_prefs:
            target_acousticness = user_prefs['target_acousticness']
            acoustic_diff = abs(song['acousticness'] - target_acousticness)
            acoustic_score = max(0.0, 0.3 - (acoustic_diff / 0.5))
            if acoustic_score > 0.0:
                score += acoustic_score
                reasons.append(f"acoustic (+{acoustic_score:.2f})")
        else:
            likes_acoustic = user_prefs.get('likes_acoustic', False)
            if (likes_acoustic and song['acousticness'] > 0.6) or (not likes_acoustic and song['acousticness'] <= 0.6):
                score += 0.3
                reasons.append("acoustic match (+0.3)")
        
        return score, reasons
    
    def max_possible_score(self) -> float:
        return 5.6


class MoodFirstStrategy(RankingStrategy):
    """Prioritize emotional mood/vibe over genre. Good for mood-based listeners."""
    
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        
        # Mood: 2.0 (highest weight)
        favorite_mood = user_prefs.get('favorite_mood') or user_prefs.get('mood')
        if favorite_mood and song['mood'].lower() == favorite_mood.lower():
            score += 2.0
            reasons.append("mood match (+2.0)")
        
        # Mood Tags: 0.6 (expanded emotional detail)
        preferred_mood_tags = user_prefs.get('preferred_mood_tags')
        if preferred_mood_tags and song.get('mood_tags'):
            song_tags_lower = [tag.lower() for tag in song['mood_tags']]
            for preferred_tag in preferred_mood_tags:
                if preferred_tag.lower() in song_tags_lower:
                    score += 0.6
                    reasons.append("mood tag match (+0.6)")
                    break
        
        # Energy: 1.5
        target_energy = user_prefs.get('target_energy') or user_prefs.get('energy', 0.5)
        energy_diff = abs(song['energy'] - target_energy)
        energy_score = max(0.0, 1.5 - (energy_diff / 0.25))
        if energy_score > 0.0:
            score += energy_score
            reasons.append(f"energy (+{energy_score:.2f})")
        
        # Genre: 0.8
        favorite_genre = user_prefs.get('favorite_genre') or user_prefs.get('genre')
        if favorite_genre and song['genre'].lower() == favorite_genre.lower():
            score += 0.8
            reasons.append("genre match (+0.8)")
        
        # Acousticness: 0.4
        if 'target_acousticness' in user_prefs:
            target_acousticness = user_prefs['target_acousticness']
            acoustic_diff = abs(song['acousticness'] - target_acousticness)
            acoustic_score = max(0.0, 0.4 - (acoustic_diff / 0.5))
            if acoustic_score > 0.0:
                score += acoustic_score
                reasons.append(f"acoustic (+{acoustic_score:.2f})")
        else:
            likes_acoustic = user_prefs.get('likes_acoustic', False)
            if (likes_acoustic and song['acousticness'] > 0.6) or (not likes_acoustic and song['acousticness'] <= 0.6):
                score += 0.4
                reasons.append("acoustic match (+0.4)")
        
        # Popularity & Decade: 0.3 each
        if user_prefs.get('popularity_preference') is not None:
            popularity_preference = user_prefs['popularity_preference']
            popularity_diff = abs(song['popularity'] - popularity_preference)
            popularity_score = max(0.0, 0.3 - (popularity_diff / 20.0))
            if popularity_score > 0.0:
                score += popularity_score
                reasons.append(f"pop (+{popularity_score:.2f})")
        
        preferred_decades = user_prefs.get('preferred_decades') or (
            [user_prefs.get('preferred_decade')] if user_prefs.get('preferred_decade') else None
        )
        if preferred_decades and song['release_decade'] in preferred_decades:
            score += 0.3
            reasons.append("decade match (+0.3)")
        
        # Instrumentation: 0.2
        preferred_instrumentation = user_prefs.get('preferred_instrumentation')
        if preferred_instrumentation and song.get('instrumentation'):
            if song['instrumentation'].lower() in [instr.lower() for instr in preferred_instrumentation]:
                score += 0.2
                reasons.append("instr match (+0.2)")
        
        return score, reasons
    
    def max_possible_score(self) -> float:
        return 6.2


class EnergyFocusedStrategy(RankingStrategy):
    """Prioritize energy level matching. Perfect for workout, focus, or party playlists."""
    
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        
        # Energy: 2.5 (highest weight)
        target_energy = user_prefs.get('target_energy') or user_prefs.get('energy', 0.5)
        energy_diff = abs(song['energy'] - target_energy)
        energy_score = max(0.0, 2.5 - (energy_diff / 0.25))
        if energy_score > 0.0:
            score += energy_score
            reasons.append(f"energy (+{energy_score:.2f})")
        
        # Mood: 1.0
        favorite_mood = user_prefs.get('favorite_mood') or user_prefs.get('mood')
        if favorite_mood and song['mood'].lower() == favorite_mood.lower():
            score += 1.0
            reasons.append("mood match (+1.0)")
        
        # Mood Tags: 0.3
        preferred_mood_tags = user_prefs.get('preferred_mood_tags')
        if preferred_mood_tags and song.get('mood_tags'):
            song_tags_lower = [tag.lower() for tag in song['mood_tags']]
            for preferred_tag in preferred_mood_tags:
                if preferred_tag.lower() in song_tags_lower:
                    score += 0.3
                    reasons.append("mood tag (+0.3)")
                    break
        
        # Genre: 0.5
        favorite_genre = user_prefs.get('favorite_genre') or user_prefs.get('genre')
        if favorite_genre and song['genre'].lower() == favorite_genre.lower():
            score += 0.5
            reasons.append("genre match (+0.5)")
        
        # Popularity: 0.4
        if user_prefs.get('popularity_preference') is not None:
            popularity_preference = user_prefs['popularity_preference']
            popularity_diff = abs(song['popularity'] - popularity_preference)
            popularity_score = max(0.0, 0.4 - (popularity_diff / 20.0))
            if popularity_score > 0.0:
                score += popularity_score
                reasons.append(f"pop (+{popularity_score:.2f})")
        
        # Acousticness: 0.3
        if 'target_acousticness' in user_prefs:
            target_acousticness = user_prefs['target_acousticness']
            acoustic_diff = abs(song['acousticness'] - target_acousticness)
            acoustic_score = max(0.0, 0.3 - (acoustic_diff / 0.5))
            if acoustic_score > 0.0:
                score += acoustic_score
                reasons.append(f"acoustic (+{acoustic_score:.2f})")
        
        # Decade & Instrumentation: 0.2 each
        preferred_decades = user_prefs.get('preferred_decades') or (
            [user_prefs.get('preferred_decade')] if user_prefs.get('preferred_decade') else None
        )
        if preferred_decades and song['release_decade'] in preferred_decades:
            score += 0.2
            reasons.append("decade match (+0.2)")
        
        preferred_instrumentation = user_prefs.get('preferred_instrumentation')
        if preferred_instrumentation and song.get('instrumentation'):
            if song['instrumentation'].lower() in [instr.lower() for instr in preferred_instrumentation]:
                score += 0.2
                reasons.append("instr match (+0.2)")
        
        return score, reasons
    
    def max_possible_score(self) -> float:
        return 5.5


class BalancedStrategy(RankingStrategy):
    """Balanced strategy across all attributes (original default scoring)."""
    
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        
        # Genre Match: 1.0
        favorite_genre = user_prefs.get('favorite_genre') or user_prefs.get('genre')
        if favorite_genre:
            if song['genre'].lower() == favorite_genre.lower():
                score += 1.0
                reasons.append("genre match (+1.0)")
        
        # Mood Match: 1.0
        favorite_mood = user_prefs.get('favorite_mood') or user_prefs.get('mood')
        if favorite_mood:
            if song['mood'].lower() == favorite_mood.lower():
                score += 1.0
                reasons.append("mood match (+1.0)")
        
        # Energy Similarity: 0.0–2.0
        target_energy = user_prefs.get('target_energy') or user_prefs.get('energy', 0.5)
        energy_diff = abs(song['energy'] - target_energy)
        energy_score = max(0.0, 2.0 - (energy_diff / 0.25))
        if energy_score > 0.0:
            score += energy_score
            reasons.append(f"energy proximity (+{energy_score:.2f})")
        
        # Acousticness Match: +0.5
        if 'target_acousticness' in user_prefs:
            target_acousticness = user_prefs['target_acousticness']
            acoustic_diff = abs(song['acousticness'] - target_acousticness)
            acoustic_score = max(0.0, 0.5 - (acoustic_diff / 0.5))
            if acoustic_score > 0.0:
                score += acoustic_score
                reasons.append(f"acousticness proximity (+{acoustic_score:.2f})")
        else:
            likes_acoustic = user_prefs.get('likes_acoustic', False)
            song_is_acoustic = song['acousticness'] > 0.6
            if (likes_acoustic and song_is_acoustic) or (not likes_acoustic and not song_is_acoustic):
                score += 0.5
                reasons.append("acousticness match (+0.5)")
        
        # Popularity Match: +0.5
        if user_prefs.get('popularity_preference') is not None:
            popularity_preference = user_prefs['popularity_preference']
            popularity_diff = abs(song['popularity'] - popularity_preference)
            popularity_score = max(0.0, 0.5 - (popularity_diff / 20.0))
            if popularity_score > 0.0:
                score += popularity_score
                reasons.append(f"popularity match (+{popularity_score:.2f})")
        
        # Decade Match: +0.3
        preferred_decades = user_prefs.get('preferred_decades') or (
            [user_prefs.get('preferred_decade')] if user_prefs.get('preferred_decade') else None
        )
        if preferred_decades:
            if song['release_decade'] in preferred_decades:
                score += 0.3
                reasons.append("decade match (+0.3)")
        
        # Mood Tags Match: +0.4
        preferred_mood_tags = user_prefs.get('preferred_mood_tags')
        if preferred_mood_tags and song.get('mood_tags'):
            song_tags_lower = [tag.lower() for tag in song['mood_tags']]
            for preferred_tag in preferred_mood_tags:
                if preferred_tag.lower() in song_tags_lower:
                    score += 0.4
                    reasons.append("mood tag match (+0.4)")
                    break
        
        # Instrumentation Match: +0.3
        preferred_instrumentation = user_prefs.get('preferred_instrumentation')
        if preferred_instrumentation and song.get('instrumentation'):
            song_instr_lower = song['instrumentation'].lower()
            if song_instr_lower in [instr.lower() for instr in preferred_instrumentation]:
                score += 0.3
                reasons.append("instrumentation match (+0.3)")
        
        # Lyrical Depth Match: +0.2
        if 'lyrical_depth_preference' in user_prefs:
            target_lyrical_depth = user_prefs['lyrical_depth_preference']
            lyrical_diff = abs(song['lyrical_depth'] - target_lyrical_depth)
            lyrical_score = max(0.0, 0.2 * (1.0 - lyrical_diff))
            if lyrical_score > 0.0:
                score += lyrical_score
                reasons.append(f"lyrical depth match (+{lyrical_score:.2f})")
        elif user_prefs.get('prefer_deep_lyrics') is not None:
            prefer_deep_lyrics = user_prefs['prefer_deep_lyrics']
            if prefer_deep_lyrics:
                lyrical_score = 0.2 * song['lyrical_depth']
                if lyrical_score > 0.0:
                    score += lyrical_score
                    reasons.append(f"lyrical depth match (+{lyrical_score:.2f})")
            else:
                if song['lyrical_depth'] < 0.2:
                    lyrical_score = 0.2
                    score += lyrical_score
                    reasons.append(f"instrumental preference match (+{lyrical_score:.2f})")
        
        return score, reasons
    
    def max_possible_score(self) -> float:
        return 6.2


class PopularityAwareStrategy(RankingStrategy):
    """Favor well-known, trending, mainstream music."""
    
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        
        # Popularity: 1.0 (highest priority)
        if user_prefs.get('popularity_preference') is not None:
            popularity_preference = user_prefs['popularity_preference']
            popularity_diff = abs(song['popularity'] - popularity_preference)
            popularity_score = max(0.0, 1.0 - (popularity_diff / 20.0))
            if popularity_score > 0.0:
                score += popularity_score
                reasons.append(f"popularity (+{popularity_score:.2f})")
        else:
            # Assume user likes mainstream (70+ popularity)
            popularity_score = max(0.0, 1.0 - (abs(song['popularity'] - 75) / 20.0))
            score += popularity_score
            reasons.append(f"popularity (+{popularity_score:.2f})")
        
        # Recent Decade: 1.0 (prefer modern music)
        if song['release_decade'] in ['2020s', '2010s']:
            score += 1.0
            reasons.append("recent era (+1.0)")
        elif song['release_decade'] == '2000s':
            score += 0.5
            reasons.append("era match (+0.5)")
        
        # Energy: 1.8
        target_energy = user_prefs.get('target_energy') or user_prefs.get('energy', 0.5)
        energy_diff = abs(song['energy'] - target_energy)
        energy_score = max(0.0, 1.8 - (energy_diff / 0.25))
        if energy_score > 0.0:
            score += energy_score
            reasons.append(f"energy (+{energy_score:.2f})")
        
        # Mood: 1.0
        favorite_mood = user_prefs.get('favorite_mood') or user_prefs.get('mood')
        if favorite_mood and song['mood'].lower() == favorite_mood.lower():
            score += 1.0
            reasons.append("mood match (+1.0)")
        
        # Genre: 0.8
        favorite_genre = user_prefs.get('favorite_genre') or user_prefs.get('genre')
        if favorite_genre and song['genre'].lower() == favorite_genre.lower():
            score += 0.8
            reasons.append("genre match (+0.8)")
        
        # Mood Tags: 0.4
        preferred_mood_tags = user_prefs.get('preferred_mood_tags')
        if preferred_mood_tags and song.get('mood_tags'):
            song_tags_lower = [tag.lower() for tag in song['mood_tags']]
            for preferred_tag in preferred_mood_tags:
                if preferred_tag.lower() in song_tags_lower:
                    score += 0.4
                    reasons.append("mood tag (+0.4)")
                    break
        
        return score, reasons
    
    def max_possible_score(self) -> float:
        return 6.5


class NicheSeekerStrategy(RankingStrategy):
    """Seek out underground, lesser-known music with unique characteristics."""
    
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []
        
        # AVOID Popularity (niche seekers want obscure music)
        # Lower popularity is better
        popularity_score = max(0.0, 1.0 - (song['popularity'] / 100.0))  # Higher score for lower popularity
        score += popularity_score
        reasons.append(f"niche appeal (+{popularity_score:.2f})")
        
        # Genre Match: 1.5 (must be right genre)
        favorite_genre = user_prefs.get('favorite_genre') or user_prefs.get('genre')
        if favorite_genre and song['genre'].lower() == favorite_genre.lower():
            score += 1.5
            reasons.append("genre match (+1.5)")
        
        # Mood Match: 1.5
        favorite_mood = user_prefs.get('favorite_mood') or user_prefs.get('mood')
        if favorite_mood and song['mood'].lower() == favorite_mood.lower():
            score += 1.5
            reasons.append("mood match (+1.5)")
        
        # Instrumentation: 0.8 (production style matters)
        preferred_instrumentation = user_prefs.get('preferred_instrumentation')
        if preferred_instrumentation and song.get('instrumentation'):
            if song['instrumentation'].lower() in [instr.lower() for instr in preferred_instrumentation]:
                score += 0.8
                reasons.append("instrumentation match (+0.8)")
        
        # Lyrical Depth: 0.6 (artist craftsmanship matters)
        if user_prefs.get('lyrical_depth_preference'):
            target_lyrical_depth = user_prefs['lyrical_depth_preference']
            lyrical_diff = abs(song['lyrical_depth'] - target_lyrical_depth)
            lyrical_score = max(0.0, 0.6 * (1.0 - lyrical_diff))
            if lyrical_score > 0.0:
                score += lyrical_score
                reasons.append(f"lyrical depth (+{lyrical_score:.2f})")
        
        # Decade: 0.8 (era authenticity matters)
        preferred_decades = user_prefs.get('preferred_decades') or (
            [user_prefs.get('preferred_decade')] if user_prefs.get('preferred_decade') else None
        )
        if preferred_decades and song['release_decade'] in preferred_decades:
            score += 0.8
            reasons.append("era match (+0.8)")
        
        # Energy: 1.0
        target_energy = user_prefs.get('target_energy') or user_prefs.get('energy', 0.5)
        energy_diff = abs(song['energy'] - target_energy)
        energy_score = max(0.0, 1.0 - (energy_diff / 0.25))
        if energy_score > 0.0:
            score += energy_score
            reasons.append(f"energy (+{energy_score:.2f})")
        
        # Mood Tags: 0.5
        preferred_mood_tags = user_prefs.get('preferred_mood_tags')
        if preferred_mood_tags and song.get('mood_tags'):
            song_tags_lower = [tag.lower() for tag in song['mood_tags']]
            for preferred_tag in preferred_mood_tags:
                if preferred_tag.lower() in song_tags_lower:
                    score += 0.5
                    reasons.append("mood tag (+0.5)")
                    break
        
        # Acousticness: 0.3
        if 'target_acousticness' in user_prefs:
            target_acousticness = user_prefs['target_acousticness']
            acoustic_diff = abs(song['acousticness'] - target_acousticness)
            acoustic_score = max(0.0, 0.3 - (acoustic_diff / 0.5))
            if acoustic_score > 0.0:
                score += acoustic_score
                reasons.append(f"acoustic (+{acoustic_score:.2f})")
        
        return score, reasons
    
    def max_possible_score(self) -> float:
        return 6.6


# Strategy Registry
STRATEGIES = {
    'genre-first': GenreFirstStrategy,
    'mood-first': MoodFirstStrategy,
    'energy-focused': EnergyFocusedStrategy,
    'balanced': BalancedStrategy,
    'popularity-aware': PopularityAwareStrategy,
    'niche-seeker': NicheSeekerStrategy,
}

def get_strategy(strategy_name: str) -> RankingStrategy:
    """Factory function to get a strategy by name."""
    if strategy_name.lower() not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(STRATEGIES.keys())}")
    return STRATEGIES[strategy_name.lower()]()

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
    danceability, acousticness, popularity, lyrical_depth) to floats/ints for 
    mathematical operations. Parses mood_tags as comma-separated list.
    """
    songs = []
    print(f"Loading songs from {csv_path}...")
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert numerical fields and parse mood_tags
            mood_tags_str = row['mood_tags'].strip()
            mood_tags = [tag.strip() for tag in mood_tags_str.split(',') if tag.strip()]
            
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
                'acousticness': float(row['acousticness']),
                # NEW ATTRIBUTES
                'popularity': float(row['popularity']),
                'release_decade': row['release_decade'],
                'mood_tags': mood_tags,
                'instrumentation': row['instrumentation'],
                'lyrical_depth': float(row['lyrical_depth'])
            }
            songs.append(song)
    
    print(f"Loaded {len(songs)} songs.")
    return songs

def score_song(user_prefs: Dict, song: Dict, strategy: RankingStrategy = None) -> Tuple[float, List[str]]:
    """
    Score a song using the specified strategy (or balanced default).
    
    Args:
        user_prefs: User preferences dictionary
        song: Song dictionary
        strategy: RankingStrategy instance (defaults to BalancedStrategy)
    
    Returns:
        Tuple of (score, reasons)
    """
    if strategy is None:
        strategy = BalancedStrategy()
    return strategy.score_song(user_prefs, song)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, 
                   strategy: RankingStrategy = None, 
                   diversity_penalty: Dict = None) -> List[Tuple[Dict, float, str]]:
    """
    Score and rank all songs; return top k recommendations with scores and explanations.
    
    DIVERSITY PENALTY FEATURE:
    Prevents recommending too many songs from the same artist or genre.
    Applies stacking penalties as duplicates are encountered.
    
    Args:
        user_prefs: User preferences dictionary
        songs: List of song dictionaries
        k: Number of top recommendations to return
        strategy: RankingStrategy instance (defaults to BalancedStrategy)
        diversity_penalty: Dict controlling diversity enforcement:
            {
                'enabled': bool (default True),
                'artist_penalty': float (default 0.15 per occurrence),
                'genre_penalty': float (default 0.10 per occurrence),
                'max_same_artist': int (default 1 - max songs from same artist),
                'max_same_genre': int (default 2 - max songs from same genre)
            }
    
    Returns:
        List of (song, score, explanation) tuples
    """
    if strategy is None:
        strategy = BalancedStrategy()
    
    # Set up diversity penalty configuration
    if diversity_penalty is None:
        diversity_penalty = {
            'enabled': True,
            'artist_penalty': 0.15,
            'genre_penalty': 0.10,
            'max_same_artist': 1,
            'max_same_genre': 2
        }
    
    # If diversity penalty disabled, use original logic
    if not diversity_penalty.get('enabled', True):
        def score_with_explanation(song):
            """Helper: scores a song and formats the explanation."""
            score, reasons = strategy.score_song(user_prefs, song)
            explanation = " + ".join(reasons) if reasons else "no matches"
            return (song, score, explanation)
        
        return sorted(
            map(score_with_explanation, songs),
            key=lambda x: x[1],
            reverse=True
        )[:k]
    
    # DIVERSITY PENALTY ENABLED: Build recommendations iteratively
    recommendations = []
    artists_count = {}  # Track how many songs from each artist
    genres_count = {}   # Track how many songs from each genre
    remaining_songs = songs.copy()
    
    for _ in range(k):
        if not remaining_songs:
            break
        
        # Score all remaining songs with penalties applied
        scored_songs = []
        for song in remaining_songs:
            score, reasons = strategy.score_song(user_prefs, song)
            penalty_applied = 0.0
            penalty_reasons = []
            
            # Apply artist penalty
            artist = song['artist']
            artist_occurrences = artists_count.get(artist, 0)
            max_artist = diversity_penalty.get('max_same_artist', 1)
            
            if artist_occurrences >= max_artist:
                artist_penalty = diversity_penalty.get('artist_penalty', 0.15) * (artist_occurrences - max_artist + 1)
                penalty_applied += artist_penalty
                penalty_reasons.append(f"artist penalty ({artist_occurrences + 1}th from {artist}): -{artist_penalty:.2f}")
            
            # Apply genre penalty
            genre = song['genre']
            genre_occurrences = genres_count.get(genre, 0)
            max_genre = diversity_penalty.get('max_same_genre', 2)
            
            if genre_occurrences >= max_genre:
                genre_penalty = diversity_penalty.get('genre_penalty', 0.10) * (genre_occurrences - max_genre + 1)
                penalty_applied += genre_penalty
                penalty_reasons.append(f"genre penalty ({genre_occurrences + 1}th from {genre}): -{genre_penalty:.2f}")
            
            # Apply penalty to score
            final_score = max(0.0, score - penalty_applied)
            
            # Include both original reasons and penalties in explanation
            combined_reasons = reasons + penalty_reasons
            explanation = " + ".join(combined_reasons) if combined_reasons else "no matches"
            
            scored_songs.append((song, final_score, explanation))
        
        # Select highest-scoring song
        if scored_songs:
            scored_songs.sort(key=lambda x: x[1], reverse=True)
            best_song, best_score, best_explanation = scored_songs[0]
            
            recommendations.append((best_song, best_score, best_explanation))
            
            # Update tracking and remove from remaining
            artist = best_song['artist']
            genre = best_song['genre']
            artists_count[artist] = artists_count.get(artist, 0) + 1
            genres_count[genre] = genres_count.get(genre, 0) + 1
            
            remaining_songs.remove(best_song)
    
    return recommendations
