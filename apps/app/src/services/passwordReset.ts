import { apiFetch } from '@/lib/api'

export function requestPasswordReset(email: string): Promise<void> {
  return apiFetch('auth/password-reset/', { method: 'POST', body: { email } })
}

export function confirmPasswordReset(payload: {
  uid: string
  token: string
  new_password: string
}): Promise<void> {
  return apiFetch('auth/password-reset/confirm/', { method: 'POST', body: payload })
}

export function verifyEmail(token: string): Promise<void> {
  return apiFetch('auth/verify-email/', { method: 'POST', body: { token } })
}
