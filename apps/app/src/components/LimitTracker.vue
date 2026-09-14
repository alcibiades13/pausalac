<script setup lang="ts">
import { computed } from 'vue'
import { MoneyDisplay } from '@pausalac/ui'
import type { LimitTrackerData } from '@/services/limits'

const props = defineProps<{
  label: string
  tracker: LimitTrackerData
}>()

const BAR_COLOR: Record<string, string> = {
  ok: 'bg-success',
  attention: 'bg-warning',
  warning: 'bg-warning',
  critical: 'bg-danger',
}

const PERIOD_LABEL: Record<string, string> = {
  calendar_year: 'kalendarska godina',
  trailing_12_months: 'poslednjih 12 meseci',
}

const barColor = computed(() => BAR_COLOR[props.tracker.warning_level])
const periodLabel = computed(() => PERIOD_LABEL[props.tracker.period.type] ?? props.tracker.period.type)
const barWidth = computed(() => `${Math.min(props.tracker.percentage, 100)}%`)
</script>

<template>
  <div class="flex flex-col gap-2">
    <div class="flex items-baseline justify-between">
      <span class="text-sm font-medium text-navy">{{ label }}</span>
      <span class="text-xs text-text-secondary">{{ periodLabel }}</span>
    </div>
    <p class="text-lg font-semibold text-navy">
      <MoneyDisplay :amount="tracker.current" :currency="tracker.currency" />
      /
      <MoneyDisplay :amount="tracker.threshold" :currency="tracker.currency" />
    </p>
    <div class="h-2 w-full overflow-hidden rounded-full bg-background">
      <div class="h-full transition-all" :class="barColor" :style="{ width: barWidth }" />
    </div>
    <div class="flex items-baseline justify-between text-sm text-text-secondary">
      <span>{{ tracker.percentage }}%</span>
      <span>Preostalo: <MoneyDisplay :amount="tracker.remaining" :currency="tracker.currency" /></span>
    </div>
    <p v-if="tracker.projection" class="text-sm text-text-secondary">
      Procena do kraja perioda:
      <MoneyDisplay :amount="tracker.projection.estimated_period_end" :currency="tracker.currency" />
      (procena)
    </p>
  </div>
</template>
