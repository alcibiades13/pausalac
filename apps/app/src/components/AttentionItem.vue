<script setup lang="ts">
import { Badge } from '@pausalac/ui'
import type { AttentionItem } from '@/services/analytics'

defineProps<{ item: AttentionItem }>()

const ICON_BY_TYPE: Record<string, string> = {
  overdue_invoices: '🔴',
  email_unverified: '✉️',
  onboarding_incomplete: '⚙️',
  limit_warning: '📈',
  tax_obligation_overdue: '🧾',
  tax_resolution_missing_document: '📎',
}
</script>

<template>
  <RouterLink
    :to="{ name: item.action.route, query: item.action.query }"
    class="flex items-center gap-3 rounded-lg border border-border bg-white px-4 py-3 hover:bg-background"
  >
    <span aria-hidden="true">{{ ICON_BY_TYPE[item.type] ?? '•' }}</span>
    <span class="flex-1 text-sm text-navy">{{ item.message }}</span>
    <Badge variant="warning">Pogledaj</Badge>
  </RouterLink>
</template>
