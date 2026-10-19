<script setup lang="ts">
/**
 * Custom SVG linear chart with a dashed projection segment past "today"
 * (blueprint §6.5, confirmed shape: linear with projection, not a radial
 * gauge). `history`/`projection` are `LimitsService.compute_pausal_limit_history`'s
 * output verbatim — this never re-derives the cumulative or projected
 * figures itself.
 */
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { scaleLinear, scalePoint } from 'd3-scale'
import { curveLinear, line } from 'd3-shape'
import { EmptyState } from '@pausalac/ui'
import type { LimitHistoryPoint } from '@/services/limits'
import { formatMonthShort } from '@/lib/formatDate'

const props = defineProps<{
  history: LimitHistoryPoint[]
  projection: LimitHistoryPoint[]
  threshold: string
  currency: string
}>()

const { t } = useI18n()

const WIDTH = 640
const HEIGHT = 240
const PADDING = { top: 16, right: 12, bottom: 24, left: 12 }

const historyPoints = computed(() =>
  props.history.map((row) => ({ month: row.month, cumulative: Number(row.cumulative) })),
)
const projectionPoints = computed(() =>
  props.projection.map((row) => ({ month: row.month, cumulative: Number(row.cumulative) })),
)
const thresholdValue = computed(() => Number(props.threshold))

const hasData = computed(() => historyPoints.value.length > 0)
const isSinglePoint = computed(() => historyPoints.value.length === 1 && projectionPoints.value.length === 0)

const allMonths = computed(() => {
  const months = historyPoints.value.map((p) => p.month)
  for (const p of projectionPoints.value) {
    if (!months.includes(p.month)) months.push(p.month)
  }
  return months
})

const xScale = computed(() =>
  scalePoint<string>().domain(allMonths.value).range([PADDING.left, WIDTH - PADDING.right]).padding(0.5),
)

const yScale = computed(() => {
  const values = [
    ...historyPoints.value.map((p) => p.cumulative),
    ...projectionPoints.value.map((p) => p.cumulative),
    thresholdValue.value,
    0,
  ]
  const min = Math.min(...values)
  const max = Math.max(...values)
  const span = max - min || 1
  return scaleLinear()
    .domain([min - span * 0.1, max + span * 0.1])
    .range([HEIGHT - PADDING.bottom, PADDING.top])
})

function pathFor(points: { month: string; cumulative: number }[]): string {
  const generator = line<{ month: string; cumulative: number }>()
    .x((p) => xScale.value(p.month) ?? 0)
    .y((p) => yScale.value(p.cumulative))
    .curve(curveLinear)
  return generator(points) ?? ''
}

const historyPath = computed(() => pathFor(historyPoints.value))
const projectionPath = computed(() => pathFor(projectionPoints.value))
const thresholdY = computed(() => yScale.value(thresholdValue.value))

const combinedPoints = computed(() => [...historyPoints.value, ...projectionPoints.value])

const labelIndices = computed(() => {
  const months = allMonths.value
  const count = months.length
  if (count <= 6) return months.map((_, i) => i)
  const step = Math.ceil(count / 6)
  const indices = months.map((_, i) => i).filter((i) => i % step === 0)
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
  combinedPoints.value.forEach((p, i) => {
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

const active = computed(() => (activeIndex.value !== null ? combinedPoints.value[activeIndex.value] : null))
const activeIsProjected = computed(
  () => active.value !== null && activeIndex.value !== null && activeIndex.value >= historyPoints.value.length,
)

const moneyFormatter = computed(
  () => new Intl.NumberFormat('sr-RS', { minimumFractionDigits: 0, maximumFractionDigits: 0 }),
)
</script>

<template>
  <div class="flex flex-col gap-2">
    <EmptyState
      v-if="!hasData"
      :title="t('limitsAccountingEtc.charts.limitProgress.emptyTitle')"
      :description="t('limitsAccountingEtc.charts.limitProgress.emptyDescription')"
    />
    <div v-else class="relative">
      <svg
        :viewBox="`0 0 ${WIDTH} ${HEIGHT}`"
        class="w-full touch-none"
        preserveAspectRatio="none"
        role="img"
        :aria-label="t('limitsAccountingEtc.charts.limitProgress.title')"
        @pointermove="onPointerMove"
        @pointerdown="onPointerMove"
        @pointerleave="onPointerLeave"
      >
        <line
          :x1="PADDING.left"
          :x2="WIDTH - PADDING.right"
          :y1="thresholdY"
          :y2="thresholdY"
          stroke="var(--color-danger)"
          stroke-width="1.5"
          stroke-dasharray="5 4"
        />
        <text :x="WIDTH - PADDING.right" :y="thresholdY - 6" text-anchor="end" class="fill-danger text-[10px]">
          {{ t('limitsAccountingEtc.charts.limitProgress.thresholdLabel') }}
        </text>

        <template v-if="isSinglePoint">
          <circle
            :cx="xScale(historyPoints[0]!.month)"
            :cy="yScale(historyPoints[0]!.cumulative)"
            r="4"
            fill="var(--color-primary-dark)"
          />
        </template>
        <template v-else>
          <path :d="historyPath" fill="none" stroke="var(--color-primary-dark)" stroke-width="2.5" />
          <path
            v-if="projectionPath"
            :d="projectionPath"
            fill="none"
            stroke="var(--color-primary)"
            stroke-width="2.5"
            stroke-dasharray="6 5"
          />
        </template>

        <circle
          v-if="active"
          :cx="xScale(active.month)"
          :cy="yScale(active.cumulative)"
          r="4"
          :fill="activeIsProjected ? 'var(--color-primary)' : 'var(--color-primary-dark)'"
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
          :key="allMonths[i]"
          :x="xScale(allMonths[i]!)"
          :y="HEIGHT - 6"
          text-anchor="middle"
          class="fill-text-secondary text-[10px]"
        >
          {{ formatMonthShort(allMonths[i]!) }}
        </text>
      </svg>

      <div
        v-if="active"
        class="pointer-events-none absolute top-0 rounded-lg border border-border bg-white px-2 py-1 text-xs shadow-md"
        :style="{ left: `${((xScale(active.month) ?? 0) / WIDTH) * 100}%`, transform: 'translate(-50%, -110%)' }"
      >
        <p class="font-medium text-navy">{{ moneyFormatter.format(active.cumulative) }} {{ currency }}</p>
        <p class="text-text-secondary">
          {{ formatMonthShort(active.month) }}
          <span v-if="activeIsProjected">— {{ t('limitsAccountingEtc.charts.limitProgress.projectedSuffix') }}</span>
        </p>
      </div>
    </div>
  </div>
</template>
