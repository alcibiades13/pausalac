import { computed, ref, watch, type Ref } from 'vue'
import { ApiError } from '@/lib/api'
import type { Paginated } from '@/lib/api'
import type { DataTableSort } from '@pausalac/ui'

export interface TableQuery {
  page: number
  pageSize: number
  search?: string
  ordering?: string
}

export interface UseTableQueryOptions {
  pageSize?: number
  genericErrorMessage: string
  initialSort?: DataTableSort | null
  initialSearch?: string
}

/**
 * Shared page/search/sort state + load lifecycle for a `DataTable`-backed
 * list view, talking to a DRF `PageNumberPagination` endpoint (the real
 * backend contract every list endpoint already speaks — see
 * `config/pagination.py` — just unused by the frontend until now).
 *
 * Deliberately does NOT own extra view-specific filters (status, type,
 * date range...) — every list view already has its own typed filter refs
 * (e.g. `InvoicesListView`'s `statusFilter`), so the caller's `fetcher`
 * closure reads those directly and the caller `watch()`es them into
 * `reload()`, same as the pre-existing pattern. Owning a generic
 * "filters bag" here would just re-wrap state that already fits the
 * view better as named refs.
 */
export function useTableQuery<T>(
  fetcher: (query: TableQuery) => Promise<Paginated<T>>,
  options: UseTableQueryOptions,
) {
  const pageSize = options.pageSize ?? 25
  const rows = ref<T[]>([]) as Ref<T[]>
  const status = ref<'loading' | 'ready' | 'error'>('loading')
  const errorMessage = ref('')
  const page = ref(1)
  const search = ref(options.initialSearch ?? '')
  const sort = ref<DataTableSort | null>(options.initialSort ?? null)
  const count = ref(0)
  const hasNext = ref(false)
  const hasPrevious = ref(false)

  const totalPages = computed(() => Math.max(1, Math.ceil(count.value / pageSize)))
  // DRF `OrderingFilter` convention: a bare field name is ascending, a
  // `-`-prefixed one is descending — same string `AccountingOrganizationView`
  // already sends by hand today.
  const ordering = computed(() =>
    sort.value ? (sort.value.direction === 'desc' ? `-${sort.value.key}` : sort.value.key) : undefined,
  )

  async function load() {
    status.value = 'loading'
    try {
      const result = await fetcher({
        page: page.value,
        pageSize,
        search: search.value || undefined,
        ordering: ordering.value,
      })
      rows.value = result.results
      count.value = result.count
      hasNext.value = result.next !== null
      hasPrevious.value = result.previous !== null
      status.value = 'ready'
    } catch (error) {
      errorMessage.value = error instanceof ApiError ? error.message : options.genericErrorMessage
      status.value = 'error'
    }
  }

  function onSort(value: DataTableSort | null) {
    sort.value = value
  }

  function nextPage() {
    if (hasNext.value) page.value += 1
  }

  function prevPage() {
    if (page.value > 1) page.value -= 1
  }

  // Any change to search/sort implies the current page may no longer
  // exist — reset to page 1 rather than silently loading an empty page.
  watch([search, sort], () => {
    page.value = 1
    load()
  })
  watch(page, load)

  return {
    rows,
    status,
    errorMessage,
    page,
    totalPages,
    hasNext,
    hasPrevious,
    search,
    sort,
    onSort,
    nextPage,
    prevPage,
    load,
    reload: load,
  }
}
