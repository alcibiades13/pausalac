<script setup lang="ts">
import { Card, Button } from '@pausalac/ui'
import AttentionMockup from '~/components/AttentionMockup.vue'
import PricingCard from '~/components/PricingCard.vue'

const config = useRuntimeConfig()
const { data: plans } = usePublicPlans()

useHead({ title: 'Vođenje poslovanja za paušalne preduzetnike' })

const PROBLEM_CARDS = [
  { icon: '💰', title: 'Koliko sam zaradio?', body: 'Fakturisano i naplaćeno na jednom mestu, uvek ažurno.' },
  { icon: '📈', title: 'Koliko mi je ostalo do limita?', body: 'Paušalni i PDV limit prate se automatski, sa projekcijom do kraja godine.' },
  { icon: '✅', title: 'Šta moram da uradim?', body: 'Jedna lista prioriteta umesto gomile razbacanih kartica i tabova.' },
  { icon: '⏰', title: 'Da li nešto zahteva hitnu reakciju?', body: 'Fakture koje kasne i obaveze koje dospevaju, na vreme, ne posle roka.' },
]

const INVOICE_STEPS = [
  { step: '1', title: 'Izaberi klijenta', body: 'Iz liste klijenata ili dodaj novog u par sekundi.' },
  { step: '2', title: 'Dodaj stavke', body: 'Usluge ili proizvodi, sa automatskim izračunom ukupnog iznosa.' },
  { step: '3', title: 'Pošalji', body: 'PDF i email idu direktno klijentu, status prati da li je faktura viđena i plaćena.' },
]
</script>

<template>
  <div class="flex flex-col gap-24 py-12 sm:py-16">
    <!-- Hero -->
    <section class="mx-auto flex w-full max-w-6xl flex-col items-center gap-10 px-4 sm:px-6 lg:flex-row lg:items-center lg:gap-16">
      <div class="flex flex-col gap-6 text-center lg:text-left">
        <h1 class="text-3xl font-semibold text-navy sm:text-4xl lg:text-5xl">
          Administracija paušalnog biznisa, bez haosa i bez iznenađenja.
        </h1>
        <p class="text-lg text-text-secondary">
          Fakture, limiti, KPO i poreske obaveze na jednom mestu — sa jasnim statusom umesto gomile
          razbacanih tabova.
        </p>
        <div class="flex flex-col gap-3 sm:flex-row sm:justify-center lg:justify-start">
          <a :href="`${config.public.appUrl}/registracija`">
            <Button class="w-full sm:w-auto">Probaj besplatno</Button>
          </a>
          <a href="#kako-radi">
            <Button variant="secondary" class="w-full sm:w-auto">Vidi kako radi</Button>
          </a>
        </div>
      </div>
      <div class="flex w-full justify-center lg:w-auto">
        <AttentionMockup />
      </div>
    </section>

    <!-- Problem -> rešenje -->
    <section id="kako-radi" class="mx-auto w-full max-w-6xl px-4 sm:px-6">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card v-for="card in PROBLEM_CARDS" :key="card.title" class="flex flex-col gap-2">
          <span class="text-2xl" aria-hidden="true">{{ card.icon }}</span>
          <h3 class="font-display text-base font-semibold text-navy">{{ card.title }}</h3>
          <p class="text-sm text-text-secondary">{{ card.body }}</p>
        </Card>
      </div>
    </section>

    <!-- Attention Center deep-dive -->
    <section class="mx-auto w-full max-w-3xl px-4 text-center sm:px-6">
      <h2 class="font-display text-2xl font-semibold text-navy">Jedan status, ne gomila kartica</h2>
      <p class="mt-4 text-text-secondary">
        Umesto da sam sastavljaš sliku iz faktura, limita i poreskih obaveza, Pausalac ih objedinjuje u
        jednu listu prioriteta — šta kasni, šta dospeva, šta zahteva pažnju. Uvek znaš odakle dolazi svaki
        broj koji vidiš.
      </p>
    </section>

    <!-- Fakturisanje flow -->
    <section class="mx-auto w-full max-w-6xl px-4 sm:px-6">
      <h2 class="mb-8 text-center font-display text-2xl font-semibold text-navy">
        Fakturisanje u tri koraka
      </h2>
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div v-for="item in INVOICE_STEPS" :key="item.step" class="flex flex-col items-center gap-2 text-center">
          <span
            class="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 font-display text-lg font-semibold text-primary"
          >
            {{ item.step }}
          </span>
          <h3 class="font-medium text-navy">{{ item.title }}</h3>
          <p class="text-sm text-text-secondary">{{ item.body }}</p>
        </div>
      </div>
    </section>

    <!-- Cenovnik preview -->
    <section class="mx-auto w-full max-w-6xl px-4 sm:px-6">
      <h2 class="mb-8 text-center font-display text-2xl font-semibold text-navy">Cenovnik</h2>
      <div v-if="plans && plans.length" class="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <PricingCard
          v-for="plan in plans"
          :key="plan.id"
          :plan="plan"
          :highlighted="plan.identifier === 'professional'"
        />
      </div>
      <div class="mt-6 text-center">
        <NuxtLink to="/cenovnik" class="text-sm text-primary hover:underline">
          Pogledaj sve pakete i detalje →
        </NuxtLink>
      </div>
    </section>

    <!-- Final CTA -->
    <section class="mx-auto w-full max-w-2xl px-4 text-center sm:px-6">
      <h2 class="font-display text-2xl font-semibold text-navy">
        Spreman da prestaneš da razmišljaš o administraciji?
      </h2>
      <div class="mt-6">
        <a :href="`${config.public.appUrl}/registracija`">
          <Button>Probaj besplatno</Button>
        </a>
      </div>
    </section>
  </div>
</template>
