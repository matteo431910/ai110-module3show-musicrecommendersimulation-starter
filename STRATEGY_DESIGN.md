# Strategy Pattern Design for Music Recommender

## Overview
Implement multiple ranking strategies to allow flexible recommendation algorithms while keeping code modular and maintainable.

## Design Pattern: Strategy Pattern

The Strategy pattern allows you to encapsulate different ranking algorithms and switch between them at runtime.

```
┌─────────────────────────────────────────┐
│      RankingStrategy (Abstract)         │
├─────────────────────────────────────────┤
│ + score_song(user_prefs, song) -> float │
│ + explain_score(...) -> str             │
│ + max_possible_score() -> float          │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┼──────────────┐
        │         │              │
        ▼         ▼              ▼
  GenreFirst  MoodFirst    EnergyFocused
  Strategy    Strategy     Strategy
```

## Concrete Strategies

### 1. **Genre-First Strategy**
**Weights:**
- Genre Match: **2.0** (prioritize genre)
- Mood Match: 0.8
- Energy: 1.5
- Acousticness: 0.3
- Popularity: 0.3
- Decade: 0.2
- Mood Tags: 0.2
- Instrumentation: 0.2
- Lyrical Depth: 0.1

**Max Score:** ~5.6

**Use Case:** Users who want a specific genre above all else.

---

### 2. **Mood-First Strategy**
**Weights:**
- Mood Match: **2.0** (prioritize mood)
- Genre Match: 0.8
- Energy: 1.5
- Acousticness: 0.4
- Mood Tags: **0.6** (expanded emotional detail)
- Popularity: 0.3
- Decade: 0.2
- Instrumentation: 0.2
- Lyrical Depth: 0.2

**Max Score:** ~6.2

**Use Case:** Users who want specific emotional vibes regardless of genre.

---

### 3. **Energy-Focused Strategy**
**Weights:**
- Energy: **2.5** (maximize energy matching)
- Mood Match: 1.0
- Genre Match: 0.5
- Acousticness: 0.3
- Popularity: 0.4
- Mood Tags: 0.3
- Decade: 0.2
- Instrumentation: 0.2
- Lyrical Depth: 0.1

**Max Score:** ~5.5

**Use Case:** Users who want specific energy levels (workout, focus, party).

---

### 4. **Balanced Strategy** (Current Default)
**Weights:** Equal distribution across all criteria
- Genre: 1.0
- Mood: 1.0
- Energy: 2.0
- Acousticness: 0.5
- Popularity: 0.5
- Decade: 0.3
- Mood Tags: 0.4
- Instrumentation: 0.3
- Lyrical Depth: 0.2

**Max Score:** 6.2

**Use Case:** General-purpose recommendations balancing all preferences.

---

### 5. **Popularity-Aware Strategy**
**Weights:**
- Popularity: **1.0** (prioritize mainstream)
- Energy: 1.8
- Mood: 1.0
- Genre: 0.8
- Mood Tags: 0.4
- Decade: 1.0 (prefer recent)
- Acousticness: 0.2
- Instrumentation: 0.2
- Lyrical Depth: 0.1

**Max Score:** ~6.5

**Use Case:** Users who want well-known, trending music.

---

### 6. **Niche-Seeker Strategy**
**Weights:**
- Genre Match: 1.5
- Mood Match: 1.5
- Instrumentation: **0.8** (production style matters)
- Lyrical Depth: **0.6** (artist depth matters)
- Decade: 0.8 (era authenticity)
- Energy: 1.0
- Mood Tags: 0.5
- Popularity: **0.0** (avoid mainstream)
- Acousticness: 0.3

**Max Score:** ~6.6

**Use Case:** Users seeking underground/indie recommendations.

---

## Code Structure

### In `recommender.py`:

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple

class RankingStrategy(ABC):
    """Abstract base class for ranking strategies."""
    
    @abstractmethod
    def score_song(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        """Score a song and return (score, reasons)."""
        pass
    
    @abstractmethod
    def max_possible_score(self) -> float:
        """Return the maximum possible score for this strategy."""
        pass
    
    def get_name(self) -> str:
        """Return strategy name."""
        return self.__class__.__name__


class GenreFirstStrategy(RankingStrategy):
    def score_song(self, user_prefs, song):
        # Implementation with genre-focused weights
        pass
    
    def max_possible_score(self):
        return 5.6


class MoodFirstStrategy(RankingStrategy):
    # Similar pattern
    pass


# More strategies...

# Strategy Registry (easy lookup)
STRATEGIES = {
    'genre-first': GenreFirstStrategy,
    'mood-first': MoodFirstStrategy,
    'energy-focused': EnergyFocusedStrategy,
    'balanced': BalancedStrategy,
    'popularity-aware': PopularityAwareStrategy,
    'niche-seeker': NicheSeeker Strategy,
}

def get_strategy(strategy_name: str) -> RankingStrategy:
    """Factory function to get a strategy by name."""
    if strategy_name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy_name}")
    return STRATEGIES[strategy_name]()


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, 
                   strategy: RankingStrategy = None) -> List[Tuple[Dict, float, str]]:
    """Score and rank songs using the specified strategy."""
    if strategy is None:
        strategy = BalancedStrategy()  # Default
    
    def score_with_explanation(song):
        score, reasons = strategy.score_song(user_prefs, song)
        explanation = " + ".join(reasons) if reasons else "no matches"
        return (song, score, explanation)
    
    return sorted(
        map(score_with_explanation, songs),
        key=lambda x: x[1],
        reverse=True
    )[:k]
```

### In `main.py`:

```python
from recommender import load_songs, recommend_songs, get_strategy

songs = load_songs("data/songs.csv")

# Example 1: Use Genre-First strategy
strategy = get_strategy('genre-first')
recommendations = recommend_songs(profile, songs, strategy=strategy)

# Example 2: Easy string-based switching
strategy_name = 'mood-first'
recommendations = recommend_songs(profile, songs, 
                                  strategy=get_strategy(strategy_name))

# Example 3: Compare strategies
print("=== Genre-First ===")
for song, score, reasons in recommend_songs(profile, songs, 
                                            strategy=get_strategy('genre-first')):
    print(f"{song['title']}: {score}")

print("\n=== Energy-Focused ===")
for song, score, reasons in recommend_songs(profile, songs,
                                            strategy=get_strategy('energy-focused')):
    print(f"{song['title']}: {score}")
```

## Benefits of This Design

1. **Modularity**: Each strategy is independent and self-contained
2. **Extensibility**: Easy to add new strategies without modifying existing code
3. **Testability**: Can test each strategy separately
4. **Clarity**: Strategy logic is explicit and easy to understand
5. **Flexibility**: Runtime switching without recompilation
6. **Easy Comparison**: Compare multiple strategies for same profile

## Next Steps

1. Create abstract `RankingStrategy` base class
2. Implement 4-6 concrete strategies with different weight distributions
3. Create a strategy registry for easy lookup
4. Update `recommend_songs()` to accept strategy parameter
5. Demo in main.py comparing multiple strategies on same profiles
