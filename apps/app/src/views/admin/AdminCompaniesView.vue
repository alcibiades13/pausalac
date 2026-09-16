<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Button, Card , DataTable, type DataTableColumn } from '@pausalac/ui'
import {
  listAdminCompanies,
  listAdminCompanyMembers,
  type AdminCompany,
  type AdminMembership,
} from '@/services/admin'
import { ApiError } from '@/lib/api'
import { formatDate } from '@/lib/formatDate'

const { t } = useI18n()

const companies = ref<AdminCompany[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const membersFor = ref<AdminCompany | null>(null)
const members = ref<AdminMembership[]>([])
const membersLoading = ref(false)

const columns = computed<DataTableColumn<AdminCompany>[]>(() => [
  { key: 'name', label: t('admin.adminCompaniesView.nameColumn') },
  { key: 'pib', label: t('admin.adminCompaniesView.pibColumn') },
  { key: 'city', label: t('admin.adminCompaniesView.cityColumn') },
  {
    key: 'created_at',
    label: t('admin.adminCompaniesView.registeredColumn'),
    format: (r) => formatDate(r.created_at),
  },
])

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await listAdminCompanies({ page: page.value })
    companies.value = result.results
    hasNext.value = result.next !== null
    hasPrevious.value = result.previous !== null
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : t('admin.adminCompaniesView.loadError')
  } finally {
    loading.value = false
  }
}

async function onShowMembers(company: AdminCompany) {
  membersFor.value = company
  membersLoading.value = true
  try {
    members.value = await listAdminCompanyMembers(company.id)
  } catch {
    members.value = []
  } finally {
    membersLoading.value = false
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
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminCompaniesView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="companies"
      :loading="loading"
      :empty-title="t('admin.adminCompaniesView.emptyTitle')"
    >
      <template #actions="{ row }">
        <Button variant="secondary" @click="onShowMembers(row)">{{ t('admin.adminCompaniesView.membersButton') }}</Button>
      </template>
    </DataTable>

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">{{ t('admin.adminCompaniesView.previousButton') }}</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">{{ t('admin.adminCompaniesView.nextButton') }}</Button>
    </div>

    <Card v-if="membersFor">
      <div class="mb-3 flex items-center justify-between">
        <h2 class="text-base font-semibold text-navy">{{ t('admin.adminCompaniesView.membersHeading', { name: membersFor.name }) }}</h2>
        <button class="text-sm text-text-secondary underline" @click="membersFor = null">{{ t('admin.adminCompaniesView.closeButton') }}</button>
      </div>
      <p v-if="membersLoading" class="text-sm text-text-secondary">{{ t('admin.adminCompaniesView.loadingMembers') }}</p>
      <p v-else-if="members.length === 0" class="text-sm text-text-secondary">{{ t('admin.adminCompaniesView.noMembers') }}</p>
      <ul v-else class="flex flex-col divide-y divide-border">
        <li v-for="(m, i) in members" :key="i" class="py-2 text-sm text-navy">
          {{ t('admin.adminCompaniesView.memberLine', { email: m.user_email, role: m.role, status: m.status }) }}
        </li>
      </ul>
    </Card>
  </div>
</template>
