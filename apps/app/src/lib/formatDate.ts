/**
 * Centralized date display formatting (master prompt §91: "Create
 * centralized date formatting. Avoid manually formatting dates in every
 * component... Frontend formats for Serbian users."). Backend stores
 * canonical ISO values (YYYY-MM-DD or a full ISO datetime); this is the
 * one place that turns those into what a Serbian user reads.
 *
 * Not for `<input type="date">` bindings — those need the raw ISO
 * YYYY-MM-DD value, a different concern from display formatting.
 */

/** e.g. "15.9.2026." — matches the format already used across the PDF templates. */
export function formatDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('sr-RS')
}

/** e.g. "15.9.2026. 14:32" — date and time, for audit-style timestamps. */
export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('sr-RS')
}

/**
 * e.g. "sep" — short month name for chart X-axis labels (RevenueTrendChart,
 * LimitProgressChart, KpoMonthlyBarChart). Parses the "YYYY-MM-DD" parts
 * directly rather than `new Date(iso)`, so a UTC-shifted local timezone
 * can't roll the label back to the previous month.
 */
export function formatMonthShort(iso: string): string {
  const parts = iso.split('-')
  const year = Number(parts[0])
  const month = Number(parts[1])
  // 'sr-RS' alone resolves to Serbian Cyrillic for word-producing formats
  // like a month name (digits/separators are script-neutral, which is why
  // formatDate/formatDateTime above never surfaced this) — this app is
  // Latin-script throughout (<html lang="sr-Latn">), so 'sr-Latn' is
  // required here, found by actually looking at a rendered chart axis.
  return new Date(year, month - 1, 1).toLocaleDateString('sr-Latn', { month: 'short' })
}
