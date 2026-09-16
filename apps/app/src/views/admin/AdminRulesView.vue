<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Badge, Button, Card, Input , DataTable, type DataTableColumn } from '@pausalac/ui'
import {
  approveAdminRegulatoryRule,
  createAdminRegulatoryRule,
  listAdminRegulatoryRules,
  type AdminRegulatoryRule,
} from '@/services/admin'
import { ApiError } from '@/lib/api'

const { t } = useI18n()

const rules = ref<AdminRegulatoryRule[]>([])
const loading = ref(true)
const errorMessage = ref('')
const saving = ref(false)
const actingOnId = ref<number | null>(null)

const formOpen = ref(false)
const form = ref({
  identifier: '',
  configJson: '{}',
  effective_from: '',
  source: '',
  version: '1',
  notes: '',
})

const columns = computed<DataTableColumn<AdminRegulatoryRule>[]>(() => [
  { key: 'identifier', label: t('admin.adminRulesView.identifierLabel') },
  { key: 'version', label: t('admin.adminRulesView.versionLabel') },
  { key: 'effective_from', label: t('admin.adminRulesView.effectiveFromLabel') },
  { key: 'source', label: t('admin.adminRulesView.sourceLabel') },
])

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    rules.value = (await listAdminRegulatoryRules()).results
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('admin.adminRulesView.loadError')
  } finally {
    loading.value = false
  }
}

function onNew() {
  formOpen.value = true
  form.value = { identifier: '', configJson: '{}', effective_from: '', source: '', version: '1', notes: '' }
}

async function onSubmit() {
  saving.value = true
  errorMessage.value = ''
  try {
    let config: Record<string, unknown>
    try {
      config = JSON.parse(form.value.configJson)
    } catch {
      errorMessage.value = t('admin.adminRulesView.invalidJsonError')
      saving.value = false
      return
    }
    await createAdminRegulatoryRule({
      identifier: form.value.identifier,
      config,
      effective_from: form.value.effective_from,
      source: form.value.source,
      version: Number(form.value.version),
      notes: form.value.notes,
    })
    formOpen.value = false
    await load()
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : t('admin.adminRulesView.saveError')
  } finally {
    saving.value = false
  }
}

async function onApprove(rule: AdminRegulatoryRule) {
  actingOnId.value = rule.id
  errorMessage.value = ''
  try {
    await approveAdminRegulatoryRule(rule.id)
    await load()
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : t('admin.adminRulesView.approveError')
  } finally {
    actingOnId.value = null
  }
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminRulesView.title') }}</h1>
      <Button @click="onNew">{{ t('admin.adminRulesView.newVersionButton') }}</Button>
    </div>
    <p class="text-sm text-text-secondary">
      {{ t('admin.adminRulesView.description') }}
    </p>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <Card v-if="formOpen">
      <h2 class="mb-3 text-base font-semibold text-navy">{{ t('admin.adminRulesView.newRuleHeading') }}</h2>
      <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input v-model="form.identifier" :label="t('admin.adminRulesView.identifierLabel')" :disabled="saving" required />
          <Input v-model="form.version" :label="t('admin.adminRulesView.versionLabel')" type="number" :disabled="saving" required />
          <Input v-model="form.effective_from" :label="t('admin.adminRulesView.effectiveFromLabel')" type="date" :disabled="saving" required />
          <Input v-model="form.source" :label="t('admin.adminRulesView.sourceLabel')" :disabled="saving" required />
        </div>
        <Input v-model="form.configJson" :label="t('admin.adminRulesView.configJsonLabel')" :disabled="saving" required />
        <Input v-model="form.notes" :label="t('admin.adminRulesView.notesLabel')" :disabled="saving" />
        <div class="flex gap-2">
          <Button type="submit" :loading="saving">{{ t('admin.adminRulesView.saveButton') }}</Button>
          <Button type="button" variant="secondary" :disabled="saving" @click="formOpen = false">
            {{ t('admin.adminRulesView.cancelButton') }}
          </Button>
        </div>
      </form>
    </Card>

    <DataTable :columns="columns" :rows="rules" :loading="loading" :empty-title="t('admin.adminRulesView.emptyTitle')">
      <template #actions="{ row }">
        <div class="flex items-center gap-2">
          <Badge :variant="row.approval_status === 'confirmed' ? 'success' : 'warning'">
            {{ row.approval_status === 'confirmed' ? t('admin.adminRulesView.confirmedBadge') : t('admin.adminRulesView.unconfirmedBadge') }}
          </Badge>
          <Button
            v-if="row.approval_status !== 'confirmed'"
            variant="secondary"
            :loading="actingOnId === row.id"
            @click="onApprove(row)"
          >
            {{ t('admin.adminRulesView.confirmButton') }}
          </Button>
        </div>
      </template>
    </DataTable>
  </div>
</template>
