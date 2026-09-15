/**
 * Cross-origin "is this visitor already logged into the app" check —
 * GET /api/v1/auth/me/ (apps/api/apps/accounts/views.py::MeView),
 * IsAuthenticated-gated, called with `credentials: 'include'` so the
 * session cookie apps/app set travels with it. Works because Django's
 * session cookie is SameSite=Lax and (in production, once
 * SESSION_COOKIE_DOMAIN is set — see config/settings/{staging,
 * production}.py) scoped to the shared parent domain, not one specific
 * host — cookies were never port-scoped to begin with, which is also
 * why this already works across apps/web (:3000) and apps/app (:5173)
 * in local dev without any extra setup.
 *
 * Deliberately client-side only (plain `onMounted`, not `useFetch`):
 * this page can be static-prerendered (`nuxt generate`), and a build-time
 * SSR request has no real visitor's cookies to read — checking has to
 * happen in the browser, after hydration, using its own cookie jar.
 */
export function useAuthStatus() {
  const config = useRuntimeConfig()
  const isLoggedIn = ref(false)
  const checked = ref(false)

  async function check() {
    try {
      await $fetch(`${config.public.apiBase}/v1/auth/me/`, { credentials: 'include' })
      isLoggedIn.value = true
    } catch {
      // 401/403 (not logged in) is the expected common case, not an error
      // worth surfacing — treated the same as any other fetch failure.
      isLoggedIn.value = false
    } finally {
      checked.value = true
    }
  }

  onMounted(check)

  return { isLoggedIn, checked }
}
