<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Badge, Button, DataTable, Pagination, type DataTableColumn } from '@pausalac/ui'
import {
  deactivateAdminUser,
  listAdminUsers,
  reactivateAdminUser,
  type AdminUser,
} from '@/services/admin'
import { formatDate } from '@/lib/formatDate'
import { useTableQuery } from '@/composables/useTableQuery'

const { t } = useI18n()

const actingOnId = ref<number | null>(null)

const columns = computed<DataTableColumn<AdminUser>[]>(() => [
  { key: 'email', label: t('admin.adminUsersView.emailColumn'), sortable: true },
  { key: 'name', label: t('admin.adminUsersView.nameColumn'), format: (r) => `${r.first_name} ${r.last_name}`.trim() || '—' },
  {
    key: 'date_joined',
    label: t('admin.adminUsersView.registeredColumn'),
    format: (r) => formatDate(r.date_joined),
    sortable: true,
  },
])

const {
  rows: users,
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
} = useTableQuery<AdminUser>(
  (q) => listAdminUsers({ page: q.page, page_size: q.pageSize, search: q.search, ordering: q.ordering }),
  { genericErrorMessage: t('admin.adminUsersView.loadError') },
)

async function onToggle(user: AdminUser) {
  actingOnId.value = user.id
  try {
    if (user.is_active) {
      await deactivateAdminUser(user.id)
    } else {
      await reactivateAdminUser(user.id)
    }
    await load()
  } catch {
    errorMessage.value = t('admin.adminUsersView.actionError')
  } finally {
    actingOnId.value = null
  }
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminUsersView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable
      :columns="columns"
      :rows="users"
      :loading="status === 'loading'"
      :sort="sort"
      :empty-title="t('admin.adminUsersView.emptyTitle')"
      @sort="onSort"
    >
      <template #actions="{ row }">
        <div class="flex items-center gap-2">
          <Badge :variant="row.is_active ? 'success' : 'neutral'">
            {{ row.is_active ? t('admin.adminUsersView.activeBadge') : t('admin.adminUsersView.deactivatedBadge') }}
          </Badge>
          <Button
            variant="secondary"
            :loading="actingOnId === row.id"
            @click="onToggle(row)"
          >
            {{ row.is_active ? t('admin.adminUsersView.deactivateButton') : t('admin.adminUsersView.reactivateButton') }}
          </Button>
        </div>
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
