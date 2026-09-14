<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { Card, Alert, EmptyState, Input, MoneyDisplay, Badge } from '@pausalac/ui'
import { listKpoEntries, kpoExportPdfUrl, kpoExportXlsxUrl, type KPOEntry } from '@/services/kpo'
import { useCompanyStore } from '@/stores/company'
import { ApiError } from '@/lib/api'

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
    errorMessage.value = error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo KPO.'
    status.value = 'error'
  }
}

onMounted(load)
watch([dateFrom, dateTo], load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-navy">KPO</h1>
      <div class="flex gap-3">
        <a :href="kpoExportPdfUrl()" target="_blank" rel="noopener" class="text-sm text-primary hover:underline">
          Izvezi PDF
        </a>
        <a :href="kpoExportXlsxUrl()" class="text-sm text-primary hover:underline">Izvezi Excel</a>
      </div>
    </div>

    <div class="flex flex-wrap items-end gap-3">
      <Input v-model="dateFrom" type="date" label="Od" />
      <Input v-model="dateTo" type="date" label="Do" />
    </div>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">Pokušaj ponovo</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <p class="text-sm text-text-secondary">Učitavanje...</p>
    </Card>

    <Card v-else-if="entries.length === 0">
      <EmptyState
        title="Još nema KPO stavki."
        description="Stavke se automatski generišu kada izdaš fakturu."
      />
    </Card>

    <Card v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-border text-left text-xs uppercase tracking-wide text-text-secondary">
            <th class="py-2 pr-3">Redni broj</th>
            <th class="py-2 pr-3">Datum</th>
            <th class="py-2 pr-3">Opis</th>
            <th class="py-2 pr-3 text-right">Proizvodi</th>
            <th class="py-2 pr-3 text-right">Usluge</th>
            <th class="py-2 pr-3 text-right">Ukupno</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in entries" :key="entry.id" class="border-b border-border">
            <td class="py-2 pr-3">{{ entry.sequence_number }}</td>
            <td class="py-2 pr-3">{{ entry.entry_date }}</td>
            <td class="py-2 pr-3">
              {{ entry.description }}
              <Badge v-if="entry.entry_type === 'storno'" variant="warning" class="ml-2">Storno</Badge>
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
