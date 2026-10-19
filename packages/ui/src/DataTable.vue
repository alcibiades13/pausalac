<script setup lang="ts" generic="T extends object">
/**
 * Generic table (master prompt §51 Table/DataTable) — columns and rows as
 * props instead of a hand-rolled table per screen. Originally built as
 * `AdminTable.vue` to drive every admin list screen (Phase 6b), promoted
 * here once it proved out as a genuinely generic, reusable primitive with
 * zero admin-specific logic (Phase 6f).
 *
 * Generic over the row type `T` so a caller's scoped slots (`row`) come
 * back correctly typed instead of `Record<string, unknown>` everywhere.
 *
 * Constrained to `object`, not `Record<string, unknown>` — real row
 * interfaces (`Invoice`, `Client`, ...) don't carry an index signature,
 * which made Vue's generic inference fail to pick up the caller's actual
 * row type at all and silently widen `T` back to the constraint itself,
 * cascading into "Type 'Invoice[]' is not assignable to
 * 'Record<string, unknown>[]'" errors on every `DataTable` usage (found
 * via `vue-tsc`, not a runtime bug). `column.key`/`rowKey` stay plain
 * `string` rather than `keyof T` — some columns are `format`-only
 * (computed, not backed by a real row field), so a `keyof T` constraint
 * would reject those legitimately key-less columns.
 */
import EmptyState from './EmptyState.vue'
import Skeleton from './Skeleton.vue'

export interface DataTableColumn<T> {
  key: string
  label: string
  format?: (row: T) => string
  /** Clickable header that cycles asc → desc → off. Backend ordering
   * param uses `sortKey` if given, else `key` — only needed when the two
   * diverge (e.g. a computed/slot-only column vs a real model field). */
  sortable?: boolean
  sortKey?: string
}

export interface DataTableSort {
  key: string
  direction: 'asc' | 'desc'
}

const props = withDefaults(
  defineProps<{
    columns: DataTableColumn<T>[]
    rows: T[]
    loading?: boolean
    rowKey?: string
    emptyTitle?: string
    emptyDescription?: string
    /** Controlled sort state — caller (typically `useTableQuery`) owns it
     * and re-fetches on `@sort`, same pattern as v-model without the
     * magic. `null` means "no column currently sorted". */
    sort?: DataTableSort | null
    /** Whole row becomes clickable (cursor + hover already exist; this
     * just adds the emit) — kept router-agnostic (a plain DOM click event
     * with the row), so the caller decides what navigating means. */
    rowClickable?: boolean
  }>(),
  {
    loading: false,
    rowKey: 'id',
    emptyTitle: 'Nema podataka.',
    emptyDescription: '',
    sort: null,
    rowClickable: false,
  },
)

const emit = defineEmits<{ sort: [value: DataTableSort | null]; 'row-click': [row: T] }>()

function cellValue(row: T, column: DataTableColumn<T>): string {
  if (column.format) return column.format(row)
  // `column.key` is a plain `string`, not `keyof T` (see the constraint
  // note above), so this lookup is inherently dynamic — same as it was
  // before this fix, just with an explicit cast instead of relying on
  // `T`'s now-removed index signature.
  const value = (row as Record<string, unknown>)[column.key]
  return value === null || value === undefined || value === '' ? '—' : String(value)
}

function keyFor(row: T, index: number): string | number {
  const value = (row as Record<string, unknown>)[props.rowKey]
  return typeof value === 'string' || typeof value === 'number' ? value : index
}

function sortKeyFor(column: DataTableColumn<T>): string {
  return column.sortKey ?? column.key
}

function directionFor(column: DataTableColumn<T>): 'asc' | 'desc' | null {
  const key = sortKeyFor(column)
  return props.sort?.key === key ? props.sort.direction : null
}

/** asc → desc → off, same convention as most desktop tables (Linear,
 * Notion, Airtable) rather than a two-state toggle. */
function toggleSort(column: DataTableColumn<T>) {
  if (!column.sortable) return
  const key = sortKeyFor(column)
  const current = directionFor(column)
  if (current === 'asc') emit('sort', { key, direction: 'desc' })
  else if (current === 'desc') emit('sort', null)
  else emit('sort', { key, direction: 'asc' })
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
            <th v-for="column in columns" :key="column.key" class="px-3 py-2">
              <button
                v-if="column.sortable"
                type="button"
                class="inline-flex items-center gap-1 uppercase tracking-wide text-text-secondary hover:text-navy"
                @click="toggleSort(column)"
              >
                {{ column.label }}
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" aria-hidden="true">
                  <polyline
                    v-if="directionFor(column) !== 'desc'"
                    points="6 15 12 9 18 15"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    :class="directionFor(column) === 'asc' ? 'opacity-100' : 'opacity-30'"
                  />
                  <polyline
                    v-if="directionFor(column) !== 'asc'"
                    points="6 9 12 15 18 9"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    :class="directionFor(column) === 'desc' ? 'opacity-100' : 'opacity-30'"
                  />
                </svg>
              </button>
              <template v-else>{{ column.label }}</template>
            </th>
            <th v-if="$slots.actions" class="px-3 py-2">
              <span class="sr-only">Akcije</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border">
          <tr
            v-for="(row, index) in rows"
            :key="keyFor(row, index)"
            :class="rowClickable ? 'cursor-pointer hover:bg-background' : 'cursor-default hover:bg-background'"
            @click="rowClickable && emit('row-click', row)"
          >
            <td v-for="column in columns" :key="column.key" class="px-3 py-2 text-navy">
              <slot :name="`cell-${column.key}`" :row="row">{{ cellValue(row, column) }}</slot>
            </td>
            <td v-if="$slots.actions" class="px-3 py-2" @click.stop>
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
        :class="[
          'flex flex-col gap-2 rounded-xl border border-border bg-surface p-4',
          rowClickable ? 'cursor-pointer hover:bg-background' : '',
        ]"
        @click="rowClickable && emit('row-click', row)"
      >
        <dl v-for="column in columns" :key="column.key" class="flex flex-col gap-0.5">
          <dt class="text-xs font-medium uppercase tracking-wide text-text-secondary">
            {{ column.label }}
          </dt>
          <dd class="text-sm text-navy">
            <slot :name="`cell-${column.key}`" :row="row">{{ cellValue(row, column) }}</slot>
          </dd>
        </dl>
        <div
          v-if="$slots.actions"
          class="mt-1 flex flex-wrap items-center gap-2 border-t border-border pt-2"
          @click.stop
        >
          <slot name="actions" :row="row" />
        </div>
      </div>
    </div>
  </div>
</template>
