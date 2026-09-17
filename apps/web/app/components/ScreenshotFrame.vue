<script setup lang="ts">
// Real screenshots of the running app (captured via Playwright against
// seeded demo data — see docs/decisions-log.md) rather than hand-drawn
// mockups, wrapped in one consistent "browser window" chrome so every
// section that embeds one reads as the same visual language.
withDefaults(defineProps<{ src: string; alt: string; shadowClass?: string }>(), {
  // Default shadow for a screenshot sitting flat in its own section.
  // Overridable per-use (e.g. the hero's overlapping phone shot wants a
  // stronger shadow to read as clearly "above" the image behind it).
  shadowClass: 'shadow-[0_20px_60px_-20px_rgba(10,10,10,0.25)]',
})
</script>

<template>
  <div :class="['overflow-hidden rounded-2xl border border-border bg-surface', shadowClass]">
    <div class="flex items-center gap-1.5 border-b border-border bg-background px-3 py-2" aria-hidden="true">
      <span class="h-2.5 w-2.5 rounded-full bg-danger/40" />
      <span class="h-2.5 w-2.5 rounded-full bg-warning/40" />
      <span class="h-2.5 w-2.5 rounded-full bg-success/40" />
    </div>
    <img :src="src" :alt="alt" class="block w-full" loading="lazy" />
  </div>
</template>
