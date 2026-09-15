import { onBeforeUnmount } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'

/**
 * Master prompt §93 FORMS: "unsaved changes handling where relevant."
 * Tracks a JSON-stringified baseline snapshot (captured once, when the
 * form's initial data finishes loading) and compares it against the
 * current form state on every navigation attempt — no deep-diffing
 * library needed for this.
 *
 * `getSnapshot` should return the same shape the form actually binds to
 * (e.g. the reactive form object itself) so the comparison reflects real
 * unsaved edits, not incidental object-identity differences.
 */
export function useUnsavedChangesGuard(getSnapshot: () => unknown) {
  let baseline: string | null = null

  /** Call once the form's initial data has been loaded/reset. */
  function markClean() {
    baseline = JSON.stringify(getSnapshot())
  }

  function isDirty(): boolean {
    if (baseline === null) return false
    return JSON.stringify(getSnapshot()) !== baseline
  }

  function onBeforeUnload(event: BeforeUnloadEvent) {
    if (!isDirty()) return
    // Legacy but still the only cross-browser way to trigger the native
    // "leave site?" prompt — the actual message shown is browser-chosen,
    // not this string, but both are required for compatibility.
    event.preventDefault()
    event.returnValue = ''
  }

  window.addEventListener('beforeunload', onBeforeUnload)
  onBeforeUnmount(() => window.removeEventListener('beforeunload', onBeforeUnload))

  onBeforeRouteLeave(() => {
    if (!isDirty()) return true
    return window.confirm('Imaš nesačuvane izmene. Da li sigurno želiš da napustiš stranicu?')
  })

  return { markClean, isDirty }
}
