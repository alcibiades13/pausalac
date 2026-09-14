<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Button, Card, Input, Select, Alert, Badge, EmptyState, Skeleton } from '@pausalac/ui'
import {
  listOrganizations,
  createOrganization,
  listOrgStaff,
  addOrgStaff,
  removeOrgStaff,
  listOrgConnections,
  createOrgConnection,
  type AccountingOrganization,
  type OrgStaffMembership,
  type OrganizationConnection,
  type GrantedRole,
  type OrgStaffRole,
} from '@/services/accounting'
import { ApiError } from '@/lib/api'

const STAFF_ROLE_OPTIONS: { value: OrgStaffRole; label: string }[] = [
  { value: 'staff', label: 'Zaposleni' },
  { value: 'admin', label: 'Administrator' },
]
const GRANTED_ROLE_OPTIONS: { value: GrantedRole; label: string }[] = [
  { value: 'accountant', label: 'Računovođa' },
  { value: 'accountant_admin', label: 'Računovođa (admin)' },
]
const CONNECTION_STATUS_LABELS: Record<OrganizationConnection['status'], string> = {
  pending: 'Na čekanju',
  active: 'Aktivna',
  declined: 'Odbijena',
  revoked: 'Opozvana',
}
const CONNECTION_STATUS_VARIANTS: Record<
  OrganizationConnection['status'],
  'neutral' | 'success' | 'danger'
> = {
  pending: 'neutral',
  active: 'success',
  declined: 'danger',
  revoked: 'danger',
}

// --- organization: load-or-create ---------------------------------------

const organization = ref<AccountingOrganization | null>(null)
const status = ref<'loading' | 'ready' | 'error'>('loading')
const errorMessage = ref('')

async function loadOrganization() {
  status.value = 'loading'
  try {
    const page = await listOrganizations()
    organization.value = page.results[0] ?? null
    status.value = 'ready'
    if (organization.value) {
      await Promise.all([loadStaff(), loadConnections()])
    }
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da učitamo podatke.'
    status.value = 'error'
  }
}

onMounted(loadOrganization)

const createForm = ref({ name: '', contact_email: '', pib: '' })
const creating = ref(false)
const createError = ref('')

async function onCreateOrganization() {
  creating.value = true
  createError.value = ''
  try {
    organization.value = await createOrganization(createForm.value)
  } catch (error) {
    createError.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da sačuvamo agenciju.'
  } finally {
    creating.value = false
  }
}

const isAdmin = computed(() => organization.value?.my_role === 'admin')

// --- staff ---------------------------------------------------------------

const staff = ref<OrgStaffMembership[]>([])

async function loadStaff() {
  if (!organization.value) return
  staff.value = await listOrgStaff(organization.value.id)
}

const staffForm = ref<{ email: string; role: OrgStaffRole }>({ email: '', role: 'staff' })
const addingStaff = ref(false)
const staffError = ref('')

async function onAddStaff() {
  if (!organization.value) return
  addingStaff.value = true
  staffError.value = ''
  try {
    await addOrgStaff(organization.value.id, staffForm.value)
    staffForm.value = { email: '', role: 'staff' }
    await loadStaff()
  } catch (error) {
    staffError.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da dodamo zaposlenog.'
  } finally {
    addingStaff.value = false
  }
}

const removingStaffId = ref<number | null>(null)
async function onRemoveStaff(membershipId: number) {
  if (!organization.value) return
  removingStaffId.value = membershipId
  try {
    await removeOrgStaff(organization.value.id, membershipId)
    await loadStaff()
  } finally {
    removingStaffId.value = null
  }
}

// --- client connections ---------------------------------------------------

const connections = ref<OrganizationConnection[]>([])

async function loadConnections() {
  if (!organization.value) return
  connections.value = await listOrgConnections(organization.value.id)
}

const connectionForm = ref<{ company_pib: string; granted_role: GrantedRole }>({
  company_pib: '',
  granted_role: 'accountant',
})
const invitingClient = ref(false)
const connectionError = ref('')

async function onInviteClient() {
  if (!organization.value) return
  invitingClient.value = true
  connectionError.value = ''
  try {
    await createOrgConnection(organization.value.id, connectionForm.value)
    connectionForm.value = { company_pib: '', granted_role: 'accountant' }
    await loadConnections()
  } catch (error) {
    connectionError.value =
      error instanceof ApiError ? error.message : 'Ne možemo trenutno da pošaljemo zahtev.'
  } finally {
    invitingClient.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <h1 class="text-xl font-semibold text-navy">Računovodstvena agencija</h1>

    <Alert v-if="status === 'error'" variant="danger">
      {{ errorMessage }}
      <button class="ml-2 underline" @click="loadOrganization">Pokušaj ponovo</button>
    </Alert>

    <Card v-else-if="status === 'loading'">
      <Skeleton :count="3" />
    </Card>

    <Card v-else-if="!organization">
      <h2 class="mb-1 text-base font-semibold text-navy">Osnuj agenciju</h2>
      <p class="mb-4 text-sm text-text-secondary">
        Registruj svoju računovodstvenu agenciju da bi mogla da se poveže sa klijentima.
      </p>
      <form class="flex flex-col gap-4" @submit.prevent="onCreateOrganization">
        <Alert v-if="createError" variant="danger">{{ createError }}</Alert>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Input v-model="createForm.name" label="Naziv agencije" required />
          <Input v-model="createForm.contact_email" type="email" label="Kontakt email" />
          <Input v-model="createForm.pib" label="PIB (opciono)" />
        </div>
        <div>
          <Button type="submit" :loading="creating">Osnuj agenciju</Button>
        </div>
      </form>
    </Card>

    <template v-else>
      <Card>
        <h2 class="font-display text-base font-semibold text-navy">{{ organization.name }}</h2>
        <p class="text-sm text-text-secondary">{{ organization.contact_email || '—' }}</p>
      </Card>

      <Card>
        <h2 class="mb-3 text-base font-semibold text-navy">Zaposleni</h2>

        <template v-if="isAdmin">
          <Alert v-if="staffError" variant="danger" class="mb-3">{{ staffError }}</Alert>
          <form class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="onAddStaff">
            <Input
              v-model="staffForm.email"
              type="email"
              label="Email zaposlenog"
              required
              class="flex-1 sm:max-w-xs"
            />
            <Select v-model="staffForm.role" label="Uloga" :options="STAFF_ROLE_OPTIONS" />
            <Button type="submit" :loading="addingStaff">Dodaj</Button>
          </form>
        </template>

        <EmptyState v-if="staff.length === 0" title="Još nema zaposlenih." />
        <ul v-else class="flex flex-col divide-y divide-border">
          <li
            v-for="member in staff"
            :key="member.id"
            class="flex items-center justify-between py-2"
          >
            <div>
              <p class="text-sm text-navy">{{ member.user_email }}</p>
              <p class="text-xs text-text-secondary">
                {{ member.role === 'admin' ? 'Administrator' : 'Zaposleni' }}
              </p>
            </div>
            <button
              v-if="isAdmin"
              type="button"
              class="text-sm text-danger hover:underline disabled:opacity-40"
              :disabled="removingStaffId === member.id"
              @click="onRemoveStaff(member.id)"
            >
              Ukloni
            </button>
          </li>
        </ul>
      </Card>

      <Card>
        <h2 class="mb-3 text-base font-semibold text-navy">Klijenti</h2>

        <form class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end" @submit.prevent="onInviteClient">
          <Input
            v-model="connectionForm.company_pib"
            label="PIB klijenta"
            required
            class="flex-1 sm:max-w-xs"
          />
          <Select
            v-model="connectionForm.granted_role"
            label="Nivo pristupa"
            :options="GRANTED_ROLE_OPTIONS"
          />
          <Button type="submit" :loading="invitingClient">Pozovi klijenta</Button>
        </form>
        <Alert v-if="connectionError" variant="danger" class="mb-3">{{ connectionError }}</Alert>

        <EmptyState v-if="connections.length === 0" title="Još nema povezanih klijenata." />
        <ul v-else class="flex flex-col divide-y divide-border">
          <li
            v-for="connection in connections"
            :key="connection.id"
            class="flex items-center justify-between py-2"
          >
            <div>
              <p class="text-sm text-navy">{{ connection.company_name }}</p>
              <p class="text-xs text-text-secondary">{{ connection.company_pib }}</p>
            </div>
            <Badge :variant="CONNECTION_STATUS_VARIANTS[connection.status]">
              {{ CONNECTION_STATUS_LABELS[connection.status] }}
            </Badge>
          </li>
        </ul>
      </Card>
    </template>
  </div>
</template>
