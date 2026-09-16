<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Button , DataTable, type DataTableColumn } from '@pausalac/ui'
import { listAdminDocuments, type AdminDocument } from '@/services/admin'
import { ApiError } from '@/lib/api'
import { formatDate } from '@/lib/formatDate'

const { t } = useI18n()

const documents = ref<AdminDocument[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const columns = computed<DataTableColumn<AdminDocument>[]>(() => [
  { key: 'company_name', label: t('admin.adminDocumentsView.companyColumn') },
  { key: 'title', label: t('admin.adminDocumentsView.nameColumn') },
  { key: 'category', label: t('admin.adminDocumentsView.categoryColumn') },
  { key: 'uploaded_by_email', label: t('admin.adminDocumentsView.uploadedByColumn'), format: (r) => r.uploaded_by_email ?? '—' },
  {
    key: 'created_at',
    label: t('admin.adminDocumentsView.dateColumn'),
    format: (r) => formatDate(r.created_at),
  },
])

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await listAdminDocuments({ page: page.value })
    documents.value = result.results
    hasNext.value = result.next !== null
    hasPrevious.value = result.previous !== null
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('admin.adminDocumentsView.loadError')
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
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminDocumentsView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="documents"
      :loading="loading"
      :empty-title="t('admin.adminDocumentsView.emptyTitle')"
    />

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">{{ t('admin.adminDocumentsView.previousButton') }}</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">{{ t('admin.adminDocumentsView.nextButton') }}</Button>
    </div>
  </div>
</template>
