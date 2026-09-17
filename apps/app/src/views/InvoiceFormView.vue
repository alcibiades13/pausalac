<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Select, Alert, Skeleton, MoneyInput, DatePicker } from '@pausalac/ui'
import { listClients, type Client } from '@/services/clients'
import {
  createInvoice,
  getInvoice,
  updateInvoice,
  type InvoiceDocumentType,
  type InvoiceDraftPayload,
} from '@/services/invoices'
import DocumentTypeBadge from '@/components/DocumentTypeBadge.vue'
import { ApiError } from '@/lib/api'
import { useUnsavedChangesGuard } from '@/composables/useUnsavedChangesGuard'

const { t } = useI18n()
const props = withDefaults(
  defineProps<{ id?: string; documentType?: InvoiceDocumentType }>(),
  { documentType: 'invoice' },
)
const route = useRoute()
const router = useRouter()
const isEditing = computed(() => Boolean(props.id))
// The type shown/sent while creating — once editing an existing draft,
// the real type comes from the fetched invoice instead (see onMounted)
// and is never re-sent as editable (apps/invoices/serializers.py rejects
// changing it anyway).
const documentType = ref<InvoiceDocumentType>(props.documentType)

// Title lookups go through t() per document type — the keys below are the
// backend document-type identifiers, translated on demand in the template.

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
  items: [{ description: '', item_type: 'service', quantity: '1', unit_price: '' }],
})

const ITEM_TYPE_OPTIONS = computed(() => [
  { value: 'service', label: t('dashboardInvoicesClients.invoiceFormView.itemTypeLabels.service') },
  { value: 'product', label: t('dashboardInvoicesClients.invoiceFormView.itemTypeLabels.product') },
])

const clients = ref<Client[]>([])
const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const fieldErrors = ref<Record<string, string>>({})

const { markClean } = useUnsavedChangesGuard(() => form.value)

function addLineItem() {
  form.value.items.push({ description: '', item_type: 'service', quantity: '1', unit_price: '' })
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
      documentType.value = invoice.document_type
      form.value = {
        client: invoice.client,
        issue_date: invoice.issue_date,
        due_date: invoice.due_date,
        service_date: invoice.service_date,
        notes: invoice.notes,
        items: invoice.items.map((item) => ({
          description: item.description,
          item_type: item.item_type,
          quantity: item.quantity,
          unit_price: item.unit_price,
        })),
      }
    } else {
      // §94 "when client is selected: prepopulate known data" — arriving
      // from a client's own profile page's "Nova faktura" CTA skips
      // having to pick the client again.
      const preselectedClientId = Number(route.query.client)
      const preselected = clients.value.find((c) => c.id === preselectedClientId)
      form.value.client = preselected ? preselected.id : (clients.value[0]?.id ?? 0)
    }
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('dashboardInvoicesClients.invoiceFormView.loadError')
  } finally {
    loading.value = false
    markClean()
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
        : await createInvoice({ ...form.value, document_type: documentType.value })
    markClean()
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
      errorMessage.value = t('dashboardInvoicesClients.invoiceFormView.saveError')
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div>
    <div class="mb-6 flex items-center gap-3">
      <h1 class="text-xl font-semibold text-navy">
        {{
          isEditing
            ? t(`dashboardInvoicesClients.invoiceFormView.editTitles.${documentType}`)
            : t(`dashboardInvoicesClients.invoiceFormView.formTitles.${documentType}`)
        }}
      </h1>
      <DocumentTypeBadge v-if="documentType !== 'invoice'" :type="documentType" />
    </div>

    <Card v-if="loading">
      <Skeleton :count="3" />
    </Card>

    <Card v-else>
      <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-navy" for="client">{{ t('dashboardInvoicesClients.invoiceFormView.clientLabel') }}</label>
          <select
            id="client"
            v-model="form.client"
            required
            class="rounded-lg border border-border bg-white px-3 py-2 text-sm text-navy focus:outline-none focus:ring-2 focus:ring-primary/40"
          >
            <option v-if="clients.length === 0" :value="0" disabled>{{ t('dashboardInvoicesClients.invoiceFormView.noClientsOption') }}</option>
            <option v-for="c in clients" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
          <p v-if="clients.length === 0" class="text-sm text-text-secondary">
            <RouterLink :to="{ name: 'client-new' }" class="text-primary-dark hover:underline">
              {{ t('dashboardInvoicesClients.invoiceFormView.addClientLink') }}
            </RouterLink>
            {{ t('dashboardInvoicesClients.invoiceFormView.addClientSuffix') }}
          </p>
        </div>

        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <DatePicker v-model="form.issue_date" :label="t('dashboardInvoicesClients.invoiceFormView.issueDateLabel')" required />
          <DatePicker v-model="form.due_date" :label="t('dashboardInvoicesClients.invoiceFormView.dueDateLabel')" required />
          <DatePicker v-model="form.service_date" :label="t('dashboardInvoicesClients.invoiceFormView.serviceDateLabel')" required />
        </div>

        <div class="flex flex-col gap-2">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-navy">{{ t('dashboardInvoicesClients.invoiceFormView.itemsLabel') }}</span>
            <button type="button" class="text-sm text-primary-dark hover:underline" @click="addLineItem">
              {{ t('dashboardInvoicesClients.invoiceFormView.addItemButton') }}
            </button>
          </div>

          <div
            v-for="(item, index) in form.items"
            :key="index"
            class="grid grid-cols-12 items-end gap-2 border-b border-border pb-3"
          >
            <div class="col-span-12 sm:col-span-5">
              <Input
                v-model="item.description"
                :label="t('dashboardInvoicesClients.invoiceFormView.descriptionLabel')"
                required
                :error="fieldErrors[`items.${index}.description`]"
              />
            </div>
            <div class="col-span-6 sm:col-span-2">
              <Select v-model="item.item_type" :label="t('dashboardInvoicesClients.invoiceFormView.typeLabel')" :options="ITEM_TYPE_OPTIONS" />
            </div>
            <div class="col-span-3 sm:col-span-2">
              <Input v-model="item.quantity" type="number" :label="t('dashboardInvoicesClients.invoiceFormView.quantityLabel')" required />
            </div>
            <div class="col-span-6 sm:col-span-2">
              <MoneyInput v-model="item.unit_price" :label="t('dashboardInvoicesClients.invoiceFormView.priceLabel')" required />
            </div>
            <div class="col-span-3 sm:col-span-1">
              <button
                type="button"
                class="text-sm text-danger hover:underline disabled:opacity-40"
                :disabled="form.items.length === 1"
                @click="removeLineItem(index)"
              >
                {{ t('dashboardInvoicesClients.invoiceFormView.removeButton') }}
              </button>
            </div>
          </div>

          <p class="text-right text-sm font-medium text-navy">
            {{ t('dashboardInvoicesClients.invoiceFormView.totalLabel') }}
            {{ grandTotal.toLocaleString('sr-RS', { minimumFractionDigits: 2 }) }}
          </p>
        </div>

        <div class="flex flex-col gap-1">
          <label class="text-sm font-medium text-navy" for="notes">{{ t('dashboardInvoicesClients.invoiceFormView.notesLabel') }}</label>
          <textarea
            id="notes"
            v-model="form.notes"
            rows="3"
            class="rounded-lg border border-border bg-white px-3 py-2 text-sm text-navy focus:outline-none focus:ring-2 focus:ring-primary/40"
          />
        </div>

        <div class="flex gap-3">
          <Button type="submit" :loading="saving" :disabled="clients.length === 0">
            {{ t('dashboardInvoicesClients.invoiceFormView.saveDraftButton') }}
          </Button>
          <RouterLink :to="{ name: 'invoices' }">
            <Button variant="ghost" type="button">{{ t('dashboardInvoicesClients.invoiceFormView.cancelButton') }}</Button>
          </RouterLink>
        </div>
      </form>
    </Card>
  </div>
</template>
