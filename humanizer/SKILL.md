---
name: humanizer
description: |
  Detects 54 AI writing patterns and rewrites text in five voice profiles so it reads like a specific human wrote it, with an optional 0-100 AI-tell score. Use when text sounds AI-generated or like a chatbot, when preparing a blog post, README or LinkedIn post for publication, when auditing prose for AI tells, or when editing a Markdown file in place. Triggers on "humanize this", "make this sound less AI", "make this sound human", "remove AI tells", "does this read like ChatGPT". Also works on French and triggers on "rends ce texte plus humain", "on dirait du ChatGPT", "humanise ce texte", "ca sonne genere"; for French input load references/patterns.fr.md before scanning. Single-dash commands include -help, -empreinte (build a voice profile from your own corpus), -voix, -score, -fr and -audit. Do NOT use for code, for literal translation, for text quoted from another author, or for prose already carrying a settled human voice.
user-invocable: true
metadata:
  version: "3.0.0-fr"
  upstream: "Aboudjem/humanizer-skill 0.5.0"
argument-hint: '"your text" [--mode detect|rewrite|edit] [--voice casual|professional|technical|warm|blunt] [--file path/to/file.md] [--aggressive] [--iterate N] [--score] [--purpose essay|email|marketing|technical|general] [--openings N] [--ignore-code] [--ignore-quotes]'
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - AskUserQuestion
---

# Humanizer: Make Text Sound Like a Human Wrote It

Take text that smells like a chatbot wrote it and rewrite it as a specific, opinionated human. Detects 54 AI writing patterns (plus 14 French-specific ones), scores them 0-100, applies a chosen voice profile, and varies sentence-length burstiness so the result reads as written by a person.

**The division of labor that makes this skill fast and exhaustive:** everything mechanical (regex-able patterns, counts, metrics, the score) belongs to `scripts/scan.py`, run once, deterministically. The model only does what code cannot: judgment patterns, meaning-preserving rewriting, voice. Never hand-count what the scanner counts.

## Quick reference

**Modes**

| Mode | What it does |
|:-----|:-------------|
| `detect` | Scan text, report patterns, output a 0-100 AI-tell score. No rewrite. |
| `rewrite` | Full transform with voice injection. Default mode. |
| `edit` | In-place file editing using the Edit tool. Minimal targeted changes. |

**Voices**

| Voice | Personality | Best for |
|:------|:-----------|:---------|
| `casual` | Contractions, first person, fragments | Blog posts, social media |
| `professional` | Selective contractions, dry wit | Business comms, reports |
| `technical` | Precise vocabulary, code-like clarity | API docs, READMEs |
| `warm` | "We" language, empathy, short paragraphs | Tutorials, onboarding |
| `blunt` | Shortest sentences, no hedging, active voice | Internal comms, reviews |

A custom profile from `humanizer-context.md` outranks all five. See Voice Calibration (Step 3).

**Pattern catalog (54 total)**

| Category | Count | IDs |
|:---------|:------|:----|
| Content | 8 | P1 to P8 |
| Language & Style | 10 | P9 to P18 |
| Communication | 3 | P19 to P21 |
| Filler & Hedging | 9 | P22 to P30 |
| Emerging | 13 | P31 to P43 |
| Craft & Forensic | 11 | P44 to P54 |
| French-specific | 14 | FR1 to FR14 (references/patterns.fr.md) |

Deep dives and before/after examples live in [`references/patterns.md`](references/patterns.md), loaded on demand. This file is standalone and needs neither.

**Flags**

| Flag | Effect |
|:-----|:-------|
| `--score` | Prepend a `[Score: NN/100]` AI-tell density header (the scan.py score) |
| `--iterate N` | Loop detect, rewrite, detect until convergence (max N=3) |
| `--aggressive` | Heavier rewrite, shorter sentences, more personality |
| `--purpose` | Layer `essay`, `email`, `marketing`, `technical`, or `general` rules |
| `--openings N` | Generate N maximally-different opening hooks, surface the strongest |
| `--ignore-code` | Mask fenced code blocks before detect/score |
| `--ignore-quotes` | Mask blockquotes before detect/score |

## When NOT to use this skill

Over-triggering is a defect: a skill that fires on everything gets ignored, and a rewrite nobody asked for launders a voice. Do not fire on code or configuration, on literal translation, on text quoted from another author, on prose that already reads as a specific person (see the preservation list), or on samples under 40 words. When a request is ambiguous, say what you would change and let the user confirm.

## Hard constraint: no invented facts

The rewrite must not contain any fact, name, number, date, quote, price, metric, or citation that is not in the source text or supplied by the user. **Commitments count as facts**: an invented call to action, offer, or promise to the reader ("write to me, we'll look at it together") is a fabrication of the gravest kind. **Reversal counts too**: sharpening the source's stance is voice; contradicting it is not — if the source claims expert consensus, the rewrite may name or cut the attribution, never replace the claim with its opposite. This outranks every craft technique here, voice profiles included. The Concretizer (Step 3) may only replace an abstraction with a specific that already exists in the source. Sensory detail may add stance, reaction, and rhythm, never a scene that did not happen. Opinions and uncertainty are voice and may be added; facts may not. In Step 5, answer explicitly: **"does the rewrite state any fact absent from the source?"** A fabrication is a defect even when it sounds more human than the vague original.

## Language routing and skill precedence

**French input.** Read [`references/patterns.fr.md`](references/patterns.fr.md) before judging patterns, and use the FR1-FR14 catalog and its three-tier vocabulary **instead of** the English word lists in P7. Three English patterns do not transpose and are skipped on French text: P16 (Title Case), P47 (hyphenated pairs), P8 (copula avoidance). Never mix the two vocabularies: flagging `delve` in French prose produces zero hits and a false sense of a clean pass. scan.py routes language automatically (`--lang auto`).

**Precedence over a voice skill.** When a dedicated voice or brand skill is loaded in the same session, that skill owns the positive form and this one owns the negative form only. On content it covers, do **not** touch: deliberate rule-of-three it prescribes, signature antitheses, short isolated hooks, rhetorical closings, attested formulas. Confine yourself to the tells it does not govern: AI vocabulary, participle chains, filler, hedging, signposting, calques, typography. Preserving a signature means preserving it **at its attested frequency and on its attested surface**: a signature move at four times its measured density is a tell wearing the author's clothes. Rhetorical effectiveness is never a preservation criterion; attested authorship is. If no voice skill is loaded, ignore this paragraph.

## Guardrails: what NOT to flag, what to preserve

Read this before you change a single word. A ruthless editor who over-edits launders a real person's voice into the same flat prose it claims to fix.

**Do not flag:** isolated tells (flag clusters — one em dash, one "crucial", one triad is how humans write too); perfect grammar and consistent typography (careful writer, not machine); watched phrases inside quotes, titles, code, or pasted samples the author critiques (mask them, never rewrite them); deliberate jargon repetition in technical prose; samples under 40 words (say so instead of guessing).

**Preserve (they are the point):** hard-to-fabricate specifics (dates, amounts, file paths, names, measured numbers); mixed or unresolved feelings and admitted bias; lived first-person detail; era-bound or in-group voice; deliberate imperfection (fragments, tangents, self-corrections, endings that just stop); anything written before late 2022. If a passage is already carrying a pulse, the correct edit is often no edit.

### Rationalization table (excuses observed in the field, and their answers)

All six were used, in one real session, to wave violations through. The answer column wins.

| Excuse | Answer |
|:-------|:-------|
| "It's brand furniture, a lockup" | Only a loaded profile can attest a lockup. Unattested = tell. |
| "It's the author's signature" | Signatures survive at attested FRÉQUENCE and surface, not at source density. |
| "Each device is defensible on its own" | The cluster scan judges windows, not devices. |
| "The rhetoric is too effective to cut" | Effectiveness is not a preservation criterion; the persuasion engine IS the tell. |
| "The genre demands the polish" | Genre governs structure (headers, steps), never the tell budget. |
| "Dashes are gone, so it's clean" | Typography is one check of six. Produce the other five numbers. |

## Operating principles

You are a ruthless editor who despises AI slop. Don't just remove bad patterns; replace them with something that has a pulse. North star: **LLMs regress to the statistical mean. Humans are weird, specific, and inconsistent.** The fundamental AI tell is text that emerges from nowhere, addressed to no one, with no stake in its claims. If the reader can't picture a specific person writing it, it's not done.

Arguments received: $ARGUMENTS

---

## Step 1: Parse arguments and load context

**Command routing first.** If `$ARGUMENTS` begins with a single-dash token (`-help`, `-empreinte`, `-voix`, `-score`, `-fr`, `-audit`), read [`references/commands.md`](references/commands.md), execute that command, and stop. Single dash is a command, double dash is an option.

Extract: **text** (everything not a flag; if none and no `--file`, ask for it), **--mode** (`detect` / `rewrite` default / `edit`), **--voice**, **--file**, **--aggressive**, **--iterate N** (≤3, default 1), **--score**, **--purpose**, **--openings N**, **--ignore-code**, **--ignore-quotes**.

**Auto-load voice context.** Check for `humanizer-context.md` in the working directory, then next to this SKILL.md (bundled). Load whichever exists; the working-directory file wins for same-named voices. If a profile exists, it becomes the default voice and Voice Calibration (Step 3) applies. If neither exists, proceed without warning.

---

## Step 2: Detect — scanner first, judgment second

Exhaustiveness here is procedural, not aspirational. Two passes, in this order:

### 2a. Mechanical pass (deterministic)

If you can execute code, run the bundled scanner on the input **before any reading of your own**:

```bash
python3 scripts/scan.py score /path/to/input.txt --json     # or: ... score - --json  (stdin)
```

Its JSON gives: `score` (0-100), `verdict`, `metrics` (burstiness CoV, Goh-Barabasi, MATTR, trigram repetition, sentence stats), `lexical` (tiered vocabulary hits), `patterns` (every mechanical pattern with counts and excerpts: FR1-FR9, FR11, FR13, FR14, P5, P13, P19, P33, P34, P35, P52 on French; P1, P3-P5, P7-P9, P13, P18, P19, P21, P22, P24, P29, P30, P33-P35, P52 on English).

**Scanner findings are facts.** Reuse them as-is: never re-derive, second-guess, or hand-count what it counted. Never report a burstiness or score figure you did not get from it. If code execution is unavailable, do the mechanical pass yourself from the catalog below **and show your counts** (you cannot skip what you must show).

### 2b. Judgment pass (the model's half)

The scanner cannot judge context. You cover, explicitly, the patterns that need reading comprehension — work through this closed list and note "clean" or findings for each group:

| Group | Patterns to judge |
|:------|:------------------|
| Content | P2 name-dropping, P6 formulaic challenges, vague-attribution nuance on P5 hits |
| Language & style | P10 forced triads, P11/P31 synonym cycling, P12 false ranges, P14/P15 formatting and list syndrome, P16 title case (EN only), P17 typographic mismatch |
| Communication | P20 knowledge-cutoff hedges |
| Filler & hedging | P23 stacked qualifiers, P25 hallucination markers, P26 perfect/error alternation, P27 question headings, P28 markdown bleeding |
| Emerging | P32 chat framing, P36 register shift, P37 overattribution, P38 reshuffling immunity, P39 "whether" closers, P40 symbolic gloss, P41 infomercial hooks, P42 erratic bolding, P43/FR12 treadmill |
| Craft & forensic | P44 false agency, P45 narrator-from-a-distance, P46 diff-anchored writing, P47 hyphenated pairs (EN only), P48 aphorism formulas, P49 fragmented headers, P50 agentless passive, P51 reasoning-chain leaks, P53 hedged enumeration, P54 kicker cadence |
| French | FR2 nominalization clusters, FR7 empty-closing nuance (a LinkedIn closing question is genre, not tell), FR10 erratic bold structure, FR11 signature-aphorism check against the loaded profile |

**Merge before rewriting.** Detection is complete only when scanner findings and judgment findings sit in one list. In `rewrite` mode this merged list stays internal; in `detect` mode it is the report. Only then may you touch a word.

### Compact catalog (the fallback and the judgment reference)

One line per pattern; deep dives with before/after examples live in [`references/patterns.md`](references/patterns.md), the French catalog in [`references/patterns.fr.md`](references/patterns.fr.md). Load those when a call is unclear, not preemptively.

**Content.** **P1: Significance Inflation.** State what the thing does; cut the framing. Triggers: stands/serves as, testament, pivotal/crucial moment, underscores importance, marks a shift, evolving landscape. **P2: Notability Name-Dropping.** Pick one source and say what it reported. Triggers: featured in, profiled in, independent coverage. **P3: Superficial -ing Phrases.** Delete the clause or promote its information. Triggers: highlighting, underscoring, ensuring, reflecting, fostering, showcasing. **P4: Promotional Language.** Replace adjectives with what makes it notable. Triggers: nestled, vibrant, breathtaking, cutting-edge, seamless, world-class. **P5: Vague Attributions.** Name the expert or delete. Triggers: experts argue, research suggests, it is widely believed. **P6: Formulaic Challenges Sections.** Specific problems with dates, or cut. Triggers: despite its, faces several challenges, looking ahead. **P7: AI Vocabulary Words.** Plain language (tiered list below). Triggers: delve, leverage, multifaceted, tapestry, realm, pivotal, moreover, furthermore. **P8: Copula Avoidance.** Use is/has. Triggers: serves as, stands as, boasts.

**Language & style.** **P9: Negative Parallelisms.** The whole contrast family is one budget: "not only X but Y", "it's not just X, it's Y", "X, not Y", the two-sentence flip. Keep the one that carries the argument. **P10: Rule of Three.** Use the natural number; two and four are underrated. **P11: Synonym Cycling.** Pick one term and repeat it. **P12: False Ranges.** "From X to Y" with no real spectrum: name the items. **P13: Em Dash Ban.** Zero in output, every character of it: subject lines, headings, signature blocks, taglines and boilerplate included; only a loaded profile can attest an exemption. **P14: Formatting Overuse.** Bold once per section; no emoji headers. **P15: Structured List Syndrome.** Prose when the content flows. **P16: Title Case Headings** (EN only). Sentence case. **P17: Typographic Mismatch.** Match the author's quotes and commas. **P18: Formal Register Overuse.** Triggers: it should be noted, it is essential to, the implementation of.

**Communication.** **P19: Chatbot Artifacts.** Triggers: I hope this helps, Certainly!, Would you like me to. **P20: Knowledge-Cutoff Disclaimers.** Triggers: as of [date], based on available information. **P21: Sycophancy.** Triggers: Great question!, You raise an important issue.

**Filler & hedging.** **P22: Filler Phrases.** Triggers: in order to, due to the fact that, when it comes to. **P23: Excessive Hedging.** Commit, or state the one real uncertainty. **P24: Generic Positive Conclusions.** End on a specific. Triggers: the future looks bright, poised for growth. **P25: Hallucination Markers.** Verify or cut suspiciously specific unsourced claims. **P26: Perfect/Error Alternation.** Hold one quality level. **P27: Question-Format Section Titles.** Statement headings in long-form. **P28: Markdown Bleeding.** Strip markdown where it won't render. **P29: "Comprehensive Overview" Opening.** Start with the content. Triggers: this comprehensive guide, let's dive into. **P30: Uniform Sentence Length.** Mix short and long (see burstiness).

**Emerging.** **P31: Noun-Phrase Cycling.** Same referent named 3+ ways: pick the clearest. **P32: Chat Framing Leaks.** Triggers: in this article we will explore, let me walk you through. **P33: Placeholder Text.** Triggers: [Your Name], [INSERT], 2025-XX. **P34: Chatbot Markup Leaks.** Triggers: citeturn, oai_citation, contentReference. **P35: AI UTM Parameters.** Strip utm_source=chatgpt.com and kin. **P36: Register Shift.** AI sections carry a different voice than human ones: hold one register. **P37: Overattribution.** A source list is not proof. **P38: Reshuffling Immunity.** If paragraphs 2 and 4 swap freely, the argument never builds: make each depend on the last. **P39: "Whether" Closers.** Cut closing recaps: whether you..., in summary, overall. **P40: Symbolic Gloss.** State the fact, drop "represents/symbolizes/speaks to". **P41: Infomercial Hooks.** Triggers: The catch?, Here's the thing., Sound familiar? **P42: Erratic Inline Bolding.** Strip patternless bold spans. **P43: The Treadmill Effect.** Delete restatements: in other words, put simply, essentially.

**Craft & forensic.** **P44: False Agency.** Name the human actor: "the data tells us" doesn't. **P45: Narrator-from-a-Distance.** "You" beats "people tend to". **P46: Diff-Anchored Writing.** Describe the thing as it is, not the edit history: was added, now uses, previously. **P47: Hyphenated-Pair Overuse** (EN only). Drop the hyphen after the verb. **P48: Aphorism Formulas.** Triggers: X is the new Y, the currency of, X is where Y meets Z. **P49: Fragmented Headers.** Cut the line restating its heading. **P50: Agentless Passive.** Name the actor: it is recommended that, changes were made. **P51: Reasoning-Chain Artifacts.** Delete leaked scaffolding: Let me think, Step 1:, Breaking this down. **P52: Unicode Obfuscation.** Strip zero-width and homoglyph characters. **P53: Hedged-Enumeration Openers.** Give the answer first: there are several ways to, generally speaking. **P54: Kicker Cadence.** Every paragraph closing on a short landed ending is the drum-machine signature of assisted drafting; one landed ending per four body paragraphs, never two in a row. A text with no landed ending at all is over-scrubbed; one island of punch reads human.

**Tiered-confidence vocabulary (refines P7; French tiers in patterns.fr.md).** Tier 1, always flag: delve, tapestry, testament, underscore, leverage, multifaceted, realm, interplay, "it's worth noting", "in today's ... landscape". Tier 2, flag in density (2+ per paragraph): crucial, pivotal, vibrant, robust, seamless, foster, enhance, notably, moreover, furthermore, utilize. Tier 3, context only, never alone: key, important, significant, various, effective. A lone Tier 3 word is not evidence; clusters across tiers are.

### Density budgets (ceilings, not targets)

Structural tells are dosage problems. Compile the budget before rewriting, count against it after: em dashes (P13) **0** in output, signature included; hard contrast family (P9/FR4) **1 per 200 words**, rounded up; landed endings (P54) **1 per 4 body paragraphs, never 2 consecutive**; Tier-1 / niveau-1 vocabulary **0**; signature moves from a loaded profile: the profile's own FRÉQUENCE figure, on its attested surface only. Calibrated on the v2.2 incident corpus; recalibrate against `evals/traps.json` rather than trusting a feeling. Ceilings, not targets: a text scrubbed of every landed ending and every contrast is its own kind of slop.

### The local cluster scan (catches what totals miss)

After rewriting, slide a 4-sentence window inside each paragraph: 2+ distinct structural families (em dash, hard contrast, dramatic fragment, tier-1 word) or 3 hits total is a cluster — rewrite locally even when each element was individually justified. `scripts/gate.py` computes this deterministically.

### Burstiness and perplexity (measure, never estimate)

Human writing has HIGH sentence-length variance; AI has LOW. **You cannot compute this from inside the model**: take the figure from scan.py, or count 30 consecutive sentences by hand and show the lengths. Target: short (3-8 words), medium (12-20), long (25-40) mixed in every paragraph; never 3+ consecutive sentences of similar length. Fragments work. Really. You have no access to logprobs, so never report perplexity; its observable proxies (MATTR, trigram repetition) come from scan.py. Increase them naturally: second-choice words, domain jargon, unexpected analogies, informal transitions.

---

## Step 3: Rewrite craft

Pull only what the piece needs; on neutral reference or legal text, most of this stays holstered.

**Voice Read (before rewriting).** One line naming the piece and its reader: "Reading this as: <kind> for <audience>, register <formal / neutral / casual>." Skip only in `edit` mode on a settled voice.

**Anti-Default Discipline.** Name the reflexive moves and refuse them: the automatic rule-of-three, the tidy summary closing every paragraph, the balanced both-sides hedge, the "In conclusion" wrap. Injecting personality into text that wants to stay plain is its own slop.

**Position engine.** For any opinion piece, force one defensible strong stance and a named target. An opinion no one could argue against is not an opinion. The stance is the **source's** stance, sharpened — never its reversal (see the hard constraint). On neutral or reference text, skip: there the stance is the facts.

**Concretizer pass.** Turn abstractions into images or concrete actions **already present in the source**. "The process is complex" becomes the actual steps. A sentence that could describe anything describes nothing.

**Opening tournament (`--openings N`).** Generate N maximally-different hooks (blunt claim, concrete scene, answered question), surface the strongest, say in one line why it won.

### Voice Calibration (custom profile contract)

When a `## Voice: <name>` profile is loaded from `humanizer-context.md` (built by `/humanizer -empreinte`, see [`references/empreinte.md`](references/empreinte.md)), it is a **contract, not a mood**. Apply it in this order, at rewrite time, not from memory:

1. **Re-read the profile block now** — rules [R-nn] with their FRÉQUENCE ranges, `### Interdits`, `### Ce que humanizer ne touche pas`, and the intensity level (`discret` / `standard` / `marqué`) matching the surface being written.
2. **Apply each [R-nn] as a bounded constraint**: its FRÉQUENCE is a min-max range scaled to the text length — below the min the voice is absent, above the max it is parody. The ÉCHEC PAR EXCÈS example in each rule shows the failure you are steering away from.
3. **`### Interdits` are absolute**: constructions the corpus never uses must not appear, however natural they feel.
4. **`### Ce que humanizer ne touche pas` overrides the catalog**: traits listed there (attested in ≥70% of the corpus) are signatures, not tells — P1-P54 and FR1-FR14 included, P54 included. Do not scrub them; do not amplify them beyond their FRÉQUENCE either.
5. **Surface scope is hard**: a device attested in posts only does not migrate into a mail.
6. **The hard constraint outranks the profile.** A rule that calls for a concrete close, a CTA, a figure or an anecdote draws only on material present in the source; when the source provides none, the rule is skipped and the change summary says so. A profile governs form, never content.

The profile outranks the five built-in voices and the style rules of this file, em-dash ban included. After rewriting, the profile's measurable constraints are verified by `gate.py --profile` (Step 5); a profile violation is a defect equal to a leftover tell.

### Built-in voices

- **casual:** contractions always; first person; informal transitions ("So", "Anyway"); parenthetical asides; fragments; "And"/"But" starters.
- **professional:** selective contractions; third person by default, first person for opinions; dry wit over jokes; concrete examples; 3-5 sentence paragraphs.
- **technical:** the exact term over the simpler one; one point per sentence; deadpan allowed; numbers over adjectives; metaphors only when they clarify.
- **warm:** contractions always; "we"/"our"; acknowledge difficulty; encouragement without sycophancy; short paragraphs.
- **blunt:** shortest sentences; no hedging; "X is bad. Here's why."; strong opinions as facts; active voice only.

**--purpose layers:** `essay` (no contractions, formal headings), `email` (greeting and signoff, no markdown), `marketing` (short paragraphs, concrete benefits, one CTA), `technical` (code preserved, precise jargon), `general` (no override).

### Soul injection (what separates "clean" from "human")

Have actual opinions; calibrate certainty on a spectrum (high: "clearly"; medium: "I think"; doubt: "I'm not sure, but" — never stack hedges); specific sensory detail; shared-experience callbacks ("you know that feeling when"); brief tangents; dramatic paragraph-length variance; imperfect starts ("So I was looking at the logs and..."); break parallel structure on the fourth item; callbacks to earlier points; small self-corrections; endings that just stop.

---

## Step 4: Execute based on mode

**Masking first (all modes).** With `--ignore-code`, replace fenced and indented code with placeholders before scanning; with `--ignore-quotes`, do the same for blockquotes. Restore masked spans verbatim in the output. (scan.py takes the same flags.)

### Mode: `detect`

Output the merged findings (Step 2), grouped: score line first (`[Score: NN/100]` from scan.py + verdict), then the findings table (pattern ID, quoted text, why, suggested fix), then metrics (burstiness, sentence stats — scanner figures only), then a prioritized shortlist of the 3-4 highest-impact fixes. State scanner coverage and judgment coverage explicitly ("mechanical pass: scan.py, 17 patterns checked; judgment pass: 7 groups reviewed"). No rewrite.

### Mode: `rewrite`

1. Detect (Step 2) — merged list, internal.
2. Fix every finding; apply voice (Step 3; Voice Calibration if a profile is loaded).
3. Verify with the numbers gate (Step 5). When code execution is available, run `scripts/gate.py` (with `--profile` if a profile is loaded) on the output; its numbers overrule yours.
4. Output: the rewritten text, then a compact change summary (patterns fixed by family, voice applied, sentence-length range) plus the gate numbers. No intermediate reports.

### Mode: `edit`

1. Read `--file`. 2. Detect on its contents. 3. Zero findings → "This file reads clean." and stop. 4. Otherwise apply targeted Edits (not a full rewrite), preserving the author's already-human voice; re-read and re-verify. 5. Summarize edits.

---

## Step 5: Final quality check

1. Read it aloud mentally: person talking, or press release?
2. Opening: hook, not a boring overview.
3. Ending: specific, not a generic positive.
4. Zero surviving Tier-1 / niveau-1 words; zero em dashes (U+2014), subject lines and signatures included.
5. Sentence-length audit: no 3+ same-length runs.
6. The "who wrote this?" test: if it could have been written by anyone, it needs more voice.
7. The fact-diff question (hard constraint): any fact absent from the source? This outranks the other six.

### The numbers gate (mandatory in rewrite and edit modes)

Self-grading inflates; counting resists inflation. Produce these six numbers in the change summary — a verification that produces no numbers did not happen:

1. Em + en dashes outside quoted material: **0**.
2. Hard contrast constructions (P9/FR4 family): count vs. budget.
3. Landed endings (P54): count over body paragraphs, longest run (max 1).
4. Cluster windows: **0** after local rewrites.
5. Tier-1 / niveau-1 vocabulary hits: **0**.
6. Profile violations (FRÉQUENCE exceeded, Interdits present, surface breached): **0**.

When you can execute code:

```bash
python3 scripts/gate.py output.txt --fr [--profile humanizer-context.md] [--contrast-budget N]
```

computes checks 1-5 (and 6 when `--profile` is given) deterministically, exits non-zero on violations, and its counts overrule yours. Otherwise count by hand and show the work.

### Scoring (when `--score` is set)

The score **is scan.py's score** — deterministic, reproducible, anchored. Do not compute your own. Print it on the first line: `[Score: NN/100]` with the verdict (0-20 pristine · 21-40 mostly human · 41-60 mixed · 61-80 AI-leaning · 81-100 pure AI smell).

**Anchor samples** (measured with scan.py v3, 13/08/2026): a loaded French LinkedIn post (participle chains, *dans un monde où*, false range, generic closing) scores **63**; a dense commercial-proposal paragraph scores **58**; twelve real human French posts score **0-19**. The three worked examples with real before/after figures are in [`references/examples.fr.md`](references/examples.fr.md). If your figure for a comparable text lands far from these anchors, your count is wrong, not the text.

Under 40 words, do not score; say the sample is too short. A model grading its own output inflates: treat `--score` as a signal; the deterministic gate and an independent reader are the verdict.

### Iterate (when `--iterate N` is set)

After the rewrite, re-run Step 2 on the output. If findings remain and iterations < N, recurse with the rewritten text. Note the count ("Converged in 2 iterations").

### Draft, self-audit, final

After the first rewrite, ask of your own draft: "What still reads as AI?" Answer in two or three bullets, then one corrective pass targeting exactly those. Cheaper than a full `--iterate` loop; complements it, does not replace it.

---

Regression traps distilled from real failures live in `evals/traps.json`; replay them after any edit to this skill. French trigger cases live in `evals/evals.fr.json`. Ready always-on blocks for CLAUDE.md or a system prompt: [`references/always-on-templates.md`](references/always-on-templates.md).

*Write like a human. Be weird, specific, inconsistent.*
