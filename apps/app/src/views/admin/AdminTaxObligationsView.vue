<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Alert, Badge, Button, MoneyDisplay , DataTable, type DataTableColumn } from '@pausalac/ui'
import { listAdminTaxObligations, type AdminTaxObligation } from '@/services/admin'
import { ApiError } from '@/lib/api'

const obligations = ref<AdminTaxObligation[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const STATUS_LABELS: Record<string, string> = {
  pending: 'Na čekanju',
  paid: 'Plaćeno',
  overdue: 'Kasni',
}
const STATUS_VARIANTS: Record<string, 'success' | 'warning' | 'danger' | 'neutral'> = {
  pending: 'neutral',
  paid: 'success',
  overdue: 'danger',
}

const columns: DataTableColumn<AdminTaxObligation>[] = [
  { key: 'company_name', label: 'Kompanija' },
  { key: 'period_start', label: 'Period' },
  { key: 'due_date', label: 'Rok' },
]

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await listAdminTaxObligations({ page: page.value })
    obligations.value = result.results
    hasNext.value = result.next !== null
    hasPrevious.value = result.previous !== null
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo poreske obaveze.'
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
    <h1 class="text-xl font-semibold text-navy">Poreske obaveze</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="obligations"
      :loading="loading"
      empty-title="Nema poreskih obaveza."
    >
      <template #actions="{ row }">
        <div class="flex items-center gap-2">
          <Badge :variant="STATUS_VARIANTS[row.status] ?? 'neutral'">
            {{ STATUS_LABELS[row.status] ?? row.status }}
          </Badge>
          <MoneyDisplay :amount="row.total_amount" currency="RSD" />
        </div>
      </template>
    </DataTable>

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">Prethodna</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">Sledeća</Button>
    </div>
  </div>
</template>
