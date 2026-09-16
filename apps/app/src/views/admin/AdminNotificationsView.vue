<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Badge, Button , DataTable, type DataTableColumn } from '@pausalac/ui'
import { listAdminNotifications, type AdminNotification } from '@/services/admin'
import { ApiError } from '@/lib/api'
import { formatDate } from '@/lib/formatDate'

const { t } = useI18n()

const notifications = ref<AdminNotification[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const columns = computed<DataTableColumn<AdminNotification>[]>(() => [
  { key: 'company_name', label: t('admin.adminNotificationsView.companyColumn') },
  { key: 'recipient_email', label: t('admin.adminNotificationsView.recipientColumn') },
  { key: 'event_type', label: t('admin.adminNotificationsView.eventColumn') },
  { key: 'channel', label: t('admin.adminNotificationsView.channelColumn') },
  {
    key: 'created_at',
    label: t('admin.adminNotificationsView.dateColumn'),
    format: (r) => formatDate(r.created_at),
  },
])

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await listAdminNotifications({ page: page.value })
    notifications.value = result.results
    hasNext.value = result.next !== null
    hasPrevious.value = result.previous !== null
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('admin.adminNotificationsView.loadError')
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
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminNotificationsView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="notifications"
      :loading="loading"
      :empty-title="t('admin.adminNotificationsView.emptyTitle')"
    >
      <template #actions="{ row }">
        <Badge :variant="row.status === 'failed' ? 'danger' : 'neutral'">{{ row.status }}</Badge>
      </template>
    </DataTable>

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">{{ t('admin.adminNotificationsView.previousButton') }}</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">{{ t('admin.adminNotificationsView.nextButton') }}</Button>
    </div>
  </div>
</template>
