# Reliability Scoring & Self-Critique System Architecture

Complete documentation of the reliability scoring and self-critique module for the Music Recommender Simulation. These diagrams will render automatically on GitHub.

---

## 1. Main System Architecture

Complete end-to-end flow from user input through recommendation generation, reliability scoring, and critique analysis to final output.

```mermaid
graph TD
    A["👤 User Prefs"] -->|favorite_genre, mood,<br/>energy, etc.| B["📊 recommend_songs()"]
    C["🎵 Song Catalog"] -->|List[Dict]| B
    D["🎯 RankingStrategy<br/>GenreFirst, MoodFirst,<br/>EnergyFocused, etc."] -->|scoring rules| B
    
    B -->|existing pipeline| E["Scored Songs<br/>List of Song, Score, Explanation"]
    
    E -->|NEW: enable_reliability=True| F["🔍 ReliabilityScorer"]
    
    F -->|Computes 5 Metrics| G["Metric 1: Score<br/>Normalization"]
    F -->|Computes 5 Metrics| H["Metric 2: Criteria<br/>Concentration"]
    F -->|Computes 5 Metrics| I["Metric 3: Coverage<br/>Bonus"]
    F -->|Computes 5 Metrics| J["Metric 4: Bias<br/>Proximity Check"]
    F -->|Computes 5 Metrics| K["Metric 5: Missing<br/>Attributes"]
    
    G --> L["Reliability Score<br/>0.0 - 1.0"]
    H --> L
    I --> L
    J --> L
    K --> L
    
    L -->|For Each Song| M["✨ Recommendation Object<br/>song, score, explanation,<br/>reliability, flags"]
    
    E -->|Same recommendations| N["🤖 SelfCritique Engine"]
    M -->|With reliability data| N
    D -->|Strategy context| N
    A -->|User context| N
    
    N -->|4 Checks| O["Check 1: Diversity<br/>Genre/Artist/Mood Analysis"]
    N -->|4 Checks| P["Check 2: Score<br/>Clustering"]
    N -->|4 Checks| Q["Check 3: Reliability<br/>Bottleneck"]
    N -->|4 Checks| R["Check 4: Strategy<br/>Alignment"]
    
    O --> S["🚨 Critique Report<br/>critique_flags,<br/>bias_warnings,<br/>diversity_score,<br/>overall_critique"]
    P --> S
    Q --> S
    R --> S
    
    M -->|Ranked List| T["🎬 Output"]
    S --> T
    
    T -->|Display| U["📱 Enhanced Table<br/>Rank | Title | Artist | Genre | Score<br/>Reliability | Confidence Label<br/>Explanation | Flags"]
    T -->|Display| V["📋 System Critique<br/>Diversity Score<br/>Bias Warnings<br/>Missing Criteria<br/>Recommendation Tips"]
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#e1f5ff
    style D fill:#f3e5f5
    style E fill:#fffacd
    style F fill:#90ee90
    style L fill:#ffc0cb
    style M fill:#87ceeb
    style N fill:#90ee90
    style S fill:#ffb6c6
    style T fill:#dda0dd
    style U fill:#fffacd
    style V fill:#fffacd
```

**Key Points:**
- Wraps existing `recommend_songs()` without changing core logic
- ReliabilityScorer: 5-metric analysis per song
- SelfCritique: 4 pattern checks across all recommendations
- Output: Enhanced recommendations + system-level critique

---

## 2. Data Flow: Three-Layer Architecture

Shows how data flows through Input → Processing → Output layers.

```mermaid
graph LR
    subgraph Input["📥 INPUT LAYER"]
        U["User Profile<br/>favorite_genre<br/>favorite_mood<br/>target_energy<br/>likes_acoustic"]
        S["Song Data<br/>title, artist<br/>genre, mood, energy<br/>acousticness<br/>popularity, decade<br/>mood_tags, instr.<br/>lyrical_depth"]
        R["Ranking Strategy<br/>GenreFirst<br/>MoodFirst<br/>EnergyFocused<br/>Balanced<br/>PopularityAware<br/>NicheSeeker"]
    end
    
    subgraph Process["⚙️ PROCESSING LAYER"]
        SC["Scoring & Ranking<br/>score_song()<br/>sort by score"]
        RS["Reliability Scoring<br/>- Normalize score<br/>- Calc concentration<br/>- Coverage bonus<br/>- Check biases<br/>- Missing attrs"]
        CR["Self-Critique<br/>- Diversity check<br/>- Score clustering<br/>- Reliability bottleneck<br/>- Strategy alignment<br/>- Missing criteria"]
    end
    
    subgraph Output["📤 OUTPUT LAYER"]
        REC["Recommendation Objects<br/>song dict<br/>+ base_score<br/>+ explanation<br/>+ reliability score<br/>+ reliability_reasons<br/>+ critique_flags"]
        CRIT["Critique Report<br/>critique_flags[]<br/>bias_warnings[]<br/>diversity_score<br/>overall_critique"]
    end
    
    U --> SC
    S --> SC
    R --> SC
    
    SC -->|Top K recs<br/>song, score, reasons| RS
    R --> RS
    U --> RS
    S --> RS
    
    RS -->|Reliability<br/>0.0-1.0 per song| REC
    
    SC -->|Full rec list| CR
    REC -->|With reliability data| CR
    R --> CR
    U --> CR
    
    CR -->|System-level<br/>patterns| CRIT
    
    REC --> Output
    CRIT --> Output
    
    style Input fill:#e3f2fd
    style Process fill:#fff3e0
    style Output fill:#f3e5f5
```

**Layer Breakdown:**
- **Input:** User preferences, song catalog, ranking strategy
- **Processing:** Scoring, reliability calculation, critique analysis
- **Output:** Enhanced recommendations with reliability + system critique

---

## 3. ReliabilityScorer: Internal Logic

Five-step algorithm for computing reliability scores (0.0-1.0) for each recommendation.

```mermaid
graph TD
    A["Song + Score + User Prefs<br/>+ Strategy"] -->|Input| B["ReliabilityScorer"]
    
    B -->|Step 1| C["Normalize Score<br/>base_score / max_possible<br/>Range: 0.0 - 1.0"]
    B -->|Step 2| D["Parse Reasons<br/>Extract points per criterion<br/>genre: 2.0, mood: 0.8, etc."]
    B -->|Step 3| E["Calculate Concentration<br/>Herfindahl Index<br/>0.33 balanced to 1.0 dominant"]
    
    C -->|normalized_score| F["Combine Metrics<br/>reliability = normalized +<br/>coverage_bonus -<br/>concentration_penalty -<br/>bias_penalty -<br/>data_penalty"]
    E -->|concentration| F
    
    B -->|Step 4| G["Check Known Biases<br/>- Energy cutoff risk<br/>- Genre dominance<br/>- Rare genre limited opts<br/>- Mood-energy mismatch<br/>- Acoustic unknown"]
    
    G -->|bias_flags| F
    
    B -->|Step 5| H["Check Missing Attributes<br/>title, artist, genre, mood<br/>energy, popularity, decade<br/>mood_tags, instr, lyrical"]
    
    H -->|missing_attrs| F
    
    D -->|coverage| F
    
    F -->|Clamp 0.0-1.0| I["Reliability Score<br/>0.0-1.0"]
    
    I -->|High 0.8+| J["🟢 HIGH<br/>Trust this rec"]
    I -->|Moderate 0.6-0.8| K["🟡 MODERATE<br/>Check manually"]
    I -->|Low 0.4-0.6| L["🟠 LOW<br/>Question carefully"]
    I -->|Very Low <0.4| M["🔴 VERY LOW<br/>Skip unless exploring"]
    
    style B fill:#90ee90
    style F fill:#ffc0cb
    style I fill:#ffb6c6
    style J fill:#90ee90
    style K fill:#ffeb99
    style L fill:#ffcc99
    style M fill:#ff9999
```

**Scoring Formula:**
```
reliability = normalized_score + coverage_bonus - concentration_penalty - bias_penalty - data_penalty
```

**Known Biases Detected:**
- Energy cutoff hard threshold (songs outside ±0.5 energy = 0 points)
- Genre dominance risk (genre-first strategy dominates)
- Rare genre bottleneck (metal, folk, jazz = 1-2 songs only)
- Mood-energy mismatch (happy should be energetic, not chill)
- Acoustic data unknown (confidence reduced)

---

## 4. SelfCritique: Pattern Detection

Four-check analysis to identify problematic patterns in the recommendation set.

```mermaid
graph TD
    A["List of K Recommendations<br/>Each with reliability"] -->|Input| B["SelfCritique Engine"]
    
    B -->|Check 1| C["Diversity Analysis<br/>Count unique genres<br/>Count unique artists<br/>Count unique moods<br/>diversity_ratio = unique_count / max"]
    
    C -->|Result| D["Diversity Score<br/>0.0 - 1.0"]
    
    D -->|< 0.4| E["🚨 LOW DIVERSITY<br/>All same genre?<br/>All same artist?<br/>Filter bubble detected"]
    
    B -->|Check 2| F["Score Clustering<br/>Score[0] - Score[1] =<br/>gap between #1 and #2<br/>avg_gap = mean of all gaps"]
    
    F -->|Result| G["Score Gap Analysis"]
    
    G -->|gap > avg * 2| H["⚠️ SCORE CLIFF<br/>#1 is obvious choice<br/>#2-K are weak alternatives"]
    
    B -->|Check 3| I["Reliability Bottleneck<br/>Count recs with<br/>reliability < 0.4<br/>Ratio to total"]
    
    I -->|Result| J["Confidence Distribution"]
    
    J -->|> 50% low| K["⚠️ LOW CONFIDENCE<br/>Most recs unreliable<br/>Insufficient data or<br/>poor matches"]
    
    B -->|Check 4| L["Strategy Alignment<br/>Check if user asked for<br/>variety but got genre-first<br/>Check strategy match"]
    
    L -->|Result| M["Strategy Mismatch"]
    
    M -->|Mismatch detected| N["⚠️ STRATEGY ISSUE<br/>Expectations vs delivery"]
    
    E --> O["Critique Report"]
    H --> O
    K --> O
    N --> O
    
    O -->|Output| P["critique_flags[]<br/>bias_warnings[]<br/>diversity_score<br/>overall_critique"]
    
    style B fill:#90ee90
    style O fill:#ffb6c6
    style P fill:#ffb6c6
    style D fill:#fffacd
    style G fill:#fffacd
    style J fill:#fffacd
    style M fill:#fffacd
```

**Four System Checks:**
1. **Diversity Analysis:** Are recommendations varied or in a filter bubble?
2. **Score Clustering:** Is #1 clearly best or are scores close?
3. **Reliability Bottleneck:** Are most recommendations low-confidence?
4. **Strategy Alignment:** Does strategy match user intent?

---

## 5. Confidence Levels: User Interpretation Guide

How to interpret reliability scores and what action to recommend.

```mermaid
graph LR
    A["Reliability Score"] -->|0.80 - 1.00| B["🟢 HIGH CONFIDENCE<br/>95% sure this is<br/>a good recommendation"]
    A -->|0.60 - 0.80| C["🟡 MODERATE<br/>Criteria well matched<br/>but some concerns"]
    A -->|0.40 - 0.60| D["🟠 LOW<br/>Weak signal<br/>Check manually<br/>Limited data"]
    A -->|0.00 - 0.40| E["🔴 VERY LOW<br/>High risk<br/>Poor match or<br/>bias detected<br/>Skip unless exploring"]
    
    B --> F["✅ Suggest immediately<br/>Explain why it's great"]
    C --> G["⚠️ Conditional suggest<br/>Mention caveats"]
    D --> H["❓ Exploratory only<br/>Flag concerns"]
    E --> I["❌ Not recommended<br/>Explain what's wrong"]
    
    style A fill:#e1f5ff
    style B fill:#90ee90
    style C fill:#ffeb99
    style D fill:#ffcc99
    style E fill:#ff9999
```

**Interpretation by Score Range:**
- **🟢 HIGH (0.80-1.00):** Multiple criteria matched, no major concerns
- **🟡 MODERATE (0.60-0.80):** Good match but some flags or data missing
- **🟠 LOW (0.40-0.60):** Weak signal, limited matches, needs manual verification
- **🔴 VERY LOW (<0.40):** High-risk recommendation, potential bias detected

---

## 6. Enhanced Output Integration

How reliability scores and critique integrate into the display.

```mermaid
graph TD
    A["Traditional Output:<br/>Rank | Title | Artist<br/>Score | Explanation"] -->|Add| B["reliability_score<br/>🟢🟡🟠🔴"]
    
    A -->|Add| C["critique_flags<br/>e.g., genre_bottleneck<br/>rare_genre_limited_opts<br/>mood_energy_mismatch"]
    
    B -->|Display| D["RECOMMENDATIONS TABLE<br/>#1 Sunrise City | pop | 4.50 | 🟢 0.78<br/>   genre + mood + energy"]
    
    C -->|Display| D
    
    E["System Report:<br/>Diversity: 80%<br/>Bias Warnings:<br/>- Genre dominance 60%<br/>- Rare genres low confidence<br/>Strategy: Mood-First"] -->|Summary| F["SYSTEM CRITIQUE<br/>Actionable insights"]
    
    style D fill:#fffacd
    style F fill:#fffacd
```

**Enhanced Display Components:**
- **Recommendation Table:** Each recommendation shows reliability score with confidence emoji
- **Critique Flags:** Per-recommendation concerns or bias risks
- **System Report:** Diversity score, bias patterns, strategy alignment notes

---

## Example Output Format

```
====================================================
TOP 5 RECOMMENDATIONS
====================================================

Rank | Title              | Artist         | Genre    | Score | Reliability        | Explanation
-----|--------------------+----------------+----------|-------|--------------------+--------------------------------------
#1   | Sunrise City       | Pop Stars      | pop      | 4.50  | 🟢 HIGH (0.78)    | genre match (+2.0) + mood match (+0.8) + energy (+1.5) + acoustic (+0.2)
#2   | Gym Hero           | Rock Anthem    | pop      | 4.20  | 🟡 MODERATE (0.64)| genre match (+2.0) + energy (+1.8) [⚠️ mood mismatch: intense vs happy]
#3   | Rooftop Lights     | Indie Vibes    | indie    | 3.80  | 🟠 LOW (0.45)     | mood match (+0.8) + energy (+1.5) [⚠️ genre mismatch, rare genre 3 songs]
#4   | Electric Dreams    | Synth Wave     | elec     | 3.10  | 🟠 LOW (0.38)     | energy (+2.0) only [⚠️ high concentration, no genre/mood match]
#5   | Midnight Groove    | Jazz Fusion    | jazz     | 2.50  | 🔴 VERY LOW (0.22)| energy (+1.5) only [🚨 rare genre bottleneck, high bias risk]

====================================================
SYSTEM CRITIQUE
====================================================

✓ Diversity Score: 80% (Good spread across genres/artists)

⚠️ Issues Detected (2):
  - SCORE_CLIFF: Gap between #1 (4.50) and #2 (4.20) is larger than average
    → Recommendation: #1 is strong consensus, #2-5 should be reviewed more carefully
  - MISSING_CRITERIA: "Acousticness" preference never matched in any recommendation
    → Recommendation: User may want to explore acoustic variants

🚨 Bias Warnings:
  - Genre Dominance: Pop appears in 2/5 recommendations (40% of top 5)
    → This aligns with user preference for pop, but limits discovery
  - Rare Genre Bottleneck: Jazz (1 song) and Indie (2 songs) have limited options
    → System recommending from constrained catalog, consider expanding data
  - Mood-Energy Mismatch: Recommendation #2 is "intense" but user asked for "happy"
    → Genre match overcame mood preference; verify if acceptable

✅ Strategy Alignment:
  Current strategy: GenreFirstStrategy
  User intent: Find happy, pop music with high energy
  Status: ✓ ALIGNED (Genre-first is appropriate for genre-specific user)

====================================================
RECOMMENDATIONS
====================================================

✅ #1 (Sunrise City):    STRONGLY RECOMMEND – High confidence, all criteria match
⚠️  #2 (Gym Hero):        RECOMMEND WITH CAUTION – Check mood compatibility
❓  #3 (Rooftop Lights):   EXPLORATORY – Lower confidence, consider for discovery
❌ #4-5:                 SKIP UNLESS EXPLORING – Low confidence due to bias/data issues
```

---

## Implementation Roadmap

These diagrams correspond to the following Python modules (to be created):

- **`src/reliability_scorer.py`** 
  - `ReliabilityScorer` class
  - `score_reliability()` method (5-metric calculation)
  - Bias detection methods

- **`src/self_critique.py`**
  - `SelfCritique` class
  - `critique_recommendations()` method (4-check analysis)
  - Pattern detection methods

- **`src/recommender.py`** (Enhanced)
  - `Recommendation` dataclass (wraps song + metadata)
  - Modified `recommend_songs()` (adds `enable_reliability` parameter)

- **`src/main.py`** (Enhanced)
  - `display_recommendations_with_reliability()` function
  - `display_system_critique()` function

---

## Key Design Principles

✅ **Minimal Refactoring:** Wraps existing scoring, doesn't change core logic
✅ **Composable:** Can enable/disable reliability scoring per session  
✅ **Observable:** Shows *why* recommendations are trustworthy (transparency)
✅ **Educational:** Teaches users about recommender biases in real time
✅ **Extensible:** New bias checks can be added to bias detection
✅ **Testable:** Each component independently testable

---

## Related Documentation

- [BIAS_AND_FILTER_BUBBLE_ANALYSIS.md](../BIAS_AND_FILTER_BUBBLE_ANALYSIS.md) — Known system biases that reliability scoring detects
- [IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md) — Core recommender features and strategies
- [README.md](../README.md) — Main project overview
