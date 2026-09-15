<script setup lang="ts">
import Button from './Button.vue'

defineProps<{
  hasNext: boolean
  hasPrevious: boolean
}>()

const emit = defineEmits<{ next: []; previous: [] }>()
</script>

<template>
  <nav v-if="hasNext || hasPrevious" aria-label="Stranice" class="flex items-center gap-2">
    <Button variant="secondary" :disabled="!hasPrevious" @click="emit('previous')">Prethodna</Button>
    <Button variant="secondary" :disabled="!hasNext" @click="emit('next')">Sledeća</Button>
  </nav>
</template>
