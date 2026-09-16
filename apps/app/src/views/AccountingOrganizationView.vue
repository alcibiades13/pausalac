<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Select, Alert, Badge, EmptyState, MoneyDisplay, Skeleton } from '@pausalac/ui'
import {
  listOrganizations,
  createOrganization,
  listOrgStaff,
  addOrgStaff,
  removeOrgStaff,
  listOrgConnections,
  createOrgConnection,
  getClientPortfolio,
  type AccountingOrganization,
  type OrgStaffMembership,
  type OrganizationConnection,
  type ClientPortfolioRow,
  type PortfolioSummary,
  type PortfolioStatus,
  type GrantedRole,
  type OrgStaffRole,
} from '@/services/accounting'
import { useCompanyStore } from '@/stores/company'
import { ApiError } from '@/lib/api'

const router = useRouter()
const company = useCompanyStore()
const { t } = useI18n()

const STAFF_ROLE_OPTIONS = computed<{ value: OrgStaffRole; label: string }[]>(() => [
  { value: 'staff', label: t('limitsAccountingEtc.accountingOrganizationView.staffRoleStaff') },
  { value: 'admin', label: t('limitsAccountingEtc.accountingOrganizationView.staffRoleAdmin') },
])
const GRANTED_ROLE_OPTIONS = computed<{ value: GrantedRole; label: string }[]>(() => [
  { value: 'accountant', label: t('limitsAccountingEtc.accountingOrganizationView.roleAccountant') },
  { value: 'accountant_admin', label: t('limitsAccountingEtc.accountingOrganizationView.roleAccountantAdmin') },
])
const CONNECTION_STATUS_LABELS = computed<Record<OrganizationConnection['status'], string>>(() => ({
  pending: t('limitsAccountingEtc.accountingOrganizationView.statusPending'),
  active: t('limitsAccountingEtc.accountingOrganizationView.statusActive'),
  declined: t('limitsAccountingEtc.accountingOrganizationView.statusDeclined'),
  revoked: t('limitsAccountingEtc.accountingOrganizationView.statusRevoked'),
}))
const CONNECTION_STATUS_VARIANTS: Record<
  OrganizationConnection['status'],
  'neutral' | 'success' | 'danger'
> = {
  pending: 'neutral',
  active: 'success',
  declined: 'danger',
  revoked: 'danger',
}
const PORTFOLIO_STATUS_LABELS = computed<Record<PortfolioStatus, string>>(() => ({
  ok: t('limitsAccountingEtc.accountingOrganizationView.portfolioStatusOk'),
  attention: t('limitsAccountingEtc.accountingOrganizationView.portfolioStatusAttention'),
  critical: t('limitsAccountingEtc.accountingOrganizationView.portfolioStatusCritical'),
}))
const PORTFOLIO_STATUS_VARIANTS: Record<PortfolioStatus, 'success' | 'warning' | 'danger'> = {
  ok: 'success',
  attention: 'warning',
  critical: 'danger',
}
const LIMIT_VARIANTS: Record<string, 'neutral' | 'warning' | 'danger'> = {
  ok: 'neutral',
  attention: 'warning',
  warning: 'warning',
  critical: 'danger',
}
const PORTFOLIO_STATUS_FILTER_OPTIONS = computed<{ value: PortfolioStatus | ''; label: string }[]>(() => [
  { value: '', label: t('limitsAccountingEtc.accountingOrganizationView.portfolioAllStatuses') },
  { value: 'ok', label: t('limitsAccountingEtc.accountingOrganizationView.portfolioStatusOk') },
  { value: 'attention', label: t('limitsAccountingEtc.accountingOrganizationView.portfolioStatusAttention') },
  { value: 'critical', label: t('limitsAccountingEtc.accountingOrganizationView.portfolioStatusCritical') },
])
const PORTFOLIO_ORDERING_OPTIONS = computed<{ value: 'name' | '-name' | 'revenue' | '-revenue'; label: string }[]>(() => [
  { value: 'name', label: t('limitsAccountingEtc.accountingOrganizationView.sortNameAsc') },
  { value: '-name', label: t('limitsAccountingEtc.accountingOrganizationView.sortNameDesc') },
  { value: '-revenue', label: t('limitsAccountingEtc.accountingOrganizationView.sortRevenueDesc') },
  { value: 'revenue', label: t('limitsAccountingEtc.accountingOrganizationView.sortRevenueAsc') },
])

// --- organization: load-or-create ---------------------------------------

const organization = ref<AccountingOrganization | null>(null)
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')

async function loadOrganization() {
  status.value = 'loading'
  try {
    const page = await listOrganizations()
    organization.value = page.results[0] ?? null
    status.value = 'ready'
    if (organization.value) {
      await Promise.all([loadStaff(), loadConnections(), loadPortfolio()])
    }
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('limitsAccountingEtc.accountingOrganizationView.loadError')
    status.value = 'error'
  }
}

onMounted(loadOrganization)

const createForm = ref({ name: '', contact_email: '', pib: '' })
const creating = ref(false)
const createError = ref('')

async function onCreateOrganization() {
  creating.value = true
  createError.value = ''
  try {
    organization.value = await createOrganization(createForm.value)
  } catch (error) {
    createError.value =
      error instanceof ApiError ? error.message : t('limitsAccountingEtc.accountingOrganizationView.createError')
  } finally {
    creating.value = false
  }
}

const isAdmin = computed(() => organization.value?.my_role === 'admin')

// --- staff ---------------------------------------------------------------

const staff = ref<OrgStaffMembership[]>([])

async function loadStaff() {
  if (!organization.value) return
  staff.value = await listOrgStaff(organization.value.id)
}

const staffForm = ref<{ email: string; role: OrgStaffRole }>({ email: '', role: 'staff' })
const addingStaff = ref(false)
const staffError = ref('')

async function onAddStaff() {
  if (!organization.value) return
  addingStaff.value = true
  staffError.value = ''
  try {
    await addOrgStaff(organization.value.id, staffForm.value)
    staffForm.value = { email: '', role: 'staff' }
    await loadStaff()
  } catch (error) {
    staffError.value =
      error instanceof ApiError ? error.message : t('limitsAccountingEtc.accountingOrganizationView.staffError')
  } finally {
    addingStaff.value = false
  }
}

const removingStaffId = ref<number | null>(null)
async function onRemoveStaff(membershipId: number) {
  if (!organization.value) return
  removingStaffId.value = membershipId
  try {
    await removeOrgStaff(organization.value.id, membershipId)
    await loadStaff()
  } finally {
    removingStaffId.value = null
  }
}

// --- client connections ---------------------------------------------------

const connections = ref<OrganizationConnection[]>([])
// The portfolio table below covers active connections in a much richer
// way — this list is only the leftovers (pending/declined/revoked) so
// the existing "did my invite go through" visibility isn't lost.
const pendingConnections = computed(() => connections.value.filter((c) => c.status !== 'active'))

async function loadConnections() {
  if (!organization.value) return
  connections.value = await listOrgConnections(organization.value.id)
}

const connectionForm = ref<{ company_pib: string; granted_role: GrantedRole }>({
  company_pib: '',
  granted_role: 'accountant',
})
const invitingClient = ref(false)
const connectionError = ref('')

async function onInviteClient() {
  if (!organization.value) return
  invitingClient.value = true
  connectionError.value = ''
  try {
    await createOrgConnection(organization.value.id, connectionForm.value)
    connectionForm.value = { company_pib: '', granted_role: 'accountant' }
    await loadConnections()
  } catch (error) {
    connectionError.value =
      error instanceof ApiError ? error.message : t('limitsAccountingEtc.accountingOrganizationView.connectionError')
  } finally {
    invitingClient.value = false
  }
}

// --- client portfolio (master prompt §28/§29) ------------------------------

const portfolioRows = ref<ClientPortfolioRow[]>([])
const portfolioSummary = ref<PortfolioSummary>({ total: 0, ok: 0, attention: 0, critical: 0 })
const portfolioStatus = ref<'loading' | 'ready' | 'error'>('loading')
const portfolioErrorMessage = ref('')
const portfolioHasNext = ref(false)
const portfolioHasPrevious = ref(false)
const portfolioPage = ref(1)
const portfolioSearch = ref('')
const portfolioStatusFilter = ref<PortfolioStatus | ''>('')
const portfolioOrdering = ref<'name' | '-name' | 'revenue' | '-revenue'>('name')

async function loadPortfolio() {
  if (!organization.value) return
  portfolioStatus.value = 'loading'
  try {
    const page = await getClientPortfolio(organization.value.id, {
      status: portfolioStatusFilter.value || undefined,
      search: portfolioSearch.value || undefined,
      ordering: portfolioOrdering.value,
      page: portfolioPage.value,
    })
    portfolioRows.value = page.results
    portfolioSummary.value = page.summary
    portfolioHasNext.value = page.next !== null
    portfolioHasPrevious.value = page.previous !== null
    portfolioStatus.value = 'ready'
  } catch (error) {
    portfolioErrorMessage.value =
      error instanceof ApiError
        ? error.message
        : t('limitsAccountingEtc.accountingOrganizationView.portfolioLoadError')
    portfolioStatus.value = 'error'
  }
}

watch([portfolioSearch, portfolioStatusFilter, portfolioOrdering], () => {
  portfolioPage.value = 1
  loadPortfolio()
})

function onPrevPortfolioPage() {
  if (portfolioPage.value <= 1) return
  portfolioPage.value -= 1
  loadPortfolio()
}

function onNextPortfolioPage() {
  if (!portfolioHasNext.value) return
  portfolioPage.value += 1
  loadPortfolio()
}

// "Klik na klijenta otvara detaljan pregled" (§29) — reuses the existing
// company switcher instead of a new detail page: switching + landing on
// Home puts the accountant on that client's own real dashboard, with
// numbers that always match what the client themselves sees.
async function onOpenClient(companyId: number) {
  company.setCurrentCompany(companyId)
  await router.push({ name: 'home' })
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('limitsAccountingEtc.accountingOrganizationView.title') }}</h1>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="loadOrganization">{{ t('limitsAccountingEtc.accountingOrganizationView.retryButton') }}</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <Card v-else-if="!organization">
      <h2 class="mb-1 text-base font-semibold text-navy">{{ t('limitsAccountingEtc.accountingOrganizationView.createTitle') }}</h2>
      <p class="mb-4 text-sm text-text-secondary">
        {{ t('limitsAccountingEtc.accountingOrganizationView.createDescription') }}
      </p>
      <form class="flex flex-col gap-4" @submit.prevent="onCreateOrganization">
        <Alert v-if="createError" variant="danger">{{ createError }}</Alert>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Input v-model="createForm.name" :label="t('limitsAccountingEtc.accountingOrganizationView.orgNameLabel')" required />
          <Input v-model="createForm.contact_email" type="email" :label="t('limitsAccountingEtc.accountingOrganizationView.contactEmailLabel')" />
          <Input v-model="createForm.pib" :label="t('limitsAccountingEtc.accountingOrganizationView.pibLabel')" />
        </div>
        <div>
          <Button type="submit" :loading="creating">{{ t('limitsAccountingEtc.accountingOrganizationView.createButton') }}</Button>
        </div>
      </form>
    </Card>

    <template v-else>
      <Card>
        <h2 class="font-display text-base font-semibold text-navy">{{ organization.name }}</h2>
        <p class="text-sm text-text-secondary">{{ organization.contact_email || '—' }}</p>
      </Card>

      <Card>
        <h2 class="mb-3 text-base font-semibold text-navy">{{ t('limitsAccountingEtc.accountingOrganizationView.staffTitle') }}</h2>

        <template v-if="isAdmin">
          <Alert v-if="staffError" variant="danger" class="mb-3">{{ staffError }}</Alert>
          <form class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="onAddStaff">
            <Input
              v-model="staffForm.email"
              type="email"
              :label="t('limitsAccountingEtc.accountingOrganizationView.staffEmailLabel')"
              required
              class="flex-1 sm:max-w-xs"
            />
            <Select v-model="staffForm.role" :label="t('limitsAccountingEtc.accountingOrganizationView.staffRoleLabel')" :options="STAFF_ROLE_OPTIONS" />
            <Button type="submit" :loading="addingStaff">{{ t('limitsAccountingEtc.accountingOrganizationView.addButton') }}</Button>
          </form>
        </template>

        <EmptyState v-if="staff.length === 0" :title="t('limitsAccountingEtc.accountingOrganizationView.emptyStaffTitle')" />
        <ul v-else class="flex flex-col divide-y divide-border">
          <li
            v-for="member in staff"
            :key="member.id"
            class="flex items-center justify-between py-2"
          >
            <div>
              <p class="text-sm text-navy">{{ member.user_email }}</p>
              <p class="text-xs text-text-secondary">
                {{ member.role === 'admin' ? t('limitsAccountingEtc.accountingOrganizationView.staffRoleAdmin') : t('limitsAccountingEtc.accountingOrganizationView.staffRoleStaff') }}
              </p>
            </div>
            <button
              v-if="isAdmin"
              type="button"
              class="text-sm text-danger hover:underline disabled:opacity-40"
              :disabled="removingStaffId === member.id"
              @click="onRemoveStaff(member.id)"
            >
              {{ t('limitsAccountingEtc.accountingOrganizationView.removeButton') }}
            </button>
          </li>
        </ul>
      </Card>

      <Card>
        <h2 class="mb-3 text-base font-semibold text-navy">{{ t('limitsAccountingEtc.accountingOrganizationView.clientsTitle') }}</h2>

        <form class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="onInviteClient">
          <Input
            v-model="connectionForm.company_pib"
            :label="t('limitsAccountingEtc.accountingOrganizationView.clientPibLabel')"
            required
            class="flex-1 sm:max-w-xs"
          />
          <Select
            v-model="connectionForm.granted_role"
            :label="t('limitsAccountingEtc.accountingOrganizationView.accessLevelLabel')"
            :options="GRANTED_ROLE_OPTIONS"
          />
          <Button type="submit" :loading="invitingClient">{{ t('limitsAccountingEtc.accountingOrganizationView.inviteButton') }}</Button>
        </form>
        <Alert v-if="connectionError" variant="danger" class="mb-3">{{ connectionError }}</Alert>

        <div v-if="pendingConnections.length" class="mb-6">
          <h3 class="mb-2 text-sm font-medium text-text-secondary">{{ t('limitsAccountingEtc.accountingOrganizationView.pendingTitle') }}</h3>
          <ul class="flex flex-col divide-y divide-border">
            <li
              v-for="connection in pendingConnections"
              :key="connection.id"
              class="flex items-center justify-between py-2"
            >
              <div>
                <p class="text-sm text-navy">{{ connection.company_name }}</p>
                <p class="text-xs text-text-secondary">{{ connection.company_pib }}</p>
              </div>
              <Badge :variant="CONNECTION_STATUS_VARIANTS[connection.status]">
                {{ CONNECTION_STATUS_LABELS[connection.status] }}
              </Badge>
            </li>
          </ul>
        </div>

        <div class="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div class="rounded-lg bg-background p-3">
            <p class="text-xs text-text-secondary">{{ t('limitsAccountingEtc.accountingOrganizationView.summaryTotal') }}</p>
            <p class="text-xl font-semibold text-navy">{{ portfolioSummary.total }}</p>
          </div>
          <div class="rounded-lg bg-background p-3">
            <p class="text-xs text-text-secondary">{{ t('limitsAccountingEtc.accountingOrganizationView.summaryOk') }}</p>
            <p class="text-xl font-semibold text-success">{{ portfolioSummary.ok }}</p>
          </div>
          <div class="rounded-lg bg-background p-3">
            <p class="text-xs text-text-secondary">{{ t('limitsAccountingEtc.accountingOrganizationView.summaryAttention') }}</p>
            <p class="text-xl font-semibold text-warning">{{ portfolioSummary.attention }}</p>
          </div>
          <div class="rounded-lg bg-background p-3">
            <p class="text-xs text-text-secondary">{{ t('limitsAccountingEtc.accountingOrganizationView.summaryCritical') }}</p>
            <p class="text-xl font-semibold text-danger">{{ portfolioSummary.critical }}</p>
          </div>
        </div>

        <div class="mb-3 flex flex-wrap items-end gap-3">
          <Input v-model="portfolioSearch" :label="t('limitsAccountingEtc.accountingOrganizationView.portfolioSearchLabel')" :placeholder="t('limitsAccountingEtc.accountingOrganizationView.portfolioSearchPlaceholder')" />
          <Select
            v-model="portfolioStatusFilter"
            :label="t('limitsAccountingEtc.accountingOrganizationView.portfolioStatusLabel')"
            :options="PORTFOLIO_STATUS_FILTER_OPTIONS"
          />
          <Select
            v-model="portfolioOrdering"
            :label="t('limitsAccountingEtc.accountingOrganizationView.sortByLabel')"
            :options="PORTFOLIO_ORDERING_OPTIONS"
          />
        </div>

        <Alert v-if="portfolioStatus === 'error'" variant="danger">
          {{ portfolioErrorMessage }}
          <button class="ml-2 underline" @click="loadPortfolio">{{ t('limitsAccountingEtc.accountingOrganizationView.retryButton') }}</button>
        </Alert>

        <Skeleton v-else-if="portfolioStatus === 'loading'" :count="3" />

        <EmptyState
          v-else-if="portfolioRows.length === 0"
          :title="t('limitsAccountingEtc.accountingOrganizationView.emptyPortfolioTitle')"
          :description="t('limitsAccountingEtc.accountingOrganizationView.emptyPortfolioDescription')"
        />

        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-border text-left text-xs uppercase tracking-wide text-text-secondary">
                <th class="py-2 pr-3">{{ t('limitsAccountingEtc.accountingOrganizationView.columnClient') }}</th>
                <th class="py-2 pr-3">{{ t('limitsAccountingEtc.accountingOrganizationView.columnStatus') }}</th>
                <th class="py-2 pr-3 text-right">{{ t('limitsAccountingEtc.accountingOrganizationView.columnRevenueYtd') }}</th>
                <th class="py-2 pr-3">{{ t('limitsAccountingEtc.accountingOrganizationView.columnLimits') }}</th>
                <th class="py-2 pr-3">{{ t('limitsAccountingEtc.accountingOrganizationView.columnNextObligation') }}</th>
                <th class="py-2 pr-3 text-right">{{ t('limitsAccountingEtc.accountingOrganizationView.columnOverdue') }}</th>
                <th class="py-2 pr-3 text-right">{{ t('limitsAccountingEtc.accountingOrganizationView.columnMissingDocs') }}</th>
                <th class="py-2 pr-3">{{ t('limitsAccountingEtc.accountingOrganizationView.columnIntegrations') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in portfolioRows"
                :key="row.company_id"
                class="cursor-pointer border-b border-border hover:bg-background"
                @click="onOpenClient(row.company_id)"
              >
                <td class="py-2 pr-3">
                  <p class="font-medium text-navy">{{ row.company_name }}</p>
                  <p class="text-xs text-text-secondary">{{ row.company_pib }}</p>
                </td>
                <td class="py-2 pr-3">
                  <Badge :variant="PORTFOLIO_STATUS_VARIANTS[row.status]">
                    {{ PORTFOLIO_STATUS_LABELS[row.status] }}
                  </Badge>
                </td>
                <td class="py-2 pr-3 text-right">
                  <MoneyDisplay :amount="row.revenue_ytd" :currency="row.currency" />
                </td>
                <td class="py-2 pr-3">
                  <div class="flex gap-1">
                    <Badge :variant="LIMIT_VARIANTS[row.pausal_limit.warning_level ?? 'ok']">
                      {{ t('limitsAccountingEtc.accountingOrganizationView.pausalBadge', { percentage: row.pausal_limit.percentage ?? '—' }) }}
                    </Badge>
                    <Badge :variant="LIMIT_VARIANTS[row.vat_threshold.warning_level ?? 'ok']">
                      {{ t('limitsAccountingEtc.accountingOrganizationView.vatBadge', { percentage: row.vat_threshold.percentage ?? '—' }) }}
                    </Badge>
                  </div>
                </td>
                <td class="py-2 pr-3" :class="row.next_obligation_overdue ? 'text-danger' : 'text-navy'">
                  {{ row.next_obligation_due ?? '—' }}
                </td>
                <td class="py-2 pr-3 text-right">{{ row.overdue_invoice_count }}</td>
                <td class="py-2 pr-3 text-right">{{ row.missing_document_count }}</td>
                <td class="py-2 pr-3 text-text-secondary">{{ row.integration_errors ?? '—' }}</td>
              </tr>
            </tbody>
          </table>

          <div class="mt-3 flex items-center justify-end gap-3">
            <button
              type="button"
              class="text-sm text-primary-dark hover:underline disabled:cursor-not-allowed disabled:text-text-secondary disabled:no-underline"
              :disabled="!portfolioHasPrevious"
              @click="onPrevPortfolioPage"
            >
              {{ t('limitsAccountingEtc.accountingOrganizationView.prevPage') }}
            </button>
            <button
              type="button"
              class="text-sm text-primary-dark hover:underline disabled:cursor-not-allowed disabled:text-text-secondary disabled:no-underline"
              :disabled="!portfolioHasNext"
              @click="onNextPortfolioPage"
            >
              {{ t('limitsAccountingEtc.accountingOrganizationView.nextPage') }}
            </button>
          </div>
        </div>
      </Card>
    </template>
  </div>
</template>
