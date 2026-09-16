<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button, Card, Alert, Input, MoneyDisplay, Skeleton, MoneyInput } from '@pausalac/ui'
import {
  getInvoice,
  issueInvoice,
  cancelInvoice,
  convertInvoice,
  duplicateInvoice,
  sendInvoice,
  invoicePdfUrl,
  type Invoice,
} from '@/services/invoices'
import { listPayments, recordPayment, type Payment } from '@/services/payments'
import { listDocuments, type AppDocument } from '@/services/documents'
import { canTransitionTo, isPayable } from '@/lib/invoiceStatus'
import { formatDate } from '@/lib/formatDate'
import { ApiError } from '@/lib/api'
import InvoiceStatusBadge from '@/components/InvoiceStatusBadge.vue'
import DocumentTypeBadge from '@/components/DocumentTypeBadge.vue'

const { t } = useI18n()
const props = defineProps<{ id: string }>()
const router = useRouter()

const invoice = ref<Invoice | null>(null)
const payments = ref<Payment[]>([])
const documents = ref<AppDocument[]>([])
const loadStatus = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')
const actionLoading = ref<'issue' | 'cancel' | 'convert' | 'duplicate' | null>(null)

// A profaktura is a non-binding quote (Phase 6c) — never payable, and
// convertible into a real invoice only once, while issued/sent.
const isProfaktura = computed(() => invoice.value?.document_type === 'profaktura')
const canConvert = computed(
  () =>
    isProfaktura.value &&
    invoice.value !== null &&
    (invoice.value.status === 'issued' || invoice.value.status === 'sent') &&
    invoice.value.converted_to === null,
)

const totalPaid = computed(() =>
  payments.value.reduce((sum, p) => sum + Number(p.amount), 0),
)
const remainingBalance = computed(() =>
  invoice.value ? Math.max(Number(invoice.value.total) - totalPaid.value, 0) : 0,
)

async function load() {
  loadStatus.value = 'loading'
  try {
    invoice.value = await getInvoice(props.id)
    const [paymentsPage, documentsPage] = await Promise.all([
      listPayments({ invoice: props.id }),
      listDocuments({ invoice: props.id }),
    ])
    payments.value = paymentsPage.results
    documents.value = documentsPage.results
    loadStatus.value = 'ready'
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('dashboardInvoicesClients.invoiceDetailView.loadError')
    loadStatus.value = 'error'
  }
}

async function onIssue() {
  actionLoading.value = 'issue'
  errorMessage.value = ''
  try {
    invoice.value = await issueInvoice(props.id)
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : t('dashboardInvoicesClients.invoiceDetailView.issueError')
  } finally {
    actionLoading.value = null
  }
}

async function onCancel() {
  actionLoading.value = 'cancel'
  errorMessage.value = ''
  try {
    invoice.value = await cancelInvoice(props.id)
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : t('dashboardInvoicesClients.invoiceDetailView.cancelError')
  } finally {
    actionLoading.value = null
  }
}

async function onConvert() {
  actionLoading.value = 'convert'
  errorMessage.value = ''
  try {
    const newInvoice = await convertInvoice(props.id)
    await router.push({ name: 'invoice-detail', params: { id: newInvoice.id } })
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('dashboardInvoicesClients.invoiceDetailView.convertError')
    actionLoading.value = null
  }
}

async function onDuplicate() {
  actionLoading.value = 'duplicate'
  errorMessage.value = ''
  try {
    const newInvoice = await duplicateInvoice(props.id)
    // Straight to the edit form, not the detail view — the duplicate is
    // a fresh draft meant to be adjusted immediately (master prompt §94:
    // minimum number of interactions).
    await router.push({ name: 'invoice-edit', params: { id: newInvoice.id } })
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : t('dashboardInvoicesClients.invoiceDetailView.duplicateError')
    actionLoading.value = null
  }
}

// --- send ----------------------------------------------------------------

const showSendForm = ref(false)
const recipientEmail = ref('')
const sendMessage = ref('')
const sending = ref(false)
const sendError = ref('')
const sendConfirmation = ref('')

function openSendForm() {
  recipientEmail.value = invoice.value?.client_email ?? ''
  sendMessage.value = ''
  sendError.value = ''
  sendConfirmation.value = ''
  showSendForm.value = true
}

async function onSend() {
  if (!invoice.value) return
  sending.value = true
  sendError.value = ''
  try {
    await sendInvoice(invoice.value.id, { recipientEmail: recipientEmail.value, message: sendMessage.value })
    sendConfirmation.value = t('dashboardInvoicesClients.invoiceDetailView.sendConfirmation')
    showSendForm.value = false
    // The status flips to "sent" only once the email actually goes out
    // (apps/invoices/tasks.py) — refetch shortly after instead of
    // assuming success immediately.
    setTimeout(load, 1500)
  } catch (error) {
    sendError.value =
      error instanceof ApiError ? error.message : t('dashboardInvoicesClients.invoiceDetailView.sendError')
  } finally {
    sending.value = false
  }
}

// --- record payment -------------------------------------------------------

const showPaymentForm = ref(false)
const paymentAmount = ref('')
const paymentDate = ref('')
const paymentMethod = ref<'bank_transfer' | 'cash' | 'other'>('bank_transfer')
const paymentNotes = ref('')
const recordingPayment = ref(false)
const paymentError = ref('')
// One key per form session, not per request — a retried submission (e.g.
// a flaky connection, or a genuine double-click before the button
// disables) reuses it, and the backend recognizes the replay instead of
// recording a second payment (master prompt §62).
let paymentIdempotencyKey = ''

function openPaymentForm() {
  paymentAmount.value = remainingBalance.value.toFixed(2)
  paymentDate.value = new Date().toISOString().slice(0, 10)
  paymentMethod.value = 'bank_transfer'
  paymentNotes.value = ''
  paymentError.value = ''
  paymentIdempotencyKey = crypto.randomUUID()
  showPaymentForm.value = true
}

async function onRecordPayment() {
  if (!invoice.value) return
  recordingPayment.value = true
  paymentError.value = ''
  try {
    await recordPayment({
      invoice: invoice.value.id,
      amount: paymentAmount.value,
      paid_at: paymentDate.value,
      method: paymentMethod.value,
      notes: paymentNotes.value,
      idempotency_key: paymentIdempotencyKey,
    })
    showPaymentForm.value = false
    await load()
  } catch (error) {
    paymentError.value =
      error instanceof ApiError ? error.message : t('dashboardInvoicesClients.invoiceDetailView.recordPaymentError')
  } finally {
    recordingPayment.value = false
  }
}

// Backend payment-method identifiers, translated on demand (no tm()/list
// iteration here beyond the three static <option> elements in the template).
function paymentMethodLabel(method: 'bank_transfer' | 'cash' | 'other'): string {
  return t(`dashboardInvoicesClients.invoiceDetailView.paymentMethodLabels.${method}`)
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <Alert v-if="loadStatus === 'error'" variant="danger">{{ errorMessage }}</Alert>

    <Card v-else-if="loadStatus === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <template v-else-if="invoice">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="font-mono text-xl font-semibold text-navy">
            {{ invoice.invoice_number ?? t('dashboardInvoicesClients.invoiceDetailView.draftNumberFallback', { id: invoice.id }) }}
          </h1>
          <RouterLink
            :to="{ name: 'client-detail', params: { id: invoice.client } }"
            class="text-sm text-primary hover:underline"
          >
            {{ invoice.client_name }}
          </RouterLink>
        </div>
        <div class="flex items-center gap-2">
          <DocumentTypeBadge v-if="invoice.document_type !== 'invoice'" :type="invoice.document_type" />
          <InvoiceStatusBadge :status="invoice.status" />
        </div>
      </div>

      <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

      <Alert v-if="invoice.converted_from_number" variant="info">
        {{ t('dashboardInvoicesClients.invoiceDetailView.convertedFromNotice') }}
        <RouterLink
          :to="{ name: 'invoice-detail', params: { id: invoice.converted_from } }"
          class="underline"
        >
          {{ invoice.converted_from_number }}
        </RouterLink>
      </Alert>

      <Alert v-if="invoice.converted_to" variant="info">
        {{ t('dashboardInvoicesClients.invoiceDetailView.convertedToNotice') }}
        <RouterLink
          :to="{ name: 'invoice-detail', params: { id: invoice.converted_to } }"
          class="underline"
        >
          {{ invoice.converted_to_number }}
        </RouterLink>
      </Alert>

      <Card>
        <dl class="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
          <div>
            <dt class="text-text-secondary">{{ t('dashboardInvoicesClients.invoiceDetailView.issueDateLabel') }}</dt>
            <dd class="text-navy">{{ formatDate(invoice.issue_date) }}</dd>
          </div>
          <div>
            <dt class="text-text-secondary">{{ t('dashboardInvoicesClients.invoiceDetailView.dueDateLabel') }}</dt>
            <dd class="text-navy">{{ formatDate(invoice.due_date) }}</dd>
          </div>
          <div>
            <dt class="text-text-secondary">{{ t('dashboardInvoicesClients.invoiceDetailView.serviceDateLabel') }}</dt>
            <dd class="text-navy">{{ formatDate(invoice.service_date) }}</dd>
          </div>
        </dl>
      </Card>

      <Card>
        <h2 class="mb-3 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.invoiceDetailView.itemsTitle') }}</h2>
        <ul class="flex flex-col divide-y divide-border">
          <li
            v-for="item in invoice.items"
            :key="item.id"
            class="flex items-center justify-between py-2 text-sm"
          >
            <div>
              <p class="text-navy">{{ item.description }}</p>
              <p class="text-text-secondary">{{ item.quantity }} × {{ item.unit_price }}</p>
            </div>
            <MoneyDisplay :amount="item.line_total ?? '0'" :currency="invoice.currency" />
          </li>
        </ul>
        <div class="mt-3 flex justify-end border-t border-border pt-3 text-base font-semibold text-navy">
          <MoneyDisplay :amount="invoice.total" :currency="invoice.currency" />
        </div>
      </Card>

      <Card v-if="invoice.notes">
        <h2 class="mb-1 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.invoiceDetailView.notesTitle') }}</h2>
        <p class="text-sm text-text-secondary">{{ invoice.notes }}</p>
      </Card>

      <Card v-if="documents.length">
        <h2 class="mb-3 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.invoiceDetailView.documentsTitle') }}</h2>
        <ul class="flex flex-col divide-y divide-border">
          <li v-for="doc in documents" :key="doc.id" class="flex items-center justify-between py-2 text-sm">
            <p class="min-w-0 truncate text-navy">{{ doc.title }}</p>
            <a v-if="doc.file_url" :href="doc.file_url" target="_blank" rel="noopener" class="shrink-0 text-primary hover:underline">
              {{ t('dashboardInvoicesClients.invoiceDetailView.openLink') }}
            </a>
          </li>
        </ul>
      </Card>

      <Card
        v-if="!isProfaktura && (payments.length || isPayable(invoice.status) || invoice.status === 'paid')"
      >
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.invoiceDetailView.paymentsTitle') }}</h2>
          <p v-if="isPayable(invoice.status)" class="text-sm text-text-secondary">
            {{ t('dashboardInvoicesClients.invoiceDetailView.remainingLabel') }}
            <MoneyDisplay :amount="remainingBalance" :currency="invoice.currency" />
          </p>
        </div>
        <ul v-if="payments.length" class="flex flex-col divide-y divide-border">
          <li v-for="payment in payments" :key="payment.id" class="flex items-center justify-between py-2 text-sm">
            <div>
              <p class="text-navy">{{ formatDate(payment.paid_at) }}</p>
              <p class="text-text-secondary">
                {{ paymentMethodLabel(payment.method) }}
              </p>
            </div>
            <MoneyDisplay :amount="payment.amount" :currency="payment.currency" />
          </li>
        </ul>
        <p v-else class="text-sm text-text-secondary">{{ t('dashboardInvoicesClients.invoiceDetailView.noPaymentsYet') }}</p>
      </Card>

      <Card v-if="showPaymentForm">
        <h2 class="mb-3 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.invoiceDetailView.recordPaymentTitle') }}</h2>
        <form class="flex flex-col gap-4" @submit.prevent="onRecordPayment">
          <Alert v-if="paymentError" variant="danger">{{ paymentError }}</Alert>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <MoneyInput
              v-model="paymentAmount"
              :currency="invoice.currency"
              :label="t('dashboardInvoicesClients.invoiceDetailView.amountLabel')"
              required
            />
            <Input v-model="paymentDate" type="date" :label="t('dashboardInvoicesClients.invoiceDetailView.paymentDateLabel')" required />
          </div>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div class="flex flex-col gap-1">
              <label class="text-sm font-medium text-navy" for="payment-method">{{ t('dashboardInvoicesClients.invoiceDetailView.paymentMethodLabel') }}</label>
              <select
                id="payment-method"
                v-model="paymentMethod"
                class="rounded-lg border border-border bg-white px-3 py-2 text-sm text-navy focus:outline-none focus:ring-2 focus:ring-primary/40"
              >
                <option value="bank_transfer">{{ t('dashboardInvoicesClients.invoiceDetailView.paymentMethodLabels.bank_transfer') }}</option>
                <option value="cash">{{ t('dashboardInvoicesClients.invoiceDetailView.paymentMethodLabels.cash') }}</option>
                <option value="other">{{ t('dashboardInvoicesClients.invoiceDetailView.paymentMethodLabels.other') }}</option>
              </select>
            </div>
            <Input v-model="paymentNotes" :label="t('dashboardInvoicesClients.invoiceDetailView.paymentNotesLabel')" />
          </div>
          <div class="flex gap-3">
            <Button type="submit" :loading="recordingPayment">{{ t('dashboardInvoicesClients.invoiceDetailView.savePaymentButton') }}</Button>
            <Button type="button" variant="ghost" @click="showPaymentForm = false">{{ t('dashboardInvoicesClients.invoiceDetailView.cancelButton') }}</Button>
          </div>
        </form>
      </Card>

      <Alert v-if="sendConfirmation" variant="success">{{ sendConfirmation }}</Alert>

      <Card v-if="showSendForm">
        <h2 class="mb-3 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.invoiceDetailView.sendInvoiceTitle') }}</h2>
        <form class="flex flex-col gap-4" @submit.prevent="onSend">
          <Alert v-if="sendError" variant="danger">{{ sendError }}</Alert>
          <Input v-model="recipientEmail" type="email" :label="t('dashboardInvoicesClients.invoiceDetailView.clientEmailLabel')" required />
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium text-navy" for="send-message">{{ t('dashboardInvoicesClients.invoiceDetailView.messageLabel') }}</label>
            <textarea
              id="send-message"
              v-model="sendMessage"
              rows="3"
              class="rounded-lg border border-border bg-white px-3 py-2 text-sm text-navy focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
          </div>
          <div class="flex gap-3">
            <Button type="submit" :loading="sending">{{ t('dashboardInvoicesClients.invoiceDetailView.sendButton') }}</Button>
            <Button type="button" variant="ghost" @click="showSendForm = false">{{ t('dashboardInvoicesClients.invoiceDetailView.cancelButton') }}</Button>
          </div>
        </form>
      </Card>

      <div class="flex flex-wrap gap-3">
        <a :href="invoicePdfUrl(invoice.id)" target="_blank" rel="noopener">
          <Button variant="secondary">{{ t('dashboardInvoicesClients.invoiceDetailView.downloadPdfButton') }}</Button>
        </a>
        <RouterLink v-if="invoice.status === 'draft'" :to="{ name: 'invoice-edit', params: { id: invoice.id } }">
          <Button variant="secondary">{{ t('dashboardInvoicesClients.invoiceDetailView.editButton') }}</Button>
        </RouterLink>
        <Button
          v-if="canTransitionTo(invoice.status, 'issued')"
          :loading="actionLoading === 'issue'"
          @click="onIssue"
        >
          {{ t('dashboardInvoicesClients.invoiceDetailView.issueInvoiceButton') }}
        </Button>
        <Button v-if="invoice.status === 'issued'" :disabled="showSendForm" @click="openSendForm">
          {{ t('dashboardInvoicesClients.invoiceDetailView.sendInvoiceButton') }}
        </Button>
        <Button
          v-if="!isProfaktura && isPayable(invoice.status)"
          variant="secondary"
          :disabled="showPaymentForm"
          @click="openPaymentForm"
        >
          {{ t('dashboardInvoicesClients.invoiceDetailView.recordPaymentButton') }}
        </Button>
        <Button v-if="canConvert" :loading="actionLoading === 'convert'" @click="onConvert">
          {{ t('dashboardInvoicesClients.invoiceDetailView.convertButton') }}
        </Button>
        <Button variant="secondary" :loading="actionLoading === 'duplicate'" @click="onDuplicate">
          {{ t('dashboardInvoicesClients.invoiceDetailView.duplicateButton') }}
        </Button>
        <Button
          v-if="canTransitionTo(invoice.status, 'cancelled')"
          variant="danger"
          :loading="actionLoading === 'cancel'"
          @click="onCancel"
        >
          {{ t('dashboardInvoicesClients.invoiceDetailView.cancelInvoiceButton') }}
        </Button>
      </div>
    </template>
  </div>
</template>
