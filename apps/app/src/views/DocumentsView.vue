<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Button, Card, Input, Select, Alert, EmptyState, Badge, Skeleton } from '@pausalac/ui'
import {
  listDocuments,
  uploadDocument,
  deleteDocument,
  type AppDocument,
  type DocumentCategory,
} from '@/services/documents'
import { listTaxResolutions, type TaxResolution } from '@/services/taxes'
import { listClients, type Client } from '@/services/clients'
import { listInvoices, type Invoice } from '@/services/invoices'
import { ApiError } from '@/lib/api'

const route = useRoute()

const CATEGORY_LABELS: Record<DocumentCategory, string> = {
  tax_resolution: 'Poresko rešenje',
  contract: 'Ugovor',
  sef_document: 'SEF dokument',
  fiscal_receipt: 'Fiskalni račun',
  other: 'Ostalo',
}
const CATEGORY_OPTIONS = Object.entries(CATEGORY_LABELS).map(([value, label]) => ({ value, label }))
const CATEGORY_FILTER_OPTIONS = [{ value: '', label: 'Sve kategorije' }, ...CATEGORY_OPTIONS]

// --- list ------------------------------------------------------------

const documents = ref<AppDocument[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')
const categoryFilter = ref('')
const searchTerm = ref('')

async function load() {
  status.value = 'loading'
  try {
    documents.value = (
      await listDocuments({
        category: (categoryFilter.value || undefined) as DocumentCategory | undefined,
        search: searchTerm.value || undefined,
      })
    ).results
    status.value = 'ready'
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo dokumente.'
    status.value = 'error'
  }
}

onMounted(async () => {
  await load()
  // Master prompt §115 deep link (e.g. from a "Dokumenti" section
  // elsewhere) — documents don't get their own detail page, so landing
  // on this list with the right row scrolled-to and highlighted is the
  // deep link.
  if (route.query.document) {
    document.getElementById(`document-${route.query.document}`)?.scrollIntoView({ block: 'center' })
  }
})
watch([categoryFilter, searchTerm], load)

const deletingId = ref<number | null>(null)
async function onDelete(id: number) {
  deletingId.value = id
  try {
    await deleteDocument(id)
    await load()
  } finally {
    deletingId.value = null
  }
}

function isImage(doc: AppDocument): boolean {
  return doc.content_type.startsWith('image/')
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// --- tax resolutions, for the optional picker --------------------------

const taxResolutions = ref<TaxResolution[]>([])
onMounted(async () => {
  try {
    taxResolutions.value = (await listTaxResolutions()).results
  } catch {
    // A failed resolution-list fetch shouldn't block the page — the
    // picker just stays empty.
  }
})
const taxResolutionOptions = computed(() => [
  { value: '', label: 'Bez povezanog rešenja' },
  ...taxResolutions.value.map((r) => ({
    value: String(r.id),
    label: `${r.effective_from} – ${r.effective_until}`,
  })),
])

// --- clients/invoices, for the optional link pickers (master prompt §102) --

const clients = ref<Client[]>([])
const invoices = ref<Invoice[]>([])
onMounted(async () => {
  try {
    clients.value = (await listClients({ pageSize: 100 })).results
  } catch {
    // A failed fetch shouldn't block the page — the picker just stays empty.
  }
  try {
    invoices.value = (await listInvoices()).results
  } catch {
    // Same as above.
  }
})
const clientOptions = computed(() => [
  { value: '', label: 'Bez povezanog klijenta' },
  ...clients.value.map((c) => ({ value: String(c.id), label: c.name })),
])
const invoiceOptions = computed(() => [
  { value: '', label: 'Bez povezane fakture' },
  ...invoices.value.map((i) => ({
    value: String(i.id),
    label: i.invoice_number ?? `Nacrt #${i.id}`,
  })),
])

// --- upload form -------------------------------------------------------

const form = ref({
  category: 'other' as DocumentCategory,
  title: '',
  description: '',
  tax_resolution: '',
  client: '',
  invoice: '',
})
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const uploadError = ref('')

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  selectedFile.value = input.files?.[0] ?? null
}

async function onUpload() {
  if (!selectedFile.value) {
    uploadError.value = 'Izaberi fajl.'
    return
  }
  uploading.value = true
  uploadError.value = ''
  try {
    await uploadDocument({
      category: form.value.category,
      title: form.value.title,
      description: form.value.description,
      tax_resolution: form.value.tax_resolution ? Number(form.value.tax_resolution) : undefined,
      client: form.value.client ? Number(form.value.client) : undefined,
      invoice: form.value.invoice ? Number(form.value.invoice) : undefined,
      file: selectedFile.value,
    })
    form.value = {
      category: 'other',
      title: '',
      description: '',
      tax_resolution: '',
      client: '',
      invoice: '',
    }
    selectedFile.value = null
    await load()
  } catch (error) {
    uploadError.value = error instanceof ApiError ? error.message : 'Ne možemo trenutno da otpremimo fajl.'
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">Dokumenti</h1>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">Otpremi dokument</h2>
      <form class="flex flex-col gap-4" @submit.prevent="onUpload">
        <Alert v-if="uploadError" variant="danger">{{ uploadError }}</Alert>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Select v-model="form.category" label="Kategorija" :options="CATEGORY_OPTIONS" required />
          <Input v-model="form.title" label="Naziv" required />
          <Input v-model="form.description" label="Opis (opciono)" />
          <Select
            v-model="form.tax_resolution"
            label="Povezano poresko rešenje"
            :options="taxResolutionOptions"
          />
          <Select v-model="form.client" label="Povezani klijent" :options="clientOptions" />
          <Select v-model="form.invoice" label="Povezana faktura" :options="invoiceOptions" />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-navy" for="doc-file">Fajl</label>
          <input
            id="doc-file"
            type="file"
            class="text-sm text-navy"
            accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.xls,.xlsx"
            @change="onFileChange"
          />
          <p class="text-xs text-text-secondary">Maksimalno 20MB — PDF, slika, Word ili Excel.</p>
        </div>
        <div>
          <Button type="submit" :loading="uploading">Otpremi</Button>
        </div>
      </form>
    </Card>

    <div class="flex flex-wrap items-end gap-3">
      <Select v-model="categoryFilter" label="Kategorija" :options="CATEGORY_FILTER_OPTIONS" />
      <Input v-model="searchTerm" label="Pretraga" placeholder="Naziv, opis, fajl..." />
    </div>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">Pokušaj ponovo</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <Card v-else-if="documents.length === 0">
      <EmptyState title="Još nema dokumenata." description="Otpremi prvi dokument iznad." />
    </Card>

    <div v-else class="flex flex-col gap-2">
      <Card
        v-for="doc in documents"
        :id="`document-${doc.id}`"
        :key="doc.id"
        class="flex flex-col gap-3 sm:flex-row sm:items-center"
        :class="String(doc.id) === route.query.document ? 'ring-2 ring-primary' : ''"
      >
        <div class="flex min-w-0 flex-1 items-center gap-4">
          <img v-if="isImage(doc)" :src="doc.file_url ?? undefined" class="h-12 w-12 shrink-0 rounded object-cover" alt="" />
          <div v-else class="flex h-12 w-12 shrink-0 items-center justify-center rounded bg-background text-xl">
            📄
          </div>
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <Badge variant="neutral">{{ CATEGORY_LABELS[doc.category] }}</Badge>
              <span class="font-medium text-navy">{{ doc.title }}</span>
            </div>
            <p class="text-sm text-text-secondary">
              {{ doc.original_filename }} · {{ formatSize(doc.size_bytes) }}
              <span v-if="doc.uploaded_by_name"> · {{ doc.uploaded_by_name }}</span>
            </p>
          </div>
        </div>
        <div class="flex items-center gap-3 sm:shrink-0">
          <a
            v-if="doc.file_url"
            :href="doc.file_url"
            target="_blank"
            rel="noopener"
            class="text-sm text-primary hover:underline"
          >
            Otvori
          </a>
          <button
            type="button"
            class="text-sm text-danger hover:underline disabled:opacity-40"
            :disabled="deletingId === doc.id"
            @click="onDelete(doc.id)"
          >
            Obriši
          </button>
        </div>
      </Card>
    </div>
  </div>
</template>
