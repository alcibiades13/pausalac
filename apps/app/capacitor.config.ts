import type { CapacitorConfig } from '@capacitor/cli'

/**
 * Master prompt §54 "Mobile app": "Vue application -> responsive web ->
 * PWA -> Capacitor -> iOS / Android." This is the prepared pipeline seam
 * (blueprint §25's "Capacitor build pipeline je pripremljen"), not a
 * shipped native app — no `ios/`/`android/` platform project exists yet.
 * `webDir` points at the same production build the PWA stage already
 * produces (`vite build` -> `dist/`), so Capacitor wraps the real app,
 * not a separate native build.
 *
 * ⚠️ `appId` below is a placeholder, not a confirmed identifier —
 * neither source document names a real domain/bundle id, and this value
 * becomes effectively permanent once an app is first published to
 * either store. Confirm the real reverse-domain id before ever running
 * `npx cap add ios/android` for a real release build.
 */
const config: CapacitorConfig = {
  appId: 'rs.pausalac.app',
  appName: 'Pausalac',
  webDir: 'dist',
}

export default config
