"""Core pluralisation logic.

Design decisions
----------------
* We return ``str`` always; there is no ``count`` parameter. The brief is about
  deriving the plural *form* of a word, not choosing between singular and plural
  based on a number. That keeps the function pure and trivial to compose.
* Irregular forms are stored in a frozen dict mapping singular -> plural.
  Compound nouns ("mother-in-law", "court-martial") are included because their
  plural is non-obvious and frequently wrong in naive implementations.
* We lowercase the input for matching against the irregular table, but return
  the plural using the original word's casing only when the entire input was
  either all-caps or title-case. This covers the common "Child"/"CHILD" cases
  without pretending to be a full case-preservation engine.
* Uncountable nouns ("sheep", "fish", "series", ...) short-circuit and return
  the input unchanged, again with case preservation.
* Regular suffix rules are ordered most-specific-first, so "city" hits the
  ``consonant + y`` rule before the generic ``s`` rule.
"""

from __future__ import annotations

import re
from typing import Mapping

# ---------------------------------------------------------------------------
# Irregular and uncountable forms.
# ---------------------------------------------------------------------------
#
# These tables were assembled from the usual offenders. The keys are
# lowercase singulars; values are lowercase plurals.

_IRREGULAR: Mapping[str, str] = {
    # Classic Germanic/Old English irregulars.
    "man": "men",
    "woman": "women",
    "child": "children",
    "brother": "brothers",  # siblings; the ``brethren`` reading is deliberately out of scope.
    "ox": "oxen",
    "foot": "feet",
    "tooth": "teeth",
    "goose": "geese",
    "mouse": "mice",
    "louse": "lice",
    "person": "people",
    # Words of foreign origin that keep their foreign plural.
    "criterion": "criteria",
    "phenomenon": "phenomena",
    "datum": "data",
    "medium": "media",
    "analysis": "analyses",
    "crisis": "crises",
    "thesis": "theses",
    "hypothesis": "hypotheses",
    "oasis": "oases",
    "parenthesis": "parentheses",
    "ellipsis": "ellipses",
    "neurosis": "neuroses",
    "diagnosis": "diagnoses",
    "schema": "schemata",
    "stigma": "stigmata",
    "lemma": "lemmata",
    "stratum": "strata",
    "die": "dice",
    " goose": "geese",  # defensive; the non-prefixed entry already covers it.
    # -is -> -es words handled separately below; these are the outliers.
    "moose": "moose",
    # Hyphenated compounds whose plural attaches to the *head* noun, not the
    # last token. Listed as full strings for reliable lookup.
    "mother-in-law": "mothers-in-law",
    "father-in-law": "fathers-in-law",
    "son-in-law": "sons-in-law",
    "daughter-in-law": "daughters-in-law",
    "brother-in-law": "brothers-in-law",
    "sister-in-law": "sisters-in-law",
    "attorney-general": "attorneys-general",
    "court-martial": "courts-martial",
    "notary-public": "notaries-public",
    "passer-by": "passers-by",
    "hanger-on": "hangers-on",
}

# Mass nouns and words that happen to share singular and plural. Returning the
# input unchanged here is the correct English answer, not a cop-out.
_UNCOUNTABLE: frozenset[str] = frozenset(
    {
        "sheep",
        "fish",
        "deer",
        "species",
        "series",
        "scissors",
        "pliers",
        "tweezers",
        "glasses",
        "pants",
        "trousers",
        "shorts",
        "jeans",
        "means",
        "news",
        "information",
        "furniture",
        "luggage",
        "baggage",
        "equipment",
        "rice",
        "money",
        "fruit",
        "moose",
        "aircraft",
        "hovercraft",
        "spacecraft",
        "salmon",
        "trout",
        "swine",
        "bison",
        "shrimp",
        "offspring",
        "data",  # "data" is both the plural of "datum" and a mass noun.
    }
)


# ---------------------------------------------------------------------------
# Regular suffix rules.
# ---------------------------------------------------------------------------
#
# Each rule is (regex, suffix_to_append). The regex must match the *end* of the
# word. Rules are evaluated top-to-bottom; the first match wins. Order matters:
# more specific patterns ("bus" -> "buses", not "busses") come first.
#
# The regexes are anchored with $ in _apply_rules so individual rules stay
# readable.

_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    # Words ending in sibilant sounds take "es".
    (re.compile(r"(?:s|x|z|ch|sh)$"), "es"),
    # "consonant + y" -> drop y, add ies. Vowel + y just takes s ("boy" ->
    # "boys"). The negative lookbehind below excludes the vowel cases.
    (re.compile(r"[^aeiou]y$"), "ies"),
    # Words ending in a consonant + o often take "es" ("potato" ->
    # "potatoes"). We deliberately do NOT try to encode the "photo"/
    # "radio" exceptions here because they are numerous and inconsistent; the
    # irregular table is the escape hatch for those that matter to a caller.
    (re.compile(r"[^aeiou]o$"), "es"),
    # "f" / "fe" -> "ves" for the common cases. Not all words follow this
    # ("roof" -> "roofs", "chief" -> "chiefs"), so callers must add overrides
    # to _IRREGULAR for the ones they care about. We match the *common*
    # -lf/-rf/-fe words explicitly to avoid false positives like "belief".
    (re.compile(r"(?:[^ei]f|fe)$"), "ves"),
)


def _preserve_case(original: str, plural_lower: str) -> str:
    """Re-apply the casing of ``original`` to ``plural_lower``.

    Only ALL CAPS and Title Case get special treatment. Mixed-case input is
    returned lowercased, because guessing how to pluralise "McDonald" or
    "iPhone" is a losing game.
    """
    if not original:
        return plural_lower
    if original.isupper():
        return plural_lower.upper()
    if original.istitle():
        return plural_lower.title()
    return plural_lower


def _apply_rules(word_lower: str) -> str | None:
    """Return the plural of ``word_lower`` by suffix rules, or ``None`` to fall
    through to the default ``+s``.
    """
    for pattern, suffix in _RULES:
        if pattern.search(word_lower):
            # For rules that *replace* a trailing letter (the y -> ies rule),
            # we strip the matched letter first. For pure-append rules we
            # keep the word intact.
            if suffix == "ies" and word_lower.endswith("y"):
                return word_lower[:-1] + "ies"
            if suffix == "ves":
                if word_lower.endswith("fe"):
                    return word_lower[:-2] + "ves"
                # ends in single 'f' (guarded by the pattern)
                return word_lower[:-1] + "ves"
            if suffix == "es" and word_lower.endswith("y") is False:
                # straightforward "add es" (sibilant and o cases)
                return word_lower + "es"
            return word_lower + suffix
    return None


def pluralize(word: str) -> str:
    """Return the English plural of ``word``.

    The function is deliberately total: any non-empty string gets a plural.
    Empty input returns an empty string, which is the least surprising option
    for callers composing this into templates.

    Casing is preserved for ALL CAPS and Title Case inputs (``"Child"`` ->
    ``"Children"``). Other mixed-case inputs are returned lowercased because
    guessing is worse than not guessing.
    """
    if not word:
        return word
    word_lower = word.lower()

    # Uncountable nouns pass through untouched.
    if word_lower in _UNCOUNTABLE:
        return word

    # Irregular table wins over suffix rules.
    if word_lower in _IRREGULAR:
        return _preserve_case(word, _IRREGULAR[word_lower])

    ruled = _apply_rules(word_lower)
    if ruled is not None:
        return _preserve_case(word, ruled)

    # Default: just add s.
    return _preserve_case(word, word_lower + "s")


# An explicit alias for callers who want the call site to read as intent rather
# than mechanism. It is the same function; no copy is made.
pluralize_irregular = pluralize
