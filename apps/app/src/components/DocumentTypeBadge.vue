<script setup lang="ts">
import { Badge } from '@pausalac/ui'
import { useI18n } from 'vue-i18n'
import type { InvoiceDocumentType } from '@/services/invoices'

const props = defineProps<{ type: InvoiceDocumentType }>()

const { t } = useI18n()

// Not sourced from @/lib/documentType's DOCUMENT_TYPE_LABELS (shared with
// InvoicesListView.vue, outside this pass's scope) — a local key map keeps
// this translation self-contained without touching that shared file.
const DOCUMENT_TYPE_LABEL_KEYS: Record<InvoiceDocumentType, string> = {
  invoice: 'limitsAccountingEtc.documentTypeBadge.invoice',
  profaktura: 'limitsAccountingEtc.documentTypeBadge.profaktura',
  avans: 'limitsAccountingEtc.documentTypeBadge.avans',
}
</script>

<template>
  <Badge variant="neutral">{{ t(DOCUMENT_TYPE_LABEL_KEYS[props.type]) }}</Badge>
</template>
