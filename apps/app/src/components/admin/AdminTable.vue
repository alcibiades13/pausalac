<script setup lang="ts" generic="T extends Record<string, unknown>">
/**
 * Generic table driving every admin list screen (Phase 6b) — columns and
 * rows as props instead of ten hand-rolled tables. Also a first real step
 * toward the Table/DataTable primitive packages/ui is missing (noted as a
 * side-benefit in the Phase 6b plan, not built as its own task).
 *
 * Generic over the row type `T` so a caller's scoped slots (`row`) come
 * back correctly typed instead of `Record<string, unknown>` everywhere.
 */
import { EmptyState, Skeleton } from '@pausalac/ui'

export interface AdminTableColumn<T> {
  key: string
  label: string
  format?: (row: T) => string
}

const props = withDefaults(
  defineProps<{
    columns: AdminTableColumn<T>[]
    rows: T[]
    loading?: boolean
    rowKey?: string
    emptyTitle?: string
    emptyDescription?: string
  }>(),
  {
    loading: false,
    rowKey: 'id',
    emptyTitle: 'Nema podataka.',
    emptyDescription: '',
  },
)

function cellValue(row: T, column: AdminTableColumn<T>): string {
  if (column.format) return column.format(row)
  const value = row[column.key]
  return value === null || value === undefined || value === '' ? '—' : String(value)
}

function keyFor(row: T, index: number): string | number {
  const value = row[props.rowKey]
  return typeof value === 'string' || typeof value === 'number' ? value : index
}
</script>

<template>
  <div v-if="loading" class="rounded-xl border border-border bg-surface p-4">
    <Skeleton :count="4" />
  </div>
  <div v-else-if="rows.length === 0" class="rounded-xl border border-border bg-surface p-4">
    <EmptyState :title="emptyTitle" :description="emptyDescription" />
  </div>
  <div v-else>
    <!-- A classic table forces every column into a fixed-width strip —
    fine for short values, but a long free-text column (e.g. a
    regulatory rule's "source") wraps into a wall of lines and squeezes
    every other column with it, especially on mobile. Below `sm`, each
    row renders as its own card (label: value stack) instead. -->
    <div class="hidden overflow-x-auto rounded-xl border border-border bg-surface sm:block">
      <table class="w-full text-left text-sm">
        <thead>
          <tr
            class="border-b border-border text-xs font-medium uppercase tracking-wide text-text-secondary"
          >
            <th v-for="column in columns" :key="column.key" class="px-4 py-2.5">
              {{ column.label }}
            </th>
            <th v-if="$slots.actions" class="px-4 py-2.5">
              <span class="sr-only">Akcije</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border">
          <tr
            v-for="(row, index) in rows"
            :key="keyFor(row, index)"
            class="cursor-default hover:bg-background"
          >
            <td v-for="column in columns" :key="column.key" class="px-4 py-2.5 text-navy">
              <slot :name="`cell-${column.key}`" :row="row">{{ cellValue(row, column) }}</slot>
            </td>
            <td v-if="$slots.actions" class="px-4 py-2.5">
              <slot name="actions" :row="row" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex flex-col gap-2 sm:hidden">
      <div
        v-for="(row, index) in rows"
        :key="keyFor(row, index)"
        class="flex flex-col gap-2 rounded-xl border border-border bg-surface p-4"
      >
        <dl v-for="column in columns" :key="column.key" class="flex flex-col gap-0.5">
          <dt class="text-xs font-medium uppercase tracking-wide text-text-secondary">
            {{ column.label }}
          </dt>
          <dd class="text-sm text-navy">
            <slot :name="`cell-${column.key}`" :row="row">{{ cellValue(row, column) }}</slot>
          </dd>
        </dl>
        <div v-if="$slots.actions" class="mt-1 flex flex-wrap items-center gap-2 border-t border-border pt-2">
          <slot name="actions" :row="row" />
        </div>
      </div>
    </div>
  </div>
</template>
