<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Button, Card, Input, Alert, MoneyDisplay, EmptyState } from '@pausalac/ui'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { createCompany } from '@/services/companies'
import { getDashboard, type Dashboard } from '@/services/analytics'
import { ApiError } from '@/lib/api'
import AttentionItem from '@/components/AttentionItem.vue'

const auth = useAuthStore()
const company = useCompanyStore()

const resending = ref(false)
const resent = ref(false)

async function onResendVerification() {
  resending.value = true
  try {
    await auth.resendVerificationEmail()
    resent.value = true
  } finally {
    resending.value = false
  }
}

// --- zero-company bridge (create-company form) ------------------------

const companyName = ref('')
const creatingCompany = ref(false)
const createCompanyError = ref('')

async function onCreateCompany() {
  creatingCompany.value = true
  createCompanyError.value = ''
  try {
    await createCompany(companyName.value)
    await auth.refreshMe()
  } catch (error) {
    createCompanyError.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da napravimo kompaniju. Pokušaj ponovo.'
  } finally {
    creatingCompany.value = false
  }
}

// --- dashboard -----------------------------------------------------------

const dashboard = ref<Dashboard | null>(null)
const dashboardStatus = ref<'loading' | 'ready' | 'error'>('loading')
const dashboardError = ref('')

const HEALTH_LABELS: Record<string, string> = {
  ok: '🟢 Sve je u redu',
  attention: '🟡 Potrebna pažnja',
  critical: '🔴 Potrebna akcija',
}

async function loadDashboard() {
  if (!company.currentCompanyId) return
  dashboardStatus.value = 'loading'
  try {
    dashboard.value = await getDashboard()
    dashboardStatus.value = 'ready'
  } catch (error) {
    dashboardError.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo pregled.'
    dashboardStatus.value = 'error'
  }
}

onMounted(loadDashboard)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">
      Zdravo, {{ auth.user?.first_name || auth.user?.email }}.
    </h1>

    <Alert v-if="auth.user && !auth.user.is_email_verified" variant="warning">
      <div class="flex items-center justify-between gap-4">
        <span>Potvrdi svoju email adresu — poslali smo ti link kada si se registrovao/la.</span>
        <Button variant="secondary" :loading="resending" :disabled="resent" @click="onResendVerification">
          {{ resent ? 'Poslato' : 'Pošalji ponovo' }}
        </Button>
      </div>
    </Alert>

    <Card v-if="!auth.user?.memberships.length">
      <h2 class="mb-1 text-base font-semibold text-navy">Podesi svoju kompaniju</h2>
      <p class="mb-4 text-sm text-text-secondary">
        Još nemaš kompaniju u sistemu. Unesi naziv da počneš.
      </p>
      <form class="flex flex-col gap-4" @submit.prevent="onCreateCompany">
        <Alert v-if="createCompanyError" variant="danger">{{ createCompanyError }}</Alert>
        <Input v-model="companyName" label="Naziv kompanije" required :disabled="creatingCompany" />
        <Button type="submit" :loading="creatingCompany">Napravi kompaniju</Button>
      </form>
    </Card>

    <template v-else>
      <Alert v-if="dashboardStatus === 'error'" variant="danger">
        {{ dashboardError }}
        <button class="ml-2 underline" @click="loadDashboard">Pokušaj ponovo</button>
      </Alert>

      <Card v-else-if="dashboardStatus === 'loading'">
        <p class="text-sm text-text-secondary">Učitavanje...</p>
      </Card>

      <template v-else-if="dashboard">
        <Card>
          <p class="text-lg font-semibold text-navy">
            {{ HEALTH_LABELS[dashboard.business_health.status] }}
          </p>
          <p v-if="dashboard.business_health.reasons.length" class="mt-1 text-sm text-text-secondary">
            {{ dashboard.business_health.reasons.join(' ') }}
          </p>
        </Card>

        <div>
          <h2 class="mb-2 text-sm font-medium text-text-secondary">Zahteva pažnju</h2>
          <div v-if="dashboard.attention.length" class="flex flex-col gap-2">
            <AttentionItem v-for="item in dashboard.attention" :key="item.type" :item="item" />
          </div>
          <Card v-else>
            <EmptyState title="Sve je u redu." description="Trenutno nema stavki koje zahtevaju tvoju pažnju." />
          </Card>
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Card>
            <p class="text-sm text-text-secondary">Fakturisano ove godine</p>
            <p class="mt-1 text-2xl font-semibold text-navy">
              <MoneyDisplay :amount="dashboard.revenue.ytd" :currency="dashboard.revenue.currency" />
            </p>
          </Card>
          <Card>
            <p class="text-sm text-text-secondary">
              Neizmireno ({{ dashboard.outstanding.count }})
            </p>
            <p class="mt-1 text-2xl font-semibold text-navy">
              <MoneyDisplay :amount="dashboard.outstanding.total" :currency="dashboard.outstanding.currency" />
            </p>
            <p v-if="dashboard.outstanding.overdue_count" class="mt-1 text-sm text-danger">
              od toga {{ dashboard.outstanding.overdue_count }} kasni
              (<MoneyDisplay :amount="dashboard.outstanding.overdue_total" :currency="dashboard.outstanding.currency" />)
            </p>
          </Card>
        </div>

        <Card v-if="dashboard.onboarding.percentage < 100">
          <div class="flex items-center justify-between">
            <span class="text-sm text-navy">Nalog je {{ dashboard.onboarding.percentage }}% podešen.</span>
            <RouterLink :to="{ name: 'settings' }" class="text-sm text-primary hover:underline">
              Dovrši podešavanje →
            </RouterLink>
          </div>
          <div class="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-background">
            <div class="h-full bg-primary" :style="{ width: `${dashboard.onboarding.percentage}%` }" />
          </div>
        </Card>

        <div class="flex flex-wrap gap-3">
          <RouterLink :to="{ name: 'invoice-new' }">
            <Button>+ Nova faktura</Button>
          </RouterLink>
          <RouterLink :to="{ name: 'client-new' }">
            <Button variant="secondary">+ Novi klijent</Button>
          </RouterLink>
        </div>
      </template>
    </template>
  </div>
</template>
