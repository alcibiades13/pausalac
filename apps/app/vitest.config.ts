import { fileURLToPath } from 'node:url'
import { mergeConfig, defineConfig, configDefaults } from 'vitest/config'
import viteConfig from './vite.config'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      exclude: [...configDefaults.exclude, 'e2e/**'],
      root: fileURLToPath(new URL('./', import.meta.url)),
      alias: {
        // jsdom has no layout engine, so the real ApexCharts throws an
        // unhandled async rejection on every mount — see the stub's own
        // comment. Test-only; production builds use vite.config.ts as-is.
        'vue3-apexcharts': fileURLToPath(new URL('./src/test/stubs/vue3-apexcharts.ts', import.meta.url)),
      },
    },
  }),
)
