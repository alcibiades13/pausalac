<script setup lang="ts">
/**
 * ApexCharts donut (paid YTD / pending / overdue) — reads the same
 * `outstanding_summary` figures DashboardView's `outstanding` field
 * exposes (apps.invoices.ledger.outstanding_summary), never a second
 * computation of what's paid/outstanding.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import VueApexCharts from 'vue3-apexcharts'
import { EmptyState } from '@pausalac/ui'
import type { InvoiceStatusBreakdown } from '@/services/invoices'

const props = defineProps<{
  breakdown: InvoiceStatusBreakdown
}>()

const { t } = useI18n()

const pending = computed(() => Number(props.breakdown.total) - Number(props.breakdown.overdue_total))
const overdue = computed(() => Number(props.breakdown.overdue_total))
const paid = computed(() => Number(props.breakdown.paid_ytd))

const hasData = computed(() => pending.value + overdue.value + paid.value > 0)

const series = computed(() => [paid.value, pending.value, overdue.value])
const labels = computed(() => [
  t('dashboardInvoicesClients.charts.invoiceStatusBreakdown.paid'),
  t('dashboardInvoicesClients.charts.invoiceStatusBreakdown.pending'),
  t('dashboardInvoicesClients.charts.invoiceStatusBreakdown.overdue'),
])

const chartOptions = computed(() => ({
  chart: { type: 'donut' as const, fontFamily: 'var(--font-sans)' },
  labels: labels.value,
  colors: ['var(--color-success)', 'var(--color-primary)', 'var(--color-danger)'],
  legend: { position: 'bottom' as const, labels: { colors: 'var(--color-navy)' } },
  dataLabels: { enabled: false },
  stroke: { width: 0 },
  tooltip: {
    y: {
      formatter: (value: number) =>
        `${new Intl.NumberFormat('sr-RS').format(value)} ${props.breakdown.currency}`,
    },
  },
}))
</script>

<template>
  <EmptyState
    v-if="!hasData"
    :title="t('dashboardInvoicesClients.charts.invoiceStatusBreakdown.emptyTitle')"
    :description="t('dashboardInvoicesClients.charts.invoiceStatusBreakdown.emptyDescription')"
  />
  <VueApexCharts v-else type="donut" height="240" :options="chartOptions" :series="series" />
</template>
