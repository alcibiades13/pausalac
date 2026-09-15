<script setup lang="ts">
import { Button } from '@pausalac/ui'
import LanguageSwitcher from '~/components/LanguageSwitcher.vue'

const config = useRuntimeConfig()
const { isLoggedIn } = useAuthStatus()
const localePath = useLocalePath()
</script>

<template>
  <div class="flex min-h-screen flex-col bg-background">
    <div class="sticky top-4 z-20 px-4 sm:px-6">
      <header
        class="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 rounded-2xl border border-border bg-surface px-4 py-3 shadow-[0_10px_40px_-10px_rgba(10,10,10,0.20)] sm:px-5"
      >
        <NuxtLink :to="localePath('/')" class="flex items-center gap-2">
          <span
            class="h-6 w-6 shrink-0 rounded-lg bg-gradient-to-br from-primary to-primary-dark"
            aria-hidden="true"
          />
          <span class="font-display text-base font-semibold text-navy">Pausalac</span>
        </NuxtLink>

        <nav class="hidden items-center gap-1 sm:flex" :aria-label="$t('nav.aplikacija') + ' / ' + $t('nav.cenovnik')">
          <NuxtLink
            :to="localePath('/cenovnik')"
            class="rounded-lg px-3 py-2 text-sm text-text-secondary hover:bg-background hover:text-primary"
          >
            {{ $t('nav.cenovnik') }}
          </NuxtLink>
          <a
            :href="config.public.appUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="rounded-lg px-3 py-2 text-sm text-text-secondary hover:bg-background hover:text-primary"
          >
            {{ $t('nav.aplikacija') }}
          </a>
        </nav>

        <div class="flex items-center gap-3">
          <LanguageSwitcher class="hidden sm:flex" />
          <template v-if="isLoggedIn">
            <a :href="`${config.public.appUrl}/pocetna`" target="_blank" rel="noopener noreferrer">
              <Button>{{ $t('nav.otvoriAplikaciju') }}</Button>
            </a>
          </template>
          <template v-else>
            <a
              :href="`${config.public.appUrl}/prijava`"
              target="_blank"
              rel="noopener noreferrer"
              class="hidden rounded-lg px-3 py-2 text-sm text-text-secondary hover:bg-background hover:text-primary sm:inline-block"
            >
              {{ $t('nav.prijava') }}
            </a>
            <a :href="`${config.public.appUrl}/registracija`" target="_blank" rel="noopener noreferrer">
              <Button>{{ $t('nav.registracija') }}</Button>
            </a>
          </template>
        </div>
      </header>
    </div>

    <main class="flex-1">
      <slot />
    </main>

    <footer class="border-t border-border bg-surface">
      <div class="mx-auto flex w-full max-w-6xl flex-col gap-8 px-4 py-12 sm:px-6">
        <div class="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
          <div class="flex flex-col gap-3">
            <div class="flex items-center gap-2">
              <span
                class="h-6 w-6 shrink-0 rounded-lg bg-gradient-to-br from-primary to-primary-dark"
                aria-hidden="true"
              />
              <span class="font-display text-base font-semibold text-navy">Pausalac</span>
            </div>
            <p class="max-w-xs text-sm text-text-secondary">
              {{ $t('footer.tagline') }}
            </p>
            <LanguageSwitcher class="mt-1" />
          </div>

          <nav :aria-label="$t('footer.product')" class="flex gap-8">
            <div class="flex flex-col gap-2 text-sm">
              <span class="font-medium text-navy">{{ $t('footer.product') }}</span>
              <NuxtLink :to="localePath('/#kako-radi')" class="text-text-secondary hover:text-primary">{{
                $t('footer.kakoRadi')
              }}</NuxtLink>
              <NuxtLink :to="localePath('/cenovnik')" class="text-text-secondary hover:text-primary">{{
                $t('footer.cenovnik')
              }}</NuxtLink>
            </div>
            <div class="flex flex-col gap-2 text-sm">
              <span class="font-medium text-navy">{{ $t('footer.nalog') }}</span>
              <a
                :href="`${config.public.appUrl}/prijava`"
                target="_blank"
                rel="noopener noreferrer"
                class="text-text-secondary hover:text-primary"
                >{{ $t('footer.prijava') }}</a
              >
              <a
                :href="`${config.public.appUrl}/registracija`"
                target="_blank"
                rel="noopener noreferrer"
                class="text-text-secondary hover:text-primary"
                >{{ $t('footer.registracija') }}</a
              >
            </div>
          </nav>
        </div>

        <div class="flex flex-col gap-2 border-t border-border pt-6 text-sm text-text-secondary sm:flex-row sm:items-center sm:justify-between">
          <p>{{ $t('footer.copyright', { year: new Date().getFullYear() }) }}</p>
          <p>{{ $t('footer.madeFor') }}</p>
        </div>
      </div>
    </footer>
  </div>
</template>
