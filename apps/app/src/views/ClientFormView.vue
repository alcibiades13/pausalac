<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Card, Input, Alert, Skeleton } from '@pausalac/ui'
import { createClient, getClient, updateClient, type ClientPayload } from '@/services/clients'
import { ApiError } from '@/lib/api'

const props = defineProps<{ id?: string }>()
const router = useRouter()
const isEditing = computed(() => Boolean(props.id))

const form = ref<ClientPayload>({
  client_type: 'company',
  name: '',
  tax_id: '',
  email: '',
  phone: '',
  address: '',
  notes: '',
})

const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const fieldErrors = ref<Record<string, string>>({})

onMounted(async () => {
  if (!props.id) return
  loading.value = true
  try {
    const client = await getClient(props.id)
    form.value = { ...client }
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo klijenta.'
  } finally {
    loading.value = false
  }
})

async function onSubmit() {
  saving.value = true
  errorMessage.value = ''
  fieldErrors.value = {}
  try {
    if (isEditing.value && props.id) {
      await updateClient(props.id, form.value)
    } else {
      await createClient(form.value)
    }
    await router.push({ name: 'clients' })
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.fields) {
        fieldErrors.value = Object.fromEntries(
          Object.entries(error.fields).map(([field, messages]) => [field, messages[0] ?? '']),
        )
      } else {
        errorMessage.value = error.message
      }
    } else {
      errorMessage.value = 'Ne možemo trenutno da sačuvamo klijenta. Pokušaj ponovo.'
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl">
    <h1 class="mb-6 text-xl font-semibold text-navy">
      {{ isEditing ? 'Izmeni klijenta' : 'Novi klijent' }}
    </h1>
    <Card>
      <Skeleton v-if="loading" :count="3" />
      <form v-else class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-navy" for="client_type">Tip klijenta</label>
          <select
            id="client_type"
            v-model="form.client_type"
            class="rounded-lg border border-border bg-white px-3 py-2 text-sm text-navy focus:outline-none focus:ring-2 focus:ring-primary/40"
          >
            <option value="company">Pravno lice</option>
            <option value="individual">Fizičko lice</option>
          </select>
        </div>

        <Input v-model="form.name" label="Naziv" required :error="fieldErrors.name" />
        <Input v-model="form.tax_id" label="PIB / matični broj" :error="fieldErrors.tax_id" />
        <Input v-model="form.email" type="email" label="Email" :error="fieldErrors.email" />
        <Input v-model="form.phone" label="Telefon" :error="fieldErrors.phone" />
        <Input v-model="form.address" label="Adresa" :error="fieldErrors.address" />

        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-navy" for="notes">Napomene</label>
          <textarea
            id="notes"
            v-model="form.notes"
            rows="3"
            class="rounded-lg border border-border bg-white px-3 py-2 text-sm text-navy focus:outline-none focus:ring-2 focus:ring-primary/40"
          />
        </div>

        <div class="flex gap-3">
          <Button type="submit" :loading="saving">Sačuvaj</Button>
          <RouterLink :to="{ name: 'clients' }">
            <Button variant="ghost" type="button">Otkaži</Button>
          </RouterLink>
        </div>
      </form>
    </Card>
  </div>
</template>
