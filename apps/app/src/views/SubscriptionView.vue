<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Button, Card, Alert, Badge, Skeleton } from '@pausalac/ui'
import {
  listPlans,
  getCurrentSubscription,
  activatePlan,
  cancelSubscription,
  type Plan,
  type Subscription,
  type SubscriptionStatus,
} from '@/services/subscriptions'
import { ApiError } from '@/lib/api'

const STATUS_LABELS: Record<SubscriptionStatus, string> = {
  trialing: 'Probni period',
  active: 'Aktivna',
  grace_period: 'Period odlaganja',
  cancelled: 'Otkazana',
  expired: 'Istekla',
}
const STATUS_VARIANTS: Record<SubscriptionStatus, 'neutral' | 'success' | 'warning' | 'danger'> = {
  trialing: 'neutral',
  active: 'success',
  grace_period: 'warning',
  cancelled: 'danger',
  expired: 'danger',
}

const subscription = ref<Subscription | null>(null)
const plans = ref<Plan[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')

async function load() {
  status.value = 'loading'
  try {
    const [sub, planList] = await Promise.all([getCurrentSubscription(), listPlans()])
    subscription.value = sub
    plans.value = planList
    status.value = 'ready'
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo pretplatu.'
    status.value = 'error'
  }
}

onMounted(load)

const trialDaysLeft = computed(() => {
  if (!subscription.value || subscription.value.status !== 'trialing') return null
  const diffMs = new Date(subscription.value.trial_ends_at).getTime() - Date.now()
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24))
})

const activatingPlanId = ref<number | null>(null)
const actionError = ref('')

async function onActivate(plan: Plan) {
  activatingPlanId.value = plan.id
  actionError.value = ''
  try {
    subscription.value = await activatePlan(plan.id)
  } catch (error) {
    actionError.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da aktiviramo plan.'
  } finally {
    activatingPlanId.value = null
  }
}

const cancelling = ref(false)

async function onCancel() {
  cancelling.value = true
  actionError.value = ''
  try {
    subscription.value = await cancelSubscription()
  } catch (error) {
    actionError.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da otkažemo pretplatu.'
  } finally {
    cancelling.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">Pretplata</h1>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">Pokušaj ponovo</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <template v-else-if="subscription">
      <Card>
        <div class="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div class="mb-1 flex items-center gap-2">
              <Badge :variant="STATUS_VARIANTS[subscription.status]">
                {{ STATUS_LABELS[subscription.status] }}
              </Badge>
              <span v-if="subscription.plan" class="text-sm font-medium text-navy">
                {{ subscription.plan.name }}
              </span>
            </div>
            <p v-if="subscription.status === 'trialing'" class="text-sm text-text-secondary">
              <template v-if="trialDaysLeft !== null && trialDaysLeft > 0">
                Probni period ističe za {{ trialDaysLeft }} dan(a).
              </template>
              <template v-else>Probni period je istekao.</template>
            </p>
            <p v-else-if="subscription.status === 'active' && subscription.current_period_end" class="text-sm text-text-secondary">
              Sledeće obnavljanje: {{ subscription.current_period_end.slice(0, 10) }}
            </p>
            <p v-else-if="subscription.status === 'expired' || subscription.status === 'cancelled'" class="text-sm text-danger">
              Pretplata nije aktivna — izaberi plan da nastaviš da izdaješ fakture.
            </p>
          </div>
          <Button
            v-if="subscription.status === 'active' || subscription.status === 'grace_period'"
            variant="ghost"
            :loading="cancelling"
            @click="onCancel"
          >
            Otkaži pretplatu
          </Button>
        </div>
      </Card>

      <Alert v-if="actionError" variant="danger">{{ actionError }}</Alert>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Card v-for="plan in plans" :key="plan.id" class="flex flex-col gap-3">
          <div>
            <h2 class="font-display text-base font-semibold text-navy">{{ plan.name }}</h2>
            <p class="mt-1 text-2xl font-semibold text-navy">
              {{ plan.price }} <span class="text-sm font-normal text-text-secondary">{{ plan.currency }}/mes</span>
            </p>
          </div>
          <Button
            v-if="subscription.plan?.id !== plan.id || subscription.status !== 'active'"
            :loading="activatingPlanId === plan.id"
            @click="onActivate(plan)"
          >
            Izaberi
          </Button>
          <Button v-else variant="secondary" disabled>Trenutni plan</Button>
        </Card>
      </div>
    </template>
  </div>
</template>
