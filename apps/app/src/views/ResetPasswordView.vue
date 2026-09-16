<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Button, Card, Input, Alert } from '@pausalac/ui'
import AuthLayout from '@/components/AuthLayout.vue'
import { confirmPasswordReset } from '@/services/passwordReset'
import { ApiError } from '@/lib/api'

const { t } = useI18n()
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
    errorMessage.value = t('authShell.resetPasswordView.passwordMismatchError')
    return
  }
  loading.value = true
  errorMessage.value = ''
  try {
    await confirmPasswordReset({ uid: uid.value, token: token.value, new_password: newPassword.value })
    await router.push({ name: 'login', query: { reset: 'success' } })
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('authShell.resetPasswordView.genericError')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout :title="t('authShell.resetPasswordView.title')">
    <Card>
      <Alert v-if="!hasValidLink" variant="danger">
        {{ t('authShell.resetPasswordView.invalidLinkMessage') }}
      </Alert>
      <form v-else class="flex flex-col gap-4" @submit.prevent="onSubmit">
        <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>
        <Input
          v-model="newPassword"
          type="password"
          :label="t('authShell.resetPasswordView.newPasswordLabel')"
          autocomplete="new-password"
          :hint="t('authShell.resetPasswordView.passwordHint')"
          required
          :disabled="loading"
        />
        <Input
          v-model="confirmPassword"
          type="password"
          :label="t('authShell.resetPasswordView.confirmPasswordLabel')"
          autocomplete="new-password"
          required
          :disabled="loading"
        />
        <Button type="submit" :loading="loading">{{ t('authShell.resetPasswordView.submitButton') }}</Button>
      </form>
    </Card>
  </AuthLayout>
</template>
