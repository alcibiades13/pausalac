<script setup lang="ts">
import { Card } from '@pausalac/ui'
import PricingCard from '~/components/PricingCard.vue'

const { data: plans, pending, error } = usePublicPlans()

useHead({ title: 'Cenovnik' })

const FAQ = [
  {
    q: 'Da li postoji besplatan probni period?',
    a: 'Da — svaka nova kompanija dobija 14 dana besplatnog probnog perioda, bez potrebe za unosom kartice.',
  },
  {
    q: 'Šta se dešava kad probni period istekne?',
    a: 'Dobićeš na vreme obaveštenje pre isteka. Do izbora paketa, pristup kreiranju novih faktura je privremeno ograničen — tvoji podaci ostaju netaknuti.',
  },
  {
    q: 'Mogu li da promenim paket kasnije?',
    a: 'Da, paket možeš promeniti u bilo kom trenutku iz podešavanja naloga.',
  },
]
</script>

<template>
  <div class="mx-auto flex w-full max-w-6xl flex-col gap-16 px-4 py-16 sm:px-6">
    <div class="text-center">
      <h1 class="font-display text-3xl font-semibold text-navy sm:text-4xl">Cenovnik</h1>
      <p class="mt-4 text-text-secondary">
        Jednostavni paketi, bez skrivenih troškova. 14 dana besplatno, bez potrebe za karticom.
      </p>
    </div>

    <p v-if="pending" class="text-center text-text-secondary">Učitavanje paketa...</p>
    <p v-else-if="error" class="text-center text-danger">
      Trenutno ne možemo da učitamo cenovnik. Pokušaj ponovo malo kasnije.
    </p>
    <div v-else-if="plans && plans.length" class="grid grid-cols-1 gap-6 sm:grid-cols-3">
      <PricingCard
        v-for="plan in plans"
        :key="plan.id"
        :plan="plan"
        :highlighted="plan.identifier === 'professional'"
      />
    </div>

    <div class="mx-auto w-full max-w-2xl">
      <h2 class="mb-6 text-center font-display text-xl font-semibold text-navy">Najčešća pitanja</h2>
      <div class="flex flex-col gap-3">
        <Card v-for="item in FAQ" :key="item.q">
          <h3 class="font-medium text-navy">{{ item.q }}</h3>
          <p class="mt-1 text-sm text-text-secondary">{{ item.a }}</p>
        </Card>
      </div>
    </div>
  </div>
</template>
