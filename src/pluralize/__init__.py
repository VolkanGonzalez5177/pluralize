"""Pluralise English nouns.

The public surface is deliberately tiny: a single ``pluralize`` function and a
``pluralize_irregular`` alias for callers who want the intent of the call to be
self-documenting.
"""

from pluralize.core import pluralize, pluralize_irregular

__all__ = ["pluralize", "pluralize_irregular"]
