<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Alert } from '@pausalac/ui'
import AuthLayout from '@/components/AuthLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/lib/api'

const { t } = useI18n()
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
      error instanceof ApiError ? error.message : t('authShell.loginView.genericError')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout :title="t('authShell.loginView.title')">
    <Card>
      <form class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>
        <Input
          v-model="email"
          type="email"
          :label="t('authShell.loginView.emailLabel')"
          autocomplete="email"
          required
          :disabled="loading"
        />
        <Input
          v-model="password"
          type="password"
          :label="t('authShell.loginView.passwordLabel')"
          autocomplete="current-password"
          required
          :disabled="loading"
        />
        <Button type="submit" :loading="loading">{{ t('authShell.loginView.submitButton') }}</Button>
      </form>
      <div class="mt-4 flex flex-col gap-1 text-center text-sm text-text-secondary">
        <RouterLink :to="{ name: 'forgot-password' }" class="text-primary-dark underline">
          {{ t('authShell.loginView.forgotPasswordLink') }}
        </RouterLink>
        <span>
          {{ t('authShell.loginView.noAccountText') }}
          <RouterLink :to="{ name: 'register' }" class="text-primary-dark underline">
            {{ t('authShell.loginView.registerLink') }}
          </RouterLink>
        </span>
      </div>
    </Card>
  </AuthLayout>
</template>
