"""
User Taste Profiles for Music Recommender Testing

Each profile represents a different listener archetype with specific target features
for testing the content-based scoring algorithm.
"""

# ============================================================================
# PRIMARY PROFILE: Vibe Coder
# ============================================================================
VIBE_CODER = {
    "name": "Vibe Coder",
    "description": "A versatile listener who enjoys exploring different musical styles. Balances focus music for work with discovery.",
    
    # Categorical preferences (None = open to all)
    "favorite_genre": None,  # Open to all genres
    "favorite_mood": None,   # Context-dependent
    
    # Numerical targets (moderate, balanced)
    "target_energy": 0.55,        # Moderate energy
    "target_valence": 0.65,       # Slightly upbeat
    "target_danceability": 0.60,  # Moderate groove
    "target_acousticness": 0.50,  # Balanced acoustic/electronic
    "context": "focused",
}

# ============================================================================
# TEST PROFILES: Different User Archetypes
# ============================================================================

WORKOUT_WARRIOR = {
    "name": "Workout Warrior",
    "description": "High-energy listener seeking intense, driving music for exercise and pump sessions.",
    
    "favorite_genre": "pop",
    "favorite_mood": "intense",
    
    "target_energy": 0.90,         # Very high energy
    "target_valence": 0.70,        # Upbeat/motivating (not dark)
    "target_danceability": 0.85,   # Highly danceable, groove-oriented
    "target_acousticness": 0.10,   # Mostly electronic/produced
    "context": "exercise",
}

LATE_NIGHT_RELAXER = {
    "name": "Late Night Relaxer",
    "description": "Wants calm, introspective music for late-night wind-down and sleep preparation.",
    
    "favorite_genre": "ambient",
    "favorite_mood": "chill",
    
    "target_energy": 0.25,         # Very low energy
    "target_valence": 0.60,        # Warm but not overly bright
    "target_danceability": 0.35,   # Static, no need to move
    "target_acousticness": 0.85,   # Highly acoustic/organic
    "context": "sleep",
}

GENRE_EXPLORER = {
    "name": "Genre Explorer",
    "description": "Curious listener constantly discovering new sounds across multiple genres and moods.",
    
    "favorite_genre": None,        # Deliberately exploring all genres
    "favorite_mood": None,         # Studies across moods
    
    "target_energy": 0.65,         # Slight lean toward energetic
    "target_valence": 0.72,        # Positive/uplifting discovery
    "target_danceability": 0.70,   # Likes groovy, rhythmic songs
    "target_acousticness": 0.55,   # Mix of both styles
    "context": "discovery",
}

CAFE_VIBE_LISTENER = {
    "name": "Cafe Vibe Listener",
    "description": "Enjoys warm, organic, acoustic sounds for study sessions and coffeehouse atmosphere.",
    
    "favorite_genre": "jazz",
    "favorite_mood": "relaxed",
    
    "target_energy": 0.40,         # Low to moderate energy
    "target_valence": 0.70,        # Warm and inviting
    "target_danceability": 0.55,   # Subtle groove, not intrusive
    "target_acousticness": 0.88,   # Very acoustic/organic
    "context": "study",
}

INTENSE_FOCUS_HARDCORE = {
    "name": "Intense Focus Hardcore",
    "description": "Demands maximum-intensity, aggressive music to maintain deep focus during demanding work.",
    
    "favorite_genre": "metal",
    "favorite_mood": "aggressive",
    
    "target_energy": 0.95,         # Nearly maximum energy
    "target_valence": 0.40,        # Dark and driving (not upbeat)
    "target_danceability": 0.70,   # Rhythm matters, intensity matters more
    "target_acousticness": 0.05,   # Purely electronic/produced
    "context": "intense-work",
}

SOUL_LOVER = {
    "name": "Soul Lover",
    "description": "Gravitates toward soulful, romantic, and emotionally expressive music with strong vocals.",
    
    "favorite_genre": "soul",
    "favorite_mood": "romantic",
    
    "target_energy": 0.65,         # Moderate energy (feeling, not intensity)
    "target_valence": 0.75,        # Warm, positive, romantic
    "target_danceability": 0.78,   # Groovy but emotional
    "target_acousticness": 0.50,   # Balanced production
    "context": "evening",
}

ELECTRONIC_SYNTH_HEAD = {
    "name": "Electronic Synth Head",
    "description": "Obsessed with synthesizers, electronic production, and futuristic soundscapes.",
    
    "favorite_genre": "electronic",
    "favorite_mood": "energetic",
    
    "target_energy": 0.88,         # High energy
    "target_valence": 0.80,        # Bright and euphoric
    "target_danceability": 0.92,   # Highly danceable
    "target_acousticness": 0.08,   # Minimal acoustic elements
    "context": "dance",
}

INDIE_MELANCHOLIC = {
    "name": "Indie Melancholic",
    "description": "Drawn to introspective indie music with emotional depth and artistic nuance.",
    
    "favorite_genre": "indie",
    "favorite_mood": "melancholic",
    
    "target_energy": 0.35,         # Low to moderate energy
    "target_valence": 0.45,        # Darker, more introspective
    "target_danceability": 0.50,   # Subtle movement, not upbeat
    "target_acousticness": 0.72,   # Organic, singer-songwriter feel
    "context": "introspection",
}

HIP_HOP_CONFIDENCE = {
    "name": "Hip-Hop Confidence",
    "description": "Loves rhythm, wordplay, and the swagger of hip-hop. High-confidence, statement music.",
    
    "favorite_genre": "hip-hop",
    "favorite_mood": "confident",
    
    "target_energy": 0.75,         # Energetic but controlled
    "target_valence": 0.68,        # Positive, statement-making
    "target_danceability": 0.84,   # Strong rhythm and groove
    "target_acousticness": 0.25,   # Mostly produced beats
    "context": "motivation",
}

# ============================================================================
# PROFILE COLLECTIONS FOR BATCH TESTING
# ============================================================================

ALL_PROFILES = [
    VIBE_CODER,
    WORKOUT_WARRIOR,
    LATE_NIGHT_RELAXER,
    GENRE_EXPLORER,
    CAFE_VIBE_LISTENER,
    INTENSE_FOCUS_HARDCORE,
    SOUL_LOVER,
    ELECTRONIC_SYNTH_HEAD,
    INDIE_MELANCHOLIC,
    HIP_HOP_CONFIDENCE,
]

PROFILES_BY_CONTEXT = {
    "work": [VIBE_CODER, CAFE_VIBE_LISTENER, INTENSE_FOCUS_HARDCORE],
    "exercise": [WORKOUT_WARRIOR, ELECTRONIC_SYNTH_HEAD],
    "relaxation": [LATE_NIGHT_RELAXER, INDIE_MELANCHOLIC, SOUL_LOVER],
    "discovery": [GENRE_EXPLORER],
}
