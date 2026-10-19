<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { MoneyDisplay, Progress } from '@pausalac/ui'
import type { LimitTrackerData } from '@/services/limits'

const props = defineProps<{
  label: string
  tracker: LimitTrackerData
}>()

const { t } = useI18n()

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

const PERIOD_LABEL_KEY: Record<string, string> = {
  calendar_year: 'limitsAccountingEtc.limitTracker.periodCalendarYear',
  trailing_12_months: 'limitsAccountingEtc.limitTracker.periodTrailing12Months',
}

const barVariant = computed(() => BAR_VARIANT[props.tracker.warning_level] ?? 'primary')
const periodLabel = computed(() =>
  PERIOD_LABEL_KEY[props.tracker.period.type] ? t(PERIOD_LABEL_KEY[props.tracker.period.type]!) : props.tracker.period.type,
)
</script>

<template>
  <!--
    Self-contained @container: a narrow-context bug (dashboard's own
    two-column layout squeezing this into a shared card with a sibling
    tracker) showed up as "10%Preostalo:" running together with no gap
    and an asymmetric mid-fraction wrap — both were @container-width
    problems, not viewport-width ones, so `sm:` breakpoints here were
    reacting to the wrong box. This card now judges its OWN rendered
    width, wherever it's placed (a full-width Card on LimitsView, half a
    shared Card on the dashboard, or full-width again on mobile).
  -->
  <div class="@container flex flex-col gap-3">
    <div class="flex flex-col gap-0.5 @xs:flex-row @xs:items-baseline @xs:justify-between @xs:gap-2">
      <span class="text-sm font-medium text-navy">{{ label }}</span>
      <span class="whitespace-nowrap text-xs text-text-secondary">{{ periodLabel }}</span>
    </div>

    <!--
      current/threshold demoted to supporting text (was the biggest,
      boldest number on the card) — the percentage below is what a user
      should read first (limit intelligence = the interpretation, not
      the raw figures). The threshold half is wrapped so a forced break
      lands before "/ 6.000.000,00 RSD" as one unit, never right after
      "/" with the number stranded on the next line alone.
    -->
    <p class="text-sm text-text-secondary">
      <MoneyDisplay :amount="tracker.current" :currency="tracker.currency" /> <span class="whitespace-nowrap">/ <MoneyDisplay :amount="tracker.threshold" :currency="tracker.currency" /></span>
    </p>

    <div class="flex flex-col gap-1.5">
      <span class="text-2xl font-semibold text-navy">{{ tracker.percentage }}%</span>
      <Progress :value="tracker.percentage" :variant="barVariant" :label="label" />
    </div>

    <p class="text-sm text-text-secondary">
      {{ t('limitsAccountingEtc.limitTracker.remainingLabel') }}
      <MoneyDisplay :amount="tracker.remaining" :currency="tracker.currency" />
    </p>

    <p v-if="tracker.projection" class="text-sm text-text-secondary">
      {{ t('limitsAccountingEtc.limitTracker.projectionLabel') }}
      <MoneyDisplay :amount="tracker.projection.estimated_period_end" :currency="tracker.currency" />
      {{ t('limitsAccountingEtc.limitTracker.projectionSuffix') }}
    </p>
  </div>
</template>
