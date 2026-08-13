# Commands

Convention: a **single dash** introduces a command (what to do), a **double dash** introduces an option (how to do it). `/humanizer -empreinte` is a command; `/humanizer "text" --voice blunt` is the default command with an option.

If `$ARGUMENTS` starts with a single-dash token, route to the command below and ignore the normal rewrite pipeline. If it starts with anything else, or is empty, fall through to Step 1 of SKILL.md as usual.

| Command | What it does |
|:--|:--|
| `-help` | Print the table below and stop. No other output. |
| `-empreinte` | Interactive: collect a corpus, build a writing fingerprint, emit a reusable voice profile. See `references/empreinte.md`. |
| `-voix` | List the voice profiles available right now: the five built-ins, plus any profile found in `humanizer-context.md`. |
| `-score` | Detect mode on the following text. Report patterns and the 0-100 score. No rewrite. Equivalent to `--mode detect --score`. |
| `-fr` | Force the French catalog (`references/patterns.fr.md`) regardless of language detection, then rewrite normally. |
| `-audit` | Detect mode over a file or a folder of Markdown, one score line per file, worst first. Read-only. |

## `-help` output

Print exactly this, nothing more:

```
/humanizer <texte>              rewrite (default)
/humanizer -score <texte>       detect + score 0-100, no rewrite
/humanizer -fr <texte>          force French catalog
/humanizer -voix                list available voices
/humanizer -empreinte           build a voice profile from your own corpus
/humanizer -audit <path>        score files, worst first
/humanizer -help                this list

options: --voice casual|professional|technical|warm|blunt|<custom>
         --purpose essay|email|marketing|technical|general
         --aggressive  --iterate N  --score  --file <path>
         --ignore-code  --ignore-quotes  --openings N
```

## `-voix` output

List the five built-ins with a one-line description each. Then read `humanizer-context.md` from the working directory and from the skill folder (next to SKILL.md). If either exists and contains one or more `## Voice: <name>` blocks, list those too, marked `(custom)`; a bundled profile, when present, is the default voice when `--voice` is omitted, and a working-directory profile overrides a bundled one for same-named voices. If neither file is present, say so in one line and name `-empreinte` as the way to create one.

## Voice profile contract

`-empreinte` writes its result into `humanizer-context.md` at the project root, because SKILL.md already auto-loads that file. This is the whole persistence mechanism: no zip rebuild, no reinstall. A profile is one block, and several can live in the same file. A profile can also ship bundled inside the skill (`humanizer-context.md` next to SKILL.md); updating a bundled profile means re-uploading the skill zip.

```markdown
## Voice: <name>

STATUS: COMPLET | PARTIEL
CORPUS: <n> textes, <n> mots, surfaces: <liste>, daté du <date>

### Règles
[R-01] pouvoir discriminant : 5/5 — présence : 7/8 textes
RÈGLE: <impérative, actionnable>
FRÉQUENCE: <min–max, par texte ou pour 1000 mots>
PREUVE: « … » (T2) / « … » (T5)
ÉCHEC PAR EXCÈS: <l'exemple raté si la règle est sur-appliquée>
ÉCHEC PAR DÉFAUT: <ce qui manque si la règle saute>

[R-02] ...

### Paliers
discret: [R-01] · standard: [R-01] [R-03] · marqué: toutes

### Interdits
<constructions absentes du corpus, à ne jamais introduire>

### Ce que humanizer ne touche pas
<les traits signature que le catalogue P1-P54 / FR1-FR14 confondrait avec des tells>

```json gate
{"surface": "...", "dashes_max": 0, "contrast_budget": 2, "kicker_ratio_max": 0.4,
 "interdits": ["..."], "signatures": [{"motif": "...", "max": 1}]}
```
```

Once a profile exists, `--voice <name>` selects it and it **overrides** the built-in voices and the style rules of SKILL.md, including the em dash ban, exactly as the **Voice Calibration** section of SKILL.md (Step 3) prescribes: re-read the profile at rewrite time, apply each [R-nn] as a bounded min-max constraint, treat `### Interdits` as absolute, and never move a device outside its attested surface. A profile built from the author's real corpus outranks a generic rule about how humans write.

The `### Ce que humanizer ne touche pas` block is not decorative. It is the same guard as the precedence note in SKILL.md, written from evidence instead of from a brand doctrine: a trait attested across most of the corpus is a signature, not a tell, and scrubbing it is the failure mode.

The ```` ```json gate ```` block is the machine-checkable half of the contract: `scripts/gate.py output.txt --fr --profile humanizer-context.md` reads it and enforces its budgets, interdits and signature ceilings deterministically (check 6 of the numbers gate). `-empreinte` (see `references/empreinte.md`, Passe 6) emits it from measured figures, never from generic defaults.
