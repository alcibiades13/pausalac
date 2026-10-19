<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, Alert, EmptyState, DatePicker, Input, MoneyDisplay, Badge, Skeleton, DataTable, Pagination, type DataTableColumn } from '@pausalac/ui'
import { listKpoEntries, getKpoMonthlySummary, kpoExportPdfUrl, kpoExportXlsxUrl, type KPOEntry, type KpoMonthlySummaryRow } from '@/services/kpo'
import { useCompanyStore } from '@/stores/company'
import { ApiError } from '@/lib/api'
import { useTableQuery } from '@/composables/useTableQuery'
import KpoMonthlyBarChart from '@/components/charts/KpoMonthlyBarChart.vue'

const { t } = useI18n()
const company = useCompanyStore()
const currency = computed(() => company.currentCompany?.default_currency ?? 'RSD')

const dateFrom = ref('')
const dateTo = ref('')

const columns: DataTableColumn<KPOEntry>[] = [
  { key: 'sequence_number', label: t('limitsAccountingEtc.kpoListView.columnSequence'), sortable: true },
  { key: 'entry_date', label: t('limitsAccountingEtc.kpoListView.columnDate'), sortable: true },
  { key: 'description', label: t('limitsAccountingEtc.kpoListView.columnDescription') },
  { key: 'product_revenue', label: t('limitsAccountingEtc.kpoListView.columnProducts') },
  { key: 'service_revenue', label: t('limitsAccountingEtc.kpoListView.columnServices') },
  { key: 'total_revenue', label: t('limitsAccountingEtc.kpoListView.columnTotal') },
]

const {
  rows: entries,
  status,
  errorMessage,
  page,
  totalPages,
  hasNext,
  hasPrevious,
  search,
  sort,
  onSort,
  nextPage,
  prevPage,
  load,
  reload,
} = useTableQuery<KPOEntry>(
  (q) =>
    listKpoEntries({
      dateFrom: dateFrom.value || undefined,
      dateTo: dateTo.value || undefined,
      page: q.page,
      pageSize: q.pageSize,
      search: q.search,
      ordering: q.ordering,
    }),
  { genericErrorMessage: t('limitsAccountingEtc.kpoListView.loadError') },
)

onMounted(load)
watch([dateFrom, dateTo], reload)

// --- monthly summary chart (independent of the date filter above) -------

const monthlySummary = ref<KpoMonthlySummaryRow[]>([])
const summaryStatus = ref<'loading' | 'ready' | 'error'>('loading')
const summaryError = ref('')

async function loadSummary() {
  summaryStatus.value = 'loading'
  try {
    monthlySummary.value = await getKpoMonthlySummary()
    summaryStatus.value = 'ready'
  } catch (error) {
    summaryError.value = error instanceof ApiError ? error.message : t('limitsAccountingEtc.kpoListView.loadError')
    summaryStatus.value = 'error'
  }
}

onMounted(loadSummary)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('limitsAccountingEtc.kpoListView.title') }}</h1>

    <Card>
      <h2 class="mb-3 text-sm font-medium text-navy">{{ t('limitsAccountingEtc.charts.kpoMonthly.title') }}</h2>
      <Alert v-if="summaryStatus === 'error'" variant="danger">
        {{ summaryError }}
        <button class="ml-2 underline" @click="loadSummary">{{ t('limitsAccountingEtc.kpoListView.retryButton') }}</button>
      </Alert>
      <Skeleton v-else-if="summaryStatus === 'loading'" :count="1" height="260px" />
      <KpoMonthlyBarChart v-else :rows="monthlySummary" :currency="currency" />
    </Card>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">{{ t('limitsAccountingEtc.kpoListView.retryButton') }}</button>
    </Alert>

    <Card v-else>
      <div class="flex flex-wrap items-end justify-between gap-3 border-b border-border pb-4">
        <div class="flex flex-wrap items-end gap-3">
          <Input
            v-model="search"
            :label="t('limitsAccountingEtc.kpoListView.searchLabel')"
            :placeholder="t('limitsAccountingEtc.kpoListView.searchPlaceholder')"
            class="min-w-[200px]"
          />
          <DatePicker v-model="dateFrom" :label="t('limitsAccountingEtc.kpoListView.dateFromLabel')" />
          <DatePicker v-model="dateTo" :label="t('limitsAccountingEtc.kpoListView.dateToLabel')" />
        </div>
        <div class="flex gap-3">
          <a :href="kpoExportPdfUrl()" target="_blank" rel="noopener" class="text-sm text-primary-dark hover:underline">
            {{ t('limitsAccountingEtc.kpoListView.exportPdf') }}
          </a>
          <a :href="kpoExportXlsxUrl()" class="text-sm text-primary-dark hover:underline">{{ t('limitsAccountingEtc.kpoListView.exportExcel') }}</a>
        </div>
      </div>

      <Skeleton v-if="status === 'loading' && entries.length === 0" class="mt-4" :count="3" />

      <EmptyState
        v-else-if="entries.length === 0"
        class="mt-4"
        :title="t('limitsAccountingEtc.kpoListView.emptyTitle')"
        :description="t('limitsAccountingEtc.kpoListView.emptyDescription')"
      />

      <template v-else>
        <DataTable
          class="mt-4"
          :columns="columns"
          :rows="entries"
          :loading="status === 'loading'"
          :sort="sort"
          row-key="id"
          @sort="onSort"
        >
          <template #cell-description="{ row }">
            {{ row.description }}
            <Badge v-if="row.entry_type === 'storno'" variant="warning" class="ml-2">{{ t('limitsAccountingEtc.kpoListView.stornoBadge') }}</Badge>
          </template>
          <template #cell-product_revenue="{ row }">
            <MoneyDisplay :amount="row.product_revenue" :currency="currency" />
          </template>
          <template #cell-service_revenue="{ row }">
            <MoneyDisplay :amount="row.service_revenue" :currency="currency" />
          </template>
          <template #cell-total_revenue="{ row }">
            <span class="font-medium text-navy"><MoneyDisplay :amount="row.total_revenue" :currency="currency" /></span>
          </template>
        </DataTable>

        <Pagination
          class="mt-4"
          :has-next="hasNext"
          :has-previous="hasPrevious"
          :page="page"
          :total-pages="totalPages"
          @next="nextPage"
          @previous="prevPage"
        />
      </template>
    </Card>
  </div>
</template>
