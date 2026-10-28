# Pluralize

A small, dependency-free English pluraliser. One function, ``pluralize(word) -> str``, that returns the plural form of a singular noun.

```python
from pluralize import pluralize, pluralize_irregular

print(pluralize("child"))        # Children
print(pluralize("mother-in-law")) # mothers-in-law
print(pluralize("city"))          # cities
print(pluralize_irregular("ox"))  # oxen
```

## Why this exists

The problem is narrow: turn a singular noun string into its plural. Most implementations either hard-code a handful of irregulars and ignore everything else, or pull in a heavy NLP dependency. This library sits in between: a curated irregular table covering the words that actually trip people up (``criterion``/``criteria``, ``mother-in-law``/``mothers-in-law``, ``ox``/``oxen``), plus ordered suffix rules for the regular cases.

The trade-off is completeness versus predictability. We do **not** try to handle every English oddity. In particular:

- ``-o`` nouns are inconsistent (``potato``/``potatoes`` vs ``photo``/``photos``). The rule assumes ``-es``; words like ``photo`` and ``radio`` must be added to the irregular table by callers who need them.
- ``-f``/``-fe`` nouns are the same: ``leaf``/``leaves`` works, ``roof``/``roofs`` does not and must be overridden.
- Case preservation covers ALL CAPS and Title Case only. Mixed-case input like ``iPhone`` is returned lowercased, because guessing at ``McDonald`` is worse than not guessing.

## The awkward edge you will hit

If a word is both in the uncountable set and has a regular plural in some dialect (``fish``/``fishes`` when talking about kinds of fish, not individuals), this library returns the uncountable form. That is the singular answer most callers want, but it is a deliberate choice. To get ``fishes``, add it to the irregular table yourself.

## Installation

Drop ``src/pluralize`` onto your ``PYTHONPATH``. There is nothing to install and nothing to configure.

## API

- ``pluralize(word: str) -> str`` — returns the plural form.
- ``pluralize_irregular(word: str) -> str`` — an alias for ``pluralize``, for call sites that want the intent to read explicitly. It is the same function object.

Empty input returns an empty string. Non-string input raises ``TypeError`` from the standard library; we do not coerce.

## Exported names

| Name | Kind |
|------|------|
| `pluralize` | function |
| `pluralize_irregular` | function (alias of `pluralize`) |

## Running the tests

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

The suite covers irregulars, hyphenated compounds, uncountable nouns, each suffix rule, case preservation, and the empty-string edge case. It does not test behaviour the implementation disclaims.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

## Contributing

Issues and pull requests are welcome. Please keep the dependency list empty —
that constraint is the point of the project, not an oversight.

