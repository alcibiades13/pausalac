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

/** Standard DRF PageNumberPagination envelope (config/pagination.py). */
export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

interface ApiFetchOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
  companyId?: string | number
  params?: Record<string, string | number | boolean | undefined>
}

/**
 * Builds a full API URL for cases that aren't a `fetch()` call — e.g. a
 * plain `<a href>` PDF download, which (unlike apiFetch) can't set a
 * custom X-Company-Id header, so the endpoints it points at resolve
 * tenancy another way (apps/invoices/views.py::InvoiceViewSet.pdf).
 */
export function buildApiUrl(
  path: string,
  params?: Record<string, string | number | boolean | undefined>,
): string {
  let url = `${API_BASE_URL}/${API_VERSION}/${path.replace(/^\//, '')}`
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params ?? {})) {
    if (value !== undefined) query.set(key, String(value))
  }
  if ([...query].length > 0) url += `?${query.toString()}`
  return url
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { body, companyId, params, headers, method = 'GET', ...rest } = options

  const isFormData = body instanceof FormData

  const requestHeaders = new Headers(headers)
  // A FormData body (file upload) must let the browser set its own
  // multipart boundary — forcing application/json here would break it.
  if (!isFormData) {
    requestHeaders.set('Content-Type', 'application/json')
  }
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

  const url = buildApiUrl(path, params)

  const response = await fetch(url, {
    ...rest,
    method,
    headers: requestHeaders,
    credentials: 'include',
    body: isFormData ? body : body !== undefined ? JSON.stringify(body) : undefined,
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
