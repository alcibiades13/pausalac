# Pausalac

SaaS platforma za srpske paušalne preduzetnike — "Tvoj paušal, na autopilotu."

Ovo je monorepo: Django/DRF backend, Vue 3 aplikacija za korisnike, Nuxt 4
marketing sajt, i deljeni frontend paketi. Za proizvodni kontekst, arhitekturu
i roadmap pogledaj:

- [`Pausalac.md`](./Pausalac.md) — Master Development Prompt (principi, pravila, faze)
- [`pausalac-blueprint.md`](./pausalac-blueprint.md) — Product Blueprint (persone, IA, MVP/V2/V3)
- [`docs/implementation-plan.md`](./docs/implementation-plan.md) — Phase 0 implementation plan
- [`docs/decisions-log.md`](./docs/decisions-log.md) — log engineering odluka (append-only)

## Struktura repozitorijuma

```
pausalac/
  apps/
    api/      # Django + DRF backend (modularni monolit, jedan app po domenu)
    app/      # Vue 3 + TS + Vite — autentifikovana aplikacija za korisnike
    web/      # Nuxt 4 — javni marketing/landing sajt
  packages/
    ui/       # (rezervisano) deljene Vue komponente
    config/   # deljeni design tokeni (Tailwind v4 @theme) i tsconfig baza
  docs/       # implementacioni plan, decisions log, arhivirani izvorni dokumenti
```

**Status:** auth/tenant/RBAC/audit backend, dizajn-sistem primitivi, auth
ekrani i Klijenti domen su gotovi (Phase 2a). Fakture, KPO, limiti, plaćanja,
pravi dashboard dolaze u sledećim fazama — videti `docs/implementation-plan.md`.

## Preduslovi

- Node.js ≥ 20 (razvijano na Node 24)
- [pnpm](https://pnpm.io) — uključi ga preko corepack-a: `corepack enable && corepack prepare pnpm@9.12.0 --activate`
- Python 3.12
- Docker + Docker Compose (Postgres, Redis, MinIO, MailHog za lokalni razvoj)

## Prvo podešavanje (jednom)

```bash
cp .env.example .env

cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py createsuperuser   # opciono, za /admin
cd ../..

pnpm install
```

## Svakodnevni rad

```bash
pnpm dev
```

Ovo pokreće (jednom komandom, u jednom terminalu, sa obojenim prefiksima
po procesu):

- infrastrukturu preko `docker compose up -d` (Postgres, Redis, MinIO,
  MailHog — ostaju u pozadini i posle Ctrl+C)
- Django dev server — http://localhost:8000 (health check `/health`)
- Celery worker (obavezan — bez njega registracija/email ne rade, jer se
  šalju kao pozadinski zadatak)
- Vue app (`apps/app`) — http://localhost:5173

Ctrl+C u tom terminalu gasi backend/Celery/frontend zajedno (infrastruktura
u Docker-u ostaje da radi — ugasi je posebno sa `docker compose down` ako
treba).

- MailHog inbox (verifikacija emaila, reset lozinke): http://localhost:8025
- MinIO konzola: http://localhost:9001 (podaci iz `.env`)

Marketing sajt (`apps/web`, trenutno prazan skeleton) nije uključen u
`pnpm dev` jer nema veze sa svakodnevnim radom na aplikaciji — pokreni ga
posebno kad zatreba: `pnpm dev:web` — http://localhost:3000.

Pokretanje backend testova: `pytest` (iz `apps/api`, sa aktivnim venv-om).

## Konvencije

- Sve poslovne/regulatorne brojke (limiti, rokovi, procenti) žive u
  rules-engine konfiguraciji, nikad hard-code-ovane u kodu — videti
  `docs/implementation-plan.md`.
- Novac je uvek `Decimal`/`NUMERIC`, nikad float.
- Svaka bitna finansijska promena mora biti auditabilna (audit domen).
- UI copy je na srpskom (latinica); kod, imena polja u bazi i identifikatori
  su na engleskom.
