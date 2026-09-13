<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { Button, Card, Input, Alert } from '@pausalac/ui'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { createCompany, updateCompany, getOnboardingStatus, type OnboardingStatus } from '@/services/companies'
import { ApiError } from '@/lib/api'

const auth = useAuthStore()
const company = useCompanyStore()

const resending = ref(false)
const resent = ref(false)

async function onResendVerification() {
  resending.value = true
  try {
    await auth.resendVerificationEmail()
    resent.value = true
  } finally {
    resending.value = false
  }
}

// --- zero-company bridge (create-company form) ------------------------

const companyName = ref('')
const creatingCompany = ref(false)
const createCompanyError = ref('')

async function onCreateCompany() {
  creatingCompany.value = true
  createCompanyError.value = ''
  try {
    await createCompany(companyName.value)
    await auth.refreshMe()
  } catch (error) {
    createCompanyError.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da napravimo kompaniju. Pokušaj ponovo.'
  } finally {
    creatingCompany.value = false
  }
}

// --- onboarding status + company info form -----------------------------

const onboarding = ref<OnboardingStatus | null>(null)

const ONBOARDING_LABELS: Record<string, string> = {
  company: 'Osnovni podaci o firmi (PIB)',
  bank: 'Račun za uplate',
  client: 'Prvi klijent',
  sef: 'SEF povezivanje',
  tax_document: 'Poresko rešenje',
}

async function loadOnboarding() {
  if (!company.currentCompanyId) return
  onboarding.value = await getOnboardingStatus(company.currentCompanyId)
}

const companyForm = ref({ pib: '', bank_account: '' })
const savingCompanyInfo = ref(false)
const companyInfoError = ref('')
const companyInfoSaved = ref(false)

watch(
  () => company.currentCompany,
  (c) => {
    if (c) {
      companyForm.value = { pib: c.pib ?? '', bank_account: c.bank_account }
    }
  },
  { immediate: true },
)

async function onSaveCompanyInfo() {
  if (!company.currentCompanyId) return
  savingCompanyInfo.value = true
  companyInfoError.value = ''
  companyInfoSaved.value = false
  try {
    await updateCompany(company.currentCompanyId, companyForm.value)
    await auth.refreshMe()
    await loadOnboarding()
    companyInfoSaved.value = true
  } catch (error) {
    companyInfoError.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da sačuvamo podatke.'
  } finally {
    savingCompanyInfo.value = false
  }
}

const missingLabels = computed(
  () => onboarding.value?.missing.map((key) => ONBOARDING_LABELS[key] ?? key) ?? [],
)

onMounted(loadOnboarding)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">
      Zdravo, {{ auth.user?.first_name || auth.user?.email }}.
    </h1>

    <Alert v-if="auth.user && !auth.user.is_email_verified" variant="warning">
      <div class="flex items-center justify-between gap-4">
        <span>Potvrdi svoju email adresu — poslali smo ti link kada si se registrovao/la.</span>
        <Button variant="secondary" :loading="resending" :disabled="resent" @click="onResendVerification">
          {{ resent ? 'Poslato' : 'Pošalji ponovo' }}
        </Button>
      </div>
    </Alert>

    <Card v-if="!auth.user?.memberships.length">
      <h2 class="mb-1 text-base font-semibold text-navy">Podesi svoju kompaniju</h2>
      <p class="mb-4 text-sm text-text-secondary">
        Još nemaš kompaniju u sistemu. Unesi naziv da počneš — ostatak podešavanja (PIB, banka)
        dolazi odmah ispod.
      </p>
      <form class="flex flex-col gap-4" @submit.prevent="onCreateCompany">
        <Alert v-if="createCompanyError" variant="danger">{{ createCompanyError }}</Alert>
        <Input v-model="companyName" label="Naziv kompanije" required :disabled="creatingCompany" />
        <Button type="submit" :loading="creatingCompany">Napravi kompaniju</Button>
      </form>
    </Card>

    <template v-else>
      <Card v-if="onboarding">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-base font-semibold text-navy">Tvoj nalog je {{ onboarding.percentage }}% podešen</h2>
        </div>
        <div class="mb-4 h-2 w-full overflow-hidden rounded-full bg-background">
          <div class="h-full bg-primary" :style="{ width: `${onboarding.percentage}%` }" />
        </div>
        <p v-if="missingLabels.length" class="text-sm text-text-secondary">
          Još nedostaje: {{ missingLabels.join(', ') }}.
        </p>
        <p v-else class="text-sm text-success">Sve je podešeno.</p>
        <p v-if="onboarding.missing.includes('client')" class="mt-3 text-sm">
          <RouterLink :to="{ name: 'client-new' }" class="text-primary hover:underline">
            Dodaj prvog klijenta →
          </RouterLink>
        </p>
      </Card>

      <Card>
        <h2 class="mb-3 text-base font-semibold text-navy">Podaci o firmi</h2>
        <form class="flex flex-col gap-4" @submit.prevent="onSaveCompanyInfo">
          <Alert v-if="companyInfoError" variant="danger">{{ companyInfoError }}</Alert>
          <Alert v-if="companyInfoSaved" variant="success">Sačuvano.</Alert>
          <Input v-model="companyForm.pib" label="PIB" :disabled="savingCompanyInfo" />
          <Input
            v-model="companyForm.bank_account"
            label="Račun za uplate"
            hint="Koristi se kasnije za podatke o plaćanju na fakturama."
            :disabled="savingCompanyInfo"
          />
          <div>
            <Button type="submit" :loading="savingCompanyInfo">Sačuvaj</Button>
          </div>
        </form>
      </Card>
    </template>
  </div>
</template>
