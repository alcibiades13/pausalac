<script setup lang="ts">
defineProps<{
  label: string
}>()
</script>

<template>
  <div class="flex flex-col gap-1">
    <p class="text-sm text-text-secondary">{{ label }}</p>
    <p class="text-2xl font-semibold text-navy"><slot /></p>
    <div v-if="$slots.secondary"><slot name="secondary" /></div>
  </div>
</template>
