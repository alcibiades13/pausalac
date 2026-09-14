<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Alert, Badge, Button } from '@pausalac/ui'
import AdminTable, { type AdminTableColumn } from '@/components/admin/AdminTable.vue'
import { listAdminSubscriptions, type AdminSubscription } from '@/services/admin'
import { ApiError } from '@/lib/api'

const subscriptions = ref<AdminSubscription[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const STATUS_LABELS: Record<AdminSubscription['status'], string> = {
  trialing: 'Probni period',
  active: 'Aktivna',
  grace_period: 'Period odlaganja',
  cancelled: 'Otkazana',
  expired: 'Istekla',
}
const STATUS_VARIANTS: Record<AdminSubscription['status'], 'success' | 'warning' | 'danger' | 'neutral'> = {
  trialing: 'neutral',
  active: 'success',
  grace_period: 'warning',
  cancelled: 'danger',
  expired: 'danger',
}

const columns: AdminTableColumn<AdminSubscription>[] = [
  { key: 'company_name', label: 'Kompanija' },
  { key: 'plan', label: 'Plan', format: (r) => r.plan?.name ?? '—' },
  { key: 'trial_ends_at', label: 'Probni period do', format: (r) => new Date(r.trial_ends_at).toLocaleDateString('sr-RS') },
]

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await listAdminSubscriptions({ page: page.value })
    subscriptions.value = result.results
    hasNext.value = result.next !== null
    hasPrevious.value = result.previous !== null
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo pretplate.'
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
    <h1 class="text-xl font-semibold text-navy">Pretplate</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <AdminTable
      :columns="columns"
      :rows="subscriptions"
      :loading="loading"
      empty-title="Nema pretplata."
    >
      <template #actions="{ row }">
        <Badge :variant="STATUS_VARIANTS[row.status]">{{ STATUS_LABELS[row.status] }}</Badge>
      </template>
    </AdminTable>

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">Prethodna</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">Sledeća</Button>
    </div>
  </div>
</template>
