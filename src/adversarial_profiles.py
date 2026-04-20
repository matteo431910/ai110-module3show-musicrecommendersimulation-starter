"""
Adversarial and Edge Case User Profiles for Testing Scoring Logic

These profiles are designed to expose weaknesses, boundary conditions, and 
contradictions in the recommender's scoring algorithm.
"""

# ============================================================================
# 1. CONFLICTING ENERGY-MOOD (Psychological Contradiction)
# ============================================================================
CONFLICTED_ENERGETIC_SAD = {
    "name": "Conflicted Energetic Sad",
    "description": "High energy but wants sad mood — tests if scorer handles contradictory emotional signals.",
    
    "favorite_genre": "pop",
    "favorite_mood": "sad",
    
    "target_energy": 0.90,        # Very high energy
    "target_valence": 0.25,       # Low valence (contradicts high energy)
    "target_danceability": 0.80,  # Wants to move but feel sad
    "target_acousticness": 0.50,  # Neutral
    "context": "contradiction",
}

# ============================================================================
# 2. IMPOSSIBLE ACOUSTIC-METAL COMBO
# ============================================================================
ACOUSTIC_METAL_PARADOX = {
    "name": "Acoustic Metal Paradox",
    "description": "Wants metal intensity with acoustic sound — niche, possibly unfindable combination.",
    
    "favorite_genre": "metal",
    "favorite_mood": "aggressive",
    
    "target_energy": 0.95,        # Maximum intensity
    "target_valence": 0.15,       # Very dark
    "target_danceability": 0.70,  # Rhythm-focused despite aggression
    "target_acousticness": 0.95,  # Wants acoustic (contradicts metal)
    "context": "impossible",
}

# ============================================================================
# 3. NULL GENRE + SPECIFIC MOOD (Incomplete Profile)
# ============================================================================
NO_GENRE_SPECIFIC_MOOD = {
    "name": "Open-Genre Specific Mood",
    "description": "No genre preference but very specific mood — tests NULL value handling + weighting.",
    
    "favorite_genre": None,       # Misses 2.0 points! 
    "favorite_mood": "chill",     # Only gets 1.0 point
    
    "target_energy": 0.35,        
    "target_valence": 0.55,       
    "target_danceability": 0.45,  
    "target_acousticness": 0.70,  
    "context": "incomplete",
}

# ============================================================================
# 4. ENERGY BOUNDARY CASE (Exact Middle)
# ============================================================================
ENERGY_BOUNDARY_NEUTRAL = {
    "name": "Energy Boundary Neutral",
    "description": "Target energy at 0.5 (the divisor in the energy formula) — edge case.",
    
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    
    "target_energy": 0.5,         # BOUNDARY: divides by 0.5 in energy_score formula
    "target_valence": 0.50,       # Also middle
    "target_danceability": 0.50,  
    "target_acousticness": 0.50,  
    "context": "boundary",
}

# ============================================================================
# 5. ACOUSTICNESS BOUNDARY CASE (Exactly 0.6)
# ============================================================================
ACOUSTICNESS_BOUNDARY = {
    "name": "Acousticness Boundary Tester",
    "description": "Tests the 0.6 threshold in acousticness scoring (>0.6 is acoustic).",
    
    "favorite_genre": "folk",
    "favorite_mood": "relaxed",
    
    "target_energy": 0.35,        
    "target_valence": 0.60,       
    "target_danceability": 0.40,  
    "target_acousticness": 0.60,  # BOUNDARY: your check is >0.6, not >=0.6
    "context": "boundary",
}

# ============================================================================
# 6. ALL NULL PREFERENCES (Maximally Open)
# ============================================================================
COMPLETELY_OPEN = {
    "name": "Completely Open Listener",
    "description": "No genre, no mood, middle values everywhere — minimum scoring potential.",
    
    "favorite_genre": None,       # -2.0 points impossible
    "favorite_mood": None,        # -1.0 points impossible
    
    "target_energy": 0.5,         
    "target_valence": 0.5,        
    "target_danceability": 0.5,   
    "target_acousticness": 0.5,   
    "context": "maximally-open",
}

# ============================================================================
# 7. ALL EXTREME PREFERENCES (Stress Test)
# ============================================================================
EXTREME_MAXIMALIST = {
    "name": "Extreme Maximalist",
    "description": "All values at extremes (0.0 or 1.0) — stress test for boundary behavior.",
    
    "favorite_genre": "ambient",
    "favorite_mood": "uplifting",
    
    "target_energy": 1.0,          # Max energy
    "target_valence": 1.0,         # Max valence
    "target_danceability": 0.0,    # Min danceability (contradicts high energy!)
    "target_acousticness": 1.0,    # Max acoustic
    "context": "extreme",
}

# ============================================================================
# 8. BIPOLAR VIBES (Sad but Danceable)
# ============================================================================
BIPOLAR_VIBES = {
    "name": "Bipolar Vibes Listener",
    "description": "Low valence (sad) but high danceability and uplifting mood.",
    
    "favorite_genre": "electronic",
    "favorite_mood": "uplifting",
    
    "target_energy": 0.70,        
    "target_valence": 0.15,       # Very sad
    "target_danceability": 0.90,  # Very danceable (contradicts sad)
    "target_acousticness": 0.10,  
    "context": "contradiction",
}

# ============================================================================
# 9. SILENT KILLER (Everything at extremes but opposite)
# ============================================================================
SILENT_KILLER = {
    "name": "Silent Killer",
    "description": "Low energy, low danceability, low acousticness — minimal match potential.",
    
    "favorite_genre": "rock",
    "favorite_mood": "melancholic",
    
    "target_energy": 0.05,         # Extremely low
    "target_valence": 0.10,        # Very sad
    "target_danceability": 0.05,   # No movement
    "target_acousticness": 0.05,   # Pure electronic
    "context": "minimal-match",
}

# ============================================================================
# 10. ZERO ENERGY GAP (Perfect Energy Match Test)
# ============================================================================
ZERO_ENERGY_GAP = {
    "name": "Zero Energy Gap Seeker",
    "description": "Tests songs with EXACT energy match (energy_diff = 0).",
    
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    
    "target_energy": 0.82,        # Matches song #1 exactly!
    "target_valence": 0.84,       # Also matches song #1
    "target_danceability": 0.79,  # Also matches song #1
    "target_acousticness": 0.18,  # Also matches song #1
    "context": "perfect-match",
}

# ============================================================================
# COLLECTION: All Adversarial Profiles
# ============================================================================
ADVERSARIAL_PROFILES = {
    "Conflicted Energetic Sad": CONFLICTED_ENERGETIC_SAD,
    "Acoustic Metal Paradox": ACOUSTIC_METAL_PARADOX,
    "Open-Genre Specific Mood": NO_GENRE_SPECIFIC_MOOD,
    "Energy Boundary Neutral": ENERGY_BOUNDARY_NEUTRAL,
    "Acousticness Boundary": ACOUSTICNESS_BOUNDARY,
    "Completely Open": COMPLETELY_OPEN,
    "Extreme Maximalist": EXTREME_MAXIMALIST,
    "Bipolar Vibes": BIPOLAR_VIBES,
    "Silent Killer": SILENT_KILLER,
    "Zero Energy Gap": ZERO_ENERGY_GAP,
}
