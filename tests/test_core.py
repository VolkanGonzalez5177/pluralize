"""Tests for ``pluralize.core.pluralize``.

The suite is organised by category: irregular, uncountable, regular suffix
rules, case preservation, and edge cases the implementation explicitly claims
to handle. Nothing here tests behaviour the implementation disclaims.
"""

import unittest

from pluralize.core import pluralize, pluralize_irregular


class TestIrregular(unittest.TestCase):
    def test_man_to_men(self):
        self.assertEqual(pluralize("man"), "men")

    def test_woman_to_women(self):
        self.assertEqual(pluralize("woman"), "women")

    def test_child_to_children(self):
        self.assertEqual(pluralize("child"), "children")

    def test_person_to_people(self):
        self.assertEqual(pluralize("person"), "people")

    def test_ox_to_oxen(self):
        self.assertEqual(pluralize("ox"), "oxen")

    def test_criterion_to_criteria(self):
        self.assertEqual(pluralize("criterion"), "criteria")

    def test_crisis_to_crises(self):
        self.assertEqual(pluralize("crisis"), "crises")

    def test_thesis_to_theses(self):
        self.assertEqual(pluralize("thesis"), "theses")

    def test_die_to_dice(self):
        self.assertEqual(pluralize("die"), "dice")


class TestHyphenatedCompounds(unittest.TestCase):
    """The irregular table includes the common hyphenated compounds whose
    plural attaches to the head noun, not the final token."""

    def test_mother_in_law(self):
        self.assertEqual(pluralize("mother-in-law"), "mothers-in-law")

    def test_court_martial(self):
        self.assertEqual(pluralize("court-martial"), "courts-martial")

    def test_attorney_general(self):
        self.assertEqual(pluralize("attorney-general"), "attorneys-general")

    def test_passer_by(self):
        self.assertEqual(pluralize("passer-by"), "passers-by")


class TestUncountable(unittest.TestCase):
    def test_sheep_unchanged(self):
        self.assertEqual(pluralize("sheep"), "sheep")

    def test_fish_unchanged(self):
        self.assertEqual(pluralize("fish"), "fish")

    def test_deer_unchanged(self):
        self.assertEqual(pluralize("deer"), "deer")

    def test_series_unchanged(self):
        self.assertEqual(pluralize("series"), "series")

    def test_information_unchanged(self):
        self.assertEqual(pluralize("information"), "information")


class TestRegularSuffixRules(unittest.TestCase):
    def test_sibilant_ch(self):
        self.assertEqual(pluralize("church"), "churches")

    def test_sibilant_sh(self):
        self.assertEqual(pluralize("brush"), "brushes")

    def test_sibilant_s(self):
        self.assertEqual(pluralize("bus"), "buses")

    def test_sibilant_x(self):
        self.assertEqual(pluralize("box"), "boxes")

    def test_sibilant_z(self):
        self.assertEqual(pluralize("buzz"), "buzzes")

    def test_consonant_plus_y(self):
        self.assertEqual(pluralize("city"), "cities")

    def test_vowel_plus_y(self):
        self.assertEqual(pluralize("boy"), "boys")

    def test_consonant_plus_o(self):
        self.assertEqual(pluralize("potato"), "potatoes")

    def test_fe_to_ves(self):
        self.assertEqual(pluralize("knife"), "knives")

    def test_single_f_to_ves(self):
        self.assertEqual(pluralize("leaf"), "leaves")

    def test_default_s(self):
        self.assertEqual(pluralize("cat"), "cats")


class TestCasePreservation(unittest.TestCase):
    def test_title_case_irregular(self):
        self.assertEqual(pluralize("Child"), "Children")

    def test_all_caps_irregular(self):
        self.assertEqual(pluralize("MAN"), "MEN")

    def test_title_case_regular(self):
        self.assertEqual(pluralize("City"), "Cities")

    def test_all_caps_regular(self):
        self.assertEqual(pluralize("CAT"), "CATS")

    def test_title_case_uncountable(self):
        self.assertEqual(pluralize("Sheep"), "Sheep")

    def test_mixed_case_lowercased(self):
        # Mixed case is deliberately not preserved; we return lowercase rather
        # than guess at conventions like "McDonald".
        self.assertEqual(pluralize("iPhone"), "iphones")


class TestEdgeCases(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(pluralize(""), "")

    def test_alias_is_same_function(self):
        # The alias must be the very same callable; the README promises this.
        self.assertIs(pluralize_irregular, pluralize)
        self.assertEqual(pluralize_irregular("person"), "people")

    def test_single_letter(self):
        # No special rule for letters; falls through to default +s.
        self.assertEqual(pluralize("a"), "as")


if __name__ == "__main__":
    unittest.main()
