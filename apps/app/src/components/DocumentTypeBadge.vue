<script setup lang="ts">
import { Badge } from '@pausalac/ui'
import type { InvoiceDocumentType } from '@/services/invoices'
import { DOCUMENT_TYPE_LABELS } from '@/lib/documentType'

const props = defineProps<{ type: InvoiceDocumentType }>()
</script>

<template>
  <Badge variant="neutral">{{ DOCUMENT_TYPE_LABELS[props.type] }}</Badge>
</template>
