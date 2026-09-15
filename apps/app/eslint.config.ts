import { globalIgnores } from 'eslint/config'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import pluginVue from 'eslint-plugin-vue'
import pluginVitest from '@vitest/eslint-plugin'
import pluginOxlint from 'eslint-plugin-oxlint'
import pluginVueA11y from 'eslint-plugin-vuejs-accessibility'
import skipFormatting from 'eslint-config-prettier/flat'

// To allow more languages other than `ts` in `.vue` files, uncomment the following lines:
// import { configureVueProject } from '@vue/eslint-config-typescript'
// configureVueProject({ scriptLangs: ['ts', 'tsx'] })
// More info at https://github.com/vuejs/eslint-config-typescript/#advanced-setup

export default defineConfigWithVueTs(
  {
    name: 'app/files-to-lint',
    files: ['**/*.{vue,ts,mts,tsx}'],
  },

  globalIgnores(['**/dist/**', '**/dist-ssr/**', '**/coverage/**']),

  ...pluginVue.configs['flat/essential'],
  vueTsConfigs.recommended,
  ...pluginVueA11y.configs['flat/recommended'],

  {
    name: 'app/a11y-overrides',
    rules: {
      // This codebase's universal label pattern is a same-scope sibling
      // pair (`<label for="x">` + `<input id="x">`), never the label
      // wrapping its control — but the rule's default `required` demands
      // BOTH that nesting AND a for/id pair. Every real for/id pair in
      // the app was failing this for no accessibility reason; `id` alone
      // matches what §55 actually asks for.
      'vuejs-accessibility/label-has-for': ['error', { required: 'id' }],
      // packages/ui's Button/Input/Select all bake in a real label
      // association internally (see each component's own tests) — but
      // this rule can't see across component boundaries, and worse,
      // `Input`/`Select`/`Progress` kebab-case down to exactly the
      // native `input`/`select`/`progress` tag names it hardcodes as
      // "always a form control," with no config to exclude them. Left
      // on, it flags every single use of our own accessible primitives.
      // Real native form controls in `apps/app` (raw <select> filters,
      // the document upload <input type="file">) were manually audited
      // and confirmed labeled — this isn't masking a live problem.
      'vuejs-accessibility/form-control-has-label': 'off',
    },
  },

  {
    ...pluginVitest.configs.recommended,
    files: ['src/**/__tests__/*'],
  },

  ...pluginOxlint.buildFromOxlintConfigFile('.oxlintrc.json'),

  skipFormatting,
)
