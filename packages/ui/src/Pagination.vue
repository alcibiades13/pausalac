<script setup lang="ts">
import Button from './Button.vue'

// `page`/`totalPages` are optional on top of the original hasNext/hasPrevious
// contract (both existing callers, ClientsListView/AdminUsersView, keep
// working unchanged) — when given, they add "Strana X od Y" context instead
// of two buttons with no sense of where you are or how much is left.
defineProps<{
  hasNext: boolean
  hasPrevious: boolean
  page?: number
  totalPages?: number
}>()

const emit = defineEmits<{ next: []; previous: [] }>()
</script>

<template>
  <nav v-if="hasNext || hasPrevious" aria-label="Stranice" class="flex items-center gap-3">
    <Button variant="secondary" :disabled="!hasPrevious" @click="emit('previous')">Prethodna</Button>
    <span v-if="page && totalPages" class="text-sm text-text-secondary"
      >Strana {{ page }} od {{ totalPages }}</span
    >
    <Button variant="secondary" :disabled="!hasNext" @click="emit('next')">Sledeća</Button>
  </nav>
</template>
