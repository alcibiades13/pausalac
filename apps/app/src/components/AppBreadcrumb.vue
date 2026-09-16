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
  <div v-if="sectionLabel" class="flex min-w-0 items-center gap-1">
    <button
      v-if="showBack"
      type="button"
      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-text-secondary hover:bg-background hover:text-primary"
      :aria-label="backLabel"
      @click="emit('back')"
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
        <polyline points="15 6 9 12 15 18" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>
    <nav aria-label="Breadcrumb" class="flex min-w-0 items-center gap-1.5 truncate text-sm">
      <span :class="leafLabel ? 'text-text-secondary' : 'font-medium text-navy'">{{ sectionLabel }}</span>
      <template v-if="leafLabel">
        <span class="text-border" aria-hidden="true">/</span>
        <span class="truncate font-medium text-navy">{{ leafLabel }}</span>
      </template>
    </nav>
  </div>
</template>
