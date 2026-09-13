import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

const STORAGE_KEY = 'pausalac.currentCompanyId'

/**
 * Which company tenant-scoped API calls (X-Company-Id header) apply to.
 * Auto-selects the first active membership — a typical paušalac has
 * exactly one company. The persisted id is a per-viewer convenience only
 * (localStorage), never trusted on its own: `currentCompany` always
 * re-validates it against `auth.user.memberships`, the authoritative
 * source. No switcher UI yet (Phase 4's accountant flows will need one).
 */
export const useCompanyStore = defineStore('company', () => {
  const auth = useAuthStore()
  const storedId = ref<number | null>(readStoredId())

  const currentCompany = computed(() => {
    const memberships = auth.user?.memberships ?? []
    if (!memberships.length) return null
    const stored = memberships.find((m) => m.company.id === storedId.value)
    return stored?.company ?? memberships[0]!.company
  })

  const currentCompanyId = computed(() => currentCompany.value?.id ?? null)

  watch(currentCompanyId, (id) => {
    if (id === null) {
      localStorage.removeItem(STORAGE_KEY)
    } else {
      localStorage.setItem(STORAGE_KEY, String(id))
    }
  })

  function readStoredId(): number | null {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? Number(raw) : null
    } catch {
      return null
    }
  }

  return { currentCompany, currentCompanyId }
})
