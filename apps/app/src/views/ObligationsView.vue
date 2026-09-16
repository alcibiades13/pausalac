<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Alert, Badge, EmptyState, MoneyDisplay, Skeleton, MoneyInput } from '@pausalac/ui'
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

const obligations = ref<TaxObligation[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')
// Seeded from ?status= on first load (master prompt §115 deep links —
// e.g. the tax_obligation_overdue notification's "Pogledaj →" link).
const statusFilter = ref<TaxObligation['status'] | ''>(
  (route.query.status as TaxObligation['status'] | undefined) ?? '',
)

async function loadObligations() {
  status.value = 'loading'
  try {
    obligations.value = (
      await listTaxObligations({ status: statusFilter.value || undefined })
    ).results
    status.value = 'ready'
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : t('limitsAccountingEtc.obligationsView.loadError')
    status.value = 'error'
  }
}

onMounted(loadObligations)
watch(statusFilter, loadObligations)

const markingPaidId = ref<number | null>(null)
async function onMarkPaid(id: number) {
  markingPaidId.value = id
  try {
    await markObligationPaid(id)
    await loadObligations()
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
          <Input v-model="form.effective_from" type="date" :label="t('limitsAccountingEtc.obligationsView.effectiveFromLabel')" required />
          <Input v-model="form.effective_until" type="date" :label="t('limitsAccountingEtc.obligationsView.effectiveUntilLabel')" required />
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
      <div class="mb-2 flex flex-wrap items-center justify-between gap-3">
        <h2 class="text-base font-semibold text-navy">{{ t('limitsAccountingEtc.obligationsView.monthlyObligationsTitle') }}</h2>
        <div class="flex items-center gap-2">
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
      </div>

      <Alert v-if="status === 'error'" variant="danger">
        {{ errorMessage }}
        <button class="ml-2 underline" @click="loadObligations">{{ t('limitsAccountingEtc.obligationsView.retryButton') }}</button>
      </Alert>

      <Card v-else-if="status === 'loading'">
        <Skeleton :count="3" />
      </Card>

      <Card v-else-if="obligations.length === 0">
        <EmptyState
          :title="t('limitsAccountingEtc.obligationsView.emptyTitle')"
          :description="t('limitsAccountingEtc.obligationsView.emptyDescription')"
        />
      </Card>

      <Card v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-border text-left text-xs uppercase tracking-wide text-text-secondary">
              <th class="py-2 pr-3">{{ t('limitsAccountingEtc.obligationsView.columnPeriod') }}</th>
              <th class="py-2 pr-3">{{ t('limitsAccountingEtc.obligationsView.columnDueDate') }}</th>
              <th class="py-2 pr-3 text-right">{{ t('limitsAccountingEtc.obligationsView.columnAmount') }}</th>
              <th class="py-2 pr-3">{{ t('limitsAccountingEtc.obligationsView.columnStatus') }}</th>
              <th class="py-2 pr-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="obligation in obligations" :key="obligation.id" class="border-b border-border">
              <td class="py-2 pr-3">{{ formatDate(obligation.period_start) }}</td>
              <td class="py-2 pr-3">{{ formatDate(obligation.due_date) }}</td>
              <td class="py-2 pr-3 text-right">
                <MoneyDisplay :amount="obligation.total_amount" :currency="currency" />
              </td>
              <td class="py-2 pr-3">
                <Badge :variant="STATUS_VARIANTS[obligation.status]">
                  {{ STATUS_LABELS[obligation.status] }}
                </Badge>
              </td>
              <td class="py-2 pr-3">
                <button
                  v-if="obligation.status !== 'paid'"
                  type="button"
                  class="text-sm text-primary-dark hover:underline disabled:opacity-40"
                  :disabled="markingPaidId === obligation.id"
                  @click="onMarkPaid(obligation.id)"
                >
                  {{ t('limitsAccountingEtc.obligationsView.markPaidButton') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>
    </div>
  </div>
</template>
