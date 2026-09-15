<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Card, Input, Alert } from '@pausalac/ui'
import AuthLayout from '@/components/AuthLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/lib/api'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const firstName = ref('')
const lastName = ref('')
const loading = ref(false)
const errorMessage = ref('')
const fieldErrors = ref<Record<string, string>>({})

async function onSubmit() {
  loading.value = true
  errorMessage.value = ''
  fieldErrors.value = {}
  try {
    await auth.register({
      email: email.value,
      password: password.value,
      first_name: firstName.value,
      last_name: lastName.value,
    })
    await router.push({ name: 'home' })
  } catch (error) {
    if (error instanceof ApiError) {
      errorMessage.value = error.fields ? '' : error.message
      fieldErrors.value = {
        email: error.fieldError('email') ?? '',
        password: error.fieldError('password') ?? '',
      }
    } else {
      errorMessage.value = 'Ne možemo trenutno da napravimo nalog. Pokušaj ponovo.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout title="Napravi nalog">
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
          :error="fieldErrors.email"
        />
        <Input
          v-model="password"
          type="password"
          label="Lozinka"
          autocomplete="new-password"
          hint="Najmanje 8 karaktera."
          required
          :disabled="loading"
          :error="fieldErrors.password"
        />
        <div class="grid grid-cols-2 gap-4">
          <Input v-model="firstName" label="Ime" autocomplete="given-name" :disabled="loading" />
          <Input v-model="lastName" label="Prezime" autocomplete="family-name" :disabled="loading" />
        </div>
        <Button type="submit" :loading="loading">Napravi nalog</Button>
      </form>
      <p class="mt-4 text-center text-sm text-text-secondary">
        Već imaš nalog?
        <RouterLink :to="{ name: 'login' }" class="text-primary underline">Prijavi se</RouterLink>
      </p>
    </Card>
  </AuthLayout>
</template>
