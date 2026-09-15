<script setup lang="ts">
/**
 * Structural chrome shared by AppShell.vue and AdminShell.vue's tablet/
 * desktop navigation (user-requested — the old horizontal top-bar nav
 * didn't scale, especially for the admin panel's 11 links). Deliberately
 * dumb: each shell keeps owning its own nav-link list/active-state logic
 * and just fills in the three slots — this component only provides
 * consistent positioning/visual chrome, not a generic data-driven nav API.
 * Hidden below `sm:` — mobile keeps its existing header + MobileBottomNav,
 * untouched by this component.
 */
withDefaults(defineProps<{ navLabel?: string }>(), { navLabel: 'Glavna navigacija' })
</script>

<template>
  <aside
    class="fixed inset-y-0 left-0 z-10 hidden w-64 flex-col border-r border-border bg-surface sm:flex"
  >
    <div class="flex items-center gap-2 border-b border-border px-4 py-4">
      <slot name="header" />
    </div>
    <nav class="flex flex-1 flex-col gap-1 overflow-y-auto px-3 py-4" :aria-label="navLabel">
      <slot />
    </nav>
    <div class="mt-auto flex flex-col gap-1 border-t border-border px-3 py-3">
      <slot name="footer" />
    </div>
  </aside>
</template>
