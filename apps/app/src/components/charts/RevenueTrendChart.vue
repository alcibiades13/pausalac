<script setup lang="ts">
/**
 * Custom SVG shaded-area chart (d3-scale/d3-shape for path math only, no
 * D3 DOM rendering) — reads `dashboard.revenue.monthly_series`, the same
 * `monthly_issued_revenue` ledger function `LimitProgressChart`'s history
 * reads, so this never computes "revenue per month" a second way.
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { scaleLinear, scalePoint } from 'd3-scale'
import { area, curveLinear, line } from 'd3-shape'
import { EmptyState } from '@pausalac/ui'
import type { MonthlyRevenuePoint } from '@/services/analytics'
import { formatMonthShort } from '@/lib/formatDate'

const props = defineProps<{
  series: MonthlyRevenuePoint[]
  currency: string
}>()

const { t } = useI18n()

const WIDTH = 640
const HEIGHT = 220
const PADDING = { top: 16, right: 12, bottom: 24, left: 12 }

// The backend zero-fills every month through year-end for a stable
// X-axis, but a future month showing "0" is indistinguishable from a
// real past month with zero revenue — the chart stops at the current
// month instead of rendering unearned months as if they were known.
const currentMonthKey = (() => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
})()

const points = computed(() =>
  props.series
    .filter((row) => row.month <= currentMonthKey)
    .map((row) => ({ month: row.month, amount: Number(row.amount) })),
)

const hasData = computed(() => points.value.length > 0)
const isSinglePoint = computed(() => points.value.length === 1)

const xScale = computed(() =>
  scalePoint<string>()
    .domain(points.value.map((p) => p.month))
    .range([PADDING.left, WIDTH - PADDING.right])
    .padding(0.5),
)

const yScale = computed(() => {
  const values = points.value.map((p) => p.amount)
  // Domain must not assume a positive minimum — a storno-heavy month can
  // legitimately net negative, and the axis has to show that, not clip it.
  const min = Math.min(0, ...values)
  const max = Math.max(0, ...values)
  const span = max - min || 1
  return scaleLinear()
    .domain([min - span * 0.1, max + span * 0.1])
    .range([HEIGHT - PADDING.bottom, PADDING.top])
})

const zeroY = computed(() => yScale.value(0))

const linePath = computed(() => {
  const generator = line<{ month: string; amount: number }>()
    .x((p) => xScale.value(p.month) ?? 0)
    .y((p) => yScale.value(p.amount))
    .curve(curveLinear)
  return generator(points.value) ?? ''
})

const areaPath = computed(() => {
  const generator = area<{ month: string; amount: number }>()
    .x((p) => xScale.value(p.month) ?? 0)
    .y0(() => zeroY.value)
    .y1((p) => yScale.value(p.amount))
    .curve(curveLinear)
  return generator(points.value) ?? ''
})

// Fewer X-axis labels on narrow viewports — every point up to 6 months,
// thinning out for a full year so labels never overlap.
const labelIndices = computed(() => {
  const count = points.value.length
  if (count <= 6) return points.value.map((_, i) => i)
  const step = Math.ceil(count / 6)
  const indices = points.value.map((_, i) => i).filter((i) => i % step === 0)
  if (!indices.includes(count - 1)) indices.push(count - 1)
  return indices
})

const activeIndex = ref<number | null>(null)

function nearestIndex(clientX: number, svg: SVGSVGElement): number {
  const rect = svg.getBoundingClientRect()
  const ratio = (clientX - rect.left) / rect.width
  const x = ratio * WIDTH
  let closest = 0
  let closestDistance = Infinity
  points.value.forEach((p, i) => {
    const px = xScale.value(p.month) ?? 0
    const distance = Math.abs(px - x)
    if (distance < closestDistance) {
      closestDistance = distance
      closest = i
    }
  })
  return closest
}

function onPointerMove(event: PointerEvent) {
  activeIndex.value = nearestIndex(event.clientX, event.currentTarget as SVGSVGElement)
}

function onPointerLeave() {
  activeIndex.value = null
}

const active = computed(() => (activeIndex.value !== null ? points.value[activeIndex.value] : null))

const moneyFormatter = computed(
  () => new Intl.NumberFormat('sr-RS', { minimumFractionDigits: 0, maximumFractionDigits: 0 }),
)
</script>

<template>
  <div class="flex flex-col gap-2">
    <EmptyState
      v-if="!hasData"
      :title="t('dashboardInvoicesClients.charts.revenueTrend.emptyTitle')"
      :description="t('dashboardInvoicesClients.charts.revenueTrend.emptyDescription')"
    />
    <div v-else class="relative">
      <svg
        :viewBox="`0 0 ${WIDTH} ${HEIGHT}`"
        class="w-full touch-none"
        preserveAspectRatio="none"
        role="img"
        :aria-label="t('dashboardInvoicesClients.charts.revenueTrend.title')"
        @pointermove="onPointerMove"
        @pointerdown="onPointerMove"
        @pointerleave="onPointerLeave"
      >
        <defs>
          <linearGradient id="revenue-trend-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="var(--color-primary)" stop-opacity="0.35" />
            <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0.02" />
          </linearGradient>
        </defs>

        <line
          :x1="PADDING.left"
          :x2="WIDTH - PADDING.right"
          :y1="zeroY"
          :y2="zeroY"
          stroke="var(--color-border)"
          stroke-width="1"
        />

        <template v-if="isSinglePoint">
          <line
            :x1="PADDING.left"
            :x2="WIDTH - PADDING.right"
            :y1="yScale(points[0]!.amount)"
            :y2="yScale(points[0]!.amount)"
            stroke="var(--color-primary)"
            stroke-width="2"
            stroke-dasharray="4 4"
          />
          <circle :cx="xScale(points[0]!.month)" :cy="yScale(points[0]!.amount)" r="4" fill="var(--color-primary-dark)" />
        </template>
        <template v-else>
          <path :d="areaPath" fill="url(#revenue-trend-fill)" />
          <path :d="linePath" fill="none" stroke="var(--color-primary-dark)" stroke-width="2.5" />
        </template>

        <circle
          v-if="active"
          :cx="xScale(active.month)"
          :cy="yScale(active.amount)"
          r="4"
          fill="var(--color-primary-dark)"
        />
        <line
          v-if="active"
          :x1="xScale(active.month)"
          :x2="xScale(active.month)"
          :y1="PADDING.top"
          :y2="HEIGHT - PADDING.bottom"
          stroke="var(--color-primary-dark)"
          stroke-width="1"
          stroke-dasharray="3 3"
          opacity="0.4"
        />

        <text
          v-for="i in labelIndices"
          :key="points[i]!.month"
          :x="xScale(points[i]!.month)"
          :y="HEIGHT - 6"
          text-anchor="middle"
          class="fill-text-secondary text-[10px]"
        >
          {{ formatMonthShort(points[i]!.month) }}
        </text>
      </svg>

      <div
        v-if="active"
        class="pointer-events-none absolute top-0 rounded-lg border border-border bg-white px-2 py-1 text-xs shadow-md"
        :style="{ left: `${((xScale(active.month) ?? 0) / WIDTH) * 100}%`, transform: 'translate(-50%, -110%)' }"
      >
        <p class="font-medium text-navy">{{ moneyFormatter.format(active.amount) }} {{ currency }}</p>
        <p class="text-text-secondary">{{ formatMonthShort(active.month) }}</p>
      </div>
    </div>
  </div>
</template>
