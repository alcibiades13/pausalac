<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Button, MoneyDisplay , DataTable, type DataTableColumn } from '@pausalac/ui'
import InvoiceStatusBadge from '@/components/InvoiceStatusBadge.vue'
import { listAdminInvoices, type AdminInvoice } from '@/services/admin'
import { ApiError } from '@/lib/api'

const { t } = useI18n()

const invoices = ref<AdminInvoice[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const columns = computed<DataTableColumn<AdminInvoice>[]>(() => [
  { key: 'company_name', label: t('admin.adminInvoicesView.companyColumn') },
  { key: 'client_name', label: t('admin.adminInvoicesView.clientColumn') },
  { key: 'invoice_number', label: t('admin.adminInvoicesView.numberColumn'), format: (r) => r.invoice_number ?? t('admin.adminInvoicesView.draftFallback') },
  { key: 'issue_date', label: t('admin.adminInvoicesView.issueDateColumn') },
])

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await listAdminInvoices({ page: page.value })
    invoices.value = result.results
    hasNext.value = result.next !== null
    hasPrevious.value = result.previous !== null
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('admin.adminInvoicesView.loadError')
  } finally {
    loading.value = false
  }
}

function goNext() {
  page.value += 1
  load()
}
function goPrevious() {
  page.value = Math.max(1, page.value - 1)
  load()
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminInvoicesView.title') }}</h1>
    <p class="text-sm text-text-secondary">
      {{ t('admin.adminInvoicesView.description') }}
    </p>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable :columns="columns" :rows="invoices" :loading="loading" :empty-title="t('admin.adminInvoicesView.emptyTitle')">
      <template #actions="{ row }">
        <div class="flex items-center gap-2">
          <InvoiceStatusBadge :status="row.status" />
          <MoneyDisplay :amount="row.total" :currency="row.currency" />
        </div>
      </template>
    </DataTable>

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">{{ t('admin.adminInvoicesView.previousButton') }}</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">{{ t('admin.adminInvoicesView.nextButton') }}</Button>
    </div>
  </div>
</template>
