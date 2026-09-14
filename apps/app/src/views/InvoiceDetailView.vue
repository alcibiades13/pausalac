<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Button, Card, Alert, Input, MoneyDisplay } from '@pausalac/ui'
import {
  getInvoice,
  issueInvoice,
  cancelInvoice,
  sendInvoice,
  invoicePdfUrl,
  type Invoice,
} from '@/services/invoices'
import { canTransitionTo } from '@/lib/invoiceStatus'
import { ApiError } from '@/lib/api'
import InvoiceStatusBadge from '@/components/InvoiceStatusBadge.vue'

const props = defineProps<{ id: string }>()

const invoice = ref<Invoice | null>(null)
const loadStatus = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')
const actionLoading = ref<'issue' | 'cancel' | null>(null)

async function load() {
  loadStatus.value = 'loading'
  try {
    invoice.value = await getInvoice(props.id)
    loadStatus.value = 'ready'
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo fakturu.'
    loadStatus.value = 'error'
  }
}

async function onIssue() {
  actionLoading.value = 'issue'
  errorMessage.value = ''
  try {
    invoice.value = await issueInvoice(props.id)
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : 'Faktura nije mogla da se izda.'
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
    errorMessage.value = error instanceof ApiError ? error.message : 'Faktura nije mogla da se stornira.'
  } finally {
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
    sendConfirmation.value = 'Faktura se šalje — status će se ažurirati za par trenutaka.'
    showSendForm.value = false
    // The status flips to "sent" only once the email actually goes out
    // (apps/invoices/tasks.py) — refetch shortly after instead of
    // assuming success immediately.
    setTimeout(load, 1500)
  } catch (error) {
    sendError.value =
      error instanceof ApiError ? error.message : 'Faktura nije mogla da se pošalje.'
  } finally {
    sending.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="mx-auto flex max-w-2xl flex-col gap-6">
    <Alert v-if="loadStatus === 'error'" variant="danger">{{ errorMessage }}</Alert>

    <Card v-else-if="loadStatus === 'loading'">
      <p class="text-sm text-text-secondary">Učitavanje...</p>
    </Card>

    <template v-else-if="invoice">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-semibold text-navy">
            {{ invoice.invoice_number ?? `Nacrt #${invoice.id}` }}
          </h1>
          <p class="text-sm text-text-secondary">{{ invoice.client_name }}</p>
        </div>
        <InvoiceStatusBadge :status="invoice.status" />
      </div>

      <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

      <Card>
        <dl class="grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
          <div>
            <dt class="text-text-secondary">Datum izdavanja</dt>
            <dd class="text-navy">{{ invoice.issue_date }}</dd>
          </div>
          <div>
            <dt class="text-text-secondary">Rok plaćanja</dt>
            <dd class="text-navy">{{ invoice.due_date }}</dd>
          </div>
          <div>
            <dt class="text-text-secondary">Datum prometa</dt>
            <dd class="text-navy">{{ invoice.service_date }}</dd>
          </div>
        </dl>
      </Card>

      <Card>
        <h2 class="mb-3 text-base font-semibold text-navy">Stavke</h2>
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
        <h2 class="mb-1 text-base font-semibold text-navy">Napomene</h2>
        <p class="text-sm text-text-secondary">{{ invoice.notes }}</p>
      </Card>

      <Alert v-if="sendConfirmation" variant="success">{{ sendConfirmation }}</Alert>

      <Card v-if="showSendForm">
        <h2 class="mb-3 text-base font-semibold text-navy">Pošalji fakturu</h2>
        <form class="flex flex-col gap-4" @submit.prevent="onSend">
          <Alert v-if="sendError" variant="danger">{{ sendError }}</Alert>
          <Input v-model="recipientEmail" type="email" label="Email klijenta" required />
          <div class="flex flex-col gap-1">
            <label class="text-sm font-medium text-navy" for="send-message">Poruka (opciono)</label>
            <textarea
              id="send-message"
              v-model="sendMessage"
              rows="3"
              class="rounded-lg border border-border bg-white px-3 py-2 text-sm text-navy focus:outline-none focus:ring-2 focus:ring-primary/40"
            />
          </div>
          <div class="flex gap-3">
            <Button type="submit" :loading="sending">Pošalji</Button>
            <Button type="button" variant="ghost" @click="showSendForm = false">Otkaži</Button>
          </div>
        </form>
      </Card>

      <div class="flex flex-wrap gap-3">
        <a :href="invoicePdfUrl(invoice.id)" target="_blank" rel="noopener">
          <Button variant="secondary">Preuzmi PDF</Button>
        </a>
        <RouterLink v-if="invoice.status === 'draft'" :to="{ name: 'invoice-edit', params: { id: invoice.id } }">
          <Button variant="secondary">Izmeni</Button>
        </RouterLink>
        <Button
          v-if="canTransitionTo(invoice.status, 'issued')"
          :loading="actionLoading === 'issue'"
          @click="onIssue"
        >
          Izdaj fakturu
        </Button>
        <Button v-if="invoice.status === 'issued'" :disabled="showSendForm" @click="openSendForm">
          Pošalji fakturu
        </Button>
        <Button
          v-if="canTransitionTo(invoice.status, 'cancelled')"
          variant="danger"
          :loading="actionLoading === 'cancel'"
          @click="onCancel"
        >
          Storniraj
        </Button>
      </div>
    </template>
  </div>
</template>
