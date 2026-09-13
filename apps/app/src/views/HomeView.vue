<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Card, Input, Alert } from '@pausalac/ui'
import { useAuthStore } from '@/stores/auth'
import { createCompany } from '@/services/companies'
import { ApiError } from '@/lib/api'

const auth = useAuthStore()
const router = useRouter()

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

async function onLogout() {
  await auth.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <div class="min-h-screen bg-background px-4 py-12">
    <div class="mx-auto flex w-full max-w-lg flex-col gap-6">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-semibold text-navy">
          Zdravo, {{ auth.user?.first_name || auth.user?.email }}.
        </h1>
        <Button variant="ghost" @click="onLogout">Odjavi se</Button>
      </div>

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
          Još nemaš kompaniju u sistemu. Unesi naziv da počneš — ostatak podešavanja (PIB, banka,
          delatnost) dolazi u sledećem koraku.
        </p>
        <form class="flex flex-col gap-4" @submit.prevent="onCreateCompany">
          <Alert v-if="createCompanyError" variant="danger">{{ createCompanyError }}</Alert>
          <Input v-model="companyName" label="Naziv kompanije" required :disabled="creatingCompany" />
          <Button type="submit" :loading="creatingCompany">Napravi kompaniju</Button>
        </form>
      </Card>

      <Card v-else>
        <h2 class="mb-3 text-base font-semibold text-navy">Tvoje kompanije</h2>
        <ul class="flex flex-col divide-y divide-border">
          <li
            v-for="membership in auth.user?.memberships"
            :key="membership.company.id"
            class="flex items-center justify-between py-2 text-sm"
          >
            <span class="text-navy">{{ membership.company.name }}</span>
            <span class="text-text-secondary">{{ membership.role }}</span>
          </li>
        </ul>
      </Card>
    </div>
  </div>
</template>
