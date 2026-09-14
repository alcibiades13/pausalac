import { apiFetch, type Paginated } from '@/lib/api'
import { useCompanyStore } from '@/stores/company'

export type NotificationPriority = 'critical' | 'attention' | 'informational'

export interface AppNotification {
  id: number
  event_type: string
  priority: NotificationPriority
  title: string
  message: string
  action_route: string
  action_query: Record<string, string>
  read_at: string | null
  created_at: string
}

function currentCompanyId(): number {
  const id = useCompanyStore().currentCompanyId
  if (id === null) {
    throw new Error('Nema aktivne kompanije — ovo se ne bi trebalo dogoditi iza requiresAuth rute.')
  }
  return id
}

export function listNotifications(
  options: { isRead?: boolean } = {},
): Promise<Paginated<AppNotification>> {
  return apiFetch<Paginated<AppNotification>>('notifications/', {
    companyId: currentCompanyId(),
    params: { is_read: options.isRead === undefined ? undefined : String(options.isRead) },
  })
}

export function markNotificationRead(id: number | string): Promise<AppNotification> {
  return apiFetch<AppNotification>(`notifications/${id}/mark-read/`, {
    method: 'POST',
    companyId: currentCompanyId(),
  })
}
