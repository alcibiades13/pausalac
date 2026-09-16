<script setup lang="ts">
import { computed, useId, useTemplateRef } from 'vue'

/**
 * A fixed-format (dd.mm.gggg — Serbian convention) replacement for a
 * bare `<input type="date">` (real user complaint: the native control's
 * *displayed* text format follows the visitor's OS/browser locale, not
 * anything this app controls — inconsistent across machines, and wrong
 * to leave to chance for a financial product where dates are read as
 * tax/accounting data). Same model contract as `type="date"` (a plain
 * `YYYY-MM-DD` string) — swapping this in wherever a `date` `Input` was
 * used is a drop-in replacement, no caller/backend changes needed.
 *
 * Deliberately not a hand-built calendar grid: the *picking* UI stays
 * the browser's own native date picker (full keyboard/a11y support for
 * free) — a real `type="date"` input sits on top, fully transparent but
 * genuinely interactive (not `display:none`), so every click/keyboard/
 * screen-reader interaction goes to it directly and its own native
 * click-to-open-picker behavior just works. The formatted text
 * underneath is purely decorative (`tabindex="-1"`, not part of the tab
 * order) — without that, there'd be two focusable stops for one field.
 * `label` points at the real date input's id, not the decorative one.
 */
const model = defineModel<string>({ default: '' })

withDefaults(
  defineProps<{
    label?: string
    error?: string
    hint?: string
    required?: boolean
    disabled?: boolean
  }>(),
  {
    required: false,
    disabled: false,
  },
)

const inputId = useId()

const displayValue = computed(() => {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(model.value)
  if (!match) return ''
  const [, year, month, day] = match
  return `${day}.${month}.${year}.`
})

function onDateInput(event: Event) {
  model.value = (event.target as HTMLInputElement).value
}
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" :for="inputId" class="text-sm font-medium text-navy">
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>
    <div class="relative">
      <input
        type="text"
        readonly
        tabindex="-1"
        aria-hidden="true"
        :value="displayValue"
        placeholder="dd.mm.gggg."
        :disabled="disabled"
        :class="[
          'w-full rounded-lg border bg-surface py-2 pl-3 pr-9 text-sm text-navy placeholder:text-text-secondary',
          'disabled:cursor-not-allowed disabled:bg-background disabled:opacity-60',
          error ? 'border-danger' : 'border-border',
        ]"
      />
      <svg
        class="pointer-events-none absolute right-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-text-secondary"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        aria-hidden="true"
      >
        <rect x="3" y="5" width="18" height="16" rx="2" />
        <path d="M8 3v4M16 3v4M3 10h18" stroke-linecap="round" />
      </svg>
      <input
        :id="inputId"
        type="date"
        :required="required"
        :disabled="disabled"
        :aria-invalid="!!error"
        :aria-describedby="error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined"
        class="absolute inset-0 h-full w-full cursor-pointer rounded-lg opacity-0 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed"
        :value="model"
        @input="onDateInput"
      />
    </div>
    <p v-if="error" :id="`${inputId}-error`" class="text-sm text-danger">{{ error }}</p>
    <p v-else-if="hint" :id="`${inputId}-hint`" class="text-sm text-text-secondary">{{ hint }}</p>
  </div>
</template>
