<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button, Card, DatePicker, Alert, Badge, EmptyState, MoneyDisplay, Skeleton, MoneyInput, DataTable, Pagination, type DataTableColumn } from '@pausalac/ui'
import {
  createTaxResolution,
  listTaxObligations,
  markObligationPaid,
  type TaxObligation,
  type TaxResolutionPayload,
} from '@/services/taxes'
import { useCompanyStore } from '@/stores/company'
import { ApiError } from '@/lib/api'
import { formatDate } from '@/lib/formatDate'
import { useTableQuery } from '@/composables/useTableQuery'

const { t } = useI18n()
const company = useCompanyStore()
const route = useRoute()
const currency = computed(() => company.currentCompany?.default_currency ?? 'RSD')

const STATUS_LABELS = computed<Record<TaxObligation['status'], string>>(() => ({
  pending: t('limitsAccountingEtc.obligationsView.statusPending'),
  paid: t('limitsAccountingEtc.obligationsView.statusPaid'),
  overdue: t('limitsAccountingEtc.obligationsView.statusOverdue'),
}))
const STATUS_VARIANTS: Record<TaxObligation['status'], 'neutral' | 'success' | 'danger'> = {
  pending: 'neutral',
  paid: 'success',
  overdue: 'danger',
}

const WHY_INCOME_TAX = computed(() => t('limitsAccountingEtc.obligationsView.incomeTaxWhy'))
const WHY_PIO = computed(() => t('limitsAccountingEtc.obligationsView.pioWhy'))
const WHY_HEALTH = computed(() => t('limitsAccountingEtc.obligationsView.healthWhy'))
const WHY_UNEMPLOYMENT = computed(() => t('limitsAccountingEtc.obligationsView.unemploymentWhy'))

// --- obligations list ---------------------------------------------------

// Seeded from ?status= on first load (master prompt §115 deep links —
// e.g. the tax_obligation_overdue notification's "Pogledaj →" link).
const statusFilter = ref<TaxObligation['status'] | ''>(
  (route.query.status as TaxObligation['status'] | undefined) ?? '',
)

const columns: DataTableColumn<TaxObligation>[] = [
  { key: 'period_start', label: t('limitsAccountingEtc.obligationsView.columnPeriod'), sortable: true },
  { key: 'due_date', label: t('limitsAccountingEtc.obligationsView.columnDueDate'), sortable: true },
  { key: 'total_amount', label: t('limitsAccountingEtc.obligationsView.columnAmount') },
  { key: 'status', label: t('limitsAccountingEtc.obligationsView.columnStatus'), sortable: true },
]

const {
  rows: obligations,
  status,
  errorMessage,
  page,
  totalPages,
  hasNext,
  hasPrevious,
  sort,
  onSort,
  nextPage,
  prevPage,
  load: loadObligations,
  reload: reloadObligations,
} = useTableQuery<TaxObligation>(
  (q) =>
    listTaxObligations({
      status: statusFilter.value || undefined,
      page: q.page,
      pageSize: q.pageSize,
      ordering: q.ordering,
    }),
  { genericErrorMessage: t('limitsAccountingEtc.obligationsView.loadError') },
)

onMounted(loadObligations)
watch(statusFilter, reloadObligations)

const markingPaidId = ref<number | null>(null)
async function onMarkPaid(id: number) {
  markingPaidId.value = id
  try {
    await markObligationPaid(id)
    await reloadObligations()
  } finally {
    markingPaidId.value = null
  }
}

// --- resolution creation form --------------------------------------------

const form = ref<TaxResolutionPayload>({
  effective_from: '',
  effective_until: '',
  tax_base: '',
  income_tax_amount: '',
  pio_amount: '',
  health_amount: '',
  unemployment_amount: '',
  notes: '',
})
const saving = ref(false)
const saveError = ref('')
const rateWarnings = ref<string[]>([])
const saved = ref(false)

async function onCreateResolution() {
  saving.value = true
  saveError.value = ''
  rateWarnings.value = []
  saved.value = false
  try {
    const resolution = await createTaxResolution(form.value)
    rateWarnings.value = resolution.rate_check_warnings
    saved.value = true
    await loadObligations()
  } catch (error) {
    saveError.value = error instanceof ApiError ? error.message : t('limitsAccountingEtc.obligationsView.saveError')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('limitsAccountingEtc.obligationsView.title') }}</h1>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">{{ t('limitsAccountingEtc.obligationsView.newResolutionTitle') }}</h2>
      <p class="mb-4 text-sm text-text-secondary">
        {{ t('limitsAccountingEtc.obligationsView.newResolutionDescription') }}
      </p>
      <form class="flex flex-col gap-4" @submit.prevent="onCreateResolution">
        <Alert v-if="saveError" variant="danger">{{ saveError }}</Alert>
        <Alert v-if="saved && rateWarnings.length === 0" variant="success">
          {{ t('limitsAccountingEtc.obligationsView.savedSuccess') }}
        </Alert>
        <Alert v-if="rateWarnings.length" variant="warning">
          <p class="mb-1 font-medium">{{ t('limitsAccountingEtc.obligationsView.warningsIntro') }}</p>
          <ul class="list-disc pl-4">
            <li v-for="warning in rateWarnings" :key="warning">{{ warning }}</li>
          </ul>
        </Alert>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <DatePicker v-model="form.effective_from" :label="t('limitsAccountingEtc.obligationsView.effectiveFromLabel')" required />
          <DatePicker v-model="form.effective_until" :label="t('limitsAccountingEtc.obligationsView.effectiveUntilLabel')" required />
          <MoneyInput v-model="form.tax_base" :label="t('limitsAccountingEtc.obligationsView.taxBaseLabel')" required />
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div class="flex flex-col gap-1">
            <MoneyInput v-model="form.income_tax_amount" :label="t('limitsAccountingEtc.obligationsView.incomeTaxLabel')" required />
            <p class="text-xs text-text-secondary">{{ WHY_INCOME_TAX }}</p>
          </div>
          <div class="flex flex-col gap-1">
            <MoneyInput v-model="form.pio_amount" :label="t('limitsAccountingEtc.obligationsView.pioLabel')" required />
            <p class="text-xs text-text-secondary">{{ WHY_PIO }}</p>
          </div>
          <div class="flex flex-col gap-1">
            <MoneyInput v-model="form.health_amount" :label="t('limitsAccountingEtc.obligationsView.healthLabel')" required />
            <p class="text-xs text-text-secondary">{{ WHY_HEALTH }}</p>
          </div>
          <div class="flex flex-col gap-1">
            <MoneyInput v-model="form.unemployment_amount" :label="t('limitsAccountingEtc.obligationsView.unemploymentLabel')" required />
            <p class="text-xs text-text-secondary">{{ WHY_UNEMPLOYMENT }}</p>
          </div>
        </div>

        <div>
          <Button type="submit" :loading="saving">{{ t('limitsAccountingEtc.obligationsView.saveButton') }}</Button>
        </div>
      </form>
    </Card>

    <div>
      <h2 class="mb-2 text-base font-semibold text-navy">{{ t('limitsAccountingEtc.obligationsView.monthlyObligationsTitle') }}</h2>

      <Alert v-if="status === 'error'" variant="danger">
        {{ errorMessage }}
        <button class="ml-2 underline" @click="reloadObligations">{{ t('limitsAccountingEtc.obligationsView.retryButton') }}</button>
      </Alert>

      <Card v-else>
        <div class="flex items-center gap-2 border-b border-border pb-4">
          <label for="obligation-status-filter" class="text-sm text-text-secondary">{{ t('limitsAccountingEtc.obligationsView.statusFilterLabel') }}</label>
          <select
            id="obligation-status-filter"
            v-model="statusFilter"
            class="rounded-lg border border-border bg-white px-3 py-1.5 text-sm text-navy focus:outline-none focus:ring-2 focus:ring-primary/40"
          >
            <option value="">{{ t('limitsAccountingEtc.obligationsView.statusAll') }}</option>
            <option v-for="[value, label] in Object.entries(STATUS_LABELS)" :key="value" :value="value">
              {{ label }}
            </option>
          </select>
        </div>

        <Skeleton v-if="status === 'loading' && obligations.length === 0" class="mt-4" :count="3" />

        <EmptyState
          v-else-if="obligations.length === 0"
          class="mt-4"
          :title="t('limitsAccountingEtc.obligationsView.emptyTitle')"
          :description="t('limitsAccountingEtc.obligationsView.emptyDescription')"
        />

        <template v-else>
          <DataTable
            class="mt-4"
            :columns="columns"
            :rows="obligations"
            :loading="status === 'loading'"
            :sort="sort"
            @sort="onSort"
          >
            <template #cell-period_start="{ row }">{{ formatDate(row.period_start) }}</template>
            <template #cell-due_date="{ row }">{{ formatDate(row.due_date) }}</template>
            <template #cell-total_amount="{ row }">
              <MoneyDisplay :amount="row.total_amount" :currency="currency" />
            </template>
            <template #cell-status="{ row }">
              <Badge :variant="STATUS_VARIANTS[row.status]">
                {{ STATUS_LABELS[row.status] }}
              </Badge>
            </template>
            <template #actions="{ row }">
              <button
                v-if="row.status !== 'paid'"
                type="button"
                class="text-sm text-primary-dark hover:underline disabled:opacity-40"
                :disabled="markingPaidId === row.id"
                @click="onMarkPaid(row.id)"
              >
                {{ t('limitsAccountingEtc.obligationsView.markPaidButton') }}
              </button>
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
  </div>
</template>
