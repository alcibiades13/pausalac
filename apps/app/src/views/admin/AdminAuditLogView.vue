<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Button , DataTable, type DataTableColumn } from '@pausalac/ui'
import { listAdminAuditLog, type AdminAuditLogEntry } from '@/services/admin'
import { ApiError } from '@/lib/api'
import { formatDateTime } from '@/lib/formatDate'

const { t } = useI18n()

const entries = ref<AdminAuditLogEntry[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const columns = computed<DataTableColumn<AdminAuditLogEntry>[]>(() => [
  {
    key: 'created_at',
    label: t('admin.adminAuditLogView.createdAtColumn'),
    format: (r) => formatDateTime(r.created_at),
  },
  {
    key: 'actor_email',
    label: t('admin.adminAuditLogView.actorColumn'),
    format: (r) => r.actor_email ?? t('admin.adminAuditLogView.systemFallback'),
  },
  { key: 'company_name', label: t('admin.adminAuditLogView.companyColumn'), format: (r) => r.company_name ?? '—' },
  { key: 'entity_type', label: t('admin.adminAuditLogView.entityColumn') },
  { key: 'action', label: t('admin.adminAuditLogView.actionColumn') },
])

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await listAdminAuditLog({ page: page.value })
    entries.value = result.results
    hasNext.value = result.next !== null
    hasPrevious.value = result.previous !== null
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('admin.adminAuditLogView.loadError')
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
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminAuditLogView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="entries"
      :loading="loading"
      :empty-title="t('admin.adminAuditLogView.emptyTitle')"
    />

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">{{ t('admin.adminAuditLogView.previousButton') }}</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">{{ t('admin.adminAuditLogView.nextButton') }}</Button>
    </div>
  </div>
</template>
