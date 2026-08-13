#!/usr/bin/env python3
"""Scanner déterministe du humanizer FR — détection + métriques + score 0-100.

Portage Python (Unicode, français d'abord) du cli/ upstream d'Aboudjem/humanizer-skill :
mêmes formules (burstiness CoV, Goh-Barabasi, TTR/MATTR, trigrammes, score composite
0.28/0.18/0.14/0.40 avec ancres documentées), plus le catalogue mécanique FR1-FR14 /
P-patterns en regex que le CLI upstream n'a pas. Zéro dépendance, déterministe :
la même entrée produit toujours les mêmes chiffres. Heuristiques assumées, pas un
détecteur entraîné.

Usage :
  python3 scan.py score <fichier|->  [--lang fr|en|auto] [--json]
                                     [--ignore-code] [--ignore-quotes]
  python3 scan.py scan <dossier>     [--json]           # .md/.txt récursif, pire d'abord
  python3 scan.py compare --before A --after B [--json]
  python3 scan.py mesures <fichier|->  [--json]         # tableau Passe 2 de l'empreinte
  python3 scan.py export-lexiques                       # dump JSON (landing page, CI)

Sortie score : {score, verdict, metrics, patterns[], lexical{}}. Exit 0.
Le modèle qui consomme ce JSON ne re-détecte PAS les patterns mécaniques : il les
reprend tels quels et n'ajoute que les patterns contextuels (jugement).
"""
import argparse
import json
import math
import os
import re
import sys
import unicodedata

# ---------------------------------------------------------------------------
# Tokenisation Unicode (le tokenizer upstream est ASCII-only et mutile "été")
# ---------------------------------------------------------------------------

WORD_RE = re.compile(r"[^\W\d_][\w'’-]*|\d+(?:[.,]\d+)?", re.UNICODE)

# Abréviations françaises courantes qui ne terminent pas une phrase.
# « etc. » n'y figure pas : il clôt très souvent la phrase en français, et le
# découpage n'opère de toute façon que devant une majuscule.
ABBREV = {"m", "mm", "mme", "mlle", "dr", "me", "st", "ste", "ex", "cf",
          "p", "pp", "art", "chap", "vol", "no", "env", "min", "max",
          "tel", "tél", "av", "bd", "resp", "vs"}

SENT_END = re.compile(r"(?<=[.!?…])\s+(?=[\"«“(\[]?[A-ZÀ-ÖØ-Þ0-9])")


def strip_marked(text, ignore_code=False, ignore_quotes=False):
    out = text
    if ignore_code:
        out = re.sub(r"```[\s\S]*?```", " ", out)
        out = re.sub(r"`[^`\n]*`", " ", out)
        out = re.sub(r"^(?: {4,}|\t).*$", " ", out, flags=re.M)
    if ignore_quotes:
        out = re.sub(r"^\s*>.*$", " ", out, flags=re.M)
    return out


def mask_quoted_spans(text):
    """Masque les citations courtes pour la détection de patterns (pas les métriques)."""
    return re.sub(r'"[^"\n]{1,300}"|«[^»\n]{1,300}»|“[^”\n]{1,300}”', ' « … » ', text)


def word_tokens(text):
    return [t.lower() for t in WORD_RE.findall(text)]


def split_sentences(text):
    flat = re.sub(r"\s+", " ", text).strip()
    if not flat:
        return []
    parts, buf = [], []
    for piece in SENT_END.split(flat):
        buf.append(piece)
        last = word_tokens(piece)
        # recolle si la "fin de phrase" était une abréviation ou une initiale
        if last and last[-1] in ABBREV or re.search(r"\b[A-ZÀ-Ö]\.\s*$", piece):
            continue
        parts.append(" ".join(buf).strip())
        buf = []
    if buf:
        parts.append(" ".join(buf).strip())
    return [s for s in parts if word_tokens(s)]


def paragraphs(text):
    return [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]


# ---------------------------------------------------------------------------
# Métriques (portage fidèle de cli/lib/metrics.js)
# ---------------------------------------------------------------------------

def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def stdev(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))


def type_token_ratio(tokens):
    return len(set(tokens)) / len(tokens) if tokens else 0.0


def mattr(tokens, window=50):
    if len(tokens) <= window:
        return type_token_ratio(tokens)
    total, n = 0.0, 0
    for i in range(len(tokens) - window + 1):
        total += len(set(tokens[i:i + window])) / window
        n += 1
    return total / n


def trigram_repetition(tokens):
    if len(tokens) < 3:
        return 0.0
    grams = [" ".join(tokens[i:i + 3]) for i in range(len(tokens) - 2)]
    return 1 - len(set(grams)) / len(grams)


def burstiness_gb(lengths):
    s, m = stdev(lengths), mean(lengths)
    return (s - m) / (s + m) if (s + m) else 0.0


# Ancres de conversion métrique brute -> composante 0..1, par langue.
# EN : valeurs upstream (validées par ses 25 tests). FR : recalibrées le 13/08/2026
# sur 12 textes humains réels (scores 1-20, MATTR 0.826-0.909, densité <= 0.0114)
# vs texte IA chargé (MATTR 0.858, densité 0.105) : le MATTR ne discrimine pas le
# français fléchi sur textes courts, la densité lexique+patterns discrimine à 9x.
# D'où : poids lexical monté à 0.55, diversité réduite à un garde-fou (ne pénalise
# que le vraiment répétitif), vocabMax relevé pour garder de la marge de saturation.
ANCHORS = {
    "fr": {"covHuman": 0.66, "ttrLow": 0.60, "ttrHigh": 0.82,
           "repMax": 0.18, "vocabMax": 0.05},
    "en": {"covHuman": 0.66, "ttrLow": 0.30, "ttrHigh": 0.72,
           "repMax": 0.18, "vocabMax": 0.035},
}
WEIGHTS = {
    "fr": {"burstiness": 0.25, "diversity": 0.10, "repetition": 0.10, "lexical": 0.55},
    "en": {"burstiness": 0.28, "diversity": 0.18, "repetition": 0.14, "lexical": 0.40},
}

VERDICTS_FR = [(20, "Irréprochable"), (40, "Majoritairement humain"),
               (60, "Mitigé"), (80, "Penchant IA"), (10**9, "Pur parfum d'IA")]


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


# ---------------------------------------------------------------------------
# Lexiques étagés (source de vérité : references/patterns.fr.md + upstream vocabulary.js)
# ---------------------------------------------------------------------------

LEXIQUES = {
    "fr": {
        # Niveau 1 : quasi jamais dans de la prose FR non assistée. Poids 1.0.
        "niveau1": [
            "incontournable", "plonger dans", "plongeons", "au cœur de", "au coeur de",
            "à l'ère de", "a l'ère de", "dans un monde où", "dans un monde ou",
            "force est de constater", "il convient de noter", "il est important de souligner",
            "s'impose comme", "témoigne de", "ne se limite pas à", "va bien au-delà de",
            "révolutionner", "révolutionne", "un enjeu majeur", "un levier puissant",
            "véritable tournant", "un véritable", "changement de paradigme",
            "paysage en constante évolution", "en constante évolution",
        ],
        # Niveau 2 : signaler en densité (2+ par paragraphe). Poids 0.6.
        "niveau2": [
            "crucial", "cruciale", "cruciaux", "essentiel", "essentielle",
            "pertinent", "pertinente", "robuste", "innovant", "innovante",
            "dynamique", "optimiser", "favoriser", "favorisant",
            "s'inscrire dans", "s'inscrit dans", "refléter", "reflète",
            "notamment", "en effet", "par ailleurs", "de plus", "en outre",
            "toutefois", "néanmoins", "dès lors", "en somme",
            "maximiser", "mesurable",
        ],
        # Niveau 3 : contexte seulement, jamais scoré. Documentaire.
        "niveau3": ["important", "significatif", "divers", "efficace", "utile", "puissant"],
    },
    "en": {
        "niveau1": [
            "delve", "delves", "delving", "tapestry", "testament", "underscore",
            "underscores", "underscoring", "leverage", "leverages", "leveraging",
            "multifaceted", "realm", "interplay", "seamless", "seamlessly",
            "groundbreaking", "it's worth noting", "it is worth noting",
            "it is important to note", "in today's", "rapidly evolving",
            "the future looks bright", "in conclusion", "cutting-edge",
            "walks of life", "push the boundaries",
        ],
        "niveau2": [
            "crucial", "pivotal", "vibrant", "robust", "foster", "fosters",
            "fostering", "enhance", "enhances", "enhancing", "showcase",
            "showcases", "notably", "moreover", "furthermore", "garner",
            "bolster", "utilize", "utilizes", "reshaping", "poised",
            "thrive", "thrives",
        ],
        "niveau3": ["key", "important", "significant", "various", "effective",
                     "valuable", "powerful", "essential"],
    },
}

W_N1, W_N2 = 1.0, 0.6

# ---------------------------------------------------------------------------
# Catalogue mécanique en regex. Chaque hit: {id, nom, extraits, count, poids}.
# Les IDs renvoient à SKILL.md / references/patterns.fr.md. Sous-ensemble
# mécanique du catalogue : les patterns de jugement (P5 fin, P25, P36, P38,
# FR12...) restent au modèle.
# ---------------------------------------------------------------------------

# FR1 : détection générique des participes présents (-ant) avec liste d'exclusion
# des mots courants en -ant qui n'en sont pas. Le seuil "2+ par phrase" limite
# les faux positifs restants (adjectifs en -ant isolés).
NON_PARTICIPES = {"avant", "pendant", "maintenant", "autant", "pourtant", "cependant",
                  "durant", "tant", "instant", "enfant", "montant", "restaurant",
                  "courant", "vivant", "suivant", "géant", "croissant", "puissant",
                  "brillant", "important", "indépendant", "correspondant", "constant",
                  "élégant", "méchant", "savant", "gagnant", "perdant", "débutant",
                  "consultant", "assistant", "quant", "devant", "auparavant"}

PATTERNS = {
    "fr": [
        ("FR1", "Participes présents en chapelet",
         r"\b(?:en\s+|s['’])?\w{3,}ant\b",
         2, "participes"),  # 2+ participes réels dans la même phrase
        ("FR2", "Nominalisations et verbes vides",
         r"\b(?:procéd(?:er|ons|ez|e|ent)|effectu(?:er|ons|ez|e|ent)|réalis(?:er|ons|ez|e|ent)|apport(?:er|ons|ez|e|ent)|mett(?:re|ons|ez|ent) en œuvre)\s+(?:à\s+)?(?:une?|la|l'|des?\s)?\s*(?:mise en place|analyse|optimisation|étude|amélioration|démarche)\b|\bdans le cadre de la mise en place\b",
         2, "each"),
        ("FR3", "« Que vous soyez X ou Y »",
         r"\bque vous soyez\b[^.!?]{0,80}\bou\b",
         3, "each"),
        ("FR4", "Parallélisme négatif",
         r"\b(?:il ne s'agit pas (?:seulement|simplement)|ce n'est pas (?:seulement|simplement|juste)[^.!?]{0,60},?\s*(?:c'est|mais bien)|loin d'être un(?:e)? simple|bien plus qu'un(?:e)?)\b",
         5, "each"),
        ("FR5", "Triade adjectivale",
         r"\b\w+(?:ants?|antes?|ents?|entes?|ifs?|ives?|ables?|ibles?|els?|elles?|ennes?|eux|euses?|iques?|ale?s?|aux|aires?|és?|ées?)\s*,\s*\w+\s+et\s+\w+(?:ants?|antes?|ents?|entes?|ifs?|ives?|ables?|ibles?|els?|elles?|ennes?|eux|euses?|iques?|ale?s?|aux|aires?|és?|ées?)\b",
         3, "each"),
        ("FR6", "Signposting",
         r"\b(?:dans cet article,? nous allons|nous allons (?:explorer|découvrir|voir)|voyons ensemble|passons maintenant à|sans plus attendre|décryptage)\b",
         4, "each"),
        ("FR7", "Clôtures génériques",
         r"\b(?:en conclusion|pour aller plus loin|n'hésitez pas à|prêt à franchir le pas|et vous, qu'en pensez-vous|l'avenir s'annonce|alors, prêts? à|à votre (?:entière )?disposition)\b",
         4, "each"),
        ("FR8", "Anglicismes de traduction",
         r"\b(?:adresser (?:un problème|une question|ce sujet)|impacter|impacte(?:nt)?\b|au final|en termes de|définitivement\b|challenger\s+(?:les|la|le|nos|vos))\b",
         2, "each"),
        ("FR9", "Cadratin collé à l'anglaise",
         r"\w—\w",
         5, "each"),
        ("FR11", "Aphorismes fabriqués",
         r"\b(?:est le nouveau\b|est la nouvelle\b|le nouvel or\b|nouveau pétrole|est le langage de demain|n'est pas un(?:e)? \w+, c'est un(?:e)?)\b",
         4, "each"),
        ("P5", "Attribution vague",
         r"\b(?:les experts s'accordent|des études (?:montrent|suggèrent)|selon (?:les|des) (?:experts|études)|il est largement admis|de nombreuses études)\b",
         3, "each"),
        # Le tiret espacé « mot — mot » est de la typographie française légitime
        # (FR9) : poids réduit au scan d'entrée. Le cadratin collé est FR9 (poids 5).
        # La doctrine zéro-cadratin de la SORTIE réécrite reste portée par gate.py.
        ("P13", "Tiret cadratin",
         r"—",
         2, "each"),
        ("P19", "Artefacts de chatbot",
         r"\b(?:j'espère que cela (?:vous )?aide|j'espère que ce (?:message|mail|courriel) vous trouve|bien sûr !|voici un(?:e)? (?:aperçu|analyse|synthèse)|n'hésitez pas si vous avez)\b",
         5, "each"),
        ("P33", "Placeholders non remplis",
         r"\[(?:votre|insérez|insérer|noms?|dates?)\b[^\]]*\]|lorem ipsum|20\d\d-XX",
         6, "each"),
        ("P34", "Balisage de chatbot",
         r"citeturn\d|oai_citation|contentReference\[oaicite|\[attached_file:\d",
         6, "each"),
        ("P35", "UTM de source IA",
         r"utm_source=(?:chatgpt\.com|openai|copilot\.com|grok\.com)",
         6, "each"),
        ("P52", "Caractères invisibles",
         "[​‌‍­⁠]",
         6, "each"),
    ],
    "en": [
        ("P1", "Significance inflation",
         r"\b(?:pivotal moment|testament to|marks? an? (?:pivotal|important|significant) (?:moment|chapter|milestone)|underscor(?:e|es|ing) the importance|reflects? broader|setting the stage|indelible mark)\b",
         4, "each"),
        ("P3", "Superficial -ing phrases",
         r"\b(?:highlighting|underscoring|emphasizing|ensuring|reflecting|symbolizing|cultivating|fostering|encompassing|showcasing)\s",
         2, "each"),
        ("P4", "Promotional language",
         r"\b(?:nestled|cutting-edge|seamless|world-class|state-of-the-art|in the heart of|must-visit|breathtaking|stunning|vibrant)\b",
         3, "each"),
        ("P5", "Vague attributions",
         r"\b(?:experts (?:argue|believe|suggest)|research suggests|some critics argue|several sources|it is widely believed|industry reports)\b",
         3, "each"),
        ("P7", "AI vocabulary",
         r"\b(?:delve|delves|delving|leverage|leverages|utilize|utilizing|multifaceted|tapestry|testament|pivotal|intricate|intricacies|moreover|furthermore|it'?s worth noting|it'?s important to note|at the end of the day)\b",
         3, "each"),
        ("P8", "Copula avoidance",
         r"\b(?:serves as|stands as|represents an? )\b",
         2, "each"),
        ("P9", "Negative parallelism",
         r"\b(?:it'?s not (?:just|merely|simply) [a-z\s]{1,40}, it'?s|not only [a-z\s]{1,40} but)\b",
         5, "each"),
        ("P13", "Em dash", "—", 4, "each"),
        ("P18", "Formal register",
         r"\b(?:it should be noted|it is essential to|in the context of|the implementation of)\b",
         3, "each"),
        ("P19", "Chatbot artifact",
         r"\b(?:I hope this helps|Of course!|Certainly!|You'?re absolutely right|Would you like me to|Let me know if)\b",
         5, "each"),
        ("P21", "Sycophancy",
         r"\b(?:Great question|That'?s an excellent point|You raise a very important issue)\b",
         5, "each"),
        ("P22", "Filler phrases",
         r"\b(?:in order to|due to the fact that|at this point in time|in the event that|has the ability to|in today'?s rapidly evolving|when it comes to)\b",
         3, "each"),
        ("P24", "Generic conclusion",
         r"\b(?:the future looks bright|exciting times lie ahead|poised for growth|step in the right direction)\b",
         4, "each"),
        ("P29", "Comprehensive overview",
         r"\b(?:this comprehensive (?:guide|overview|analysis)|in this article, we will explore|let'?s dive (?:into|in)|delves into)\b",
         4, "each"),
        ("P33", "Placeholders", r"\[(?:Your|INSERT)[^\]]*\]|lorem ipsum|20\d\d-XX", 6, "each"),
        ("P34", "Chatbot markup leak",
         r"citeturn\d|oai_citation|contentReference\[oaicite|\[attached_file:\d",
         6, "each"),
        ("P35", "UTM source from AI",
         r"utm_source=(?:chatgpt\.com|openai|copilot\.com|grok\.com)",
         6, "each"),
        ("P52", "Unicode obfuscation", "[​‌‍­⁠]", 6, "each"),
    ],
}

CONNECTEURS_TETE = re.compile(
    r"^(?:De plus|Par ailleurs|En outre|En effet|Ainsi|Néanmoins|Cependant|Toutefois|Dès lors|Par conséquent)\b[, ]",
    re.I)

FR_STOPWORDS = {"le", "la", "les", "de", "des", "du", "et", "est", "un", "une",
                "pour", "dans", "que", "qui", "ne", "pas", "vous", "nous", "sur",
                "avec", "ce", "cette", "il", "elle", "au", "aux", "en", "à"}


def detect_lang(tokens):
    if not tokens:
        return "en"
    hits = sum(1 for t in tokens[:400] if t in FR_STOPWORDS)
    return "fr" if hits / min(len(tokens), 400) > 0.12 else "en"


def lexical_tells(text_lower, tokens, lang):
    """Compte les entrées du lexique. Multi-mots : frontières de mots obligatoires
    (« de plus » ne doit pas matcher « de plusieurs »)."""
    lex = LEXIQUES[lang]
    n1 = n2 = 0
    hits1, hits2 = [], []
    for entry in lex["niveau1"]:
        c = (len(re.findall(r"\b" + re.escape(entry) + r"\b", text_lower))
             if " " in entry else sum(1 for t in tokens if t == entry))
        if c:
            n1 += c
            hits1.append(f"{entry} ×{c}" if c > 1 else entry)
    for entry in lex["niveau2"]:
        c = (len(re.findall(r"\b" + re.escape(entry) + r"\b", text_lower))
             if " " in entry else sum(1 for t in tokens if t == entry))
        if c:
            n2 += c
            hits2.append(f"{entry} ×{c}" if c > 1 else entry)
    weighted = n1 * W_N1 + n2 * W_N2
    return {"niveau1": n1, "niveau2": n2, "niveau1_hits": hits1, "niveau2_hits": hits2,
            "weighted": weighted,
            "density": weighted / len(tokens) if tokens else 0.0}


def detect_patterns(text, lang):
    """Passe mécanique exhaustive : chaque regex du catalogue est essayée."""
    masked = mask_quoted_spans(text)
    found = []
    for pid, name, rx, weight, scope in PATTERNS[lang]:
        # EN : P19/P21 sensibles à la casse ("Of course!") ; en FR l'inflexion
        # de casse ne porte pas de signal, tout est insensible.
        flags = 0 if (lang == "en" and pid in ("P19", "P21")) else re.I
        creg = re.compile(rx, flags)
        if scope == "participes":
            count, examples = 0, []
            for sent in split_sentences(masked):
                hits = [h for h in creg.findall(sent)
                        if re.sub(r"^(?:en\s+|s['’])", "", h).lower() not in NON_PARTICIPES]
                if len(hits) >= 2:
                    count += 1
                    examples.append(sent[:90])
            if count:
                found.append({"id": pid, "nom": name, "count": count,
                              "poids": weight, "extraits": examples[:3]})
        else:
            matches = [m.group(0) if hasattr(m, "group") else m
                       for m in creg.finditer(masked)]
            if matches:
                found.append({"id": pid, "nom": name, "count": len(matches),
                              "poids": weight,
                              "extraits": [str(x)[:60] for x in matches[:3]]})
    # FR13 : connecteurs scolaires en tête de paragraphes (structurel)
    if lang == "fr":
        pars = paragraphs(masked)
        openers = [bool(CONNECTEURS_TETE.match(p)) for p in pars]
        consec = max_run(openers)
        total = sum(openers)
        if consec >= 2 or total >= 3:
            found.append({"id": "FR13", "nom": "Connecteurs scolaires en tête de paragraphe",
                          "count": total, "poids": 3,
                          "extraits": [p.split(",")[0][:40] for p, o in zip(pars, openers) if o][:3]})
    # FR14/P30 : runs de phrases de longueur uniforme (structurel)
    lengths = [len(word_tokens(s)) for s in split_sentences(text)]
    runs = uniform_runs(lengths)
    if runs:
        found.append({"id": "FR14" if lang == "fr" else "P30",
                      "nom": "Uniformité rythmique (runs de phrases de longueur similaire)",
                      "count": len(runs), "poids": 3,
                      "extraits": [f"phrases {a+1}-{b+1} ({lengths[a:b+1]} mots)" for a, b in runs[:3]]})
    return found


def max_run(bools):
    best = cur = 0
    for b in bools:
        cur = cur + 1 if b else 0
        best = max(best, cur)
    return best


def uniform_runs(lengths, span=5, min_run=3):
    """Runs de >= min_run phrases consécutives à ±span mots les unes des autres.
    Min/max maintenus au fil de l'eau : pas de re-slice quadratique."""
    runs, start = [], 0
    lo = hi = lengths[0] if lengths else 0
    for i in range(1, len(lengths) + 1):
        cut = i == len(lengths)
        if not cut:
            nlo, nhi = min(lo, lengths[i]), max(hi, lengths[i])
            cut = abs(lengths[i] - lengths[start]) > span or nhi - nlo > span
            if not cut:
                lo, hi = nlo, nhi
        if cut:
            if i - start >= min_run:
                runs.append((start, i - 1))
            start = i
            if i < len(lengths):
                lo = hi = lengths[i]
    return runs


# ---------------------------------------------------------------------------
# Score composite (formule upstream, densité lexicale enrichie des patterns)
# ---------------------------------------------------------------------------

def analyze(text, lang="auto", ignore_code=False, ignore_quotes=False):
    text = unicodedata.normalize("NFC", text).replace("’", "'")
    cleaned = strip_marked(text, ignore_code, ignore_quotes)
    tokens = word_tokens(cleaned)
    if lang == "auto":
        lang = detect_lang(tokens)
    sents = split_sentences(cleaned)
    lengths = [len(word_tokens(s)) for s in sents]

    m = mean(lengths)
    sd = stdev(lengths)
    cov = sd / m if m else 0.0
    metrics = {
        "words": len(tokens),
        "sentences": len(sents),
        "mean_sentence_length": round(m, 2),
        "sentence_length_stdev": round(sd, 2),
        "burstiness": round(cov, 3),          # CoV, proxy humain-vs-IA
        "burstiness_gb": round(burstiness_gb(lengths), 3),
        "ttr": round(type_token_ratio(tokens), 3),
        "mattr": round(mattr(tokens), 3),
        "trigram_repetition": round(trigram_repetition(tokens), 3),
        "short_sample": len(tokens) < 40,
    }

    # Les citations sont masquées pour le lexique comme pour les patterns
    # (un texte humain qui CITE du slop ne doit pas en porter le score) ;
    # les métriques (burstiness, MATTR...) restent sur le texte complet.
    masked_for_tells = mask_quoted_spans(cleaned)
    lex = lexical_tells(masked_for_tells.lower(), word_tokens(masked_for_tells), lang)
    patterns = detect_patterns(cleaned, lang)

    # densité lexicale élargie : lexique pondéré + hits de patterns pondérés/6
    pattern_weight = sum(p["count"] * p["poids"] for p in patterns) / 6.0
    density = ((lex["weighted"] + pattern_weight) / len(tokens)) if tokens else 0.0

    anch, wts = ANCHORS[lang], WEIGHTS[lang]
    low_burst = clamp((anch["covHuman"] - metrics["burstiness"]) / anch["covHuman"], 0, 1)
    low_div = clamp((anch["ttrHigh"] - metrics["mattr"]) / (anch["ttrHigh"] - anch["ttrLow"]), 0, 1)
    high_rep = clamp(metrics["trigram_repetition"] / anch["repMax"], 0, 1)
    lexical = clamp(density / anch["vocabMax"], 0, 1)
    raw = (wts["burstiness"] * low_burst + wts["diversity"] * low_div
           + wts["repetition"] * high_rep + wts["lexical"] * lexical)
    score = 0 if not tokens else round(100 * raw)
    verdict = "Pas de texte" if not tokens else next(v for cap, v in VERDICTS_FR if score <= cap)

    return {"lang": lang, "score": score, "verdict": verdict,
            "metrics": metrics, "lexical": lex, "patterns": patterns,
            "components": {"low_burstiness": round(low_burst, 3),
                            "low_diversity": round(low_div, 3),
                            "high_repetition": round(high_rep, 3),
                            "lexical_density": round(lexical, 3)}}


# ---------------------------------------------------------------------------
# Mode mesures : le tableau chiffré de la Passe 2 de references/empreinte.md
# ---------------------------------------------------------------------------

PRONOMS = {
    "je": re.compile(r"\b(?:je|j'|j’)", re.I),
    "on": re.compile(r"\bon\b", re.I),
    "nous": re.compile(r"\bnous\b", re.I),
    "vous": re.compile(r"\bvous\b", re.I),
    "il/elle": re.compile(r"\b(?:il|elle|ils|elles)\b", re.I),
}


def mesures(text):
    text = unicodedata.normalize("NFC", text).replace("’", "'")
    tokens = word_tokens(text)
    sents = split_sentences(text)
    pars = paragraphs(text)
    lengths = sorted(len(word_tokens(s)) for s in sents)
    n = len(lengths)
    kw = max(len(tokens), 1) / 1000.0

    def pct(f):
        return round(100 * sum(1 for l in lengths if f(l)) / n, 1) if n else 0.0

    ponct = {c: text.count(c) for c in [":", ";", "…", "?", "!", "(", "—", "–"]}
    persons = {}
    for name, rx in PRONOMS.items():
        persons[name] = round(100 * sum(1 for s in sents if rx.search(s)) / n, 1) if n else 0.0
    openers = [" ".join(word_tokens(p)[:2]) for p in pars]
    subord = sum(1 for s in sents if re.search(
        r"\b(?:que|qui|dont|lorsque|parce que|alors que|tandis que|si\b|quand)\b", s, re.I))
    chiffres = len(re.findall(r"\b\d[\d\s.,%€$hk]*\b", text))
    noms_propres = len(re.findall(r"(?<=[a-zà-ÿ,;] )[A-ZÀ-Ö][a-zà-ÿ]+", text))

    return {
        "textes_mots": len(tokens), "phrases": n, "paragraphes": len(pars),
        "longueur_phrase": {
            "mediane": lengths[n // 2] if n else 0,
            "ecart_type": round(stdev(lengths), 1), "min": lengths[0] if n else 0,
            "max": lengths[-1] if n else 0,
            "pct_moins_8": pct(lambda l: l < 8), "pct_plus_30": pct(lambda l: l > 30)},
        "longueur_paragraphe_mediane_phrases":
            sorted(len(split_sentences(p)) for p in pars)[len(pars) // 2] if pars else 0,
        "ratio_subordonnees": round(subord / n, 2) if n else 0,
        "ponctuation_pour_1000_mots": {k: round(v / kw, 1) for k, v in ponct.items() if v},
        "chiffres_dates_pour_1000_mots": round(chiffres / kw, 1),
        "noms_propres_pour_1000_mots_approx": round(noms_propres / kw, 1),
        "personne_dominante_pct_phrases": persons,
        "diversite_ouvertures_paragraphe":
            round(len(set(openers)) / len(openers), 2) if openers else 0,
        "burstiness": round((stdev(lengths) / mean(lengths)) if mean(lengths) else 0, 3),
        "mattr": round(mattr(tokens), 3),
        "trigram_repetition": round(trigram_repetition(tokens), 3),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def read_input(path):
    return sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()


def fmt_score(r):
    lines = [f"score={r['score']}/100  verdict={r['verdict']}  lang={r['lang']}  "
             f"mots={r['metrics']['words']}  burstiness={r['metrics']['burstiness']}  "
             f"mattr={r['metrics']['mattr']}"]
    if r["metrics"]["short_sample"]:
        lines.append("  ATTENTION : <40 mots, score non fiable")
    for p in r["patterns"]:
        lines.append(f"  {p['id']} {p['nom']} ×{p['count']} : " + " | ".join(p["extraits"]))
    if r["lexical"]["niveau1_hits"]:
        lines.append("  lexique niveau 1 : " + ", ".join(r["lexical"]["niveau1_hits"]))
    if r["lexical"]["niveau2_hits"]:
        lines.append("  lexique niveau 2 : " + ", ".join(r["lexical"]["niveau2_hits"]))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["score", "scan", "compare", "mesures", "export-lexiques"])
    ap.add_argument("path", nargs="?", default="-")
    ap.add_argument("--before")
    ap.add_argument("--after")
    ap.add_argument("--lang", choices=["fr", "en", "auto"], default="auto")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--ignore-code", action="store_true")
    ap.add_argument("--ignore-quotes", action="store_true")
    a = ap.parse_args()

    if a.mode == "export-lexiques":
        print(json.dumps({"lexiques": LEXIQUES,
                          "patterns": {lg: [{"id": p[0], "nom": p[1], "regex": p[2],
                                              "poids": p[3], "scope": p[4]} for p in pats]
                                        for lg, pats in PATTERNS.items()},
                          "anchors": ANCHORS, "weights": WEIGHTS},
                         ensure_ascii=False, indent=1))
        return

    if a.mode == "compare":
        rb = analyze(read_input(a.before), a.lang, a.ignore_code, a.ignore_quotes)
        ra = analyze(read_input(a.after), a.lang, a.ignore_code, a.ignore_quotes)
        out = {"before": {"score": rb["score"], "patterns": sum(p["count"] for p in rb["patterns"])},
               "after": {"score": ra["score"], "patterns": sum(p["count"] for p in ra["patterns"])},
               "delta_score": ra["score"] - rb["score"]}
        print(json.dumps(out, ensure_ascii=False, indent=1) if a.json else
              f"before={out['before']['score']}  after={out['after']['score']}  delta={out['delta_score']:+d}")
        return

    if a.mode == "scan":
        rows = []
        for root, dirs, files in os.walk(a.path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
            for f in files:
                if f.endswith((".md", ".txt")):
                    fp = os.path.join(root, f)
                    r = analyze(open(fp, encoding="utf-8").read(), a.lang,
                                a.ignore_code, a.ignore_quotes)
                    rows.append((r["score"], fp, r["verdict"]))
        rows.sort(reverse=True)
        if a.json:
            print(json.dumps([{"score": s, "file": f, "verdict": v} for s, f, v in rows],
                             ensure_ascii=False, indent=1))
        else:
            for s, f, v in rows:
                print(f"{s:3d}  {v:24s}  {f}")
        return

    text = read_input(a.path)
    if a.mode == "mesures":
        r = mesures(text)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return

    r = analyze(text, a.lang, a.ignore_code, a.ignore_quotes)
    print(json.dumps(r, ensure_ascii=False, indent=1) if a.json else fmt_score(r))


if __name__ == "__main__":
    main()
