
# **NO TURNS, ONLY VIBES**  
### A Simultaneous-Play Roguelike Deckbuilder (Slay‑the‑Spire‑style) — Game Design Document

> “You know my options. I know yours. Now commit. 😈”

---

## 1) High Concept

A single‑player, run‑based deckbuilder where **turns don’t exist**. In each combat “beat,” both the player and the enemy **draw visible rows of options** (e.g., 4 cards each). The player secretly commits one card and a **Prediction** of the enemy’s choice; the enemy secretly chooses via a mixed‑strategy AI. Both resolve **simultaneously** using a clean **Speed → Keyword → Damage/Stun** priority. The core tension is the **mind‑read**, not the hand count.

- **Elevator**: “Slay the Spire meets simultaneous rock‑paper‑scissors—but with readable tactics instead of coin‑flips.”  
- **Session length**: 30–45 min runs.  
- **Audience**: Spire enjoyers, fighting‑game footsie lovers, and people who yell “I KNEW you’d do that!” at their monitor.

---

## 2) Design Pillars

1. **Perfect Info, Imperfect Commitment**: You can see enemy options, not their choice.  
2. **Reads Rewarded, Not Required**: Correct Predictions give **bonuses**, not auto‑wins.  
3. **Resolve Cleanly**: Minimal math, crisp timing windows, tiny numbers (1–6).  
4. **Deckbuilding Feels Intentional**: Every card matters; low variance, high agency.  
5. **No Sandbagging**: Visible rows + burn mechanics prevent hoarding; pace stays hot.

---

## 3) Core Loops

### 3.1 Run Loop
- Draft a starting deck + starting relic.  
- Traverse **3 Acts** of branching maps (Normal → Elite → Boss each Act).  
- Earn **cards / relics / currency**; remove/upgrade cards at camps & shops.  
- Lose? Unlock meta stuff and try again at higher **Heat** (Ascension).

### 3.2 Map Loop (Nodes)
- **Combat**, **Elite**, **Event**, **Shop**, **Camp (Rest/Tinker)**, **Treasure**.
- Events lean into mind‑games: pick outcomes with partial reveals or “opponent row” style dilemmas.

### 3.3 Combat Loop (“Beats”)
1. **Show**: Player and Enemy each draw **4** cards **face‑up** into their rows.  
2. **Scheme**: Player secretly chooses **1** card and places a **Prediction** marker on an enemy card slot (A/B/C/D).  
3. **Commit**: Enemy AI secretly picks **1** from its 4 (mixed strategy).  
4. **Reveal & Resolve**: Flip; resolve **Keywords → Speed → Damage/Stun**; apply **Read** if the player’s Prediction was correct.  
5. **Cleanup**: Played cards go to discard. Unplayed cards **Burn** (exile) unless a card or relic says otherwise. Draw back to **4** next beat.  
6. **End**: Repeat until one side hits **0 HP** or a scripted end condition triggers.

> Default hand/row size is **4**, can be modified by cards/relics/status.

---

## 4) Combat System

### 4.1 Card Anatomy
**Name • Type • Speed (S1–S6) • Effect • Stability (Stab 1–4) • Read • Clash**  
- **Speed**: Higher acts first. Ties: both act; check each card’s **Clash** line.  
- **Stability**: If you take incoming damage **≥ your Stability** before your effect resolves, you **Stun** and your effect **fizzles**.  
- **Read**: Triggers only if the player’s Prediction token matches the enemy’s revealed card; small, satisfying perk (e.g., +1 Speed or +2 dmg).  
- **Clash**: A tie‑breaker line; both cards execute but with a special clause if simultaneous (e.g., “both take 1”).

### 4.2 Resolution Order
1. **Keywords** (Intercept/Guard/Dodge/Counter/Ignore)  
2. **Speed** (higher first; tiebreak with **Clash**)  
3. **Damage & Effects**  
4. **Stun Check** (if stunned, your effect fizzles)  
5. **End‑of‑Beat** effects

### 4.3 Keywords (Starter Set)
- **Guard X**: Prevent X damage this beat.  
- **Intercept**: If you act first, cancel target card’s effect (unless it has **Unstoppable**).  
- **Dodge**: If foe played *Attack* or *Grapple*, it misses you.  
- **Grapple**: On hit, apply **Stun** even if damage < Stability.  
- **Unstoppable**: This effect can’t be canceled, only stunned by damage.  
- **Bleed (n)**: Take n damage at end of each of your next **k** beats (default k=2).  
- **Slow (n)**: –n Speed (min S1) this beat (or next beat if specified).  
- **Charge**: If not hit this beat, bank +1 **Focus** (see 4.5).  
- **Feint**: After reveal, you may swap this with one unplayed row card; the new card resolves at S5.

### 4.4 Resources
- **HP**: Start at 70–80 for the player; enemies vary.  
- **Focus** (0–3): A lightweight banked resource that some cards spend for bonuses.  
- **Instants**: One‑shot consumables (Spire‑like potions) that modify a beat (e.g., “+1 Speed this beat”).

### 4.5 Deck Flow
- Start deck ~12 cards.  
- Per beat, draw a fresh row to 4.  
- **Burn** the 3 unplayed cards by default (keeps reads sharp, avoids hoarding).  
- Discard piles reshuffle when needed. Some relics switch to **Countdown Hands** (keep your row instead of burning), creating deeper planning.

---

## 5) Player Progression

- **Card Rewards** (1 of 3; sometimes 4): common/uncommon/rare with synergies.  
- **Relics**: Passive rules‑changers that bend the mind‑game (e.g., “Your Predictions show as a face‑up decoy.”).  
- **Upgrades**: Smith node improves cards (usually +1 Speed, +1 dmg, +Stability, or a stronger Read).  
- **Removals**: Shop/Event/Camp options to trim the deck.  
- **Instants**: Held in 3 slots; found from combats/events/shops.

---

## 6) Enemies & AI

### 6.1 Enemy Anatomy
- **Deck** (12–20 cards), scaled by Act.  
- **Row Size**: 4 (modifiers exist).  
- **Archetype**: Bruiser / Turtle / Trickster / Grappler / Tempo.  
- **Telegraphs**: Passive tells like “If they drew *Crush* this beat, it glows red.” (soft info, still guessy).

### 6.2 AI Card Choice (Mixed Strategy)
We avoid deterministic “best card” picks to keep Predictions meaningful.

**Algorithm (per beat):**
1. Score each available enemy card with a **Payoff** estimator vs each of the player’s 4 visible options.  
2. Assume the player uses a **level‑k** mixed strategy (weighting high‑payoff counters).  
3. Compute **expected value** (EV) for each enemy card under that belief.  
4. Build a softmax distribution over EV with **temperature τ** (lower τ means more spiky/predictable).  
5. Sample one card from that distribution.  
6. (Boss/Elite) Add a small **anti‑repeat penalty** if the same card was played last beat.

**Tuning knobs**: τ (unpredictability), level‑k depth, anti‑repeat, bias to showcase signature moves.

### 6.3 Sample Enemies (Act 1)
- **Brawler Pup** (Bruiser): Rows with *Quick Maul*, *Heavy Chomp*, *Howl (Charge)*, *Guard*. Predictable damage spiker.  
- **Sand Serpent** (Grappler): Loves **Grapple** and **Slow** packages; punishes your speed plans.  
- **Mime of Mirrors** (Trickster): Copies your last played card’s type; rows often include **Feint**.  
- **Wallflower** (Turtle): Big **Guard**, low Speed; beats your Greed plays if you mess up.

---

## 7) Content (MVP Targets)

### 7.1 Cards (Player) — 60 for MVP
**Attacks**  
- **Quick Jab** — *Attack* — **S5** — Deal **1**. — **Stab 1** — **Read**: +1 dmg — **Clash**: both take 1.  
- **Heavy Swing** — *Attack* — **S2** — Deal **4**. — **Stab 3** — **Clash**: both take 2.  
- **Lunge** — *Attack* — **S4** — Deal **2**; if you resolve before foe, +1 dmg. — **Stab 2**.

**Defense / Trick**  
- **Guard Wall** — *Guard* — **S1** — Prevent **4** this beat. If not hit, next beat +1 Speed. — **Stab 4**.  
- **Parry** — *Counter* — **S4** — If foe played *Attack* and you act first, **cancel** it and deal **2**. — **Stab 2**.  
- **Sidestep** — *Dodge* — **S6** — If foe played *Attack* or *Grapple*, it **misses**; **Charge**. — **Stab 1** — **Clash**: no effect.

**Grapples / Disruption**  
- **Grapple** — *Grapple* — **S3** — Deal **2** and **Stun** even if dmg < Stability. — **Stab 2**.  
- **Choke Chain** — *Grapple* — **S2** — Deal **1**; apply **Slow 1** next beat. — **Stab 3**.  
- **Disrupt** — *Trick* — **S5** — Foe **Slow 2** (min S1) this beat; deal **1**. — **Stab 1**.

**Tempo & Build**  
- **Feint** — *Trick* — **S6** — After reveal, swap with an unplayed row card; new card resolves at **S5**. — **Stab 1** — **Read**: +1 dmg.  
- **Focus** — *Prep* — **S2** — Heal **2**; next beat +1 **Stability**. — **Stab 3**.  
- **Ignite** — *Skill* — **S3** — Deal **1** and apply **Bleed 1 (2 beats)**. — **Stab 2** — **Read**: +Bleed 1.

> Upgrades typically add +1 Speed, +1 dmg, or stronger Read/keyword (e.g., **Guard Wall+**: Prevent 5 and +2 Speed next beat).

### 7.2 Relics — 30 for MVP
- **Smirk Mask**: Your **Read** gives +1 Speed instead of +1 dmg (choose at start of run).  
- **Telltale Locket**: One random enemy card in their row is **highlighted**; its pick chance is doubled.  
- **Honed Instinct**: Every 3rd correct Read: gain +1 Focus.  
- **Countdown Ledger**: Your unplayed row **does not Burn** (Countdown Hands mode).  
- **Double‑Fake**: Your Prediction token is placed face‑up, but gives **+2** if correct (else 0).

### 7.3 Instants (Potions) — 12
- **Adrenaline Vial**: +1 Speed this beat.  
- **Stone Skin**: +3 Guard this beat.  
- **Gambler’s Brew**: Replace your entire row (Burn the old 4).

### 7.4 Events — 15 (Act‑agnostic)
- **Whispering Doors**: Pick a door; preview an enemy’s **next fight signature row** vs a relic reward.  
- **The Bluffsmith**: Upgrade one card, but it gains **Feint** (may help or hurt your line‑reading).  
- **Mirror Match**: Copy a card in your deck; the copy has **Clash: both take 1**.

---

## 8) Difficulty & Heat (Ascension)

- **Heat 1**: Enemies gain +5% HP.  
- **Heat 2**: Enemy AI τ lowers (more sharky/predictable—harder to read).  
- **Heat 3**: Your Read gives only +1 Speed **or** +1 dmg (choose at run start).  
- **Heat 4**: Unplayed enemy cards don’t Burn (they get Countdown Hands).  
- **Heat 5**: Bosses gain **Unstoppable** on one signature card per beat.

---

## 9) Economy, Rewards, & Pacing

- **Normal fights**: ~12–16 gold, 1 card pick, 30% chance of Instant.  
- **Elites**: 1 relic, 1 card pick (upgrade), 40–50 gold.  
- **Boss**: 1 boss relic choice (1 of 3), 2 card picks.  
- **Shops**: Cards (50–200), Removes (75→100→125), Instants (60–120), Relics (150–300).  
- **Camps**: **Rest** (heal 25%) or **Tinker** (upgrade 1); late‑game unlock: **Study** (peek at Boss signature row).

---

## 10) UX / UI Sketch

- **Top‑Center**: Enemy HP, Focus, statuses, and their 4 visible cards (row A–D).  
- **Bottom‑Center**: Your HP, Focus, statuses, and your 4 visible cards.  
- **Left**: Prediction marker (drag onto enemy A–D).  
- **Right**: Instants; Run log with **Speed order** icons.  
- **Reveal Phase**: Dramatic flip; arrows show **Speed order**; stun sparks if a card fizzles.  
- **Accessibility**: Toggle “Always Explain Why” that overlays the cause of each cancel/stun.

---

## 11) Example Beat (Annotated)

Setup: You: **Feint, Parry, Disrupt, Heavy Swing**. Foe: **Grapple, Guard Wall, Fireburst, Sidestep**.  
You Predict **Fireburst** (greedy).

- Reveal: You played **Feint**, foe played **Grapple**.  
- **Feint** swaps into **Parry**, which now resolves at **S5**.  
- **S5 Parry** vs **S3 Grapple**: Parry only cancels *Attacks*, not *Grapples* → doesn’t cancel, but still deals **2**.  
- Foe takes 2 (Stab 2) → not stunned; **Grapple** hits for 2 and **Stuns** you -> your later effects would fizzle.  
- No correct Read on either side → no bonus.  
- Both discard played cards; other 3 Burn. Draw 4 new cards each. Next beat begins.

---

## 12) Balance Guidelines

- Average per‑beat damage (net) in Act 1: **3–5**.  
- Speed bands: S1 turtle, S3/S4 default, S6 emergency/reactive.  
- Stability avg: **2**; raising Stability slows combat, favors setup cards.  
- Reads should be **+1 dmg** **or** **+1 Speed** baseline; stacking both is rare/special.

---

## 13) MVP Scope (12–14 Weeks)

- **Systems**: Core combat, Prediction UI, Speed/Stability/Stun rules, Burn/Countdown toggle.  
- **Content**: 60 player cards, 20 enemy cards per Act (x3), 30 relics, 12 instants, 15 events, 12 enemies, 6 elites, 3 bosses.  
- **AI**: Mixed‑strategy picker with τ + anti‑repeat.  
- **Meta**: 5 Heat levels, unlock tracks, run stats.  
- **Polish**: FX for Reveal/Stun/Clash, “Explain Why”, seed export.  
- **Out of scope (MVP)**: Multiple classes, map modifiers, daily climbs.

---

## 14) Telemetry (so we can be clever later)

- Per‑beat logs: rows, chosen cards, Predictions, correctness, Speed order, stuns, net damage.  
- Card pick/skip rates; relic winrate deltas; foe AI distribution (how often each card is picked).  
- Streaks of correct/incorrect Reads (do players learn a foe’s mixed strategy?).  
- Beat duration, misclicks, tooltip opens, “Explain Why” usage.

---

## Appendix A — Starter Card List (Print‑n‑Play prototype)
Use **2 copies** of each of the 12 cards below for a 24‑card player pool for quick testing (mirror a 24‑card enemy pool).

1. Quick Jab — Attack — S5 — Deal 1. — Stab 1 — Read: +1 dmg — Clash: both take 1.  
2. Heavy Swing — Attack — S2 — Deal 4. — Stab 3 — Clash: both take 2.  
3. Lunge — Attack — S4 — Deal 2; if you resolve before them, +1 dmg. — Stab 2.  
4. Guard Wall — Guard — S1 — Prevent 4; if not hit, next beat +1 Speed. — Stab 4.  
5. Parry — Counter — S4 — If foe played Attack and you act first, cancel it; deal 2. — Stab 2.  
6. Sidestep — Dodge — S6 — If foe played Attack or Grapple, it misses; Charge. — Stab 1 — Clash: no effect.  
7. Grapple — Grapple — S3 — Deal 2; Stun even if dmg < Stability. — Stab 2.  
8. Choke Chain — Grapple — S2 — Deal 1; Slow 1 next beat. — Stab 3.  
9. Disrupt — Trick — S5 — Foe Slow 2 (min S1) this beat; deal 1. — Stab 1.  
10. Focus — Prep — S2 — Heal 2; next beat +1 Stability. — Stab 3.  
11. Ignite — Skill — S3 — Deal 1; Bleed 1 (2 beats). — Stab 2 — Read: +Bleed 1.  
12. Feint — Trick — S6 — After reveal, swap with an unplayed row card; new card resolves at S5. — Stab 1 — Read: +1 dmg.

---

## Appendix B — Boss Signatures (Taste)
- **The Undertow**: Has one **Unstoppable** S3 pull that drags your Speed to S2 if it hits.  
- **Lady Coinflip**: Her chosen card is sometimes shown as **two facedown cards**; if you Predict either one correctly, you still get the Read bonus.  
- **The Arbiter**: Every 3rd beat forces **Clash** resolution regardless of Speed.

---

## Final Note

We keep the drama of reads without opaque randomness. Every beat is a little duel of “do they know that I know that they know?”—and when your Prediction lands, it *feels* like galaxy‑brain without the headache.

Let’s build the prototype with a debug **“Explain Why”** overlay and a **seeded AI** so runs are reviewable. I’ll bring the smirk. You bring the instincts. 😈
