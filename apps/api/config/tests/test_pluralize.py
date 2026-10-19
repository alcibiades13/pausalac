"""
Regression tests for `config/pluralize.py` — added after a real,
user-flagged bug: dashboard attention messages were shipping literal
"faktura(e)"/"poresko(a) rešenje(a)" placeholder text instead of picking
one grammatically correct Serbian form.
"""

from django.test import SimpleTestCase

from config.pluralize import pluralize_sr


class PluralizeSrTests(SimpleTestCase):
    def test_one_for_numbers_ending_in_one_except_eleven(self):
        for n in (1, 21, 31, 101):
            self.assertEqual(pluralize_sr(n, "one", "few", "many"), "one")
        self.assertEqual(pluralize_sr(11, "one", "few", "many"), "many")

    def test_few_for_two_to_four_except_twelve_to_fourteen(self):
        for n in (2, 3, 4, 22, 23, 24):
            self.assertEqual(pluralize_sr(n, "one", "few", "many"), "few")
        for n in (12, 13, 14):
            self.assertEqual(pluralize_sr(n, "one", "few", "many"), "many")

    def test_many_for_zero_and_five_through_twenty(self):
        for n in (0, 5, 6, 10, 15, 20, 25, 100):
            self.assertEqual(pluralize_sr(n, "one", "few", "many"), "many")

    def test_hundreds_ending_in_eleven_stay_many_not_one(self):
        # The specific exception a native speaker would check first:
        # 111/211/311... end in "1" but belong to the 11-14 exception
        # (their last TWO digits are "11"), same as bare 11 — "111
        # faktura", never "111 faktura" read as the singular form.
        for n in (111, 211, 311, 411):
            self.assertEqual(pluralize_sr(n, "one", "few", "many"), "many")

    def test_hundreds_ending_in_twenty_one_are_genuinely_one(self):
        # Contrast case: 121's last two digits are "21", not "11-14",
        # so the ordinary "ends in 1" rule applies again.
        for n in (121, 221, 321):
            self.assertEqual(pluralize_sr(n, "one", "few", "many"), "one")

    def test_zero_is_many_not_a_fabricated_singular(self):
        self.assertEqual(pluralize_sr(0, "faktura", "fakture", "faktura"), "faktura")
