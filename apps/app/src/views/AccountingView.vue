<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Card, Alert, Badge, Button, EmptyState, Skeleton } from '@pausalac/ui'
import {
  listClientConnections,
  acceptConnection,
  declineConnection,
  revokeConnection,
  type ClientConnection,
} from '@/services/accounting'
import { ApiError } from '@/lib/api'

const STATUS_LABELS: Record<ClientConnection['status'], string> = {
  pending: 'Na čekanju',
  active: 'Aktivna',
  declined: 'Odbijena',
  revoked: 'Opozvana',
}
const STATUS_VARIANTS: Record<ClientConnection['status'], 'neutral' | 'success' | 'danger'> = {
  pending: 'neutral',
  active: 'success',
  declined: 'danger',
  revoked: 'danger',
}
const ROLE_LABELS: Record<ClientConnection['granted_role'], string> = {
  accountant: 'Računovođa',
  accountant_admin: 'Računovođa (admin)',
}

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
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo podatke.'
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
  <div class="mx-auto flex max-w-2xl flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">Moj računovođa</h1>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">Pokušaj ponovo</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <Card v-else-if="connections.length === 0">
      <EmptyState
        title="Još nema povezane računovodstvene agencije."
        description="Kada te agencija pozove, zahtev će se pojaviti ovde."
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
            Prihvati
          </Button>
          <Button
            variant="ghost"
            :loading="actingId === connection.id"
            @click="onDecline(connection.id)"
          >
            Odbij
          </Button>
        </div>
        <div v-else-if="connection.status === 'active'">
          <button
            type="button"
            class="text-sm text-danger hover:underline disabled:opacity-40"
            :disabled="actingId === connection.id"
            @click="onRevoke(connection.id)"
          >
            Opozovi pristup
          </button>
        </div>
      </Card>
    </div>
  </div>
</template>
