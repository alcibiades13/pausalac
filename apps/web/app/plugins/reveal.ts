/**
 * `v-reveal` — a small fade+rise-in-on-scroll directive for the marketing
 * site. Kept deliberately tiny and dependency-free rather than pulling in
 * an animation library for one effect. Honors `prefers-reduced-motion`
 * (master prompt §55 accessibility discipline, already applied to the
 * app itself in Phase 6f) — reduced-motion visitors see content appear
 * immediately, with no transform/opacity animation at all.
 *
 * Deliberately a universal plugin, not `.client.ts`: the directive still
 * needs to *exist* during SSR (a static build/nuxt generate renders these
 * pages on the server) even though its actual scroll behavior is
 * client-only — an unregistered directive makes Vue's server renderer
 * throw ("Cannot read properties of undefined (reading 'getSSRProps')")
 * rather than just skip it, so `getSSRProps` below ships the initial
 * hidden state as part of the server-rendered markup itself, and
 * `mounted` (which the SSR pass never calls) does the same on a pure
 * client-side navigation where no SSR markup existed to begin with.
 */
const HIDDEN_CLASSES = ['opacity-0', 'translate-y-6']
const TRANSITION_CLASSES = ['transition-all', 'duration-700', 'ease-out']

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive('reveal', {
    getSSRProps() {
      return { class: [...HIDDEN_CLASSES, ...TRANSITION_CLASSES].join(' ') }
    },
    mounted(el: HTMLElement) {
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        el.classList.remove(...HIDDEN_CLASSES)
        return
      }

      el.classList.add(...HIDDEN_CLASSES, ...TRANSITION_CLASSES)

      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry?.isIntersecting) {
            el.classList.remove(...HIDDEN_CLASSES)
            observer.disconnect()
          }
        },
        { threshold: 0.15 },
      )
      observer.observe(el)
    },
  })
})
