<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Badge } from '@pausalac/ui'
import type { InvoiceStatus } from '@/services/invoices'
import { STATUS_VARIANTS } from '@/lib/invoiceStatus'

const { t } = useI18n()
const props = defineProps<{ status: InvoiceStatus }>()
</script>

<template>
  <Badge :variant="STATUS_VARIANTS[props.status]">{{ t(`dashboardInvoicesClients.invoiceStatusBadge.${props.status}`) }}</Badge>
</template>
