import { getCookie } from './cookies'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'
const API_VERSION = 'v1'

/**
 * Mirrors the backend's error contract (apps/api/config/exceptions.py):
 *   {"error": {"code", "message", "request_id", "fields"?}}
 * `fields` is only present for per-field validation errors — views should
 * prefer it for inline form errors and fall back to `message` otherwise.
 */
export class ApiError extends Error {
  code: string
  requestId: string
  fields?: Record<string, string[]>

  constructor(payload: { code: string; message: string; request_id: string; fields?: Record<string, string[]> }) {
    super(payload.message)
    this.code = payload.code
    this.requestId = payload.request_id
    this.fields = payload.fields
  }

  /** First error message for `field`, if the backend reported one. */
  fieldError(field: string): string | undefined {
    return this.fields?.[field]?.[0]
  }
}

const UNSAFE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

interface ApiFetchOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
  companyId?: string | number
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { body, companyId, headers, method = 'GET', ...rest } = options

  const requestHeaders = new Headers(headers)
  requestHeaders.set('Content-Type', 'application/json')
  requestHeaders.set('Accept', 'application/json')
  if (companyId !== undefined) {
    requestHeaders.set('X-Company-Id', String(companyId))
  }
  if (UNSAFE_METHODS.has(method.toUpperCase())) {
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      requestHeaders.set('X-CSRFToken', csrfToken)
    }
  }

  const response = await fetch(`${API_BASE_URL}/${API_VERSION}/${path.replace(/^\//, '')}`, {
    ...rest,
    method,
    headers: requestHeaders,
    credentials: 'include',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (response.status === 204) {
    return undefined as T
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    if (data?.error) {
      throw new ApiError(data.error)
    }
    throw new ApiError({
      code: 'UNKNOWN_ERROR',
      message: 'Ne možemo trenutno da učitamo podatke. Pokušaj ponovo.',
      request_id: '',
    })
  }

  return data as T
}
