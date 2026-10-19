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
  // 'sr-RS' alone resolves to Serbian Cyrillic for compact-notation words
  // ("хиљ."/"мил." instead of "hilj."/"mil.") even though this app is
  // Latin-script throughout (<html lang="sr-Latn">) — plain digit
  // grouping is script-neutral, which is why this never surfaced outside
  // `compact` mode. Found via a real rendered chart, not assumed.
  const formatter = new Intl.NumberFormat(props.compact ? 'sr-Latn' : 'sr-RS', {
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
