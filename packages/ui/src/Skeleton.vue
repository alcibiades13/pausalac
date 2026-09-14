<script setup lang="ts">
/**
 * Replaces bare "Učitavanje..." loading text (Phase 3f) — a simple
 * pulsing placeholder, composed by count for a multi-line/row context
 * rather than a bespoke skeleton per screen.
 */
withDefaults(
  defineProps<{
    count?: number
    height?: string
    width?: string
  }>(),
  {
    count: 1,
    height: '1rem',
    width: '100%',
  },
)
</script>

<template>
  <div class="flex flex-col gap-2" role="status" aria-label="Učitavanje">
    <div
      v-for="i in count"
      :key="i"
      class="animate-pulse rounded-md bg-border"
      :style="{ height, width: i === count && count > 1 ? '60%' : width }"
    />
  </div>
</template>
