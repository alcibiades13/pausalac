<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Button, Card, Input, Alert, Skeleton } from '@pausalac/ui'
import { getLimits, simulateLimits, type Limits, type LimitsSimulation } from '@/services/limits'
import { ApiError } from '@/lib/api'
import LimitTracker from '@/components/LimitTracker.vue'

const limits = ref<Limits | null>(null)
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')

async function load() {
  status.value = 'loading'
  try {
    limits.value = await getLimits()
    status.value = 'ready'
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo limite.'
    status.value = 'error'
  }
}

onMounted(load)

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
    simulateError.value = error instanceof ApiError ? error.message : 'Ne možemo trenutno da izračunamo simulaciju.'
  } finally {
    simulating.value = false
  }
}
</script>

<template>
  <div class="mx-auto flex max-w-lg flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">Limiti</h1>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">Pokušaj ponovo</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <template v-else-if="limits">
      <Card>
        <LimitTracker label="Paušalni limit" :tracker="limits.pausal_limit" />
      </Card>
      <Card>
        <LimitTracker label="PDV prag" :tracker="limits.vat_threshold" />
      </Card>

      <Card>
        <h2 class="mb-1 text-base font-semibold text-navy">Simulacija — ništa se ne čuva</h2>
        <p class="mb-4 text-sm text-text-secondary">
          Unesi iznos hipotetičke fakture da vidiš kako bi uticala na oba limita.
        </p>
        <form class="flex flex-col gap-4" @submit.prevent="onSimulate">
          <Alert v-if="simulateError" variant="danger">{{ simulateError }}</Alert>
          <Input
            v-model="hypotheticalAmount"
            label="Iznos hipotetičke fakture"
            placeholder="800000.00"
            required
            :disabled="simulating"
          />
          <div>
            <Button type="submit" :loading="simulating">Simuliraj</Button>
          </div>
        </form>

        <div v-if="simulation" class="mt-6 flex flex-col gap-6">
          <div>
            <p class="mb-2 text-sm font-medium text-text-secondary">Pre</p>
            <LimitTracker label="Paušalni limit" :tracker="simulation.before.pausal_limit" />
          </div>
          <div>
            <p class="mb-2 text-sm font-medium text-text-secondary">Posle</p>
            <LimitTracker label="Paušalni limit" :tracker="simulation.after.pausal_limit" />
          </div>
          <div>
            <p class="mb-2 text-sm font-medium text-text-secondary">Pre</p>
            <LimitTracker label="PDV prag" :tracker="simulation.before.vat_threshold" />
          </div>
          <div>
            <p class="mb-2 text-sm font-medium text-text-secondary">Posle</p>
            <LimitTracker label="PDV prag" :tracker="simulation.after.vat_threshold" />
          </div>
        </div>
      </Card>
    </template>
  </div>
</template>
