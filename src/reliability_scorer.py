"""
Reliability Scorer Module

Measures confidence in recommendations by analyzing:
1. Score Normalization: How close to max possible?
2. Criteria Concentration: Is score dominated by one criterion?
3. Coverage Bonus: How many different criteria matched?
4. Bias Proximity: Are known biases triggered?
5. Missing Attributes: Are critical data points available?
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ReliabilityMetrics:
    """Container for individual reliability metrics."""
    normalized_score: float
    coverage_bonus: float
    concentration_penalty: float
    bias_penalty: float
    data_penalty: float
    bias_flags: List[str]
    missing_attrs: List[str]
    reliability_score: float
    confidence_label: str


class ReliabilityScorer:
    """
    Measures recommendation confidence (0.0-1.0).
    
    Scoring Formula:
        reliability = normalized_score + coverage_bonus - concentration_penalty 
                     - bias_penalty - data_penalty
    """
    
    # Known bias thresholds (from BIAS_AND_FILTER_BUBBLE_ANALYSIS.md)
    ENERGY_CUTOFF_THRESHOLD = 0.5
    RARE_GENRES = {"metal", "folk", "jazz", "reggae", "ambient"}
    
    def score_reliability(self, 
                         song: Dict,
                         user_prefs: Dict,
                         base_score: float,
                         reasons: List[str],
                         max_possible_score: float) -> Tuple[float, List[str]]:
        """
        Calculate reliability score for a recommendation.
        
        Args:
            song: Song dictionary
            user_prefs: User preferences dictionary
            base_score: Score from ranking strategy
            reasons: List of explanation strings (e.g., ["genre match (+2.0)", "mood match (+0.8)"])
            max_possible_score: Maximum possible score for the strategy
        
        Returns:
            (reliability_score: 0.0-1.0, reliability_reasons: List[str])
        """
        
        # Step 1: Normalize score (0-1 scale)
        normalized_score = min(1.0, base_score / max_possible_score) if max_possible_score > 0 else 0.0
        
        # Step 2: Parse reasons and extract criterion points
        reason_scores = self._parse_reasons(reasons)
        
        # Step 3: Calculate concentration (Herfindahl index)
        concentration = self._calculate_concentration(reason_scores)
        concentration_penalty = min(0.25, concentration * 0.25) if concentration > 0.7 else 0.0
        
        # Step 4: Coverage bonus (reward multiple criteria)
        coverage = len(set(self._extract_criterion_types(reasons)))
        coverage_bonus = min(0.15, coverage * 0.05)
        
        # Step 5: Check known biases
        bias_flags = self._check_known_biases(song, user_prefs)
        bias_penalty = min(0.30, len(bias_flags) * 0.10)
        
        # Step 6: Check missing attributes
        missing_attrs = self._check_missing_attributes(song)
        data_penalty = min(0.15, len(missing_attrs) * 0.05)
        
        # Final calculation
        reliability = (
            normalized_score +
            coverage_bonus -
            concentration_penalty -
            bias_penalty -
            data_penalty
        )
        
        reliability = max(0.0, min(1.0, reliability))  # Clamp to 0-1
        
        # Generate explanation
        reliability_reasons = self._generate_reliability_reasons(
            normalized_score, coverage_bonus, concentration_penalty,
            bias_penalty, data_penalty, bias_flags
        )
        
        return reliability, reliability_reasons
    
    
    def _parse_reasons(self, reasons: List[str]) -> Dict[str, float]:
        """
        Extract score points from reason strings like "genre match (+2.0)".
        Returns: {"genre": 2.0, "energy": 1.5, "mood": 0.8}
        """
        scores = {}
        for reason in reasons:
            if "(+" in reason and ")" in reason:
                try:
                    score_str = reason.split("(+")[1].split(")")[0]
                    points = float(score_str)
                    criterion = reason.split()[0].lower()
                    scores[criterion] = scores.get(criterion, 0) + points
                except (ValueError, IndexError):
                    pass
        return scores
    
    
    def _calculate_concentration(self, reason_scores: Dict[str, float]) -> float:
        """
        Herfindahl-like index measuring score concentration.
        
        Returns 0.0 (perfectly balanced) to 1.0 (single criterion dominates)
        
        Example:
        - [2.0, 0.8, 0.6] (equal distribution) → ~0.33
        - [3.5, 0.1, 0.1] (high concentration) → ~0.90
        """
        if not reason_scores:
            return 0.0
        
        total = sum(reason_scores.values())
        if total == 0:
            return 0.0
        
        normalized = [v / total for v in reason_scores.values()]
        concentration = sum(x**2 for x in normalized)  # Herfindahl index
        
        return concentration
    
    
    def _extract_criterion_types(self, reasons: List[str]) -> List[str]:
        """Extract unique criterion types from reasons."""
        types = set()
        keywords = ["genre", "mood", "energy", "acoustic", "pop", "decade", 
                   "instr", "tag", "lyrical", "cover"]
        
        for reason in reasons:
            reason_lower = reason.lower()
            for keyword in keywords:
                if keyword in reason_lower:
                    types.add(keyword)
                    break
        
        return list(types)
    
    
    def _check_known_biases(self, song: Dict, user_prefs: Dict) -> List[str]:
        """
        Check if recommendation triggers known bias thresholds.
        Returns list of bias flags detected.
        """
        flags = []
        
        # BIAS 1: HARD ENERGY CUTOFF
        target_energy = user_prefs.get('target_energy', 0.5)
        energy_diff = abs(song.get('energy', 0.5) - target_energy)
        if energy_diff > self.ENERGY_CUTOFF_THRESHOLD:
            flags.append("energy_cutoff_risk")
        
        # BIAS 2: RARE GENRE (limited options)
        if song.get('genre', '').lower() in self.RARE_GENRES:
            flags.append("rare_genre_limited_options")
        
        # BIAS 3: MOOD-ENERGY MISMATCH
        mood = song.get('mood', '').lower()
        energy = song.get('energy', 0.5)
        if mood == "happy" and energy < 0.4:
            flags.append("mood_energy_mismatch")
        elif mood == "chill" and energy > 0.75:
            flags.append("mood_energy_mismatch")
        elif mood == "intense" and energy < 0.6:
            flags.append("mood_energy_mismatch")
        
        # BIAS 4: ACOUSTIC UNCERTAINTY
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
    
    
    def _generate_reliability_reasons(self,
                                     normalized: float,
                                     coverage_bonus: float,
                                     concentration_penalty: float,
                                     bias_penalty: float,
                                     data_penalty: float,
                                     bias_flags: List[str]) -> List[str]:
        """Generate human-readable explanations for reliability score."""
        reasons = []
        
        if normalized >= 0.8:
            reasons.append("Score is near maximum for strategy")
        elif normalized >= 0.6:
            reasons.append("Score is moderate for strategy")
        else:
            reasons.append("Score is below average for strategy")
        
        if coverage_bonus > 0.1:
            reasons.append(f"Multiple criteria matched (+{coverage_bonus:.2f})")
        
        if concentration_penalty > 0.15:
            reasons.append(f"Score dominated by single criterion (-{concentration_penalty:.2f})")
        
        if bias_penalty > 0.15:
            reasons.append(f"Multiple known biases detected (-{bias_penalty:.2f})")
        
        if data_penalty > 0.1:
            reasons.append(f"Missing attribute data (-{data_penalty:.2f})")
        
        if bias_flags:
            for flag in bias_flags:
                if flag == "energy_cutoff_risk":
                    reasons.append("⚠️ Energy outside preference range")
                elif flag == "rare_genre_limited_options":
                    reasons.append("⚠️ Limited songs available in this genre")
                elif flag == "mood_energy_mismatch":
                    reasons.append("⚠️ Mood-energy combination seems misaligned")
                elif flag == "acoustic_unknown":
                    reasons.append("⚠️ Acoustic properties unknown")
        
        return reasons if reasons else ["Standard recommendation"]
    
    
    def get_confidence_label(self, reliability: float) -> str:
        """Return confidence label with text indicators."""
        if reliability >= 0.80:
            return "[HIGH]"
        elif reliability >= 0.60:
            return "[MODERATE]"
        elif reliability >= 0.40:
            return "[LOW]"
        else:
            return "[VERY LOW]"
