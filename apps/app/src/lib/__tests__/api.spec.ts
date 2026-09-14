import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { apiFetch } from '../api'

describe('apiFetch', () => {
  const originalFetch = globalThis.fetch

  beforeEach(() => {
    globalThis.fetch = vi.fn<typeof fetch>(
      async () =>
        new Response(JSON.stringify({ ok: true }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
    )
  })

  afterEach(() => {
    globalThis.fetch = originalFetch
  })

  it('sends a FormData body as-is without forcing Content-Type', async () => {
    const formData = new FormData()
    formData.set('title', 'Test')

    await apiFetch('documents/', { method: 'POST', body: formData })

    const [, init] = vi.mocked(globalThis.fetch).mock.calls[0]!
    expect(init?.body).toBe(formData)
    const headers = init?.headers as Headers
    expect(headers.has('Content-Type')).toBe(false)
  })

  it('JSON-serializes a plain object body and sets Content-Type', async () => {
    await apiFetch('invoices/', { method: 'POST', body: { title: 'Test' } })

    const [, init] = vi.mocked(globalThis.fetch).mock.calls[0]!
    expect(init?.body).toBe(JSON.stringify({ title: 'Test' }))
    const headers = init?.headers as Headers
    expect(headers.get('Content-Type')).toBe('application/json')
  })
})
