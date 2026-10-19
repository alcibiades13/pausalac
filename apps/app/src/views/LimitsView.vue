<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Alert, Skeleton } from '@pausalac/ui'
import { getLimits, getLimitHistory, simulateLimits, type Limits, type LimitHistory, type LimitsSimulation } from '@/services/limits'
import { ApiError } from '@/lib/api'
import LimitTracker from '@/components/LimitTracker.vue'
import LimitProgressChart from '@/components/charts/LimitProgressChart.vue'

const { t } = useI18n()

const limits = ref<Limits | null>(null)
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')

async function load() {
  status.value = 'loading'
  try {
    limits.value = await getLimits()
    status.value = 'ready'
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : t('limitsAccountingEtc.limitsView.loadError')
    status.value = 'error'
  }
}

onMounted(load)

// --- history + projection chart (blueprint §6.5, detail page only) ------

const history = ref<LimitHistory | null>(null)
const historyStatus = ref<'loading' | 'ready' | 'error'>('loading')
const historyError = ref('')

async function loadHistory() {
  historyStatus.value = 'loading'
  try {
    history.value = await getLimitHistory()
    historyStatus.value = 'ready'
  } catch (error) {
    historyError.value = error instanceof ApiError ? error.message : t('limitsAccountingEtc.limitsView.loadError')
    historyStatus.value = 'error'
  }
}

onMounted(loadHistory)

// --- what-if calculator (§19/§98 — pure simulation, ništa se ne čuva) ---

const hypotheticalAmount = ref('')
const simulating = ref(false)
const simulateError = ref('')
const simulation = ref<LimitsSimulation | null>(null)

async function onSimulate() {
  simulateError.value = ''
  simulation.value = null
  simulating.value = true
  try {
    simulation.value = await simulateLimits(hypotheticalAmount.value)
  } catch (error) {
    simulateError.value = error instanceof ApiError ? error.message : t('limitsAccountingEtc.limitsView.simulateError')
  } finally {
    simulating.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('limitsAccountingEtc.limitsView.title') }}</h1>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">{{ t('limitsAccountingEtc.limitsView.retryButton') }}</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <template v-else-if="limits">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Card>
          <LimitTracker :label="t('limitsAccountingEtc.limitsView.pausalLimitLabel')" :tracker="limits.pausal_limit" />
        </Card>
        <Card>
          <LimitTracker :label="t('limitsAccountingEtc.limitsView.vatThresholdLabel')" :tracker="limits.vat_threshold" />
        </Card>
      </div>

      <Card>
        <h2 class="mb-3 text-sm font-medium text-navy">{{ t('limitsAccountingEtc.charts.limitProgress.title') }}</h2>
        <Alert v-if="historyStatus === 'error'" variant="danger">
          {{ historyError }}
          <button class="ml-2 underline" @click="loadHistory">{{ t('limitsAccountingEtc.limitsView.retryButton') }}</button>
        </Alert>
        <Skeleton v-else-if="historyStatus === 'loading'" :count="1" height="220px" />
        <LimitProgressChart
          v-else-if="history"
          :history="history.history"
          :projection="history.projection"
          :threshold="history.threshold"
          :currency="history.currency"
        />
      </Card>

      <Card>
        <h2 class="mb-1 text-base font-semibold text-navy">{{ t('limitsAccountingEtc.limitsView.simulationTitle') }}</h2>
        <p class="mb-4 text-sm text-text-secondary">
          {{ t('limitsAccountingEtc.limitsView.simulationDescription') }}
        </p>
        <form class="flex flex-col gap-4 sm:flex-row sm:items-end" @submit.prevent="onSimulate">
          <Input
            v-model="hypotheticalAmount"
            :label="t('limitsAccountingEtc.limitsView.hypotheticalAmountLabel')"
            placeholder="800000.00"
            required
            :disabled="simulating"
            class="sm:max-w-xs"
          />
          <div>
            <Button type="submit" :loading="simulating">{{ t('limitsAccountingEtc.limitsView.simulateButton') }}</Button>
          </div>
        </form>
        <Alert v-if="simulateError" variant="danger" class="mt-4">{{ simulateError }}</Alert>

        <div v-if="simulation" class="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div>
            <p class="mb-2 text-sm font-medium text-text-secondary">{{ t('limitsAccountingEtc.limitsView.beforeLabel') }}</p>
            <LimitTracker :label="t('limitsAccountingEtc.limitsView.pausalLimitLabel')" :tracker="simulation.before.pausal_limit" />
          </div>
          <div>
            <p class="mb-2 text-sm font-medium text-text-secondary">{{ t('limitsAccountingEtc.limitsView.afterLabel') }}</p>
            <LimitTracker :label="t('limitsAccountingEtc.limitsView.pausalLimitLabel')" :tracker="simulation.after.pausal_limit" />
          </div>
          <div>
            <p class="mb-2 text-sm font-medium text-text-secondary">{{ t('limitsAccountingEtc.limitsView.beforeLabel') }}</p>
            <LimitTracker :label="t('limitsAccountingEtc.limitsView.vatThresholdLabel')" :tracker="simulation.before.vat_threshold" />
          </div>
          <div>
            <p class="mb-2 text-sm font-medium text-text-secondary">{{ t('limitsAccountingEtc.limitsView.afterLabel') }}</p>
            <LimitTracker :label="t('limitsAccountingEtc.limitsView.vatThresholdLabel')" :tracker="simulation.after.vat_threshold" />
          </div>
        </div>
      </Card>
    </template>
  </div>
</template>
