<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Alert, Badge, Button } from '@pausalac/ui'
import AdminTable, { type AdminTableColumn } from '@/components/admin/AdminTable.vue'
import {
  deactivateAdminUser,
  listAdminUsers,
  reactivateAdminUser,
  type AdminUser,
} from '@/services/admin'
import { ApiError } from '@/lib/api'

const users = ref<AdminUser[]>([])
const loading = ref(true)
const errorMessage = ref('')
const actingOnId = ref<number | null>(null)
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const columns: AdminTableColumn<AdminUser>[] = [
  { key: 'email', label: 'Email' },
  { key: 'name', label: 'Ime', format: (r) => `${r.first_name} ${r.last_name}`.trim() || '—' },
  {
    key: 'date_joined',
    label: 'Registrovan',
    format: (r) => new Date(r.date_joined).toLocaleDateString('sr-RS'),
  },
]

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
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo korisnike.'
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
    errorMessage.value = error instanceof ApiError ? error.message : 'Akcija nije uspela.'
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
    <h1 class="text-xl font-semibold text-navy">Korisnici</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <AdminTable :columns="columns" :rows="users" :loading="loading" empty-title="Nema korisnika.">
      <template #actions="{ row }">
        <div class="flex items-center gap-2">
          <Badge :variant="row.is_active ? 'success' : 'neutral'">
            {{ row.is_active ? 'Aktivan' : 'Deaktiviran' }}
          </Badge>
          <Button
            variant="secondary"
            :loading="actingOnId === row.id"
            @click="onToggle(row)"
          >
            {{ row.is_active ? 'Deaktiviraj' : 'Reaktiviraj' }}
          </Button>
        </div>
      </template>
    </AdminTable>

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">Prethodna</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">Sledeća</Button>
    </div>
  </div>
</template>
