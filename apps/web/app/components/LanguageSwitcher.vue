<script setup lang="ts">
/**
 * sr/en/ru switcher — sr is default/primary (master prompt §83), en/ru
 * are user-selectable. `switchLocalePath` (from @nuxtjs/i18n) keeps the
 * visitor on the same page, just under the other locale's URL prefix
 * (`strategy: 'prefix_except_default'` in nuxt.config.ts — sr has no
 * prefix, en/ru get /en/, /ru/).
 */
const { locale, locales } = useI18n()
const switchLocalePath = useSwitchLocalePath()

const CODES: Record<string, string> = { sr: 'SR', en: 'EN', ru: 'RU' }
</script>

<template>
  <div class="flex items-center gap-0.5" aria-label="Izbor jezika">
    <template v-for="(loc, i) in locales" :key="loc.code">
      <span v-if="i > 0" class="text-border" aria-hidden="true">·</span>
      <NuxtLink
        :to="switchLocalePath(loc.code)"
        :class="[
          'rounded-md px-1.5 py-1 text-xs font-medium',
          loc.code === locale ? 'text-navy' : 'text-text-secondary hover:text-primary',
        ]"
        :aria-current="loc.code === locale ? 'true' : undefined"
      >
        {{ CODES[loc.code] ?? loc.code.toUpperCase() }}
      </NuxtLink>
    </template>
  </div>
</template>
