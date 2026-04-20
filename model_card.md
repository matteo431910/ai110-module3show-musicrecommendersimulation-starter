# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**GrooveMatch 1.0**

It finds songs that match your vibe by scoring energy, mood, and genre.  

---

## 2. Intended Use  

This is a classroom tool for learning how music recommenders work. It shows how hidden biases can affect recommendations even when the code seems logical. It's not meant for real-world music apps—it's too small and too opinionated. We use it to explore questions like: What happens when energy matters more than genre? What do users with extreme tastes experience? Can we trick the system with contradictory preferences?  

---

## 3. How the Model Works  

For every song, the system scores it on four things your taste:

**Energy match** (up to 2.0 points): Songs close to your energy level score high. But there's a hard rule: anything more than 0.5 away gets zero points. This creates invisible walls—if you like super chill music (0.05), half the catalog disappears.

**Mood match** (up to 1.0 points): Songs with your mood get points. Melancholic matches melancholic. Intense matches intense.

**Genre match** (up to 1.0 points): Exact genre match gets full points. No partial credit.

**Acousticness** (up to 0.5 points): How acoustic the song is compared to what you want.

All scores are added together (max 4.5 points). The system ranks songs by total score and shows you the top picks with reasons why they matched.

---

## 4. Data  

The dataset has 20 songs across 15 genres: pop, lofi, rock, indie, electronic, ambient, jazz, classical, hip-hop, soul, folk, reggae, synthwave, indie pop, and metal.

But it's unbalanced. Lofi has 3 songs, electronic has 2, indie has 2, pop has 2. Everything else has just 1 song. If you want jazz recommendations and don't like the one jazz song, you're stuck.

The songs range from super chill (0.25 energy) to aggressive (0.97 energy). Moods include happy, chill, intense, relaxed, energetic, melancholic, romantic, and more. No data was added or removed—this is the starter dataset.  

---

## 5. Strengths  

The system excels at finding exact matches. If your energy and mood perfectly align with a song, it will rank at the top—we tested this with a "perfect match" profile and got a 4.50/4.50 score.

It handles NULL preferences gracefully. If you don't care about genre, the system skips that score and moves on. It doesn't crash or default to weird values.

For typical users with moderate tastes (like wanting chill lofi or energetic pop), the recommendations feel reasonable and matched my intuition. The system is internally consistent—run the same profile twice and you get the same answer.  

---

## 6. Limitations and Bias 

**Hard energy cutoff:** Any song more than 0.5 energy away gets zero points. This creates "invisible walls." If you want super low-energy (0.05) or super high-energy (0.95) music, you can only pick from a tiny slice of songs.

**No compromise:** If you want energetic AND acoustic music, the system can't find it—high-energy songs are mostly not acoustic. The system commits to one preference and ignores the other.

**Genre imbalance:** Lofi has 3 songs. Jazz, metal, and folk have 1 each. If you don't like the one jazz song, there are no alternatives.

**Energy beats genre:** With current weights, the system prioritizes energy matching over genre matching. Ask for jazz and you might get electronic music—just because the energy is perfect.

**Binary acousticness:** Songs are either acoustic or not. There's no middle ground at the threshold.

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

We tested 13 user profiles: 3 standard (High-Energy Pop, Chill Lofi, Deep Intense Rock) and 10 adversarial ones designed to break the system.

Adversarial profiles included: Conflicted (wants happy AND sad), Impossible (wants metal AND acoustic), Open (no preferences), Boundaries (energy at exact thresholds), and a Perfect Match test.

**Key findings:**

- **Perfect match works:** Zero Energy Gap scored 4.50/4.50, confirming exact matching is precise.
- **No compromise:** Acoustic Metal Paradox got rock songs—metal won, acousticness lost. The system can't blend conflicting preferences.
- **Weights matter a lot:** Changing energy from 1.0→2.0 and genre from 2.0→1.0 flipped which songs ranked first for some profiles.
- **Energy walls are real:** Users wanting 0.05 or 0.95 energy could only access 2-3 songs each. Everyone else saw way more options.
- **Genre becomes invisible:** When energy doubled, some genre-matching disappeared. Jazz fans might get electronic music instead.

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

**Soften the energy cutoff:** Instead of zero points beyond ±0.5, fade the score gradually. This would prevent invisible walls for extreme energy preferences.

**Add compromise scoring:** If a song partially matches multiple preferences (e.g., energetic BUT not your genre), give it partial points instead of ignoring it completely. Real music taste is messy.

**Expand the dataset:** Get more songs in rare genres and fix the energy-acousticness imbalance. With only 20 songs, some user types have almost no valid recommendations.  

---

## 9. Personal Reflection  

Building GrooveMatch taught me that recommender systems are never neutral—every design choice (weights, cutoffs, features) is a hidden opinion. I expected the system to be broken if the weights were off, but it actually worked consistently. What surprised me was that it worked *too consistently*—it would confidently recommend the wrong thing if the weights favored energy over genre.

Testing adversarial profiles made me realize that small numbers look like problems in fake data but feel like limitations in real systems. A dataset of 20 songs is obviously small, but I bet real Spotify has similar invisible walls for users with unusual tastes—superspecific genre + mood combos that nothing satisfies.

Now when I use music apps, I notice things like: Do they let me tweak what "matters" to recommendations? Can they suggest things outside my usual zone? Or do they trap me in a narrow slice? GrooveMatch trapped me, and I don't think my recommender system is that different from real ones—just more honest about it.  
