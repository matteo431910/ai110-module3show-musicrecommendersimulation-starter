# Reliability Scoring + Self-Critique Implementation Plan

## Overview
Add confidence assessment and automated critique to recommendations without refactoring core scoring logic. The system will tell users *why* they should trust (or question) each recommendation.

---

## Architecture: Three-Layer System

```
recommend_songs() [EXISTING]
         ↓
    reliability_score() [NEW]
         ↓  
    self_critique_check() [NEW]
         ↓
Enhanced Recommendation Object
  - song
  - score
  - explanation (existing)
  - reliability: 0.0-1.0 ← NEW
  - critiques: [List[str]] ← NEW
```

---

## Component 1: ReliabilityScorer Class

**Purpose:** Measure how trustworthy each recommendation is.

### Key Metrics

```python
class ReliabilityScorer:
    """
    Measures recommendation confidence based on:
    1. Score Concentration: Is score spread across criteria or dominated by one?
    2. Criteria Coverage: How many user preferences were satisfied?
    3. Bias Proximity: Is this recommendation near a known bias threshold?
    4. Uncertainty Factors: Missing data, edge cases?
    """
    
    def score_reliability(self, song: Dict, user_prefs: Dict, 
                         base_score: float, reasons: List[str], 
                         strategy: RankingStrategy,
                         max_possible_score: float) -> float:
        """
        Returns reliability score (0.0-1.0)
        1.0 = very confident in this recommendation
        0.5 = moderate confidence, some flags
        0.2 = low confidence, many concerns
        """
        
        # 1. SCORE NORMALIZATION (0-1 scale)
        # How close to the max possible for this strategy?
        normalized_score = min(1.0, base_score / max_possible_score)
        
        # 2. CRITERIA CONCENTRATION PENALTY
        # If recommendation relies heavily on 1-2 criteria → lower reliability
        # Extract points from reasons list
        reason_counts = self._parse_reasons(reasons)
        concentration = self._calculate_concentration(reason_counts)
        # concentration: 0.0 (perfectly balanced) to 1.0 (single criterion)
        # Penalty: -0.25 if concentration > 0.7
        
        # 3. CRITERIA COVERAGE BONUS
        # How many distinct types of criteria matched?
        coverage = len(set(self._extract_criterion_types(reasons)))
        coverage_bonus = min(0.15, coverage * 0.05)  # +0.05 per criterion, max +0.15
        
        # 4. BIAS PROXIMITY CHECK
        bias_flags = self._check_known_biases(song, user_prefs, strategy)
        bias_penalty = len(bias_flags) * 0.10  # -0.10 per flag, capped at -0.30
        
        # 5. DATA AVAILABILITY PENALTY
        # Missing/null attributes reduce confidence
        missing_attrs = self._check_missing_attributes(song)
        data_penalty = len(missing_attrs) * 0.05
        
        # Final formula
        reliability = (
            normalized_score +           # Base normalized score
            coverage_bonus -             # Bonus for covering multiple criteria
            min(0.25, concentration * 0.25) -  # Penalty for concentration
            min(0.30, bias_penalty) -    # Penalty for bias proximity
            min(0.15, data_penalty)      # Penalty for missing data
        )
        
        return max(0.0, min(1.0, reliability))  # Clamp to 0-1
    
    
    def _parse_reasons(self, reasons: List[str]) -> Dict[str, float]:
        """
        Extract score points from reason strings like "genre match (+2.0)"
        Returns: {"genre": 2.0, "energy": 1.5, "mood": 0.8}
        """
        scores = {}
        for reason in reasons:
            # Parse: "genre match (+2.0)"
            if "(+" in reason and ")" in reason:
                score_str = reason.split("(+")[1].split(")")[0]
                points = float(score_str)
                criterion = reason.split()[0].lower()  # "genre", "energy", etc.
                scores[criterion] = points
        return scores
    
    
    def _calculate_concentration(self, reason_scores: Dict[str, float]) -> float:
        """
        Herfindahl-like index measuring if score is concentrated.
        Returns 0.0 (perfectly balanced) to 1.0 (single criterion dominates)
        
        Example:
        - [2.0, 0.8, 0.6] (total 3.4) → normalized = [0.59, 0.24, 0.18]
          → sum of squares = 0.59² + 0.24² + 0.18² = 0.40 (moderate concentration)
        - [3.5, 0.1, 0.1] (total 3.7) → normalized = [0.95, 0.03, 0.03]
          → sum of squares = 0.95² + ... = 0.91 (high concentration!)
        """
        if not reason_scores:
            return 0.0
        
        total = sum(reason_scores.values())
        normalized = [v / total for v in reason_scores.values()]
        concentration = sum(x**2 for x in normalized)  # Herfindahl index
        
        return concentration  # Range: ~0.33 (3 equal) to 1.0 (single)
    
    
    def _extract_criterion_types(self, reasons: List[str]) -> List[str]:
        """Extract unique criterion types from reasons."""
        types = set()
        for reason in reasons:
            if "match" in reason or "proximity" in reason:
                criterion = reason.split()[0].lower()
                types.add(criterion)
        return list(types)
    
    
    def _check_known_biases(self, song: Dict, user_prefs: Dict, 
                            strategy: RankingStrategy) -> List[str]:
        """
        Check if recommendation triggers known bias thresholds.
        Returns list of bias flags detected.
        """
        flags = []
        
        # BIAS 1: HARD ENERGY CUTOFF (from BIAS_AND_FILTER_BUBBLE_ANALYSIS.md)
        target_energy = user_prefs.get('target_energy', 0.5)
        energy_diff = abs(song['energy'] - target_energy)
        if energy_diff > 0.5:
            flags.append("energy_cutoff_risk")
        
        # BIAS 2: GENRE BOTTLENECK
        # If genre match is only criterion with >0.5 points
        if strategy.get_name() == "GenreFirstStrategy":
            flags.append("genre_dominance_risk")
        
        # BIAS 3: RARE GENRE (inferred from limited options)
        # If only 1-2 songs available for this genre
        rare_genres = {"metal", "folk", "jazz", "reggae", "ambient"}
        if song['genre'].lower() in rare_genres:
            flags.append("rare_genre_limited_options")
        
        # BIAS 4: MOOD-ENERGY MISMATCH
        # Happy songs typically have high valence + energy
        # Intense songs have high energy but low valence
        # If user prefers happy + low energy, recommend high-energy happy song
        # → potential mismatch detected
        mood = song['mood'].lower()
        if mood == "happy" and song['energy'] < 0.4:
            flags.append("mood_energy_mismatch")  # Happy should be energetic
        elif mood == "chill" and song['energy'] > 0.75:
            flags.append("mood_energy_mismatch")  # Chill should be low energy
        
        # BIAS 5: ACOUSTIC UNCERTAINTY
        if song.get('acousticness') is None:
            flags.append("acoustic_unknown")
        
        return flags
    
    
    def _check_missing_attributes(self, song: Dict) -> List[str]:
        """Check for missing/None attributes that reduce confidence."""
        required_attrs = [
            'title', 'artist', 'genre', 'mood', 'energy',
            'popularity', 'release_decade', 'mood_tags',
            'instrumentation', 'lyrical_depth'
        ]
        
        missing = []
        for attr in required_attrs:
            if attr not in song or song[attr] is None:
                missing.append(attr)
        
        return missing
```

---

## Component 2: SelfCritique Class

**Purpose:** Automatically flag problematic patterns and generate explanations.

```python
class SelfCritique:
    """
    Reviews a list of recommendations and flags:
    1. Diversity issues (too similar across top K)
    2. Bias patterns (e.g., all same genre despite user requesting variety)
    3. Anomalies (e.g., #1 scored 4.5 but #2 scored 2.1 — huge gap?)
    4. Strategy-User Mismatch (e.g., genre-first strategy but user asked for mood-first)
    """
    
    def critique_recommendations(self, 
                                recommendations: List[Tuple[Dict, float, str, float]],
                                user_prefs: Dict,
                                strategy: RankingStrategy) -> Dict:
        """
        Args:
            recommendations: List of (song, score, explanation, reliability) tuples
            user_prefs: User preferences
            strategy: The ranking strategy used
        
        Returns: {
            'critique_flags': [List of critique strings],
            'diversity_score': 0.0-1.0,  # How diverse are these recommendations?
            'bias_warnings': [List of potential bias issues],
            'overall_critique': str  # Human-readable summary
        }
        """
        
        critique = {
            'critique_flags': [],
            'diversity_score': 0.0,
            'bias_warnings': [],
            'overall_critique': ''
        }
        
        if not recommendations:
            critique['overall_critique'] = "No recommendations to critique."
            return critique
        
        # CHECK 1: DIVERSITY
        genres = [song['genre'] for song, _, _, _ in recommendations]
        artists = [song['artist'] for song, _, _, _ in recommendations]
        moods = [song['mood'] for song, _, _, _ in recommendations]
        
        unique_genres = len(set(genres))
        unique_artists = len(set(artists))
        unique_moods = len(set(moods))
        
        diversity_ratio = (unique_genres + unique_artists + unique_moods) / (len(recommendations) * 3)
        critique['diversity_score'] = diversity_ratio
        
        if diversity_ratio < 0.4:
            critique['critique_flags'].append("LOW_DIVERSITY: Recommendations are very similar to each other")
            if unique_genres == 1:
                critique['bias_warnings'].append(f"All {len(recommendations)} songs are {genres[0]} genre - strong filter bubble detected")
            if unique_artists == 1:
                critique['bias_warnings'].append(f"All songs are from same artist - no discovery")
        
        # CHECK 2: SCORE CLUSTERING
        scores = [score for _, score, _, _ in recommendations]
        score_gap_1_to_2 = scores[0] - scores[1] if len(scores) > 1 else 0
        avg_gap = sum(scores[i] - scores[i+1] for i in range(len(scores)-1)) / (len(scores)-1) if len(scores) > 1 else 0
        
        if score_gap_1_to_2 > avg_gap * 2:
            critique['critique_flags'].append("SCORE_CLIFF: Large gap between #1 and #2 - #1 might be obvious choice, #2-K might be weak")
        
        # CHECK 3: RELIABILITY BOTTLENECK
        reliabilities = [rel for _, _, _, rel in recommendations]
        low_reliability_count = sum(1 for r in reliabilities if r < 0.4)
        
        if low_reliability_count > len(recommendations) * 0.5:
            critique['critique_flags'].append("LOW_CONFIDENCE: More than half of recommendations have low reliability")
        
        # CHECK 4: STRATEGY ALIGNMENT WITH USER REQUEST
        # If user mentioned wanting "variety" but strategy is "genre-first"
        if "variety" in str(user_prefs).lower() and strategy.get_name() == "GenreFirstStrategy":
            critique['bias_warnings'].append(f"User requested variety but using {strategy.get_name()} (typically narrows options)")
        
        # CHECK 5: MISSING CRITERIA
        # Did ANY recommendation satisfy some user preferences?
        all_reasons = set()
        for _, _, explanation, _ in recommendations:
            criteria = [r.split()[0] for r in explanation.split(" + ")]
            all_reasons.update(criteria)
        
        expected_criteria = ['genre', 'mood', 'energy']
        missing_criteria = [c for c in expected_criteria if c.lower() not in [r.lower() for r in all_reasons]]
        
        if missing_criteria:
            critique['critique_flags'].append(f"MISSING_CRITERIA: These criteria were never matched: {', '.join(missing_criteria)}")
        
        # Generate human-readable summary
        critique['overall_critique'] = self._generate_summary(critique)
        
        return critique
    
    
    def _generate_summary(self, critique: Dict) -> str:
        """Generate human-readable critique summary."""
        parts = []
        
        if not critique['critique_flags']:
            parts.append("✓ All checks passed. Recommendations look solid.")
        else:
            parts.append(f"⚠️ {len(critique['critique_flags'])} issues detected:")
            for flag in critique['critique_flags']:
                parts.append(f"  - {flag}")
        
        if critique['bias_warnings']:
            parts.append("\n🚨 Bias Warnings:")
            for warning in critique['bias_warnings']:
                parts.append(f"  - {warning}")
        
        diversity_pct = int(critique['diversity_score'] * 100)
        parts.append(f"\nDiversity Score: {diversity_pct}% (higher is better)")
        
        return "\n".join(parts)
```

---

## Component 3: Enhanced Recommendation Object

Replace the tuple `(song, score, explanation)` with a structured object:

```python
from dataclasses import dataclass

@dataclass
class Recommendation:
    """Enhanced recommendation with reliability and critique info."""
    song: Dict
    score: float
    explanation: str
    reliability: float  # 0.0-1.0
    reliability_reasons: List[str]  # Why this reliability score
    critique_flags: List[str]  # Any red flags
    
    def confidence_label(self) -> str:
        """Human-readable confidence level."""
        if self.reliability >= 0.8:
            return "🟢 HIGH"
        elif self.reliability >= 0.6:
            return "🟡 MODERATE"
        elif self.reliability >= 0.4:
            return "🟠 LOW"
        else:
            return "🔴 VERY LOW"
    
    def as_dict(self) -> Dict:
        """Convert to dict for logging/display."""
        return {
            'song': self.song['title'],
            'artist': self.song['artist'],
            'score': round(self.score, 2),
            'reliability': f"{self.reliability_label()} ({round(self.reliability, 2)})",
            'explanation': self.explanation,
            'flags': self.critique_flags if self.critique_flags else "none"
        }
```

---

## Component 4: Integration Points

### Modify `recommend_songs()` function:

```python
def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, 
                   strategy: RankingStrategy = None, 
                   diversity_penalty: Dict = None,
                   enable_reliability: bool = True) -> Tuple[List[Recommendation], Dict]:
    """
    Args:
        enable_reliability: If True, compute reliability scores + self-critique
    
    Returns:
        (recommendations: List[Recommendation], critique: Dict)
    """
    
    # [EXISTING CODE - score and rank recommendations]
    # ...
    
    # [NEW CODE - add reliability scoring]
    if enable_reliability:
        scorer = ReliabilityScorer()
        critique_engine = SelfCritique()
        
        # Score each recommendation's reliability
        recommendations_with_reliability = []
        for song, score, explanation in recommendations[:k]:
            reliability = scorer.score_reliability(
                song=song,
                user_prefs=user_prefs,
                base_score=score,
                reasons=explanation.split(" + "),
                strategy=strategy,
                max_possible_score=strategy.max_possible_score()
            )
            
            rec = Recommendation(
                song=song,
                score=score,
                explanation=explanation,
                reliability=reliability,
                reliability_reasons=scorer._generate_reliability_explanation(reliability),
                critique_flags=[]  # Per-recommendation flags
            )
            recommendations_with_reliability.append(rec)
        
        # Run system-level critique
        critique = critique_engine.critique_recommendations(
            recommendations_with_reliability,
            user_prefs,
            strategy
        )
        
        return recommendations_with_reliability, critique
    else:
        # Legacy mode: return tuples
        return recommendations[:k], {'critique_flags': [], 'overall_critique': 'Disabled'}
```

---

## Component 5: Display Enhancement

Update `display_recommendations_table()` in `main.py`:

```python
def display_recommendations_with_reliability(recommendations, critique, title="Recommendations"):
    """Display with reliability scores and critique."""
    
    print("\n" + "="*120)
    print(title.center(120))
    print("="*120 + "\n")
    
    # Main recommendations table
    table_data = []
    for rank, rec in enumerate(recommendations, 1):
        table_data.append([
            f"#{rank}",
            rec.song['title'][:25],
            rec.song['artist'][:18],
            rec.song['genre'],
            f"{rec.score:.2f}",
            f"{rec.reliability_label()} {round(rec.reliability, 2)}",
            rec.explanation[:40] + "..." if len(rec.explanation) > 40 else rec.explanation
        ])
    
    headers = ["Rank", "Title", "Artist", "Genre", "Score", "Reliability", "Explanation"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # System-level critique
    print("\n" + "="*120)
    print("SYSTEM CRITIQUE".center(120))
    print("="*120)
    print(critique['overall_critique'])
```

---

## Example Output

```
====================================================
TOP 5 RECOMMENDATIONS
====================================================

Rank | Title              | Artist      | Genre | Score | Reliability        | Explanation
-----|--------------------+-------------|-------|-------|--------------------+----------------------------------
#1   | Sunrise City       | Pop Stars   | pop   | 4.50  | 🟢 HIGH (0.78)    | genre match (+2.0) + mood match (+0.8) + energy (+1.5) + acoustic (+0.2)
#2   | Gym Hero           | Rock Anthem | pop   | 4.20  | 🟡 MODERATE (0.64)| genre match (+2.0) + energy (+1.8) [mood mismatch: intense vs happy]
#3   | Rooftop Lights     | Indie Vibes | indie | 3.80  | 🟠 LOW (0.45)     | mood match (+0.8) + energy (+1.5) [genre mismatch, niche genre only 3 songs available]
#4   | Electric Dreams    | Synth Wave  | elec. | 3.10  | 🟠 LOW (0.38)     | energy (+2.0) only [high concentration, missing genre/mood matches]
#5   | Midnight Groove    | Jazz Fusion | jazz  | 2.50  | 🔴 VERY LOW (0.22)| energy (+1.5) only [rare genre bottleneck detected]

==================================================
SYSTEM CRITIQUE
==================================================

✓ Checks Passed: Diversity score 80% (good spread)

⚠️ Issues Detected (2):
  - SCORE_CLIFF: Large gap between #1 (4.50) and #2 (4.20) - #1 is strong consensus
  - MISSING_CRITERIA: "Acousticness" never matched in top recommendations

🚨 Bias Warnings:
  - Recommendations #1-2 dominated by pop genre (60% of top 5)
  - Rare genre songs (#3 indie, #5 jazz) have low reliability due to limited catalog
  - User requested "chill" mood but #2 recommendation is "intense" despite genre match

Recommendation: 
  ✅ Trust #1 (Sunrise City) - high confidence
  ⚠️ Question #2-3 - consider manually checking mood compatibility
  ❌ Skip #4-5 unless exploring niche - low confidence due to genre/dataset limitations
```

---

## Implementation Checklist

- [ ] Create `reliability_scorer.py` with `ReliabilityScorer` class
- [ ] Create `self_critique.py` with `SelfCritique` class
- [ ] Add `Recommendation` dataclass to `recommender.py`
- [ ] Modify `recommend_songs()` to compute reliability + critique
- [ ] Update `main.py` display functions to show reliability + critique
- [ ] Add command-line flag `--disable-reliability` for legacy mode
- [ ] Add tests for edge cases (empty lists, all low reliability, etc.)
- [ ] Update README with reliability scoring explanation

---

## Why This Approach Works

✅ **Minimal Refactoring**: Wraps existing scoring, doesn't change core logic
✅ **Composable**: Can enable/disable reliability scoring per session
✅ **Observable**: Shows *why* recommendations are trustworthy (transparency)
✅ **Educational**: Teaches users about recommender biases in real time
✅ **Extensible**: New bias checks can be added to `_check_known_biases()`
✅ **Testable**: Each component can be tested independently

---

## Future Enhancements

1. **Learning Loop**: Track which recommendations user actually liked → refine reliability model
2. **Counterfactual Explanations**: "If you preferred high-energy songs, recommendation #3 would rank #1"
3. **Bias Mitigation**: Auto-adjust scores when high-bias patterns detected
4. **A/B Testing**: Compare strategies by reliability scores
5. **Export Audit Trail**: Save recommendations + reliability scores for analysis
