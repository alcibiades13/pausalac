<script setup lang="ts">
/**
 * sr/en/ru switcher — a real dropdown (native <select>), not the text
 * toggle this started as (user feedback: a toggle read as three buttons
 * competing for attention; a dropdown reads as one control). Native
 * <select> over a custom-built popover: free keyboard/mobile/screen-
 * reader support, and this only ever needs 3 options.
 * `switchLocalePath` (@nuxtjs/i18n) keeps the visitor on the same page,
 * just under the other locale's URL prefix (`strategy:
 * 'prefix_except_default'` in nuxt.config.ts — sr has no prefix, en/ru
 * get /en/, /ru/).
 */
const { locale, locales } = useI18n()
const switchLocalePath = useSwitchLocalePath()
const router = useRouter()

const NAMES: Record<string, string> = { sr: 'Srpski', en: 'English', ru: 'Русский' }

function onChange(event: Event) {
  const code = (event.target as HTMLSelectElement).value
  router.push(switchLocalePath(code))
}
</script>

<template>
  <div class="relative">
    <select
      :value="locale"
      aria-label="Izbor jezika"
      class="cursor-pointer appearance-none rounded-lg border border-border bg-surface py-2 pl-3 pr-7 text-sm text-navy hover:bg-background focus-visible:border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
      @change="onChange"
    >
      <option v-for="loc in locales" :key="loc.code" :value="loc.code">
        {{ NAMES[loc.code] ?? loc.code }}
      </option>
    </select>
    <svg
      class="pointer-events-none absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-text-secondary"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      aria-hidden="true"
    >
      <polyline points="6 9 12 15 18 9" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
  </div>
</template>
