<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Button, Card, DataTable, Pagination, type DataTableColumn } from '@pausalac/ui'
import {
  listAdminCompanies,
  listAdminCompanyMembers,
  type AdminCompany,
  type AdminMembership,
} from '@/services/admin'
import { formatDate } from '@/lib/formatDate'
import { useTableQuery } from '@/composables/useTableQuery'

const { t } = useI18n()

const membersFor = ref<AdminCompany | null>(null)
const members = ref<AdminMembership[]>([])
const membersLoading = ref(false)

const columns = computed<DataTableColumn<AdminCompany>[]>(() => [
  { key: 'name', label: t('admin.adminCompaniesView.nameColumn'), sortable: true },
  { key: 'pib', label: t('admin.adminCompaniesView.pibColumn') },
  { key: 'city', label: t('admin.adminCompaniesView.cityColumn') },
  {
    key: 'created_at',
    label: t('admin.adminCompaniesView.registeredColumn'),
    format: (r) => formatDate(r.created_at),
    sortable: true,
  },
])

const {
  rows: companies,
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
} = useTableQuery<AdminCompany>(
  (q) => listAdminCompanies({ page: q.page, page_size: q.pageSize, search: q.search, ordering: q.ordering }),
  { genericErrorMessage: t('admin.adminCompaniesView.loadError') },
)

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

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminCompaniesView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="companies"
      :loading="status === 'loading'"
      :sort="sort"
      :empty-title="t('admin.adminCompaniesView.emptyTitle')"
      @sort="onSort"
    >
      <template #actions="{ row }">
        <Button variant="secondary" @click="onShowMembers(row)">{{ t('admin.adminCompaniesView.membersButton') }}</Button>
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
