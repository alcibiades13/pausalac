<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Alert, Button } from '@pausalac/ui'
import AdminTable, { type AdminTableColumn } from '@/components/admin/AdminTable.vue'
import { listAdminDocuments, type AdminDocument } from '@/services/admin'
import { ApiError } from '@/lib/api'
import { formatDate } from '@/lib/formatDate'

const documents = ref<AdminDocument[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const columns: AdminTableColumn<AdminDocument>[] = [
  { key: 'company_name', label: 'Kompanija' },
  { key: 'title', label: 'Naziv' },
  { key: 'category', label: 'Kategorija' },
  { key: 'uploaded_by_email', label: 'Otpremio', format: (r) => r.uploaded_by_email ?? '—' },
  {
    key: 'created_at',
    label: 'Datum',
    format: (r) => formatDate(r.created_at),
  },
]

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
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo dokumente.'
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
    <h1 class="text-xl font-semibold text-navy">Dokumenti</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <AdminTable
      :columns="columns"
      :rows="documents"
      :loading="loading"
      empty-title="Nema dokumenata."
    />

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">Prethodna</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">Sledeća</Button>
    </div>
  </div>
</template>
