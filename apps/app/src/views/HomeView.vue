<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Alert, MoneyDisplay, EmptyState, Skeleton, Metric } from '@pausalac/ui'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { createCompany } from '@/services/companies'
import { getDashboard, type Dashboard } from '@/services/analytics'
import { ApiError } from '@/lib/api'
import AttentionItem from '@/components/AttentionItem.vue'
import LimitTracker from '@/components/LimitTracker.vue'
import RevenueTrendChart from '@/components/charts/RevenueTrendChart.vue'

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

// The "verify your email" banner above already covers this exact case
// with a working resend action — the attention item stays in the API
// response (it still correctly feeds business_health/reasons) but would
// be a pure duplicate if also rendered in the "Zahteva pažnju" list on
// this same page.
const visibleAttention = computed(
  () => dashboard.value?.attention.filter((item) => item.type !== 'email_unverified') ?? [],
)
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

        <!--
          Two-column on desktop (blueprint §4.7's "desktop = mass work,
          use the width") — everything used to stack in one column full
          page width, forcing a full scroll to reach "Sledeća obaveza"/
          the chart even though a wide screen had plenty of room beside
          the attention list. Below `lg:` this still collapses to the
          original single stacked column. Reusable split if another
          view needs the same "worklist beside at-a-glance numbers"
          shape — not pulled into a shared component until a second
          page actually needs it.
        -->
        <div class="flex flex-col gap-6 lg:grid lg:grid-cols-[2fr_1fr] lg:items-start">
          <div class="flex flex-col gap-6">
            <div>
              <h2 class="mb-2 text-sm font-medium text-text-secondary">{{ t('dashboardInvoicesClients.homeView.attentionHeading') }}</h2>
              <div v-if="visibleAttention.length" class="flex flex-col gap-2">
                <AttentionItem v-for="item in visibleAttention" :key="item.type" :item="item" />
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
              <!--
                @container, not `sm:` — this card can sit in the
                dashboard's own narrower left column, where the viewport
                is wide but the card itself isn't. `sm:grid-cols-2` fired
                at 640px of VIEWPORT width regardless of how squeezed this
                particular card actually was, cramming two trackers into
                a card too narrow for either — the exact bug a real
                screenshot caught. `@lg` here judges this card's own
                rendered width instead.
              -->
              <!--
                Tailwind v4's `divide-x` puts the border on the TRAILING
                edge of every non-last child (v3 put it on the LEADING
                edge of every non-first child) — with only `pl-8` on the
                second tracker, the border sat flush against the first
                tracker's own content (zero gap) while all the breathing
                room piled up on the far side, reading as "stuck to the
                left" instead of centered. `gap-x-0` + matching `pr-8`/
                `pl-8` on both sides of the border fixes the actual
                cause instead of nudging padding until it looks right.
              -->
              <div class="@container mt-4">
                <div class="grid grid-cols-1 gap-8 @lg:grid-cols-2 @lg:gap-x-0 @lg:divide-x @lg:divide-border">
                  <LimitTracker
                    :label="t('dashboardInvoicesClients.homeView.pausalLimitLabel')"
                    :tracker="dashboard.limits.pausal_limit"
                    class="@lg:pr-8"
                  />
                  <LimitTracker
                    :label="t('dashboardInvoicesClients.homeView.vatThresholdLabel')"
                    :tracker="dashboard.limits.vat_threshold"
                    class="@lg:pl-8"
                  />
                </div>
              </div>
            </Card>
          </div>

          <div class="flex flex-col gap-6">
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-1">
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
                <p class="mt-1 text-sm text-text-secondary">
                  {{ t('dashboardInvoicesClients.homeView.nextObligationDue', { date: dashboard.next_obligation.due_date }) }}
                </p>
              </template>
              <p v-else class="mt-1 text-sm text-text-secondary">{{ t('dashboardInvoicesClients.homeView.noUpcomingObligation') }}</p>
            </Card>
          </div>
        </div>

        <!--
          Full width, not squeezed into the narrower right column above —
          a revenue trend is visually "heavy" enough (and important
          enough) to earn its own row rather than share a cramped column
          with three other cards.
        -->
        <Card>
          <h2 class="mb-3 text-sm font-medium text-navy">{{ t('dashboardInvoicesClients.charts.revenueTrend.title') }}</h2>
          <RevenueTrendChart :series="dashboard.revenue.monthly_series" :currency="dashboard.revenue.currency" />
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
      </template>
    </template>
  </div>
</template>
