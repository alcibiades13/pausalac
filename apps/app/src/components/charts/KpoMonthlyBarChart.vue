<script setup lang="ts">
/**
 * ApexCharts stacked bar (products vs. services per month) — reads
 * `apps.kpo.services.monthly_summary`'s rows verbatim, the same
 * `KPOEntry` totals the table above it already lists.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import VueApexCharts from 'vue3-apexcharts'
import { EmptyState } from '@pausalac/ui'
import type { KpoMonthlySummaryRow } from '@/services/kpo'
import { formatMonthShort } from '@/lib/formatDate'

const props = defineProps<{
  rows: KpoMonthlySummaryRow[]
  currency: string
}>()

const { t } = useI18n()

const hasActivity = computed(() => props.rows.some((row) => Number(row.total) !== 0))

const categories = computed(() => props.rows.map((row) => formatMonthShort(row.month)))

const series = computed(() => [
  { name: t('limitsAccountingEtc.charts.kpoMonthly.products'), data: props.rows.map((row) => Number(row.products)) },
  { name: t('limitsAccountingEtc.charts.kpoMonthly.services'), data: props.rows.map((row) => Number(row.services)) },
])

const chartOptions = computed(() => ({
  chart: { type: 'bar' as const, stacked: true, toolbar: { show: false }, fontFamily: 'var(--font-sans)' },
  colors: ['var(--color-primary)', 'var(--color-primary-dark)'],
  plotOptions: { bar: { columnWidth: '55%', borderRadius: 3 } },
  dataLabels: { enabled: false },
  xaxis: { categories: categories.value, labels: { style: { colors: 'var(--color-text-secondary)' } } },
  yaxis: {
    labels: {
      style: { colors: 'var(--color-text-secondary)' },
      // 'sr-RS' resolves to Cyrillic for compact-notation words ("хиљ."
      // instead of "hilj.") even though this app is Latin-script
      // throughout — see formatMonthShort's comment for the same issue.
      formatter: (value: number) => new Intl.NumberFormat('sr-Latn', { notation: 'compact' }).format(value),
    },
  },
  grid: { borderColor: 'var(--color-border)' },
  legend: { position: 'top' as const, labels: { colors: 'var(--color-navy)' } },
  tooltip: {
    y: {
      formatter: (value: number) => `${new Intl.NumberFormat('sr-RS').format(value)} ${props.currency}`,
    },
  },
}))
</script>

<template>
  <EmptyState
    v-if="!hasActivity"
    :title="t('limitsAccountingEtc.charts.kpoMonthly.emptyTitle')"
    :description="t('limitsAccountingEtc.charts.kpoMonthly.emptyDescription')"
  />
  <div v-else class="min-w-[420px] overflow-x-auto">
    <VueApexCharts type="bar" height="260" :options="chartOptions" :series="series" />
  </div>
</template>
