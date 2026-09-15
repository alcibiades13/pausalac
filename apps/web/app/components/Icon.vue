<script setup lang="ts">
/**
 * Marketing-site icon set — same rendering convention the app's own
 * AppSidebar/AppShell nav already uses (24x24 viewBox, stroke=currentColor,
 * stroke-width 2, round caps: apps/app/src/components/AppShell.vue), so the
 * site and the product read as the same visual language instead of the
 * emoji placeholders this page shipped with initially. Built from plain
 * circle/line/polyline/rect primitives rather than hand-authored bezier
 * paths — safer to get pixel-correct by hand and easy to verify by eye.
 *
 * `module-*` icons are a deliberate exception: those six are the exact
 * `d` path strings from AppShell.vue's own NAV_LINKS (invoices, clients,
 * limits, kpo, obligations, documents) copied verbatim, so the "sve na
 * jednom mestu" feature grid shows literally the same iconography as the
 * real in-app sidebar, not a lookalike.
 */
withDefaults(defineProps<{ name: string; size?: number }>(), { size: 24 })

const MODULE_PATHS: Record<string, string> = {
  'module-invoices': 'M7 3h7l5 5v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z;M14 3v5h5;M9 13h6M9 17h6',
  'module-clients': 'M5 20a7 7 0 0 1 14 0;M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z',
  'module-limits': 'M4 20V11M12 20V4M20 20v-6',
  'module-kpo':
    'M4 6.5A1.5 1.5 0 0 1 5.5 5H11v14H5.5A1.5 1.5 0 0 1 4 17.5v-11Z;M20 6.5A1.5 1.5 0 0 0 18.5 5H13v14h5.5a1.5 1.5 0 0 0 1.5-1.5v-11Z',
  'module-obligations': 'M4 10h16M8 3v4M16 3v4',
  'module-documents':
    'M4 7.5A1.5 1.5 0 0 1 5.5 6H10l2 2h6.5A1.5 1.5 0 0 1 20 9.5v8A1.5 1.5 0 0 1 18.5 19h-13A1.5 1.5 0 0 1 4 17.5v-10Z',
}
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    aria-hidden="true"
  >
    <template v-if="name in MODULE_PATHS">
      <path
        v-for="(d, i) in MODULE_PATHS[name].split(';')"
        :key="i"
        stroke-linecap="round"
        stroke-linejoin="round"
        :d="d"
      />
    </template>

    <template v-else-if="name === 'card'">
      <rect x="3" y="6" width="18" height="12" rx="2" stroke-linejoin="round" />
      <line x1="3" y1="10" x2="21" y2="10" />
      <line x1="7" y1="15" x2="11" y2="15" stroke-linecap="round" />
    </template>

    <template v-else-if="name === 'trending-up'">
      <polyline points="3 17 9 11 13 15 21 7" stroke-linecap="round" stroke-linejoin="round" />
      <polyline points="15 7 21 7 21 13" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <template v-else-if="name === 'check-circle'">
      <circle cx="12" cy="12" r="9" />
      <polyline points="8 12.5 10.5 15 16 9" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <template v-else-if="name === 'clock'">
      <circle cx="12" cy="12" r="9" />
      <polyline points="12 7 12 12 15 14" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <template v-else-if="name === 'arrow-right'">
      <line x1="5" y1="12" x2="19" y2="12" stroke-linecap="round" />
      <polyline points="13 6 19 12 13 18" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <template v-else-if="name === 'shield-check'">
      <path d="M12 3 19 6 19 12 12 21 5 12 5 6Z" stroke-linejoin="round" />
      <polyline points="9 12 11 14 15 9" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <template v-else-if="name === 'layers'">
      <polygon points="12 4 20 8 12 12 4 8" stroke-linejoin="round" />
      <polyline points="4 12 12 16 20 12" stroke-linecap="round" stroke-linejoin="round" />
      <polyline points="4 16 12 20 20 16" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <template v-else-if="name === 'check'">
      <polyline points="5 12.5 9.5 17 19 7" stroke-linecap="round" stroke-linejoin="round" />
    </template>

    <template v-else-if="name === 'x-mark'">
      <line x1="6" y1="6" x2="18" y2="18" stroke-linecap="round" />
      <line x1="18" y1="6" x2="6" y2="18" stroke-linecap="round" />
    </template>
  </svg>
</template>
