<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Alert, Badge, Button , DataTable, type DataTableColumn } from '@pausalac/ui'
import { listAdminNotifications, type AdminNotification } from '@/services/admin'
import { ApiError } from '@/lib/api'
import { formatDate } from '@/lib/formatDate'

const notifications = ref<AdminNotification[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const columns: DataTableColumn<AdminNotification>[] = [
  { key: 'company_name', label: 'Kompanija' },
  { key: 'recipient_email', label: 'Primalac' },
  { key: 'event_type', label: 'Događaj' },
  { key: 'channel', label: 'Kanal' },
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
    const result = await listAdminNotifications({ page: page.value })
    notifications.value = result.results
    hasNext.value = result.next !== null
    hasPrevious.value = result.previous !== null
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo obaveštenja.'
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
    <h1 class="text-xl font-semibold text-navy">Obaveštenja</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="notifications"
      :loading="loading"
      empty-title="Nema obaveštenja."
    >
      <template #actions="{ row }">
        <Badge :variant="row.status === 'failed' ? 'danger' : 'neutral'">{{ row.status }}</Badge>
      </template>
    </DataTable>

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">Prethodna</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">Sledeća</Button>
    </div>
  </div>
</template>
