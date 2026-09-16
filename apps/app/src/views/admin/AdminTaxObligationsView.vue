<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Badge, Button, MoneyDisplay , DataTable, type DataTableColumn } from '@pausalac/ui'
import { listAdminTaxObligations, type AdminTaxObligation } from '@/services/admin'
import { ApiError } from '@/lib/api'

const { t } = useI18n()

const obligations = ref<AdminTaxObligation[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const STATUS_LABELS = computed<Record<string, string>>(() => ({
  pending: t('admin.adminTaxObligationsView.statusPending'),
  paid: t('admin.adminTaxObligationsView.statusPaid'),
  overdue: t('admin.adminTaxObligationsView.statusOverdue'),
}))
const STATUS_VARIANTS: Record<string, 'success' | 'warning' | 'danger' | 'neutral'> = {
  pending: 'neutral',
  paid: 'success',
  overdue: 'danger',
}

const columns = computed<DataTableColumn<AdminTaxObligation>[]>(() => [
  { key: 'company_name', label: t('admin.adminTaxObligationsView.companyColumn') },
  { key: 'period_start', label: t('admin.adminTaxObligationsView.periodColumn') },
  { key: 'due_date', label: t('admin.adminTaxObligationsView.dueDateColumn') },
])

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
      error instanceof ApiError ? error.message : t('admin.adminTaxObligationsView.loadError')
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
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminTaxObligationsView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="obligations"
      :loading="loading"
      :empty-title="t('admin.adminTaxObligationsView.emptyTitle')"
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
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">{{ t('admin.adminTaxObligationsView.previousButton') }}</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">{{ t('admin.adminTaxObligationsView.nextButton') }}</Button>
    </div>
  </div>
</template>
