<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Alert, MoneyDisplay, EmptyState, Skeleton, Metric } from '@pausalac/ui'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { createCompany } from '@/services/companies'
import { getDashboard, type Dashboard } from '@/services/analytics'
import { ApiError } from '@/lib/api'
import AttentionItem from '@/components/AttentionItem.vue'
import LimitTracker from '@/components/LimitTracker.vue'

const { t } = useI18n()
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
      error instanceof ApiError ? error.message : t('dashboardInvoicesClients.homeView.createCompanyError')
  } finally {
    creatingCompany.value = false
  }
}

// --- dashboard -----------------------------------------------------------

const dashboard = ref<Dashboard | null>(null)
const dashboardStatus = ref<'loading' | 'ready' | 'error'>('loading')
const dashboardError = ref('')

const HEALTH_LABEL_KEYS: Record<string, string> = {
  ok: 'healthOk',
  attention: 'healthAttention',
  critical: 'healthCritical',
}

async function loadDashboard() {
  if (!company.currentCompanyId) return
  dashboardStatus.value = 'loading'
  try {
    dashboard.value = await getDashboard()
    dashboardStatus.value = 'ready'
  } catch (error) {
    dashboardError.value =
      error instanceof ApiError ? error.message : t('dashboardInvoicesClients.homeView.dashboardError')
    dashboardStatus.value = 'error'
  }
}

onMounted(loadDashboard)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">
      {{ t('dashboardInvoicesClients.homeView.greeting', { name: auth.user?.first_name || auth.user?.email }) }}
    </h1>

    <Alert v-if="auth.user && !auth.user.is_email_verified" variant="warning">
      <div class="flex items-center justify-between gap-4">
        <span>{{ t('dashboardInvoicesClients.homeView.verifyEmailPrompt') }}</span>
        <Button variant="secondary" :loading="resending" :disabled="resent" @click="onResendVerification">
          {{ resent ? t('dashboardInvoicesClients.homeView.verifyEmailSent') : t('dashboardInvoicesClients.homeView.verifyEmailResend') }}
        </Button>
      </div>
    </Alert>

    <Card v-if="!auth.user?.memberships.length">
      <h2 class="mb-1 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.homeView.setupCompanyTitle') }}</h2>
      <p class="mb-4 text-sm text-text-secondary">
        {{ t('dashboardInvoicesClients.homeView.setupCompanyDescription') }}
      </p>
      <form class="flex flex-col gap-4" @submit.prevent="onCreateCompany">
        <Alert v-if="createCompanyError" variant="danger">{{ createCompanyError }}</Alert>
        <Input
          v-model="companyName"
          :label="t('dashboardInvoicesClients.homeView.companyNameLabel')"
          required
          :disabled="creatingCompany"
        />
        <Button type="submit" :loading="creatingCompany">{{ t('dashboardInvoicesClients.homeView.createCompanyButton') }}</Button>
      </form>
    </Card>

    <template v-else>
      <Alert v-if="dashboardStatus === 'error'" variant="danger">
        {{ dashboardError }}
        <button class="ml-2 underline" @click="loadDashboard">{{ t('dashboardInvoicesClients.homeView.retryButton') }}</button>
      </Alert>

      <Card v-else-if="dashboardStatus === 'loading'">
        <Skeleton :count="3" />
      </Card>

      <template v-else-if="dashboard">
        <Card>
          <p class="text-lg font-semibold text-navy">
            {{ t(`dashboardInvoicesClients.homeView.${HEALTH_LABEL_KEYS[dashboard.business_health.status]}`) }}
          </p>
          <p v-if="dashboard.business_health.reasons.length" class="mt-1 text-sm text-text-secondary">
            {{ dashboard.business_health.reasons.join(' ') }}
          </p>
        </Card>

        <div>
          <h2 class="mb-2 text-sm font-medium text-text-secondary">{{ t('dashboardInvoicesClients.homeView.attentionHeading') }}</h2>
          <div v-if="dashboard.attention.length" class="flex flex-col gap-2">
            <AttentionItem v-for="item in dashboard.attention" :key="item.type" :item="item" />
          </div>
          <Card v-else>
            <EmptyState
              :title="t('dashboardInvoicesClients.homeView.attentionEmptyTitle')"
              :description="t('dashboardInvoicesClients.homeView.attentionEmptyDescription')"
            />
          </Card>
        </div>

        <Card>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-navy">{{ t('dashboardInvoicesClients.homeView.limitsCardTitle') }}</span>
            <RouterLink :to="{ name: 'limits' }" class="text-sm text-primary-dark hover:underline">
              {{ t('dashboardInvoicesClients.homeView.detailsLink') }}
            </RouterLink>
          </div>
          <div class="mt-4 grid grid-cols-1 gap-8 sm:grid-cols-2 sm:divide-x sm:divide-border">
            <LimitTracker :label="t('dashboardInvoicesClients.homeView.pausalLimitLabel')" :tracker="dashboard.limits.pausal_limit" />
            <LimitTracker
              :label="t('dashboardInvoicesClients.homeView.vatThresholdLabel')"
              :tracker="dashboard.limits.vat_threshold"
              class="sm:pl-8"
            />
          </div>
        </Card>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Card>
            <Metric :label="t('dashboardInvoicesClients.homeView.revenueYtdLabel')">
              <MoneyDisplay :amount="dashboard.revenue.ytd" :currency="dashboard.revenue.currency" />
            </Metric>
          </Card>
          <Card>
            <Metric :label="t('dashboardInvoicesClients.homeView.outstandingLabel', { count: dashboard.outstanding.count })">
              <MoneyDisplay :amount="dashboard.outstanding.total" :currency="dashboard.outstanding.currency" />
              <template v-if="dashboard.outstanding.overdue_count" #secondary>
                <p class="text-sm text-danger">
                  {{ t('dashboardInvoicesClients.homeView.outstandingOverdue', { count: dashboard.outstanding.overdue_count }) }}
                  (<MoneyDisplay :amount="dashboard.outstanding.overdue_total" :currency="dashboard.outstanding.currency" />)
                </p>
              </template>
            </Metric>
          </Card>
        </div>

        <Card>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-navy">{{ t('dashboardInvoicesClients.homeView.nextObligationTitle') }}</span>
            <RouterLink :to="{ name: 'obligations' }" class="text-sm text-primary-dark hover:underline">
              {{ t('dashboardInvoicesClients.homeView.detailsLink') }}
            </RouterLink>
          </div>
          <template v-if="dashboard.next_obligation">
            <p class="mt-1 text-2xl font-semibold text-navy">
              <MoneyDisplay
                :amount="dashboard.next_obligation.total_amount"
                :currency="dashboard.next_obligation.currency"
              />
            </p>
            <p class="mt-1 text-sm" :class="dashboard.next_obligation.status === 'overdue' ? 'text-danger' : 'text-text-secondary'">
              {{ t('dashboardInvoicesClients.homeView.nextObligationDue', { date: dashboard.next_obligation.due_date }) }}
              <span v-if="dashboard.next_obligation.status === 'overdue'">{{ t('dashboardInvoicesClients.homeView.nextObligationOverdueSuffix') }}</span>
            </p>
          </template>
          <p v-else class="mt-1 text-sm text-text-secondary">{{ t('dashboardInvoicesClients.homeView.noUpcomingObligation') }}</p>
        </Card>

        <Card v-if="dashboard.onboarding.percentage < 100">
          <div class="flex items-center justify-between">
            <span class="text-sm text-navy">{{ t('dashboardInvoicesClients.homeView.onboardingProgress', { percentage: dashboard.onboarding.percentage }) }}</span>
            <RouterLink :to="{ name: 'settings' }" class="text-sm text-primary-dark hover:underline">
              {{ t('dashboardInvoicesClients.homeView.completeSetupLink') }}
            </RouterLink>
          </div>
          <div class="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-background">
            <div class="h-full bg-primary" :style="{ width: `${dashboard.onboarding.percentage}%` }" />
          </div>
        </Card>

        <div class="flex flex-wrap gap-3">
          <RouterLink :to="{ name: 'invoice-new' }">
            <Button>{{ t('dashboardInvoicesClients.homeView.newInvoiceButton') }}</Button>
          </RouterLink>
          <RouterLink :to="{ name: 'client-new' }">
            <Button variant="secondary">{{ t('dashboardInvoicesClients.homeView.newClientButton') }}</Button>
          </RouterLink>
        </div>
      </template>
    </template>
  </div>
</template>
