<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    amount: string | number
    currency: string
    compact?: boolean
  }>(),
  {
    compact: false,
  },
)

// Serbian formatting convention (master prompt §90): dot thousands
// separator, comma decimal separator — e.g. "2.840.000 RSD" / "1.500,00 EUR".
const formatted = computed(() => {
  const value = typeof props.amount === 'string' ? Number(props.amount) : props.amount
  const formatter = new Intl.NumberFormat('sr-RS', {
    minimumFractionDigits: props.compact ? 0 : 2,
    maximumFractionDigits: props.compact ? 1 : 2,
    notation: props.compact ? 'compact' : 'standard',
  })
  return `${formatter.format(value)} ${props.currency}`
})
</script>

<template>
  <span class="tabular-nums">{{ formatted }}</span>
</template>
