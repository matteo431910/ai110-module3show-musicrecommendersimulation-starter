# Reliability Scoring & Self-Critique Architecture

## System Architecture Diagram

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

---

## Data Flow: Detailed Layer Breakdown

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

---

## ReliabilityScorer: Internal Logic

```mermaid
graph TD
    A["Song + Score + User Prefs<br/>+ Strategy"] -->|Input| B["ReliabilityScorer"]
    
    B -->|Step 1| C["Normalize Score<br/>base_score / max_possible<br/>Range: 0.0 - 1.0"]
    B -->|Step 2| D["Parse Reasons<br/>Extract points per criterion<br/>genre: 2.0, mood: 0.8, etc."]
    B -->|Step 3| E["Calculate Concentration<br/>Herfindahl Index<br/>0.33 balanced to 1.0 dominant"]
    
    C -->|normalized_score| F["Combine Metrics<br/>reliability = normalized +<br/>coverage_bonus -<br/>concentration_penalty -<br/>bias_penalty -<br/>data_penalty"]
    E -->|concentration| F
    
    B -->|Step 4| G["Check Known Biases<br/>- Energy cutoff risk<br/>- Genre dominance<br/>- Rare genre (limited opts)<br/>- Mood-energy mismatch<br/>- Acoustic unknown"]
    
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

---

## SelfCritique: Pattern Detection

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

---

## Confidence Labels & User Interpretation

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

---

## Integration: Enhanced Output

```mermaid
graph TD
    A["Traditional Output:<br/>Rank | Title | Artist<br/>Score | Explanation"] -->|Add| B["reliability_score<br/>🟢🟡🟠🔴"]
    
    A -->|Add| C["critique_flags<br/>e.g., genre_bottleneck<br/>rare_genre_limited_opts<br/>mood_energy_mismatch"]
    
    B -->|Display| D["RECOMMENDATIONS TABLE<br/>#1 Sunrise City | pop | 4.50 | 🟢 0.78<br/>   genre + mood + energy"]
    
    C -->|Display| D
    
    E["System Report:<br/>Diversity: 80%<br/>Bias Warnings:<br/>- Genre dominance (60%)<br/>- Rare genres low confidence<br/>Strategy: Mood-First"] -->|Summary| F["SYSTEM CRITIQUE<br/>Actionable insights"]
    
    style D fill:#fffacd
    style F fill:#fffacd
```
