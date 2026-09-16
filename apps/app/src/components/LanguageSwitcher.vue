<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import { SUPPORTED_LANGUAGES, type SupportedLanguage } from '@/i18n'

const { locale } = useI18n()
const auth = useAuthStore()

const NAMES: Record<SupportedLanguage, string> = { sr: 'Srpski', en: 'English', ru: 'Русский' }

function onChange(event: Event) {
  auth.setLanguage((event.target as HTMLSelectElement).value as SupportedLanguage)
}
</script>

<template>
  <div class="relative">
    <select
      :value="locale"
      aria-label="Izbor jezika"
      class="cursor-pointer appearance-none rounded-lg border border-border bg-surface py-1.5 pl-2.5 pr-6 text-sm text-navy hover:bg-background focus-visible:border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40"
      @change="onChange"
    >
      <option v-for="lang in SUPPORTED_LANGUAGES" :key="lang" :value="lang">{{ NAMES[lang] }}</option>
    </select>
    <svg
      class="pointer-events-none absolute right-1.5 top-1/2 h-3 w-3 -translate-y-1/2 text-text-secondary"
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
