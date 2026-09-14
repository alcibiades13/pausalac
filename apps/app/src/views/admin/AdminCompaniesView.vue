<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Alert, Button, Card } from '@pausalac/ui'
import AdminTable, { type AdminTableColumn } from '@/components/admin/AdminTable.vue'
import {
  listAdminCompanies,
  listAdminCompanyMembers,
  type AdminCompany,
  type AdminMembership,
} from '@/services/admin'
import { ApiError } from '@/lib/api'

const companies = ref<AdminCompany[]>([])
const loading = ref(true)
const errorMessage = ref('')
const page = ref(1)
const hasNext = ref(false)
const hasPrevious = ref(false)

const membersFor = ref<AdminCompany | null>(null)
const members = ref<AdminMembership[]>([])
const membersLoading = ref(false)

const columns: AdminTableColumn<AdminCompany>[] = [
  { key: 'name', label: 'Naziv' },
  { key: 'pib', label: 'PIB' },
  { key: 'city', label: 'Grad' },
  {
    key: 'created_at',
    label: 'Registrovana',
    format: (r) => new Date(r.created_at).toLocaleDateString('sr-RS'),
  },
]

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    const result = await listAdminCompanies({ page: page.value })
    companies.value = result.results
    hasNext.value = result.next !== null
    hasPrevious.value = result.previous !== null
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo kompanije.'
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
    <h1 class="text-xl font-semibold text-navy">Kompanije</h1>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <AdminTable
      :columns="columns"
      :rows="companies"
      :loading="loading"
      empty-title="Nema kompanija."
    >
      <template #actions="{ row }">
        <Button variant="secondary" @click="onShowMembers(row)">Članovi</Button>
      </template>
    </AdminTable>

    <div v-if="hasNext || hasPrevious" class="flex items-center gap-2">
      <Button variant="secondary" :disabled="!hasPrevious" @click="goPrevious">Prethodna</Button>
      <Button variant="secondary" :disabled="!hasNext" @click="goNext">Sledeća</Button>
    </div>

    <Card v-if="membersFor">
      <div class="mb-3 flex items-center justify-between">
        <h2 class="text-base font-semibold text-navy">Članovi — {{ membersFor.name }}</h2>
        <button class="text-sm text-text-secondary underline" @click="membersFor = null">Zatvori</button>
      </div>
      <p v-if="membersLoading" class="text-sm text-text-secondary">Učitavanje...</p>
      <p v-else-if="members.length === 0" class="text-sm text-text-secondary">Nema članova.</p>
      <ul v-else class="flex flex-col divide-y divide-border">
        <li v-for="(m, i) in members" :key="i" class="py-2 text-sm text-navy">
          {{ m.user_email }} — {{ m.role }} ({{ m.status }})
        </li>
      </ul>
    </Card>
  </div>
</template>
