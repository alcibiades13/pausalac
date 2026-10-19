<script setup lang="ts">
/**
 * Deliberately dumb (same philosophy as AppSidebar.vue): the parent
 * shell already has to resolve section/leaf i18n keys via its own
 * NAV_LINKS naming, so this component just renders already-resolved
 * strings rather than knowing anything about route meta or translation
 * namespaces itself — AppShell's and AdminShell's key structures don't
 * match (`breadcrumb.sections.*` vs `adminShell.navLinks.*`), and a
 * "smart" shared component would need to know about both.
 */
defineProps<{
  sectionLabel?: string
  leafLabel?: string
  showBack?: boolean
  backLabel: string
}>()

const emit = defineEmits<{ back: [] }>()
</script>

<template>
  <!--
    Always renders this wrapper, even with nothing inside (home page has
    no sectionLabel) — a real bug found the hard way: the parent header
    is `justify-between` with this as its first of two children, and a
    `v-if` on this ROOT element removed it from the DOM entirely rather
    than just being visually empty, collapsing the header to a single
    child. `justify-content: space-between` with one child pins it to
    the start, not wherever it "should" be — on the home page that
    dragged the whole right-side icon group (search/notifications/
    language/user menu) over to the far left. An empty-but-present div
    keeps the two-child layout intact regardless of content.
  -->
  <div class="flex min-w-0 items-center gap-1">
    <button
      v-if="showBack"
      type="button"
      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-text-secondary hover:bg-background hover:text-primary-dark"
      :aria-label="backLabel"
      @click="emit('back')"
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <polyline points="15 6 9 12 15 18" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>
    <nav v-if="sectionLabel" aria-label="Breadcrumb" class="flex min-w-0 items-center gap-1.5 truncate text-sm">
      <span :class="leafLabel ? 'text-text-secondary' : 'font-medium text-navy'">{{ sectionLabel }}</span>
      <template v-if="leafLabel">
        <span class="text-text-secondary" aria-hidden="true">/</span>
        <span class="truncate font-medium text-navy">{{ leafLabel }}</span>
      </template>
    </nav>
  </div>
</template>
