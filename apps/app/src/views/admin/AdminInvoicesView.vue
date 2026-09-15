<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Alert, Button, MoneyDisplay , DataTable, type DataTableColumn } from '@pausalac/ui'
import InvoiceStatusBadge from '@/components/InvoiceStatusBadge.vue'
import { listAdminInvoices, type AdminInvoice } from '@/services/admin'
import { ApiError } from '@/lib/api'

const invoices = ref<AdminInvoice[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const columns: DataTableColumn<AdminInvoice>[] = [
  { key: 'company_name', label: 'Kompanija' },
  { key: 'client_name', label: 'Klijent' },
  { key: 'invoice_number', label: 'Broj', format: (r) => r.invoice_number ?? 'nacrt' },
  { key: 'issue_date', label: 'Datum izdavanja' },
]

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
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo fakture.'
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
    <h1 class="text-xl font-semibold text-navy">Fakture</h1>
    <p class="text-sm text-text-secondary">
      Samo pregled — namenjeno podršci i debagovanju, ne izmeni tuđih finansijskih zapisa.
    </p>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable :columns="columns" :rows="invoices" :loading="loading" empty-title="Nema faktura.">
      <template #actions="{ row }">
        <div class="flex items-center gap-2">
          <InvoiceStatusBadge :status="row.status" />
          <MoneyDisplay :amount="row.total" :currency="row.currency" />
        </div>
      </template>
    </DataTable>

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">Prethodna</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">Sledeća</Button>
    </div>
  </div>
</template>
