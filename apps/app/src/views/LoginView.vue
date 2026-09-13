<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, Card, Input, Alert } from '@pausalac/ui'
import AuthLayout from '@/components/AuthLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/lib/api'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function onSubmit() {
  loading.value = true
  errorMessage.value = ''
  try {
    await auth.login({ email: email.value, password: password.value })
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : undefined
    await router.push(redirect ?? { name: 'home' })
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da te prijavimo. Pokušaj ponovo.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout title="Prijava">
    <Card>
      <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>
        <Input
          v-model="email"
          type="email"
          label="Email adresa"
          autocomplete="email"
          required
          :disabled="loading"
        />
        <Input
          v-model="password"
          type="password"
          label="Lozinka"
          autocomplete="current-password"
          required
          :disabled="loading"
        />
        <Button type="submit" :loading="loading">Prijavi se</Button>
      </form>
      <div class="mt-4 flex flex-col gap-1 text-center text-sm text-text-secondary">
        <RouterLink :to="{ name: 'forgot-password' }" class="text-primary hover:underline">
          Zaboravio/la si lozinku?
        </RouterLink>
        <span>
          Nemaš nalog?
          <RouterLink :to="{ name: 'register' }" class="text-primary hover:underline">
            Registruj se
          </RouterLink>
        </span>
      </div>
    </Card>
  </AuthLayout>
</template>
