<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Card, Alert, EmptyState, Badge, Skeleton } from '@pausalac/ui'
import {
  listNotifications,
  markNotificationRead,
  type AppNotification,
  type NotificationPriority,
} from '@/services/notifications'
import { ApiError } from '@/lib/api'

const PRIORITY_VARIANTS: Record<NotificationPriority, 'danger' | 'warning' | 'info'> = {
  critical: 'danger',
  attention: 'warning',
  informational: 'info',
}
const PRIORITY_LABELS: Record<NotificationPriority, string> = {
  critical: 'Kritično',
  attention: 'Pažnja',
  informational: 'Informativno',
}

const notifications = ref<AppNotification[]>([])
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')

async function load() {
  status.value = 'loading'
  try {
    notifications.value = (await listNotifications()).results
    status.value = 'ready'
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo obaveštenja.'
    status.value = 'error'
  }
}

onMounted(load)

const markingReadId = ref<number | null>(null)
async function onMarkRead(notification: AppNotification) {
  markingReadId.value = notification.id
  try {
    const updated = await markNotificationRead(notification.id)
    const index = notifications.value.findIndex((n) => n.id === notification.id)
    if (index !== -1) notifications.value[index] = updated
  } finally {
    markingReadId.value = null
  }
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">Obaveštenja</h1>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="load">Pokušaj ponovo</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <Card v-else-if="notifications.length === 0">
      <EmptyState title="Nema obaveštenja." description="Ovde će se pojaviti stvari koje zahtevaju tvoju pažnju." />
    </Card>

    <div v-else class="flex flex-col gap-2">
      <Card
        v-for="notification in notifications"
        :key="notification.id"
        :class="!notification.read_at ? 'border-l-4 border-l-primary' : ''"
      >
        <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div class="flex flex-col gap-1">
            <div class="flex flex-wrap items-center gap-2">
              <Badge :variant="PRIORITY_VARIANTS[notification.priority]">
                {{ PRIORITY_LABELS[notification.priority] }}
              </Badge>
              <span :class="!notification.read_at ? 'font-semibold text-navy' : 'font-medium text-navy'">
                {{ notification.title }}
              </span>
              <span v-if="!notification.read_at" class="h-2 w-2 shrink-0 rounded-full bg-primary" aria-hidden="true" />
            </div>
            <p class="text-sm text-text-secondary">{{ notification.message }}</p>
            <RouterLink
              v-if="notification.action_route"
              :to="{ name: notification.action_route, query: notification.action_query }"
              class="text-sm text-primary hover:underline"
            >
              Pogledaj →
            </RouterLink>
          </div>
          <button
            v-if="!notification.read_at"
            type="button"
            class="self-start text-sm text-text-secondary hover:text-navy disabled:opacity-40"
            :disabled="markingReadId === notification.id"
            @click="onMarkRead(notification)"
          >
            Označi kao pročitano
          </button>
        </div>
      </Card>
    </div>
  </div>
</template>
