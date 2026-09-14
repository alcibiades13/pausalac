<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Alert, Badge, Button, Card, Input, Select } from '@pausalac/ui'
import AdminTable, { type AdminTableColumn } from '@/components/admin/AdminTable.vue'
import {
  createAdminPlan,
  listAdminPlans,
  updateAdminPlan,
} from '@/services/admin'
import type { Plan } from '@/services/subscriptions'
import { ApiError } from '@/lib/api'

type AdminPlan = Plan & { is_active: boolean }

const plans = ref<AdminPlan[]>([])
const loading = ref(true)
const errorMessage = ref('')
const saving = ref(false)

const editingId = ref<number | null>(null)
const formOpen = ref(false)
const form = ref({
  identifier: '',
  name: '',
  price: '',
  currency: 'RSD',
  billing_interval: 'monthly' as const,
  is_active: 'true',
})

const columns: AdminTableColumn<AdminPlan>[] = [
  { key: 'identifier', label: 'Identifikator' },
  { key: 'name', label: 'Naziv' },
  { key: 'price', label: 'Cena', format: (r) => `${r.price} ${r.currency}` },
]

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    plans.value = (await listAdminPlans()).results
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo planove.'
  } finally {
    loading.value = false
  }
}

function onNew() {
  editingId.value = null
  form.value = {
    identifier: '',
    name: '',
    price: '',
    currency: 'RSD',
    billing_interval: 'monthly',
    is_active: 'true',
  }
  formOpen.value = true
}

function onEdit(plan: AdminPlan) {
  editingId.value = plan.id
  form.value = {
    identifier: plan.identifier,
    name: plan.name,
    price: plan.price,
    currency: plan.currency,
    billing_interval: 'monthly',
    is_active: String(plan.is_active),
  }
  formOpen.value = true
}

async function onSubmit() {
  saving.value = true
  errorMessage.value = ''
  try {
    const payload = {
      identifier: form.value.identifier,
      name: form.value.name,
      price: form.value.price,
      currency: form.value.currency,
      billing_interval: 'monthly' as const,
      entitlements: {},
      is_active: form.value.is_active === 'true',
    }
    if (editingId.value) {
      await updateAdminPlan(editingId.value, payload)
    } else {
      await createAdminPlan(payload)
    }
    formOpen.value = false
    await load()
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : 'Čuvanje nije uspelo.'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-navy">Planovi</h1>
      <Button @click="onNew">+ Novi plan</Button>
    </div>
    <p class="text-sm text-text-secondary">
      Cena ovde je jedini izvor istine za sve klijentske ekrane (master prompt §50) — nema
      hardkodovanih cena u frontendu.
    </p>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <Card v-if="formOpen">
      <h2 class="mb-3 text-base font-semibold text-navy">
        {{ editingId ? 'Izmeni plan' : 'Novi plan' }}
      </h2>
      <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input v-model="form.identifier" label="Identifikator" :disabled="!!editingId || saving" required />
          <Input v-model="form.name" label="Naziv" :disabled="saving" required />
          <Input v-model="form.price" label="Cena" :disabled="saving" required />
          <Input v-model="form.currency" label="Valuta" :disabled="saving" required />
          <Select
            v-model="form.is_active"
            label="Status"
            :options="[
              { value: 'true', label: 'Dostupan za izbor' },
              { value: 'false', label: 'Nedostupan' },
            ]"
            :disabled="saving"
          />
        </div>
        <div class="flex gap-2">
          <Button type="submit" :loading="saving">Sačuvaj</Button>
          <Button type="button" variant="secondary" :disabled="saving" @click="formOpen = false">
            Otkaži
          </Button>
        </div>
      </form>
    </Card>

    <AdminTable :columns="columns" :rows="plans" :loading="loading" empty-title="Nema planova.">
      <template #actions="{ row }">
        <div class="flex items-center gap-2">
          <Badge :variant="row.is_active ? 'success' : 'neutral'">
            {{ row.is_active ? 'Dostupan' : 'Nedostupan' }}
          </Badge>
          <Button variant="secondary" @click="onEdit(row)">Izmeni</Button>
        </div>
      </template>
    </AdminTable>
  </div>
</template>
