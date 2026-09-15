<script setup lang="ts">
import { computed } from 'vue'
import { MoneyDisplay, Progress } from '@pausalac/ui'
import type { LimitTrackerData } from '@/services/limits'

const props = defineProps<{
  label: string
  tracker: LimitTrackerData
}>()

// 'ok' (the common, default state — most companies most of the time)
// renders in the neutral primary color rather than a saturated success
// green: a calm "nothing to report" baseline that only escalates to a
// real color once there's actually something worth flagging, matching
// this session's move toward a muted palette with color used sparingly.
const BAR_VARIANT: Record<string, 'primary' | 'warning' | 'danger'> = {
  ok: 'primary',
  attention: 'warning',
  warning: 'warning',
  critical: 'danger',
}

const PERIOD_LABEL: Record<string, string> = {
  calendar_year: 'kalendarska godina',
  trailing_12_months: 'poslednjih 12 meseci',
}

const barVariant = computed(() => BAR_VARIANT[props.tracker.warning_level] ?? 'primary')
const periodLabel = computed(() => PERIOD_LABEL[props.tracker.period.type] ?? props.tracker.period.type)
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
    <Progress :value="tracker.percentage" :variant="barVariant" :label="label" />
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
