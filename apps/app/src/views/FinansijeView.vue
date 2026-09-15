<script setup lang="ts">
/**
 * "Finansije" is named as a nav destination in both the mobile and desktop
 * nav lists (master prompt §7, blueprint §5) but neither document ever
 * describes what the page contains — no such page existed anywhere in the
 * app before Phase 6d. Resolved as a small hub linking to the three
 * existing pages that are genuinely "finance" in nature, rather than
 * aliasing the tab to one of them (which would misrepresent what's there).
 */
import { Button, Card } from '@pausalac/ui'
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">Finansije</h1>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">Limiti</h2>
      <p class="mb-3 text-sm text-text-secondary">
        Prati godišnji limit prometa i prag za registraciju u sistem PDV-a.
      </p>
      <RouterLink :to="{ name: 'limits' }">
        <Button variant="secondary">Otvori</Button>
      </RouterLink>
    </Card>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">KPO</h2>
      <p class="mb-3 text-sm text-text-secondary">
        Knjiga prometa ostvarenog obavljanjem delatnosti — hronološka evidencija prometa.
      </p>
      <RouterLink :to="{ name: 'kpo' }">
        <Button variant="secondary">Otvori</Button>
      </RouterLink>
    </Card>

    <Card>
      <h2 class="mb-1 text-base font-semibold text-navy">Obaveze</h2>
      <p class="mb-3 text-sm text-text-secondary">
        Poreske i doprinosne obaveze i njihovi rokovi plaćanja.
      </p>
      <RouterLink :to="{ name: 'obligations' }">
        <Button variant="secondary">Otvori</Button>
      </RouterLink>
    </Card>
  </div>
</template>
