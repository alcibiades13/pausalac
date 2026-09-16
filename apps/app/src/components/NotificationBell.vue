<script setup lang="ts">
/**
 * Extracted from AppShell.vue's mobile header so the exact same
 * bell+badge markup can be reused in the new desktop/tablet TopHeader
 * without duplicating the SVG/badge by hand — `unreadCount` stays owned
 * by AppShell.vue (it already polls it on mount/route-change), this is
 * purely presentational.
 *
 * Prop named `label`, not `ariaLabel`: Vue's TSX prop typing special-
 * cases anything bound via an `aria-*`/`data-*` template attribute as
 * universal fallthrough, never matching it to a same-named declared
 * prop — naming a prop `ariaLabel` compiles fine but fails `vue-tsc
 * --build`'s stricter check ("Property 'ariaLabel' is missing"), a real
 * error `--noEmit` doesn't catch (same class of gap as this project's
 * i18n-b build-vs-noEmit mismatch).
 */
defineProps<{ unreadCount: number; label: string }>()
</script>

<template>
  <RouterLink
    :to="{ name: 'notifications' }"
    class="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-navy hover:bg-background"
    :aria-label="label"
  >
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M15 17h5l-1.4-1.4A2 2 0 0 1 18 14.2V11a6 6 0 1 0-12 0v3.2a2 2 0 0 1-.6 1.4L4 17h5m6 0v1a3 3 0 1 1-6 0v-1m6 0H9"
      />
    </svg>
    <span
      v-if="unreadCount > 0"
      class="absolute right-1 top-1 flex h-4 min-w-4 animate-pulse items-center justify-center rounded-full bg-danger px-1 text-[10px] font-medium text-white"
      aria-hidden="true"
    >
      {{ unreadCount > 9 ? '9+' : unreadCount }}
    </span>
  </RouterLink>
</template>
