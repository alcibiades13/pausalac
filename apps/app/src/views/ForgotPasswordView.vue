<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Alert } from '@pausalac/ui'
import AuthLayout from '@/components/AuthLayout.vue'
import { requestPasswordReset } from '@/services/passwordReset'

const { t } = useI18n()
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
  <AuthLayout :title="t('authShell.forgotPasswordView.title')">
    <Card>
      <Alert v-if="submitted" variant="success">
        {{ t('authShell.forgotPasswordView.successMessage') }}
      </Alert>
      <form v-else class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <p class="text-sm text-text-secondary">
          {{ t('authShell.forgotPasswordView.instructions') }}
        </p>
        <Input
          v-model="email"
          type="email"
          :label="t('authShell.forgotPasswordView.emailLabel')"
          autocomplete="email"
          required
          :disabled="loading"
        />
        <Button type="submit" :loading="loading">{{ t('authShell.forgotPasswordView.submitButton') }}</Button>
      </form>
      <p class="mt-4 text-center text-sm text-text-secondary">
        <RouterLink :to="{ name: 'login' }" class="text-primary-dark underline">{{ t('authShell.forgotPasswordView.backToLoginLink') }}</RouterLink>
      </p>
    </Card>
  </AuthLayout>
</template>
