<script setup lang="ts">
import { Badge } from '@pausalac/ui'
import type { InvoiceStatus } from '@/services/invoices'
import { STATUS_LABELS, STATUS_VARIANTS } from '@/lib/invoiceStatus'

const props = defineProps<{ status: InvoiceStatus }>()
</script>

<template>
  <Badge :variant="STATUS_VARIANTS[props.status]">{{ STATUS_LABELS[props.status] }}</Badge>
</template>
