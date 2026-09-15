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
