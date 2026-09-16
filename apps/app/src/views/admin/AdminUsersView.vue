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
import { ApiError } from '@/lib/api'
import { formatDate } from '@/lib/formatDate'

const { t } = useI18n()

const users = ref<AdminUser[]>([])
const loading = ref(true)
const errorMessage = ref('')
const actingOnId = ref<number | null>(null)
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const columns = computed<DataTableColumn<AdminUser>[]>(() => [
  { key: 'email', label: t('admin.adminUsersView.emailColumn') },
  { key: 'name', label: t('admin.adminUsersView.nameColumn'), format: (r) => `${r.first_name} ${r.last_name}`.trim() || '—' },
  {
    key: 'date_joined',
    label: t('admin.adminUsersView.registeredColumn'),
    format: (r) => formatDate(r.date_joined),
  },
])

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await listAdminUsers({ page: page.value })
    users.value = result.results
    hasNext.value = result.next !== null
    hasPrevious.value = result.previous !== null
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('admin.adminUsersView.loadError')
  } finally {
    loading.value = false
  }
}

async function onToggle(user: AdminUser) {
  actingOnId.value = user.id
  try {
    if (user.is_active) {
      await deactivateAdminUser(user.id)
    } else {
      await reactivateAdminUser(user.id)
    }
    await load()
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : t('admin.adminUsersView.actionError')
  } finally {
    actingOnId.value = null
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
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminUsersView.title') }}</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <DataTable :columns="columns" :rows="users" :loading="loading" :empty-title="t('admin.adminUsersView.emptyTitle')">
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

    <Pagination :has-next="hasNext" :has-previous="hasPrevious" @next="goNext" @previous="goPrevious" />
  </div>
</template>
