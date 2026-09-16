<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Alert } from '@pausalac/ui'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { updateCompany } from '@/services/companies'
import { ApiError } from '@/lib/api'

const { t } = useI18n()
const auth = useAuthStore()
const company = useCompanyStore()

const companyForm = ref({ pib: '', bank_account: '' })
const saving = ref(false)
const errorMessage = ref('')
const saved = ref(false)

watch(
  () => company.currentCompany,
  (c) => {
    if (c) {
      companyForm.value = { pib: c.pib ?? '', bank_account: c.bank_account }
    }
  },
  { immediate: true },
)

async function onSave() {
  if (!company.currentCompanyId) return
  saving.value = true
  errorMessage.value = ''
  saved.value = false
  try {
    await updateCompany(company.currentCompanyId, companyForm.value)
    await auth.refreshMe()
    saved.value = true
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('dashboardInvoicesClients.settingsView.saveError')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('dashboardInvoicesClients.settingsView.title') }}</h1>

    <Card>
      <h2 class="mb-3 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.settingsView.companyInfoTitle') }}</h2>
      <form class="flex flex-col gap-4" @submit.prevent="onSave">
        <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>
        <Alert v-if="saved" variant="success">{{ t('dashboardInvoicesClients.settingsView.saved') }}</Alert>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input v-model="companyForm.pib" :label="t('dashboardInvoicesClients.settingsView.pibLabel')" :disabled="saving" />
          <Input
            v-model="companyForm.bank_account"
            :label="t('dashboardInvoicesClients.settingsView.bankAccountLabel')"
            :hint="t('dashboardInvoicesClients.settingsView.bankAccountHint')"
            :disabled="saving"
          />
        </div>
        <div>
          <Button type="submit" :loading="saving">{{ t('dashboardInvoicesClients.settingsView.saveButton') }}</Button>
        </div>
      </form>
    </Card>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.settingsView.subscriptionTitle') }}</h2>
      <p class="mb-3 text-sm text-text-secondary">
        {{ t('dashboardInvoicesClients.settingsView.subscriptionDescription') }}
      </p>
      <RouterLink :to="{ name: 'subscription' }">
        <Button variant="secondary">{{ t('dashboardInvoicesClients.settingsView.openButton') }}</Button>
      </RouterLink>
    </Card>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.settingsView.accountingTitle') }}</h2>
      <p class="mb-3 text-sm text-text-secondary">
        {{ t('dashboardInvoicesClients.settingsView.accountingDescription') }}
      </p>
      <RouterLink :to="{ name: 'accounting-organization' }">
        <Button variant="secondary">{{ t('dashboardInvoicesClients.settingsView.openButton') }}</Button>
      </RouterLink>
    </Card>

    <Card v-if="auth.user?.is_staff">
      <h2 class="mb-1 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.settingsView.adminTitle') }}</h2>
      <p class="mb-3 text-sm text-text-secondary">
        {{ t('dashboardInvoicesClients.settingsView.adminDescription') }}
      </p>
      <RouterLink :to="{ name: 'admin-users' }">
        <Button variant="secondary">{{ t('dashboardInvoicesClients.settingsView.openButton') }}</Button>
      </RouterLink>
    </Card>
  </div>
</template>
