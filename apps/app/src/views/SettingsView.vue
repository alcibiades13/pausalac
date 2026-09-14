<script setup lang="ts">
import { ref, watch } from 'vue'
import { Button, Card, Input, Alert } from '@pausalac/ui'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { updateCompany } from '@/services/companies'
import { ApiError } from '@/lib/api'

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
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da sačuvamo podatke.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto flex max-w-2xl flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">Podešavanja</h1>

    <Card>
      <h2 class="mb-3 text-base font-semibold text-navy">Podaci o firmi</h2>
      <form class="flex flex-col gap-4" @submit.prevent="onSave">
        <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>
        <Alert v-if="saved" variant="success">Sačuvano.</Alert>
        <Input v-model="companyForm.pib" label="PIB" :disabled="saving" />
        <Input
          v-model="companyForm.bank_account"
          label="Račun za uplate"
          hint="Prikazuje se na fakturama kao podatak za plaćanje."
          :disabled="saving"
        />
        <div>
          <Button type="submit" :loading="saving">Sačuvaj</Button>
        </div>
      </form>
    </Card>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">Računovodstvena agencija</h2>
      <p class="mb-3 text-sm text-text-secondary">
        Vodiš računovodstvenu agenciju? Ovde možeš da je registruješ, dodaš zaposlene i povežeš
        se sa klijentima.
      </p>
      <RouterLink :to="{ name: 'accounting-organization' }">
        <Button variant="secondary">Otvori</Button>
      </RouterLink>
    </Card>
  </div>
</template>
