<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Button, Card, Input, Alert, Badge, EmptyState, MoneyDisplay, Skeleton } from '@pausalac/ui'
import {
  createTaxResolution,
  listTaxObligations,
  markObligationPaid,
  type TaxObligation,
  type TaxResolutionPayload,
} from '@/services/taxes'
import { useCompanyStore } from '@/stores/company'
import { ApiError } from '@/lib/api'

const company = useCompanyStore()
const currency = computed(() => company.currentCompany?.default_currency ?? 'RSD')

const STATUS_LABELS: Record<TaxObligation['status'], string> = {
  pending: 'Na čekanju',
  paid: 'Plaćeno',
  overdue: 'Kasni',
}
const STATUS_VARIANTS: Record<TaxObligation['status'], 'neutral' | 'success' | 'danger'> = {
  pending: 'neutral',
  paid: 'success',
  overdue: 'danger',
}

const WHY_INCOME_TAX = 'Porez na prihod od samostalne delatnosti.'
const WHY_PIO = 'Doprinos za penzijsko i invalidsko osiguranje.'
const WHY_HEALTH = 'Doprinos za zdravstveno osiguranje.'
const WHY_UNEMPLOYMENT = 'Doprinos za osiguranje za slučaj nezaposlenosti.'

// --- obligations list ---------------------------------------------------

const obligations = ref<TaxObligation[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')

async function loadObligations() {
  status.value = 'loading'
  try {
    obligations.value = (await listTaxObligations()).results
    status.value = 'ready'
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo obaveze.'
    status.value = 'error'
  }
}

onMounted(loadObligations)

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
    saveError.value = error instanceof ApiError ? error.message : 'Ne možemo trenutno da sačuvamo rešenje.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto flex max-w-2xl flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">Obaveze</h1>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">Novo poresko rešenje</h2>
      <p class="mb-4 text-sm text-text-secondary">
        Unesi iznose iz svog poreskog rešenja — aplikacija automatski generiše mesečne obaveze za
        period koji unese.
      </p>
      <form class="flex flex-col gap-4" @submit.prevent="onCreateResolution">
        <Alert v-if="saveError" variant="danger">{{ saveError }}</Alert>
        <Alert v-if="saved && rateWarnings.length === 0" variant="success">
          Rešenje sačuvano, obaveze generisane.
        </Alert>
        <Alert v-if="rateWarnings.length" variant="warning">
          <p class="mb-1 font-medium">Rešenje je sačuvano, ali proveri sledeće:</p>
          <ul class="list-disc pl-4">
            <li v-for="warning in rateWarnings" :key="warning">{{ warning }}</li>
          </ul>
        </Alert>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input v-model="form.effective_from" type="date" label="Važi od" required />
          <Input v-model="form.effective_until" type="date" label="Važi do" required />
        </div>

        <Input v-model="form.tax_base" type="number" label="Poreska osnovica" required />

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div class="flex flex-col gap-1">
            <Input v-model="form.income_tax_amount" type="number" label="Porez na prihod" required />
            <p class="text-xs text-text-secondary">{{ WHY_INCOME_TAX }}</p>
          </div>
          <div class="flex flex-col gap-1">
            <Input v-model="form.pio_amount" type="number" label="PIO" required />
            <p class="text-xs text-text-secondary">{{ WHY_PIO }}</p>
          </div>
          <div class="flex flex-col gap-1">
            <Input v-model="form.health_amount" type="number" label="Zdravstveno" required />
            <p class="text-xs text-text-secondary">{{ WHY_HEALTH }}</p>
          </div>
          <div class="flex flex-col gap-1">
            <Input v-model="form.unemployment_amount" type="number" label="Nezaposlenost" required />
            <p class="text-xs text-text-secondary">{{ WHY_UNEMPLOYMENT }}</p>
          </div>
        </div>

        <div>
          <Button type="submit" :loading="saving">Sačuvaj rešenje</Button>
        </div>
      </form>
    </Card>

    <div>
      <h2 class="mb-2 text-base font-semibold text-navy">Mesečne obaveze</h2>

      <Alert v-if="status === 'error'" variant="danger">
        {{ errorMessage }}
        <button class="ml-2 underline" @click="loadObligations">Pokušaj ponovo</button>
      </Alert>

      <Card v-else-if="status === 'loading'">
        <Skeleton :count="3" />
      </Card>

      <Card v-else-if="obligations.length === 0">
        <EmptyState
          title="Još nema obaveza."
          description="Unesi poresko rešenje iznad da generišeš mesečne obaveze."
        />
      </Card>

      <Card v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-border text-left text-xs uppercase tracking-wide text-text-secondary">
              <th class="py-2 pr-3">Period</th>
              <th class="py-2 pr-3">Rok</th>
              <th class="py-2 pr-3 text-right">Iznos</th>
              <th class="py-2 pr-3">Status</th>
              <th class="py-2 pr-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="obligation in obligations" :key="obligation.id" class="border-b border-border">
              <td class="py-2 pr-3">{{ obligation.period_start }}</td>
              <td class="py-2 pr-3">{{ obligation.due_date }}</td>
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
                  class="text-sm text-primary hover:underline disabled:opacity-40"
                  :disabled="markingPaidId === obligation.id"
                  @click="onMarkPaid(obligation.id)"
                >
                  Označi kao plaćeno
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>
    </div>
  </div>
</template>
