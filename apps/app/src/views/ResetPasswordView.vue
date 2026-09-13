<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, Card, Input, Alert } from '@pausalac/ui'
import AuthLayout from '@/components/AuthLayout.vue'
import { confirmPasswordReset } from '@/services/passwordReset'
import { ApiError } from '@/lib/api'

const route = useRoute()
const router = useRouter()

const uid = computed(() => String(route.query.uid ?? ''))
const token = computed(() => String(route.query.token ?? ''))
const hasValidLink = computed(() => Boolean(uid.value && token.value))

const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMessage = ref('')

const passwordsMatch = computed(() => newPassword.value === confirmPassword.value)

async function onSubmit() {
  if (!passwordsMatch.value) {
    errorMessage.value = 'Lozinke se ne poklapaju.'
    return
  }
  loading.value = true
  errorMessage.value = ''
  try {
    await confirmPasswordReset({ uid: uid.value, token: token.value, new_password: newPassword.value })
    await router.push({ name: 'login', query: { reset: 'success' } })
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da promenimo lozinku. Pokušaj ponovo.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout title="Nova lozinka">
    <Card>
      <Alert v-if="!hasValidLink" variant="danger">
        Ovaj link nije validan. Zatraži novi link za resetovanje lozinke.
      </Alert>
      <form v-else class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>
        <Input
          v-model="newPassword"
          type="password"
          label="Nova lozinka"
          autocomplete="new-password"
          hint="Najmanje 8 karaktera."
          required
          :disabled="loading"
        />
        <Input
          v-model="confirmPassword"
          type="password"
          label="Ponovi novu lozinku"
          autocomplete="new-password"
          required
          :disabled="loading"
        />
        <Button type="submit" :loading="loading">Postavi novu lozinku</Button>
      </form>
    </Card>
  </AuthLayout>
</template>
