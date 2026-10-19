<script setup lang="ts">
/**
 * ApexCharts donut over the accountant panel's client-portfolio status
 * counts — reads the `portfolioSummary` the page already fetches
 * (apps.accounting.dashboard.summarize_portfolio), no new API call.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import VueApexCharts from 'vue3-apexcharts'
import { EmptyState } from '@pausalac/ui'
import type { PortfolioSummary } from '@/services/accounting'

const props = defineProps<{
  summary: PortfolioSummary
}>()

const { t } = useI18n()

const hasData = computed(() => props.summary.total > 0)

const series = computed(() => [props.summary.ok, props.summary.attention, props.summary.critical])
const labels = computed(() => [
  t('limitsAccountingEtc.charts.clientStatusDistribution.ok'),
  t('limitsAccountingEtc.charts.clientStatusDistribution.attention'),
  t('limitsAccountingEtc.charts.clientStatusDistribution.critical'),
])

const chartOptions = computed(() => ({
  chart: { type: 'donut' as const, fontFamily: 'var(--font-sans)' },
  labels: labels.value,
  colors: ['var(--color-success)', 'var(--color-warning)', 'var(--color-danger)'],
  legend: { position: 'bottom' as const, labels: { colors: 'var(--color-navy)' } },
  dataLabels: { enabled: false },
  stroke: { width: 0 },
}))
</script>

<template>
  <EmptyState
    v-if="!hasData"
    :title="t('limitsAccountingEtc.charts.clientStatusDistribution.emptyTitle')"
    :description="t('limitsAccountingEtc.charts.clientStatusDistribution.emptyDescription')"
  />
  <div v-else class="min-w-[280px]">
    <VueApexCharts type="donut" height="220" :options="chartOptions" :series="series" />
  </div>
</template>
