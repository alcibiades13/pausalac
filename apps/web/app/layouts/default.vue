<script setup lang="ts">
import { Button } from '@pausalac/ui'

const config = useRuntimeConfig()
const { isLoggedIn } = useAuthStatus()
</script>

<template>
  <div class="flex min-h-screen flex-col bg-background">
    <header class="sticky top-0 z-10 bg-surface shadow-[0_1px_2px_rgba(23,32,51,0.04),0_4px_16px_-8px_rgba(23,32,51,0.10)]">
      <div class="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <NuxtLink to="/" class="flex items-center gap-2">
          <span
            class="h-6 w-6 shrink-0 rounded-lg bg-gradient-to-br from-primary to-primary-dark"
            aria-hidden="true"
          />
          <span class="font-display text-base font-semibold text-navy">Pausalac</span>
        </NuxtLink>

        <nav class="hidden items-center gap-1 sm:flex" aria-label="Glavna navigacija">
          <NuxtLink
            to="/cenovnik"
            class="rounded-lg px-3 py-2 text-sm text-text-secondary hover:bg-background hover:text-primary"
          >
            Cenovnik
          </NuxtLink>
        </nav>

        <div class="flex items-center gap-2">
          <template v-if="isLoggedIn">
            <a :href="`${config.public.appUrl}/pocetna`">
              <Button>Idi u aplikaciju</Button>
            </a>
          </template>
          <template v-else>
            <a
              :href="`${config.public.appUrl}/prijava`"
              class="hidden rounded-lg px-3 py-2 text-sm text-text-secondary hover:bg-background hover:text-primary sm:inline-block"
            >
              Prijavi se
            </a>
            <a :href="`${config.public.appUrl}/registracija`">
              <Button>Probaj besplatno</Button>
            </a>
          </template>
        </div>
      </div>
    </header>

    <main class="flex-1">
      <slot />
    </main>

    <footer class="border-t border-border bg-surface">
      <div class="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-8 text-sm text-text-secondary sm:px-6">
        <p>© {{ new Date().getFullYear() }} Pausalac.</p>
        <p>Aplikacija za vođenje poslovanja paušalnih preduzetnika.</p>
      </div>
    </footer>
  </div>
</template>
