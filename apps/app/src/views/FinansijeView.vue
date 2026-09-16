<script setup lang="ts">
/**
 * "Finansije" is named as a nav destination in both the mobile and desktop
 * nav lists (master prompt §7, blueprint §5) but neither document ever
 * describes what the page contains — no such page existed anywhere in the
 * app before Phase 6d. Resolved as a small hub linking to the three
 * existing pages that are genuinely "finance" in nature, rather than
 * aliasing the tab to one of them (which would misrepresent what's there).
 */
import { useI18n } from 'vue-i18n'
import { Button, Card } from '@pausalac/ui'

const { t } = useI18n()
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">{{ t('dashboardInvoicesClients.finansijeView.title') }}</h1>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.finansijeView.limitsTitle') }}</h2>
      <p class="mb-3 text-sm text-text-secondary">
        {{ t('dashboardInvoicesClients.finansijeView.limitsDescription') }}
      </p>
      <RouterLink :to="{ name: 'limits' }">
        <Button variant="secondary">{{ t('dashboardInvoicesClients.finansijeView.openButton') }}</Button>
      </RouterLink>
    </Card>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.finansijeView.kpoTitle') }}</h2>
      <p class="mb-3 text-sm text-text-secondary">
        {{ t('dashboardInvoicesClients.finansijeView.kpoDescription') }}
      </p>
      <RouterLink :to="{ name: 'kpo' }">
        <Button variant="secondary">{{ t('dashboardInvoicesClients.finansijeView.openButton') }}</Button>
      </RouterLink>
    </Card>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">{{ t('dashboardInvoicesClients.finansijeView.obligationsTitle') }}</h2>
      <p class="mb-3 text-sm text-text-secondary">
        {{ t('dashboardInvoicesClients.finansijeView.obligationsDescription') }}
      </p>
      <RouterLink :to="{ name: 'obligations' }">
        <Button variant="secondary">{{ t('dashboardInvoicesClients.finansijeView.openButton') }}</Button>
      </RouterLink>
    </Card>
  </div>
</template>
