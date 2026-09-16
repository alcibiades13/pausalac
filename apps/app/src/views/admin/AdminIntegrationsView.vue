<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Alert, Badge, Card, Skeleton } from '@pausalac/ui'
import { getAdminIntegrationsStatus, type AdminIntegrationsStatus } from '@/services/admin'
import { ApiError } from '@/lib/api'

const { t } = useI18n()

const status = ref<AdminIntegrationsStatus | null>(null)
const loading = ref(true)
const errorMessage = ref('')

async function load() {
  loading.value = true
  errorMessage.value = ''
  try {
    status.value = await getAdminIntegrationsStatus()
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('admin.adminIntegrationsView.loadError')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('admin.adminIntegrationsView.title') }}</h1>
    <p class="text-sm text-text-secondary">
      {{ t('admin.adminIntegrationsView.description') }}
    </p>

    <Alert v-if="errorMessage" variant="danger">{{ errorMessage }}</Alert>

    <Card v-if="loading">
      <Skeleton :count="4" />
    </Card>

    <Card v-else-if="status">
      <ul class="flex flex-col divide-y divide-border">
        <li class="flex items-center justify-between py-3">
          <span class="text-sm text-navy">{{ t('admin.adminIntegrationsView.sentryLabel') }}</span>
          <Badge :variant="status.sentry.configured ? 'success' : 'neutral'">
            {{ status.sentry.configured ? t('admin.adminIntegrationsView.configuredBadge') : t('admin.adminIntegrationsView.notConfiguredBadge') }}
          </Badge>
        </li>
        <li class="flex items-center justify-between py-3">
          <span class="text-sm text-navy">{{ t('admin.adminIntegrationsView.storageLabel') }}</span>
          <Badge :variant="status.storage.configured ? 'success' : 'danger'">
            {{ status.storage.configured ? t('admin.adminIntegrationsView.availableBadge') : t('admin.adminIntegrationsView.unavailableBadge') }}
          </Badge>
        </li>
        <li class="flex items-center justify-between py-3">
          <span class="text-sm text-navy">{{ t('admin.adminIntegrationsView.emailServerLabel') }}</span>
          <Badge :variant="status.email.configured ? 'success' : 'neutral'">
            {{ status.email.configured ? t('admin.adminIntegrationsView.configuredBadge') : t('admin.adminIntegrationsView.notConfiguredBadge') }}
          </Badge>
        </li>
        <li class="flex flex-col gap-1 py-3">
          <div class="flex items-center justify-between">
            <span class="text-sm text-navy">{{ t('admin.adminIntegrationsView.sefLabel') }}</span>
            <Badge variant="neutral">{{ t('admin.adminIntegrationsView.notConfiguredBadge') }}</Badge>
          </div>
          <p class="text-xs text-text-secondary">{{ status.sef.note }}</p>
        </li>
      </ul>
    </Card>
  </div>
</template>
