import { defineComponent, h } from 'vue'

/**
 * Test-only stand-in for `vue3-apexcharts` (aliased in vitest.config.ts).
 * The real component renders into a DOM node ApexCharts measures with
 * layout APIs jsdom doesn't implement, which throws an unhandled async
 * rejection on every mount — this renders a plain div with the series/
 * options as data attributes instead, enough for chart component tests
 * to assert "did it receive the right data" without touching ApexCharts.
 */
export default defineComponent({
  name: 'VueApexCharts',
  props: {
    type: { type: String, default: undefined },
    series: { type: [Array, Object], default: () => [] },
    options: { type: Object, default: () => ({}) },
    height: { type: [String, Number], default: undefined },
    width: { type: [String, Number], default: undefined },
  },
  setup(props) {
    return () =>
      h('div', {
        'data-testid': 'apexchart-stub',
        'data-type': props.type,
        'data-series': JSON.stringify(props.series),
      })
  },
})
