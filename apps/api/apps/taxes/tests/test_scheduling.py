from datetime import date

from django.test import SimpleTestCase

from apps.taxes.scheduling import next_due_date


class NextDueDateTests(SimpleTestCase):
    def test_weekday_15th_unchanged(self):
        # 2026-02-15 is a Sunday — pick a month where the 15th is a weekday.
        # 2026-04-15 is a Wednesday.
        self.assertEqual(next_due_date(date(2026, 3, 1)), date(2026, 4, 15))

    def test_saturday_15th_rolls_to_monday(self):
        # 2026-08-15 is a Saturday.
        self.assertEqual(next_due_date(date(2026, 7, 1)), date(2026, 8, 17))

    def test_sunday_15th_rolls_to_monday(self):
        # 2026-02-15 is a Sunday.
        self.assertEqual(next_due_date(date(2026, 1, 1)), date(2026, 2, 16))

    def test_december_rolls_into_next_year(self):
        self.assertEqual(next_due_date(date(2026, 12, 1)), date(2027, 1, 15))
