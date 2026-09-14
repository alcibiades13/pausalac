<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { Button, Card, Alert, EmptyState, MoneyDisplay, Skeleton } from '@pausalac/ui'
import { listInvoices, type Invoice, type InvoiceStatus } from '@/services/invoices'
import { STATUS_LABELS } from '@/lib/invoiceStatus'
import { ApiError } from '@/lib/api'
import InvoiceStatusBadge from '@/components/InvoiceStatusBadge.vue'

const invoices = ref<Invoice[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')
const statusFilter = ref<InvoiceStatus | ''>('')

const STATUS_OPTIONS = Object.entries(STATUS_LABELS) as [InvoiceStatus, string][]

async function load() {
  status.value = 'loading'
  try {
    const page = await listInvoices({ status: statusFilter.value || undefined })
    invoices.value = page.results
    status.value = 'ready'
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo fakture.'
    status.value = 'error'
  }
}

onMounted(load)
watch(statusFilter, load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-navy">Fakture</h1>
      <RouterLink :to="{ name: 'invoice-new' }">
        <Button>+ Nova faktura</Button>
      </RouterLink>
    </div>

    <div class="flex items-center gap-2">
      <label for="status-filter" class="text-sm text-text-secondary">Status:</label>
      <select
        id="status-filter"
        v-model="statusFilter"
        class="rounded-lg border border-border bg-white px-3 py-1.5 text-sm text-navy focus:outline-none focus:ring-2 focus:ring-primary/40"
      >
        <option value="">Sve</option>
        <option v-for="[value, label] in STATUS_OPTIONS" :key="value" :value="value">{{ label }}</option>
      </select>
    </div>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">Pokušaj ponovo</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <Card v-else-if="invoices.length === 0">
      <EmptyState
        title="Još nemaš fakture."
        description="Prva faktura može biti gotova za manje od minuta."
      >
        <template #action>
          <RouterLink :to="{ name: 'invoice-new' }">
            <Button>+ Nova faktura</Button>
          </RouterLink>
        </template>
      </EmptyState>
    </Card>

    <Card v-else>
      <ul class="flex flex-col divide-y divide-border">
        <li v-for="invoice in invoices" :key="invoice.id" class="py-3">
          <RouterLink
            :to="{ name: 'invoice-detail', params: { id: invoice.id } }"
            class="-mx-2 flex flex-col gap-1 rounded-lg px-2 py-1 hover:bg-background sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <p class="font-mono font-medium text-navy">
                {{ invoice.invoice_number ?? `Nacrt #${invoice.id}` }}
              </p>
              <p class="text-sm text-text-secondary">{{ invoice.client_name }}</p>
            </div>
            <div class="flex items-center gap-3">
              <MoneyDisplay :amount="invoice.total" :currency="invoice.currency" />
              <InvoiceStatusBadge :status="invoice.status" />
            </div>
          </RouterLink>
        </li>
      </ul>
    </Card>
  </div>
</template>
