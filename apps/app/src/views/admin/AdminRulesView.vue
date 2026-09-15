<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Alert, Badge, Button, Card, Input , DataTable, type DataTableColumn } from '@pausalac/ui'
import {
  approveAdminRegulatoryRule,
  createAdminRegulatoryRule,
  listAdminRegulatoryRules,
  type AdminRegulatoryRule,
} from '@/services/admin'
import { ApiError } from '@/lib/api'

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

const columns: DataTableColumn<AdminRegulatoryRule>[] = [
  { key: 'identifier', label: 'Identifikator' },
  { key: 'version', label: 'Verzija' },
  { key: 'effective_from', label: 'Važi od' },
  { key: 'source', label: 'Izvor' },
]

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    rules.value = (await listAdminRegulatoryRules()).results
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo pravila.'
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
      errorMessage.value = 'Konfiguracija mora biti ispravan JSON.'
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
    errorMessage.value = error instanceof ApiError ? error.message : 'Čuvanje nije uspelo.'
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
    errorMessage.value = error instanceof ApiError ? error.message : 'Potvrda nije uspela.'
  } finally {
    actingOnId.value = null
  }
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-semibold text-navy">Regulatorna pravila</h1>
      <Button @click="onNew">+ Nova verzija</Button>
    </div>
    <p class="text-sm text-text-secondary">
      Verzije se samo dodaju, nikad ne menjaju (master prompt §81/82) — nova verzija je uvek nov
      red; "Potvrdi" samo označava postojeći red kao potvrđen, sa audit zapisom.
    </p>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <Card v-if="formOpen">
      <h2 class="mb-3 text-base font-semibold text-navy">Nova verzija pravila</h2>
      <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input v-model="form.identifier" label="Identifikator" :disabled="saving" required />
          <Input v-model="form.version" label="Verzija" type="number" :disabled="saving" required />
          <Input v-model="form.effective_from" label="Važi od" type="date" :disabled="saving" required />
          <Input v-model="form.source" label="Izvor" :disabled="saving" required />
        </div>
        <Input v-model="form.configJson" label="Konfiguracija (JSON)" :disabled="saving" required />
        <Input v-model="form.notes" label="Napomene" :disabled="saving" />
        <div class="flex gap-2">
          <Button type="submit" :loading="saving">Sačuvaj</Button>
          <Button type="button" variant="secondary" :disabled="saving" @click="formOpen = false">
            Otkaži
          </Button>
        </div>
      </form>
    </Card>

    <DataTable :columns="columns" :rows="rules" :loading="loading" empty-title="Nema pravila.">
      <template #actions="{ row }">
        <div class="flex items-center gap-2">
          <Badge :variant="row.approval_status === 'confirmed' ? 'success' : 'warning'">
            {{ row.approval_status === 'confirmed' ? 'Potvrđeno' : 'Nepotvrđeno' }}
          </Badge>
          <Button
            v-if="row.approval_status !== 'confirmed'"
            variant="secondary"
            :loading="actingOnId === row.id"
            @click="onApprove(row)"
          >
            Potvrdi
          </Button>
        </div>
      </template>
    </DataTable>
  </div>
</template>
