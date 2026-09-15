<script setup lang="ts">
import { ref } from 'vue'
import { Button, Card, Input, Alert } from '@pausalac/ui'
import AuthLayout from '@/components/AuthLayout.vue'
import { requestPasswordReset } from '@/services/passwordReset'

const email = ref('')
const loading = ref(false)
const submitted = ref(false)

async function onSubmit() {
  loading.value = true
  try {
    await requestPasswordReset(email.value)
  } finally {
    // Always show the same result, whether or not the address is
    // registered — the backend itself never reveals that (accounts/views.py
    // PasswordResetRequestView), so the UI must not either.
    loading.value = false
    submitted.value = true
  }
}
</script>

<template>
  <AuthLayout title="Zaboravljena lozinka">
    <Card>
      <Alert v-if="submitted" variant="success">
        Ako nalog sa ovom email adresom postoji, poslali smo link za resetovanje lozinke.
      </Alert>
      <form v-else class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <p class="text-sm text-text-secondary">
          Unesi email adresu i poslaćemo ti link za postavljanje nove lozinke.
        </p>
        <Input
          v-model="email"
          type="email"
          label="Email adresa"
          autocomplete="email"
          required
          :disabled="loading"
        />
        <Button type="submit" :loading="loading">Pošalji link</Button>
      </form>
      <p class="mt-4 text-center text-sm text-text-secondary">
        <RouterLink :to="{ name: 'login' }" class="text-primary underline">Nazad na prijavu</RouterLink>
      </p>
    </Card>
  </AuthLayout>
</template>
