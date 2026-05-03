"""
Self-Critique Module

Analyzes entire recommendation sets for problematic patterns:
1. Diversity: Are recommendations varied or in a filter bubble?
2. Score Clustering: Is #1 obviously best or scores close?
3. Reliability Bottleneck: Are most recommendations low-confidence?
4. Strategy Alignment: Does strategy match user intent?
5. Missing Criteria: Were some preferences never satisfied?
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CritiqueReport:
    """Container for system-level critique analysis."""
    diversity_score: float
    diversity_warning: Optional[str]
    score_cliff_warning: Optional[str]
    reliability_bottleneck_warning: Optional[str]
    strategy_alignment_status: str
    missing_criteria: List[str]
    critique_flags: List[str]
    bias_warnings: List[str]
    overall_critique: str


class SelfCritique:
    """
    Reviews a list of recommendations and flags problematic patterns.
    """
    
    def critique_recommendations(self,
                                recommendations: List[Tuple],
                                user_prefs: Dict,
                                strategy_name: str) -> CritiqueReport:
        """
        Analyze recommendations for patterns and issues.
        
        Args:
            recommendations: List of (song, score, explanation, reliability) tuples
            user_prefs: User preferences
            strategy_name: Name of the ranking strategy used
        
        Returns:
            CritiqueReport with analysis results
        """
        
        if not recommendations:
            return CritiqueReport(
                diversity_score=0.0,
                diversity_warning="No recommendations to analyze",
                score_cliff_warning=None,
                reliability_bottleneck_warning=None,
                strategy_alignment_status="N/A",
                missing_criteria=[],
                critique_flags=["EMPTY_RECOMMENDATIONS"],
                bias_warnings=[],
                overall_critique="No recommendations to critique."
            )
        
        # CHECK 1: DIVERSITY ANALYSIS
        genres = [song['genre'] for song, _, _, _ in recommendations]
        artists = [song['artist'] for song, _, _, _ in recommendations]
        moods = [song['mood'] for song, _, _, _ in recommendations]
        
        unique_genres = len(set(genres))
        unique_artists = len(set(artists))
        unique_moods = len(set(moods))
        
        k = len(recommendations)
        max_diversity = k * 3  # Perfect diversity: all genres, artists, moods unique
        actual_diversity = unique_genres + unique_artists + unique_moods
        diversity_score = actual_diversity / max_diversity
        
        diversity_warning = None
        if diversity_score < 0.4:
            diversity_warning = f"LOW DIVERSITY ({int(diversity_score*100)}%): Recommendations are very similar"
        
        # CHECK 2: SCORE CLUSTERING
        scores = [score for _, score, _, _ in recommendations]
        score_cliff_warning = None
        
        if len(scores) > 1:
            score_gap_1_to_2 = scores[0] - scores[1]
            avg_gap = sum(scores[i] - scores[i+1] for i in range(len(scores)-1)) / (len(scores)-1)
            
            if score_gap_1_to_2 > avg_gap * 2:
                score_cliff_warning = (
                    f"SCORE CLIFF: Large gap between #1 ({scores[0]:.2f}) and #2 ({scores[1]:.2f})"
                )
        
        # CHECK 3: RELIABILITY BOTTLENECK
        reliabilities = [rel for _, _, _, rel in recommendations]
        low_reliability_count = sum(1 for r in reliabilities if r < 0.4)
        reliability_bottleneck_warning = None
        
        if low_reliability_count > k * 0.5:
            reliability_bottleneck_warning = (
                f"LOW CONFIDENCE: {low_reliability_count}/{k} recommendations have low reliability"
            )
        
        # CHECK 4: STRATEGY ALIGNMENT
        strategy_alignment_status = self._check_strategy_alignment(
            strategy_name, user_prefs
        )
        
        # CHECK 5: MISSING CRITERIA
        all_criteria = set()
        for _, _, explanation, _ in recommendations:
            criteria = self._extract_criteria(explanation)
            all_criteria.update(criteria)
        
        expected_criteria = {'genre', 'mood', 'energy'}
        missing_criteria = list(expected_criteria - all_criteria)
        
        # COMPILE CRITIQUE
        critique_flags = []
        bias_warnings = []
        
        if diversity_warning:
            critique_flags.append(diversity_warning)
            if unique_genres == 1:
                bias_warnings.append(f"All {k} songs are from '{genres[0]}' genre - strong filter bubble")
            if unique_artists == 1:
                bias_warnings.append("All songs are from same artist - no discovery potential")
        
        if score_cliff_warning:
            critique_flags.append(score_cliff_warning)
        
        if reliability_bottleneck_warning:
            critique_flags.append(reliability_bottleneck_warning)
        
        if missing_criteria:
            critique_flags.append(f"MISSING CRITERIA: Never matched {', '.join(missing_criteria)}")
        
        # Check for rare genres
        rare_genres_found = []
        for genre in set(genres):
            if genres.count(genre) == 1 and genre.lower() in {"metal", "folk", "jazz", "reggae", "ambient"}:
                rare_genres_found.append(genre)
        
        if rare_genres_found:
            bias_warnings.append(
                f"Rare genres detected ({', '.join(rare_genres_found)}) - limited catalog options available"
            )
        
        overall_critique = self._generate_summary(
            critique_flags, bias_warnings, diversity_score, 
            reliability_bottleneck_warning is not None
        )
        
        return CritiqueReport(
            diversity_score=diversity_score,
            diversity_warning=diversity_warning,
            score_cliff_warning=score_cliff_warning,
            reliability_bottleneck_warning=reliability_bottleneck_warning,
            strategy_alignment_status=strategy_alignment_status,
            missing_criteria=missing_criteria,
            critique_flags=critique_flags,
            bias_warnings=bias_warnings,
            overall_critique=overall_critique
        )
    
    
    def _check_strategy_alignment(self, strategy_name: str, user_prefs: Dict) -> str:
        """Check if strategy matches user intent."""
        # This is basic - could be expanded with user intent detection
        
        user_str = str(user_prefs).lower()
        
        strategy_to_intent = {
            "GenreFirstStrategy": "Users who know exactly what genre they want",
            "MoodFirstStrategy": "Users prioritizing emotional experience",
            "EnergyFocusedStrategy": "Activity-based or energy-level driven",
            "BalancedStrategy": "General recommendations, first-time users",
            "PopularityAwareStrategy": "Following current hits and trends",
            "NicheSeekerStrategy": "Music enthusiasts seeking hidden gems"
        }
        
        if strategy_name in strategy_to_intent:
            return f"[OK] {strategy_name} ({strategy_to_intent[strategy_name]})"
        
        return f"Using {strategy_name}"
    
    
    def _extract_criteria(self, explanation: str) -> set:
        """Extract criteria mentioned in explanation."""
        criteria = set()
        keywords = {
            'genre': 'genre',
            'mood': 'mood',
            'energy': 'energy',
            'acoustic': 'acoustic',
            'pop': 'popularity',
            'decade': 'decade',
            'instr': 'instrumentation',
            'tag': 'mood_tags',
            'lyrical': 'lyrical'
        }
        
        explanation_lower = explanation.lower()
        for keyword, criterion in keywords.items():
            if keyword in explanation_lower:
                criteria.add(criterion)
        
        return criteria
    
    
    def _generate_summary(self, 
                         critique_flags: List[str],
                         bias_warnings: List[str],
                         diversity_score: float,
                         has_low_confidence: bool) -> str:
        """Generate human-readable critique summary."""
        parts = []
        
        # Header
        if not critique_flags:
            parts.append("[OK] All checks passed. Recommendations look solid.")
        else:
            parts.append(f"[!] {len(critique_flags)} issues detected:")
            for i, flag in enumerate(critique_flags, 1):
                parts.append(f"  {i}. {flag}")
        
        # Bias warnings
        if bias_warnings:
            parts.append("\n[BIAS] Bias Warnings:")
            for warning in bias_warnings:
                parts.append(f"  - {warning}")
        
        # Diversity
        parts.append(f"\nDiversity Score: {int(diversity_score*100)}% (higher is better)")
        
        # Confidence warning
        if has_low_confidence:
            parts.append("\n[!] Note: Many recommendations have low confidence.")
            parts.append("   Consider verifying recommendations manually or expanding dataset.")
        
        return "\n".join(parts)
