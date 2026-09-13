<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Card, Input, Alert } from '@pausalac/ui'
import { listClients, type Client } from '@/services/clients'
import {
  createInvoice,
  getInvoice,
  updateInvoice,
  type InvoiceDraftPayload,
} from '@/services/invoices'
import { ApiError } from '@/lib/api'

const props = defineProps<{ id?: string }>()
const router = useRouter()
const isEditing = computed(() => Boolean(props.id))

function todayIsoDate(): string {
  return new Date().toISOString().slice(0, 10)
}

function addDays(isoDate: string, days: number): string {
  const date = new Date(isoDate)
  date.setDate(date.getDate() + days)
  return date.toISOString().slice(0, 10)
}

const form = ref<InvoiceDraftPayload>({
  client: 0,
  issue_date: todayIsoDate(),
  due_date: addDays(todayIsoDate(), 15),
  service_date: todayIsoDate(),
  notes: '',
  items: [{ description: '', quantity: '1', unit_price: '' }],
})

const clients = ref<Client[]>([])
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const fieldErrors = ref<Record<string, string>>({})

function addLineItem() {
  form.value.items.push({ description: '', quantity: '1', unit_price: '' })
}

function removeLineItem(index: number) {
  form.value.items.splice(index, 1)
}

function lineTotal(item: { quantity: string; unit_price: string }): number {
  const quantity = Number(item.quantity) || 0
  const unitPrice = Number(item.unit_price) || 0
  return quantity * unitPrice
}

const grandTotal = computed(() => form.value.items.reduce((sum, item) => sum + lineTotal(item), 0))

onMounted(async () => {
  loading.value = true
  try {
    clients.value = (await listClients({ pageSize: 100 })).results
    if (props.id) {
      const invoice = await getInvoice(props.id)
      if (invoice.status !== 'draft') {
        // Editing is draft-only (apps/invoices/services.py) — send the
        // user to the read-only detail view instead of a form that would
        // just get a 400 back on submit.
        await router.replace({ name: 'invoice-detail', params: { id: invoice.id } })
        return
      }
      form.value = {
        client: invoice.client,
        issue_date: invoice.issue_date,
        due_date: invoice.due_date,
        service_date: invoice.service_date,
        notes: invoice.notes,
        items: invoice.items.map((item) => ({
          description: item.description,
          quantity: item.quantity,
          unit_price: item.unit_price,
        })),
      }
    } else if (clients.value.length > 0) {
      form.value.client = clients.value[0]!.id
    }
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo podatke.'
  } finally {
    loading.value = false
  }
})

async function onSubmit() {
  saving.value = true
  errorMessage.value = ''
  fieldErrors.value = {}
  try {
    const invoice =
      isEditing.value && props.id
        ? await updateInvoice(props.id, form.value)
        : await createInvoice(form.value)
    await router.push({ name: 'invoice-detail', params: { id: invoice.id } })
  } catch (error) {
    if (error instanceof ApiError) {
      if (error.fields) {
        fieldErrors.value = Object.fromEntries(
          Object.entries(error.fields).map(([field, messages]) => [field, messages[0] ?? '']),
        )
      }
      errorMessage.value = error.message
    } else {
      errorMessage.value = 'Ne možemo trenutno da sačuvamo fakturu. Pokušaj ponovo.'
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl">
    <h1 class="mb-6 text-xl font-semibold text-navy">
      {{ isEditing ? 'Izmeni fakturu' : 'Nova faktura' }}
    </h1>

    <Card v-if="loading">
      <p class="text-sm text-text-secondary">Učitavanje...</p>
    </Card>

    <Card v-else>
      <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-navy" for="client">Klijent</label>
          <select
            id="client"
            v-model="form.client"
            required
            class="rounded-lg border border-border bg-white px-3 py-2 text-sm text-navy focus:outline-none focus:ring-2 focus:ring-primary/40"
          >
            <option v-if="clients.length === 0" :value="0" disabled>Nema klijenata</option>
            <option v-for="c in clients" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
          <p v-if="clients.length === 0" class="text-sm text-text-secondary">
            <RouterLink :to="{ name: 'client-new' }" class="text-primary hover:underline">
              Dodaj klijenta
            </RouterLink>
            pre nego što napraviš fakturu.
          </p>
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Input v-model="form.issue_date" type="date" label="Datum izdavanja" required />
          <Input v-model="form.due_date" type="date" label="Rok plaćanja" required />
          <Input v-model="form.service_date" type="date" label="Datum prometa" required />
        </div>

        <div class="flex flex-col gap-2">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-navy">Stavke</span>
            <button type="button" class="text-sm text-primary hover:underline" @click="addLineItem">
              + Dodaj stavku
            </button>
          </div>

          <div
            v-for="(item, index) in form.items"
            :key="index"
            class="grid grid-cols-12 items-end gap-2 border-b border-border pb-3"
          >
            <div class="col-span-12 sm:col-span-6">
              <Input v-model="item.description" label="Opis" required :error="fieldErrors[`items.${index}.description`]" />
            </div>
            <div class="col-span-4 sm:col-span-2">
              <Input v-model="item.quantity" type="number" label="Količina" required />
            </div>
            <div class="col-span-5 sm:col-span-3">
              <Input v-model="item.unit_price" type="number" label="Cena" required />
            </div>
            <div class="col-span-3 sm:col-span-1">
              <button
                type="button"
                class="text-sm text-danger hover:underline disabled:opacity-40"
                :disabled="form.items.length === 1"
                @click="removeLineItem(index)"
              >
                Ukloni
              </button>
            </div>
          </div>

          <p class="text-right text-sm font-medium text-navy">
            Ukupno: {{ grandTotal.toLocaleString('sr-RS', { minimumFractionDigits: 2 }) }}
          </p>
        </div>

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
          <Button type="submit" :loading="saving" :disabled="clients.length === 0">
            Sačuvaj kao nacrt
          </Button>
          <RouterLink :to="{ name: 'invoices' }">
            <Button variant="ghost" type="button">Otkaži</Button>
          </RouterLink>
        </div>
      </form>
    </Card>
  </div>
</template>
