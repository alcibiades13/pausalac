<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Card, Alert } from '@pausalac/ui'
import AuthLayout from '@/components/AuthLayout.vue'
import { verifyEmail } from '@/services/passwordReset'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/lib/api'

const route = useRoute()
const auth = useAuthStore()

type State = 'verifying' | 'success' | 'error'
const state = ref<State>('verifying')
const errorMessage = ref('')

onMounted(async () => {
  const token = typeof route.query.token === 'string' ? route.query.token : ''
  if (!token) {
    state.value = 'error'
    errorMessage.value = 'Link za potvrdu nije validan.'
    return
  }
  try {
    await verifyEmail(token)
    state.value = 'success'
    // Reflect the now-verified state if the user is already logged in
    // (the common case — registration logs the user in immediately).
    if (auth.isAuthenticated) {
      await auth.refreshMe()
    }
  } catch (error) {
    state.value = 'error'
    errorMessage.value = error instanceof ApiError ? error.message : 'Link za potvrdu nije validan.'
  }
})
</script>

<template>
  <AuthLayout title="Potvrda email adrese">
    <Card>
      <Alert v-if="state === 'verifying'" variant="info">Proveravamo tvoj link...</Alert>
      <Alert v-else-if="state === 'success'" variant="success">
        Email adresa je uspešno potvrđena.
      </Alert>
      <Alert v-else variant="danger">{{ errorMessage }}</Alert>
      <p class="mt-4 text-center text-sm">
        <RouterLink
          :to="auth.isAuthenticated ? { name: 'home' } : { name: 'login' }"
          class="text-primary hover:underline"
        >
          {{ auth.isAuthenticated ? 'Nastavi na početnu' : 'Idi na prijavu' }}
        </RouterLink>
      </p>
    </Card>
  </AuthLayout>
</template>
