import { describe, it, expect, vi } from 'vitest'
import { flushPromises } from '@vue/test-utils'
import { useTableQuery } from '../useTableQuery'

function page(results: number[], overrides: Partial<{ count: number; next: string | null; previous: string | null }> = {}) {
  return {
    results,
    count: overrides.count ?? results.length,
    next: overrides.next ?? null,
    previous: overrides.previous ?? null,
  }
}

describe('useTableQuery', () => {
  it('loads once and exposes the results, with totalPages from count/pageSize', async () => {
    const fetcher = vi.fn().mockResolvedValue(page([1, 2, 3], { count: 47 }))
    const query = useTableQuery(fetcher, { genericErrorMessage: 'Greška.', pageSize: 25 })

    await query.load()

    expect(query.rows.value).toEqual([1, 2, 3])
    expect(query.status.value).toBe('ready')
    expect(query.totalPages.value).toBe(2)
    expect(fetcher).toHaveBeenCalledWith({ page: 1, pageSize: 25, search: undefined, ordering: undefined })
  })

  it('sets status to error and keeps a message on failure', async () => {
    const fetcher = vi.fn().mockRejectedValue(new Error('boom'))
    const query = useTableQuery(fetcher, { genericErrorMessage: 'Greška pri učitavanju.' })

    await query.load()

    expect(query.status.value).toBe('error')
    expect(query.errorMessage.value).toBe('Greška pri učitavanju.')
  })

  it('resets to page 1 and reloads when search changes', async () => {
    const fetcher = vi.fn().mockResolvedValue(page([1]))
    const query = useTableQuery(fetcher, { genericErrorMessage: 'Greška.' })
    await query.load()
    query.page.value = 3

    query.search.value = 'marko'
    await flushPromises()

    expect(query.page.value).toBe(1)
    expect(fetcher).toHaveBeenLastCalledWith({ page: 1, pageSize: 25, search: 'marko', ordering: undefined })
  })

  it('builds the DRF ordering string from sort, and resets page on sort change', async () => {
    const fetcher = vi.fn().mockResolvedValue(page([1]))
    const query = useTableQuery(fetcher, { genericErrorMessage: 'Greška.' })
    await query.load()
    query.page.value = 2

    query.onSort({ key: 'due_date', direction: 'desc' })
    await flushPromises()
    expect(query.page.value).toBe(1)
    expect(fetcher).toHaveBeenLastCalledWith({ page: 1, pageSize: 25, search: undefined, ordering: '-due_date' })

    query.onSort({ key: 'due_date', direction: 'asc' })
    await flushPromises()
    expect(fetcher).toHaveBeenLastCalledWith({ page: 1, pageSize: 25, search: undefined, ordering: 'due_date' })
  })

  it('nextPage/prevPage respect hasNext/hasPrevious and reload', async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(page([1], { next: 'http://x/?page=2' }))
      .mockResolvedValueOnce(page([2], { previous: 'http://x/?page=1' }))
    const query = useTableQuery(fetcher, { genericErrorMessage: 'Greška.' })
    await query.load()

    expect(query.hasNext.value).toBe(true)
    query.nextPage()
    await flushPromises()
    expect(query.page.value).toBe(2)
    expect(fetcher).toHaveBeenLastCalledWith({ page: 2, pageSize: 25, search: undefined, ordering: undefined })
    expect(query.hasPrevious.value).toBe(true)

    query.prevPage()
    expect(query.page.value).toBe(1)
  })

  it('does not advance past the last page or before the first', async () => {
    const fetcher = vi.fn().mockResolvedValue(page([1]))
    const query = useTableQuery(fetcher, { genericErrorMessage: 'Greška.' })
    await query.load()

    query.prevPage()
    expect(query.page.value).toBe(1)

    query.nextPage() // hasNext is false
    expect(query.page.value).toBe(1)
  })
})
