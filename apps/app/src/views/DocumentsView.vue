<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Select, Alert, EmptyState, Badge, DataTable, Pagination, Skeleton, type DataTableColumn } from '@pausalac/ui'
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
import { useTableQuery } from '@/composables/useTableQuery'
import { formatDate } from '@/lib/formatDate'

const { t } = useI18n()
const route = useRoute()

const CATEGORY_LABELS = computed<Record<DocumentCategory, string>>(() => ({
  tax_resolution: t('limitsAccountingEtc.documentsView.categoryTaxResolution'),
  contract: t('limitsAccountingEtc.documentsView.categoryContract'),
  sef_document: t('limitsAccountingEtc.documentsView.categorySefDocument'),
  fiscal_receipt: t('limitsAccountingEtc.documentsView.categoryFiscalReceipt'),
  other: t('limitsAccountingEtc.documentsView.categoryOther'),
}))
const CATEGORY_OPTIONS = computed(() =>
  Object.entries(CATEGORY_LABELS.value).map(([value, label]) => ({ value, label })),
)
const CATEGORY_FILTER_OPTIONS = computed(() => [
  { value: '', label: t('limitsAccountingEtc.documentsView.allCategoriesOption') },
  ...CATEGORY_OPTIONS.value,
])

// --- list ------------------------------------------------------------

const categoryFilter = ref('')

const columns: DataTableColumn<AppDocument>[] = [
  { key: 'title', label: t('limitsAccountingEtc.documentsView.columnTitle'), sortable: true },
  { key: 'category', label: t('limitsAccountingEtc.documentsView.columnCategory') },
  { key: 'original_filename', label: t('limitsAccountingEtc.documentsView.columnFile') },
  { key: 'size_bytes', label: t('limitsAccountingEtc.documentsView.columnSize') },
  { key: 'created_at', label: t('limitsAccountingEtc.documentsView.columnCreatedAt'), sortable: true },
]

const {
  rows: documents,
  status,
  errorMessage,
  page,
  totalPages,
  hasNext,
  hasPrevious,
  search: searchTerm,
  sort,
  onSort,
  nextPage,
  prevPage,
  load,
  reload,
} = useTableQuery<AppDocument>(
  (q) =>
    listDocuments({
      category: (categoryFilter.value || undefined) as DocumentCategory | undefined,
      page: q.page,
      pageSize: q.pageSize,
      search: q.search,
      ordering: q.ordering,
    }),
  { genericErrorMessage: t('limitsAccountingEtc.documentsView.loadError') },
)

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
watch(categoryFilter, reload)

const deletingId = ref<number | null>(null)
async function onDelete(id: number) {
  deletingId.value = id
  try {
    await deleteDocument(id)
    await reload()
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
  { value: '', label: t('limitsAccountingEtc.documentsView.noTaxResolutionOption') },
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
  { value: '', label: t('limitsAccountingEtc.documentsView.noClientOption') },
  ...clients.value.map((c) => ({ value: String(c.id), label: c.name })),
])
const invoiceOptions = computed(() => [
  { value: '', label: t('limitsAccountingEtc.documentsView.noInvoiceOption') },
  ...invoices.value.map((i) => ({
    value: String(i.id),
    label: i.invoice_number ?? t('limitsAccountingEtc.documentsView.draftInvoiceLabel', { id: i.id }),
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
    uploadError.value = t('limitsAccountingEtc.documentsView.selectFileError')
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
    uploadError.value = error instanceof ApiError ? error.message : t('limitsAccountingEtc.documentsView.uploadError')
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('limitsAccountingEtc.documentsView.title') }}</h1>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">{{ t('limitsAccountingEtc.documentsView.uploadTitle') }}</h2>
      <form class="flex flex-col gap-4" @submit.prevent="onUpload">
        <Alert v-if="uploadError" variant="danger">{{ uploadError }}</Alert>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Select v-model="form.category" :label="t('limitsAccountingEtc.documentsView.categoryLabel')" :options="CATEGORY_OPTIONS" required />
          <Input v-model="form.title" :label="t('limitsAccountingEtc.documentsView.titleLabel')" required />
          <Input v-model="form.description" :label="t('limitsAccountingEtc.documentsView.descriptionLabel')" />
          <Select
            v-model="form.tax_resolution"
            :label="t('limitsAccountingEtc.documentsView.taxResolutionLabel')"
            :options="taxResolutionOptions"
          />
          <Select v-model="form.client" :label="t('limitsAccountingEtc.documentsView.clientLabel')" :options="clientOptions" />
          <Select v-model="form.invoice" :label="t('limitsAccountingEtc.documentsView.invoiceLabel')" :options="invoiceOptions" />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-navy" for="doc-file">{{ t('limitsAccountingEtc.documentsView.fileLabel') }}</label>
          <input
            id="doc-file"
            type="file"
            class="text-sm text-navy"
            accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.xls,.xlsx"
            @change="onFileChange"
          />
          <p class="text-xs text-text-secondary">{{ t('limitsAccountingEtc.documentsView.fileHint') }}</p>
        </div>
        <div>
          <Button type="submit" :loading="uploading">{{ t('limitsAccountingEtc.documentsView.uploadButton') }}</Button>
        </div>
      </form>
    </Card>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="reload">{{ t('limitsAccountingEtc.documentsView.retryButton') }}</button>
    </Alert>

    <Card v-else>
      <div class="flex flex-wrap items-end gap-3 border-b border-border pb-4">
        <Select v-model="categoryFilter" :label="t('limitsAccountingEtc.documentsView.categoryLabel')" :options="CATEGORY_FILTER_OPTIONS" />
        <Input
          v-model="searchTerm"
          label-sr-only
          :label="t('limitsAccountingEtc.documentsView.searchLabel')"
          :placeholder="t('limitsAccountingEtc.documentsView.searchPlaceholder')"
        />
      </div>

      <Skeleton v-if="status === 'loading' && documents.length === 0" class="mt-4" :count="3" />

      <EmptyState
        v-else-if="documents.length === 0"
        class="mt-4"
        :title="t('limitsAccountingEtc.documentsView.emptyTitle')"
        :description="t('limitsAccountingEtc.documentsView.emptyDescription')"
      />

      <template v-else>
        <DataTable
          class="mt-4"
          :columns="columns"
          :rows="documents"
          :loading="status === 'loading'"
          :sort="sort"
          @sort="onSort"
        >
          <template #cell-title="{ row }">
            <div class="flex min-w-0 items-center gap-3">
              <img
                v-if="isImage(row)"
                :src="row.file_url ?? undefined"
                class="h-8 w-8 shrink-0 rounded object-cover"
                :alt="t('limitsAccountingEtc.documentsView.previewAlt', { title: row.title })"
              />
              <div
                v-else
                class="flex h-8 w-8 shrink-0 items-center justify-center rounded bg-background text-base"
                aria-hidden="true"
              >
                📄
              </div>
              <div class="min-w-0">
                <span
                  :id="`document-${row.id}`"
                  class="font-medium text-navy"
                  :class="String(row.id) === route.query.document ? 'rounded ring-2 ring-primary' : ''"
                >
                  {{ row.title }}
                </span>
                <p v-if="row.uploaded_by_name" class="text-xs text-text-secondary">{{ row.uploaded_by_name }}</p>
              </div>
            </div>
          </template>
          <template #cell-category="{ row }">
            <Badge variant="neutral">{{ CATEGORY_LABELS[row.category] }}</Badge>
          </template>
          <template #cell-size_bytes="{ row }">
            {{ formatSize(row.size_bytes) }}
          </template>
          <template #cell-created_at="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
          <template #actions="{ row }">
            <div class="flex items-center gap-3">
              <a
                v-if="row.file_url"
                :href="row.file_url"
                target="_blank"
                rel="noopener"
                class="text-sm text-primary-dark hover:underline"
              >
                {{ t('limitsAccountingEtc.documentsView.openLink') }}
              </a>
              <button
                type="button"
                class="text-sm text-danger hover:underline disabled:opacity-40"
                :disabled="deletingId === row.id"
                @click="onDelete(row.id)"
              >
                {{ t('limitsAccountingEtc.documentsView.deleteButton') }}
              </button>
            </div>
          </template>
        </DataTable>

        <Pagination
          class="mt-4"
          :has-next="hasNext"
          :has-previous="hasPrevious"
          :page="page"
          :total-pages="totalPages"
          @next="nextPage"
          @previous="prevPage"
        />
      </template>
    </Card>
  </div>
</template>
