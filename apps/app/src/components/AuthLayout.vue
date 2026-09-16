<script setup lang="ts">
import LanguageSwitcher from './LanguageSwitcher.vue'

defineProps<{ title: string }>()
</script>

<template>
  <div
    class="flex min-h-screen items-center justify-center bg-background px-4 py-12"
    style="background-image: radial-gradient(circle at 15% 10%, color-mix(in srgb, var(--color-primary) 10%, transparent), transparent 45%), radial-gradient(circle at 85% 90%, color-mix(in srgb, var(--color-primary-dark) 8%, transparent), transparent 45%)"
  >
    <!-- No account yet on these screens — the choice only persists via
         localStorage (see src/i18n/index.ts) until the user registers/
         logs in and it starts following User.language instead. -->
    <div class="fixed right-4 top-4">
      <LanguageSwitcher />
    </div>
    <div class="w-full max-w-sm">
      <h1 class="mb-6 text-center font-display text-xl font-semibold text-navy">{{ title }}</h1>
      <slot />
    </div>
  </div>
</template>
