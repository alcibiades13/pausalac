<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Badge, Button, DataTable, Pagination, type DataTableColumn } from '@pausalac/ui'
import { listAdminSubscriptions, type AdminSubscription } from '@/services/admin'
import { formatDate } from '@/lib/formatDate'
import { useTableQuery } from '@/composables/useTableQuery'

const { t } = useI18n()

const STATUS_LABELS = computed<Record<AdminSubscription['status'], string>>(() => ({
  trialing: t('admin.adminSubscriptionsView.statusTrialing'),
  active: t('admin.adminSubscriptionsView.statusActive'),
  grace_period: t('admin.adminSubscriptionsView.statusGracePeriod'),
  cancelled: t('admin.adminSubscriptionsView.statusCancelled'),
  expired: t('admin.adminSubscriptionsView.statusExpired'),
}))
const STATUS_VARIANTS: Record<AdminSubscription['status'], 'success' | 'warning' | 'danger' | 'neutral'> = {
  trialing: 'neutral',
  active: 'success',
  grace_period: 'warning',
  cancelled: 'danger',
  expired: 'danger',
}

const columns = computed<DataTableColumn<AdminSubscription>[]>(() => [
  { key: 'company_name', label: t('admin.adminSubscriptionsView.companyColumn') },
  { key: 'plan', label: t('admin.adminSubscriptionsView.planColumn'), format: (r) => r.plan?.name ?? '—' },
  {
    key: 'trial_ends_at',
    label: t('admin.adminSubscriptionsView.trialEndsColumn'),
    format: (r) => formatDate(r.trial_ends_at),
    sortable: true,
  },
])

const {
  rows: subscriptions,
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
  load,
} = useTableQuery<AdminSubscription>(
  (q) => listAdminSubscriptions({ page: q.page, page_size: q.pageSize, search: q.search, ordering: q.ordering }),
  { genericErrorMessage: t('admin.adminSubscriptionsView.loadError') },
)

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminSubscriptionsView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="subscriptions"
      :loading="status === 'loading'"
      :sort="sort"
      :empty-title="t('admin.adminSubscriptionsView.emptyTitle')"
      @sort="onSort"
    >
      <template #actions="{ row }">
        <Badge :variant="STATUS_VARIANTS[row.status]">{{ STATUS_LABELS[row.status] }}</Badge>
      </template>
    </DataTable>

    <Pagination
      :has-next="hasNext"
      :has-previous="hasPrevious"
      :page="page"
      :total-pages="totalPages"
      @next="nextPage"
      @previous="prevPage"
    />
  </div>
</template>
