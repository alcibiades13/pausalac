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

**Status (Phase 1a — bootstrap):** monorepo, tooling i prazni ali pokretni
skeletoni su na mestu. Auth, tenant model, RBAC, audit infrastruktura i sav
poslovni domenski kod (fakture, KPO, limiti, ...) dolaze u sledećim fazama —
videti `docs/implementation-plan.md`.

## Preduslovi

- Node.js ≥ 20 (razvijano na Node 24)
- [pnpm](https://pnpm.io) — uključi ga preko corepack-a: `corepack enable && corepack prepare pnpm@9.12.0 --activate`
- Python 3.12
- Docker + Docker Compose (Postgres, Redis, MinIO, MailHog za lokalni razvoj)

## Prvo pokretanje

### 1. Infrastruktura (Postgres, Redis, MinIO, MailHog)

```bash
cp .env.example .env
docker compose up -d
```

- MinIO konzola: http://localhost:9001 (podaci iz `.env`)
- MailHog inbox: http://localhost:8025

### 2. Backend (`apps/api`)

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend je dostupan na http://localhost:8000, health check na
http://localhost:8000/health.

Pokretanje testova: `pytest` (iz `apps/api`, sa aktivnim venv-om).

### 3. Frontend (iz root-a repozitorijuma, jednom instalira oba app-a)

```bash
pnpm install
pnpm dev:app   # Vue app — http://localhost:5173
pnpm dev:web   # Nuxt marketing sajt — http://localhost:3000
```

## Konvencije

- Sve poslovne/regulatorne brojke (limiti, rokovi, procenti) žive u
  rules-engine konfiguraciji, nikad hard-code-ovane u kodu — videti
  `docs/implementation-plan.md`.
- Novac je uvek `Decimal`/`NUMERIC`, nikad float.
- Svaka bitna finansijska promena mora biti auditabilna (audit domen).
- UI copy je na srpskom (latinica); kod, imena polja u bazi i identifikatori
  su na engleskom.
