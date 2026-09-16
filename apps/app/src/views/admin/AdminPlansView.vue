<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Badge, Button, Card, Input, Select , DataTable, type DataTableColumn } from '@pausalac/ui'
import {
  createAdminPlan,
  listAdminPlans,
  updateAdminPlan,
} from '@/services/admin'
import type { Plan } from '@/services/subscriptions'
import { ApiError } from '@/lib/api'

const { t } = useI18n()

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

const columns = computed<DataTableColumn<AdminPlan>[]>(() => [
  { key: 'identifier', label: t('admin.adminPlansView.identifierLabel') },
  { key: 'name', label: t('admin.adminPlansView.nameLabel') },
  { key: 'price', label: t('admin.adminPlansView.priceLabel'), format: (r) => `${r.price} ${r.currency}` },
])

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    plans.value = (await listAdminPlans()).results
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : t('admin.adminPlansView.loadError')
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
    errorMessage.value = error instanceof ApiError ? error.message : t('admin.adminPlansView.saveError')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminPlansView.title') }}</h1>
      <Button @click="onNew">{{ t('admin.adminPlansView.newPlanButton') }}</Button>
    </div>
    <p class="text-sm text-text-secondary">
      {{ t('admin.adminPlansView.description') }}
    </p>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <Card v-if="formOpen">
      <h2 class="mb-3 text-base font-semibold text-navy">
        {{ editingId ? t('admin.adminPlansView.editPlanHeading') : t('admin.adminPlansView.newPlanHeading') }}
      </h2>
      <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input v-model="form.identifier" :label="t('admin.adminPlansView.identifierLabel')" :disabled="!!editingId || saving" required />
          <Input v-model="form.name" :label="t('admin.adminPlansView.nameLabel')" :disabled="saving" required />
          <Input v-model="form.price" :label="t('admin.adminPlansView.priceLabel')" :disabled="saving" required />
          <Input v-model="form.currency" :label="t('admin.adminPlansView.currencyLabel')" :disabled="saving" required />
          <Select
            v-model="form.is_active"
            :label="t('admin.adminPlansView.statusLabel')"
            :options="[
              { value: 'true', label: t('admin.adminPlansView.statusActiveOption') },
              { value: 'false', label: t('admin.adminPlansView.statusInactiveOption') },
            ]"
            :disabled="saving"
          />
        </div>
        <div class="flex gap-2">
          <Button type="submit" :loading="saving">{{ t('admin.adminPlansView.saveButton') }}</Button>
          <Button type="button" variant="secondary" :disabled="saving" @click="formOpen = false">
            {{ t('admin.adminPlansView.cancelButton') }}
          </Button>
        </div>
      </form>
    </Card>

    <DataTable :columns="columns" :rows="plans" :loading="loading" :empty-title="t('admin.adminPlansView.emptyTitle')">
      <template #actions="{ row }">
        <div class="flex items-center gap-2">
          <Badge :variant="row.is_active ? 'success' : 'neutral'">
            {{ row.is_active ? t('admin.adminPlansView.activeBadge') : t('admin.adminPlansView.inactiveBadge') }}
          </Badge>
          <Button variant="secondary" @click="onEdit(row)">{{ t('admin.adminPlansView.editButton') }}</Button>
        </div>
      </template>
    </DataTable>
  </div>
</template>
