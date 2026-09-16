<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, Alert, EmptyState, Input, MoneyDisplay, Badge, Skeleton } from '@pausalac/ui'
import { listKpoEntries, kpoExportPdfUrl, kpoExportXlsxUrl, type KPOEntry } from '@/services/kpo'
import { useCompanyStore } from '@/stores/company'
import { ApiError } from '@/lib/api'

const { t } = useI18n()
const company = useCompanyStore()
const currency = computed(() => company.currentCompany?.default_currency ?? 'RSD')

const entries = ref<KPOEntry[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')
const dateFrom = ref('')
const dateTo = ref('')

async function load() {
  status.value = 'loading'
  try {
    const page = await listKpoEntries({ dateFrom: dateFrom.value || undefined, dateTo: dateTo.value || undefined })
    entries.value = page.results
    status.value = 'ready'
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : t('limitsAccountingEtc.kpoListView.loadError')
    status.value = 'error'
  }
}

onMounted(load)
watch([dateFrom, dateTo], load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-navy">{{ t('limitsAccountingEtc.kpoListView.title') }}</h1>
      <div class="flex gap-3">
        <a :href="kpoExportPdfUrl()" target="_blank" rel="noopener" class="text-sm text-primary-dark hover:underline">
          {{ t('limitsAccountingEtc.kpoListView.exportPdf') }}
        </a>
        <a :href="kpoExportXlsxUrl()" class="text-sm text-primary-dark hover:underline">{{ t('limitsAccountingEtc.kpoListView.exportExcel') }}</a>
      </div>
    </div>

    <div class="flex flex-wrap items-end gap-3">
      <Input v-model="dateFrom" type="date" :label="t('limitsAccountingEtc.kpoListView.dateFromLabel')" />
      <Input v-model="dateTo" type="date" :label="t('limitsAccountingEtc.kpoListView.dateToLabel')" />
    </div>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">{{ t('limitsAccountingEtc.kpoListView.retryButton') }}</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <Card v-else-if="entries.length === 0">
      <EmptyState
        :title="t('limitsAccountingEtc.kpoListView.emptyTitle')"
        :description="t('limitsAccountingEtc.kpoListView.emptyDescription')"
      />
    </Card>

    <Card v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-border text-left text-xs uppercase tracking-wide text-text-secondary">
            <th class="py-2 pr-3">{{ t('limitsAccountingEtc.kpoListView.columnSequence') }}</th>
            <th class="py-2 pr-3">{{ t('limitsAccountingEtc.kpoListView.columnDate') }}</th>
            <th class="py-2 pr-3">{{ t('limitsAccountingEtc.kpoListView.columnDescription') }}</th>
            <th class="py-2 pr-3 text-right">{{ t('limitsAccountingEtc.kpoListView.columnProducts') }}</th>
            <th class="py-2 pr-3 text-right">{{ t('limitsAccountingEtc.kpoListView.columnServices') }}</th>
            <th class="py-2 pr-3 text-right">{{ t('limitsAccountingEtc.kpoListView.columnTotal') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in entries" :key="entry.id" class="border-b border-border">
            <td class="py-2 pr-3 font-mono">{{ entry.sequence_number }}</td>
            <td class="py-2 pr-3">{{ entry.entry_date }}</td>
            <td class="py-2 pr-3">
              {{ entry.description }}
              <Badge v-if="entry.entry_type === 'storno'" variant="warning" class="ml-2">{{ t('limitsAccountingEtc.kpoListView.stornoBadge') }}</Badge>
            </td>
            <td class="py-2 pr-3 text-right"><MoneyDisplay :amount="entry.product_revenue" :currency="currency" /></td>
            <td class="py-2 pr-3 text-right"><MoneyDisplay :amount="entry.service_revenue" :currency="currency" /></td>
            <td class="py-2 pr-3 text-right font-medium text-navy">
              <MoneyDisplay :amount="entry.total_revenue" :currency="currency" />
            </td>
          </tr>
        </tbody>
      </table>
    </Card>
  </div>
</template>
