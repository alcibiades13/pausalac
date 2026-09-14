<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Alert, Button } from '@pausalac/ui'
import AdminTable, { type AdminTableColumn } from '@/components/admin/AdminTable.vue'
import { listAdminAuditLog, type AdminAuditLogEntry } from '@/services/admin'
import { ApiError } from '@/lib/api'

const entries = ref<AdminAuditLogEntry[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const columns: AdminTableColumn<AdminAuditLogEntry>[] = [
  {
    key: 'created_at',
    label: 'Vreme',
    format: (r) => new Date(r.created_at).toLocaleString('sr-RS'),
  },
  { key: 'actor_email', label: 'Izvršilac', format: (r) => r.actor_email ?? 'sistem' },
  { key: 'company_name', label: 'Kompanija', format: (r) => r.company_name ?? '—' },
  { key: 'entity_type', label: 'Entitet' },
  { key: 'action', label: 'Akcija' },
]

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
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo audit log.'
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
    <h1 class="text-xl font-semibold text-navy">Audit log</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <AdminTable
      :columns="columns"
      :rows="entries"
      :loading="loading"
      empty-title="Nema zapisa."
    />

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">Prethodna</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">Sledeća</Button>
    </div>
  </div>
</template>
