<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, Alert, Badge, Button, EmptyState, Skeleton } from '@pausalac/ui'
import {
  listClientConnections,
  acceptConnection,
  declineConnection,
  revokeConnection,
  type ClientConnection,
} from '@/services/accounting'
import { ApiError } from '@/lib/api'

const { t } = useI18n()

const STATUS_LABELS = computed<Record<ClientConnection['status'], string>>(() => ({
  pending: t('limitsAccountingEtc.accountingView.statusPending'),
  active: t('limitsAccountingEtc.accountingView.statusActive'),
  declined: t('limitsAccountingEtc.accountingView.statusDeclined'),
  revoked: t('limitsAccountingEtc.accountingView.statusRevoked'),
}))
const STATUS_VARIANTS: Record<ClientConnection['status'], 'neutral' | 'success' | 'danger'> = {
  pending: 'neutral',
  active: 'success',
  declined: 'danger',
  revoked: 'danger',
}
const ROLE_LABELS = computed<Record<ClientConnection['granted_role'], string>>(() => ({
  accountant: t('limitsAccountingEtc.accountingView.roleAccountant'),
  accountant_admin: t('limitsAccountingEtc.accountingView.roleAccountantAdmin'),
}))

const connections = ref<ClientConnection[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')

async function load() {
  status.value = 'loading'
  try {
    connections.value = (await listClientConnections()).results
    status.value = 'ready'
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : t('limitsAccountingEtc.accountingView.loadError')
    status.value = 'error'
  }
}

onMounted(load)

const actingId = ref<number | null>(null)

async function onAccept(id: number) {
  actingId.value = id
  try {
    await acceptConnection(id)
    await load()
  } finally {
    actingId.value = null
  }
}

async function onDecline(id: number) {
  actingId.value = id
  try {
    await declineConnection(id)
    await load()
  } finally {
    actingId.value = null
  }
}

async function onRevoke(id: number) {
  actingId.value = id
  try {
    await revokeConnection(id)
    await load()
  } finally {
    actingId.value = null
  }
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('limitsAccountingEtc.accountingView.title') }}</h1>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">{{ t('limitsAccountingEtc.accountingView.retryButton') }}</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <Card v-else-if="connections.length === 0">
      <EmptyState
        :title="t('limitsAccountingEtc.accountingView.emptyTitle')"
        :description="t('limitsAccountingEtc.accountingView.emptyDescription')"
      />
    </Card>

    <div v-else class="flex flex-col gap-3">
      <Card v-for="connection in connections" :key="connection.id" class="flex flex-col gap-3">
        <div class="flex items-center justify-between gap-3">
          <div>
            <p class="font-medium text-navy">{{ connection.organization_name }}</p>
            <p class="text-sm text-text-secondary">{{ ROLE_LABELS[connection.granted_role] }}</p>
          </div>
          <Badge :variant="STATUS_VARIANTS[connection.status]">
            {{ STATUS_LABELS[connection.status] }}
          </Badge>
        </div>

        <div v-if="connection.status === 'pending'" class="flex gap-2">
          <Button :loading="actingId === connection.id" @click="onAccept(connection.id)">
            {{ t('limitsAccountingEtc.accountingView.acceptButton') }}
          </Button>
          <Button
            variant="ghost"
            :loading="actingId === connection.id"
            @click="onDecline(connection.id)"
          >
            {{ t('limitsAccountingEtc.accountingView.declineButton') }}
          </Button>
        </div>
        <div v-else-if="connection.status === 'active'">
          <button
            type="button"
            class="text-sm text-danger hover:underline disabled:opacity-40"
            :disabled="actingId === connection.id"
            @click="onRevoke(connection.id)"
          >
            {{ t('limitsAccountingEtc.accountingView.revokeButton') }}
          </button>
        </div>
      </Card>
    </div>
  </div>
</template>
