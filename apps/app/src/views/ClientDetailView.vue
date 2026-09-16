<script setup lang="ts">
/**
 * Client profile page (master prompt §15/blueprint §6.3): contact info,
 * lifetime totals (server-computed, apps.clients.services.ClientService),
 * invoice history, and a "Nova faktura" CTA that pre-selects this client
 * (§94 "prepopulate known data" — see InvoiceFormView.vue's ?client= read).
 */
import { onMounted, ref } from 'vue'
import { Button, Card, Alert, EmptyState, MoneyDisplay, Skeleton } from '@pausalac/ui'
import { getClient, getClientSummary, type Client, type ClientSummary } from '@/services/clients'
import { listInvoices, type Invoice } from '@/services/invoices'
import { listDocuments, type AppDocument } from '@/services/documents'
import { formatDate } from '@/lib/formatDate'
import { ApiError } from '@/lib/api'
import InvoiceStatusBadge from '@/components/InvoiceStatusBadge.vue'
import DocumentTypeBadge from '@/components/DocumentTypeBadge.vue'

const props = defineProps<{ id: string }>()

const client = ref<Client | null>(null)
const summary = ref<ClientSummary | null>(null)
const invoices = ref<Invoice[]>([])
const documents = ref<AppDocument[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')

async function load() {
  status.value = 'loading'
  try {
    const [clientData, summaryData, invoicesPage, documentsPage] = await Promise.all([
      getClient(props.id),
      getClientSummary(props.id),
      listInvoices({ client: props.id }),
      listDocuments({ client: props.id }),
    ])
    client.value = clientData
    summary.value = summaryData
    invoices.value = invoicesPage.results
    documents.value = documentsPage.results
    status.value = 'ready'
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo klijenta.'
    status.value = 'error'
  }
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">Pokušaj ponovo</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="4" />
    </Card>

    <template v-else-if="client && summary">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-xl font-semibold text-navy">{{ client.name }}</h1>
          <p class="text-sm text-text-secondary">
            {{ client.client_type === 'company' ? 'Pravno lice' : 'Fizičko lice' }}
          </p>
        </div>
        <div class="flex gap-2">
          <RouterLink :to="{ name: 'invoice-new', query: { client: client.id } }">
            <Button>+ Nova faktura</Button>
          </RouterLink>
          <RouterLink :to="{ name: 'client-edit', params: { id: client.id } }">
            <Button variant="secondary">Izmeni</Button>
          </RouterLink>
        </div>
      </div>

      <Card>
        <h2 class="mb-3 text-base font-semibold text-navy">Kontakt podaci</h2>
        <dl class="grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
          <div>
            <dt class="text-text-secondary">PIB / matični broj</dt>
            <dd class="text-navy">{{ client.tax_id || '—' }}</dd>
          </div>
          <div>
            <dt class="text-text-secondary">Email</dt>
            <dd class="text-navy">{{ client.email || '—' }}</dd>
          </div>
          <div>
            <dt class="text-text-secondary">Telefon</dt>
            <dd class="text-navy">{{ client.phone || '—' }}</dd>
          </div>
          <div>
            <dt class="text-text-secondary">Adresa</dt>
            <dd class="text-navy">{{ client.address || '—' }}</dd>
          </div>
        </dl>
        <p v-if="client.notes" class="mt-4 text-sm text-text-secondary">{{ client.notes }}</p>
      </Card>

      <Card>
        <h2 class="mb-3 text-base font-semibold text-navy">Pregled</h2>
        <dl class="grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
          <div>
            <dt class="text-text-secondary">Ukupno fakturisano</dt>
            <dd class="font-medium text-navy">
              <MoneyDisplay :amount="summary.total_invoiced" :currency="client.default_currency" />
            </dd>
          </div>
          <div>
            <dt class="text-text-secondary">Ukupno naplaćeno</dt>
            <dd class="font-medium text-navy">
              <MoneyDisplay :amount="summary.total_paid" :currency="client.default_currency" />
            </dd>
          </div>
          <div>
            <dt class="text-text-secondary">Otvoreno potraživanje</dt>
            <dd class="font-medium text-navy">
              <MoneyDisplay :amount="summary.outstanding" :currency="client.default_currency" />
            </dd>
          </div>
          <div>
            <dt class="text-text-secondary">Broj faktura</dt>
            <dd class="font-medium text-navy">{{ summary.invoice_count }}</dd>
          </div>
        </dl>
        <p v-if="summary.last_invoice_date" class="mt-3 text-sm text-text-secondary">
          Poslednja faktura: {{ formatDate(summary.last_invoice_date) }}
        </p>
      </Card>

      <Card>
        <h2 class="mb-3 text-base font-semibold text-navy">Fakture</h2>
        <EmptyState v-if="invoices.length === 0" title="Još nema faktura za ovog klijenta." />
        <ul v-else class="flex flex-col divide-y divide-border">
          <li v-for="invoice in invoices" :key="invoice.id" class="py-3">
            <RouterLink
              :to="{ name: 'invoice-detail', params: { id: invoice.id } }"
              class="-mx-2 flex flex-col gap-1 rounded-lg px-2 py-1 hover:bg-background sm:flex-row sm:items-center sm:justify-between"
            >
              <p class="font-mono font-medium text-navy">
                {{ invoice.invoice_number ?? `Nacrt #${invoice.id}` }}
              </p>
              <div class="flex items-center gap-3">
                <MoneyDisplay :amount="invoice.total" :currency="invoice.currency" />
                <DocumentTypeBadge v-if="invoice.document_type !== 'invoice'" :type="invoice.document_type" />
                <InvoiceStatusBadge :status="invoice.status" />
              </div>
            </RouterLink>
          </li>
        </ul>
      </Card>

      <Card>
        <h2 class="mb-3 text-base font-semibold text-navy">Dokumenti</h2>
        <p v-if="documents.length === 0" class="text-sm text-text-secondary">
          Nema dokumenata povezanih sa ovim klijentom.
        </p>
        <ul v-else class="flex flex-col divide-y divide-border">
          <li v-for="doc in documents" :key="doc.id" class="flex items-center justify-between py-2 text-sm">
            <div class="min-w-0">
              <p class="truncate text-navy">{{ doc.title }}</p>
              <p class="text-text-secondary">{{ doc.original_filename }}</p>
            </div>
            <a v-if="doc.file_url" :href="doc.file_url" target="_blank" rel="noopener" class="shrink-0 text-primary-dark hover:underline">
              Otvori
            </a>
          </li>
        </ul>
      </Card>
    </template>
  </div>
</template>
