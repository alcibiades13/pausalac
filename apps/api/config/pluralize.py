"""
Serbian numeral-noun agreement (1 / 2-4 / 0,5+,11-14) — replaces the
"faktura(e)"/"poresko(a) rešenje(a)" unresolved-placeholder pattern that
was leaving a literal "(e)"/"(a)" visible in production text instead of
picking one grammatically correct form. Not a general Serbian
pluralization library — callers pass the exact phrase for each of the
three count categories, since Serbian's agreement also changes verbs and
noun case, not just a suffix.
"""


def pluralize_sr(count: int, one: str, few: str, many: str) -> str:
    """`one` for 1, 21, 31... (not 11); `few` for 2-4, 22-24... (not 12-14);
    `many` for everything else (0, 5-20, 25-30, ...)."""
    if count % 10 == 1 and count % 100 != 11:
        return one
    if 2 <= count % 10 <= 4 and not (12 <= count % 100 <= 14):
        return few
    return many
