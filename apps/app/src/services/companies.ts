import { apiFetch } from '@/lib/api'
import type { Company } from '@/stores/auth'

export function createCompany(name: string): Promise<Company> {
  return apiFetch<Company>('companies/', { method: 'POST', body: { name } })
}
