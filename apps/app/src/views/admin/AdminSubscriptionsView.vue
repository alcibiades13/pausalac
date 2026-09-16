<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Badge, Button , DataTable, type DataTableColumn } from '@pausalac/ui'
import { listAdminSubscriptions, type AdminSubscription } from '@/services/admin'
import { ApiError } from '@/lib/api'
import { formatDate } from '@/lib/formatDate'

const { t } = useI18n()

const subscriptions = ref<AdminSubscription[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

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
  { key: 'trial_ends_at', label: t('admin.adminSubscriptionsView.trialEndsColumn'), format: (r) => formatDate(r.trial_ends_at) },
])

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await listAdminSubscriptions({ page: page.value })
    subscriptions.value = result.results
    hasNext.value = result.next !== null
    hasPrevious.value = result.previous !== null
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('admin.adminSubscriptionsView.loadError')
  } finally {
    loading.value = false
  }
}

function goNext() {
  page.value += 1
  load()
}
function goPrevious() {
  page.value = Math.max(1, page.value - 1)
  load()
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminSubscriptionsView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="subscriptions"
      :loading="loading"
      :empty-title="t('admin.adminSubscriptionsView.emptyTitle')"
    >
      <template #actions="{ row }">
        <Badge :variant="STATUS_VARIANTS[row.status]">{{ STATUS_LABELS[row.status] }}</Badge>
      </template>
    </DataTable>

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">{{ t('admin.adminSubscriptionsView.previousButton') }}</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">{{ t('admin.adminSubscriptionsView.nextButton') }}</Button>
    </div>
  </div>
</template>
