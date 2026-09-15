<script setup lang="ts">
defineProps<{ text: string; tone?: 'default' | 'inverted' }>()
</script>

<template>
  <span
    :class="[
      'inline-flex items-center gap-2 font-mono text-xs font-medium uppercase tracking-wider',
      tone === 'inverted' ? 'text-white/60' : 'text-text-secondary',
    ]"
  >
    <span :class="['h-px w-4', tone === 'inverted' ? 'bg-white/30' : 'bg-border']" aria-hidden="true" />
    {{ text }}
  </span>
</template>
