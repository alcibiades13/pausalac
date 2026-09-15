# Plan sajta za Paušalac (promo + app u istom proizvodu)

Ovaj dokument je namenjen tebi i Claude-u u VS Code-u kao zajednička referenca. Baziran je na `Pausalac.md` (master prompt), `pausalac-blueprint.md` (product blueprint) i pregledu strukture pausal.rs (samo kao referenca tržišta, ne kao template za kopiranje).

---

## 1. Prvo: odluka koja određuje sve ostalo

**Sajt i app NISU dva projekta. To je jedan proizvod sa dva "moda":**

- **Public mod** — marketing/informativni sadržaj, dostupan bez logina, mora biti brz, SEO-friendly, indeksiran od Google-a.
- **App mod** — sve iza logina, SPA ponašanje, ne mora biti SEO-friendly, mora biti brzo za svakodnevnu upotrebu.

Ovo je tačno razlog zašto je u blueprintu (14.1) naveden **Nuxt 4 "za web/marketing sloj gde je opravdano"** pored Vue 3 aplikacije — to nije slučajna napomena, to je arhitektonska odluka koju sad samo treba formalizovati.

### Preporučena struktura (monorepo, jedan domen)

```
pausalac.rs/                  ← Nuxt 4 (marketing, SSR/SSG, javne stranice)
pausalac.rs/app/*             ← ista Nuxt instanca, ali app deo (SPA rute iza auth)
```

ILI, ako je Vue app već razvijena kao samostalna SPA (Vite):

```
pausalac.rs           → Nuxt 4 marketing sajt (SSG/SSR, brz, SEO)
app.pausalac.rs        → postojeća Vue/Vite SPA (login, dashboard, fakture...)
```

**Preporuka: subdomain pristup (opcija 2), ne monolitni Nuxt za sve.**

Razlozi:
1. Ne diraš postojeću app arhitekturu — ono što je već napravljeno u VS Code-u ostaje netaknuto.
2. Marketing sajt i app imaju potpuno različite performansne i SEO zahteve; mešanje toga u jedan Nuxt app usložnjava build i deployment bez prave koristi.
3. `app.pausalac.rs` je i psihološki jasan signal korisniku: "ovo je moj radni prostor", dok je `pausalac.rs` "prodavnica/izlog".
4. Isti pattern koriste pausal.rs (`moj.pausal.rs`), Paušalko i većina sličnih proizvoda — ovo je etablirano očekivanje korisnika, ne kopiranje dizajna.

Deljeno između ta dva projekta treba da bude samo:
- **Design tokeni** (boje, tipografija, spacing iz blueprint sekcije 18) — kao zaseban npm paket ili shared folder ako je monorepo (npm/pnpm workspaces).
- **Auth handoff**: klik na "Prijavi se" / "Probaj besplatno" na marketing sajtu vodi na `app.pausalac.rs/register` ili `/login`, sa mogućim query parametrima (npr. `?plan=professional&utm_source=...`) da app zna odakle je korisnik došao i koji plan je izabrao.

Ako je monorepo previše za sad — potpuno je u redu da to budu dva odvojena repozitorijuma koja dele samo `design-tokens.css` / Tailwind config fajl koji kopirate ručno ili preko git submodule-a. Ne treba komplikovati zbog toga u ovoj fazi.

---

## 2. Sitemap — javni (marketing) deo

Cilj svake stranice mora biti jasan: **šta korisnik treba da uradi kad je pročita**. Ne pravimo stranice "da postoje".

| Ruta | Svrha | Primarni CTA |
|---|---|---|
| `/` | Landing — hero, problem/rešenje, dashboard preview, poverenje | Probaj besplatno |
| `/funkcionalnosti` | Detaljan pregled: fakture, KPO, limiti, obaveze, attention center | Probaj besplatno |
| `/funkcionalnosti/fakturisanje` | Deep-dive na fakturisanje (opciono, kasnije) | Probaj besplatno |
| `/funkcionalnosti/limiti-i-porezi` | Deep-dive na limit intelligence — **ovo je signature feature, zaslužuje svoju stranicu** | Probaj besplatno |
| `/cenovnik` | Paketi, poređenje, FAQ o naplati | Izaberi paket |
| `/za-racunovodje` | Zaseban landing za Personu 3 (računovođe) — potpuno drugačiji copy i CTA | Zakaži razgovor |
| `/baza-znanja` (blog/vodiči) | SEO + edukacija, hrani knowledge base iz blueprinta 6.10 | (soft) Probaj besplatno |
| `/baza-znanja/[slug]` | Pojedinačni članak/vodič | — |
| `/alati` | Kalkulatori (porez, limit, "šta ako") — javno dostupni, veliki SEO/organic potencijal | Probaj besplatno (posle rezultata) |
| `/o-nama` | Tim, priča, poverenje (posebno bitno jer stoji iza toga i računovodstvena firma) | — |
| `/kontakt` | Kontakt forma, telefon, adresa | Pošalji poruku |
| `/uslovi-koriscenja`, `/politika-privatnosti` | Pravno | — |
| `/status` (opciono, kasnije) | Uptime/status stranica — gradi poverenje kod finansijskog proizvoda | — |

**Auth-related rute** (`/login`, `/register`, `/zaboravljena-lozinka`) žive u app-u (`app.pausalac.rs`), ne na marketing sajtu — marketing sajt samo linkuje ka njima.

### Napomena o "za računovođe"
Blueprint jasno kaže da je računovodstvena firma strateška prednost (sekcija 7, persona 3/4). Ovo **mora** imati sopstvenu marketing stranicu i sopstveni funnel, ne samo pasus na landing stranici. To je B2B2C prodajni kanal — različit jezik, različit dokaz vrednosti (ne "uštedi vreme sebi" nego "vodi 100+ klijenata bez haosa").

---

## 3. Landing page (`/`) — struktura sekcija

1. **Hero** — jedna rečenica problema, jedna rečenica rešenja, dva CTA (Probaj besplatno / Vidi kako radi). Vizuelno: screenshot/mockup dashboarda (pravi UI iz app-a, ne stock ilustracija — blueprint sekcija 118 zabranjuje "unnecessary illustrations" i cheesy stil).
2. **Poverenje odmah ispod hero-a** — broj korisnika (kad ih bude), ili "iza nas stoji [ime računovodstvene firme]" ako je to prodajni adut od starta.
3. **Problem → Rešenje, u 3-4 kartice** — mapirati direktno na "4 ključna pitanja" iz blueprinta:
   - Koliko sam zaradio? → Revenue/Dashboard
   - Koliko mi je ostalo do limita? → Limit intelligence
   - Šta moram da uradim? → Attention center
   - Da li nešto zahteva hitnu reakciju? → Attention center / obaveze
4. **Signature feature deep-dive: Attention Center** — ovo je diferencijator, zaslužuje najviše prostora na sajtu. Prikazati pravi UI snippet ("3 stvari zahtevaju tvoju pažnju...").
5. **Kako izgleda fakturisanje** — kratak flow/GIF/screenshot niza (izaberi klijenta → stavke → pošalji).
6. **Veza sa računovođom** (ako je relevantno za primarnu personu) — kratko, sa linkom ka `/za-racunovodje`.
7. **Cenovnik preview** (3 kartice, link ka punom `/cenovnik`).
8. **Testimonijali** — samo kad budu stvarni (vidi sekciju 6 "Ne izmišljati" niže).
9. **Sadržaj iz baze znanja** (3 najnovija članka) — SEO signal + poverenje.
10. **Finalni CTA** — "Spreman da prestaneš da razmišljaš o administraciji?"

**Ton copy-ja**: direktno iz blueprint sekcije 117 — "Preostalo do limita", "Faktura kasni 12 dana", ne birokratski jezik. Isto pravilo važi i za marketing copy, ne samo za app UI.

---

## 4. Diferencijacija naspram pausal.rs — konkretno

Pregledao sam pausal.rs kao referencu (ne kopiram im dizajn niti copy). Par zapažanja koja ti mogu pomoći da pozicioniraš svoj sajt originalno:

- Njihov glavni ugao je **"mi vodimo administraciju umesto tebe"** (naglasak na uslugu/računovođu — "Radiša", chatbot/asistent lik). Jak fokus na personifikaciju podrške.
- Cenovnik im je **uslužno orijentisan** (paketi uključuju knjigovodstvene usluge, ne samo softver) — to je model "SaaS + usluga u jednom".
- Nemaju jasno istaknut "attention/status" koncept na landing-u — najviše ističu pojedinačne funkcije (fakture, kasa, KPO, porezi) kao odvojene kartice, ne kao jedan povezan sistem.

**Tvoja prilika za diferencijaciju** (i ovo se poklapa tačno sa onim što blueprint sekcija 119 kaže da treba da bude "competitive advantage"):
- Naglasi **"jedan status, ne gomilu kartica"** — business health + attention center kao centralni koncept sajta, ne fakture/kasa/porez kao tri odvojene stvari.
- Naglasi **transparentnost i auditabilnost** ("uvek znaš odakle dolazi svaki broj") — ovo niko od konkurencije eksplicitno ne komunicira, a tebi je duboko u proizvodu (blueprint 4.4, 4.5, 15).
- Ako računovodstvena firma iza proizvoda ima ime/reputaciju — iskoristi to kao "built by accountants, not just developers" ugao, što je verodostojnije od generičkog SaaS marketinga.

---

## 5. Tehnička implementacija — konkretni koraci za VS Code par

### Marketing sajt (novi projekat)
1. `npx nuxi init pausalac-web`, Nuxt 4, TypeScript, Tailwind.
2. Postaviti **isti Tailwind config/tokene** kao u app-u (kopirati `tailwind.config` boje iz blueprint sekcije 18: Deep Navy `#172033`, Off White `#F7F8FA`, Indigo `#4F46E5`, itd.) — sajt i app moraju izgledati kao **jedan proizvod**, ne kao landing page kupljen od agencije i app razvijena posebno. Ovo je čest fail kod SaaS proizvoda i vredi ga rešiti odmah.
3. Font: Inter (isti kao app).
4. Statične/SSG stranice za sve marketing rute (`nitro.prerender` u Nuxt configu) — brzina i SEO.
5. Blog/baza znanja: content sloj preko **Nuxt Content** (markdown fajlovi, git-based CMS) — jednostavno za održavanje bez potrebe za posebnim CMS-om u MVP fazi. Kasnije, ako obim sadržaja poraste, može se migrirati na headless CMS.
6. Kalkulatori (`/alati`) — mogu biti Vue komponente koje pozivaju **isti rules-engine koncept** koji app koristi za limite/poreze (blueprint sekcija 16). Bitno: **ne duplirati poresku logiku ručno u dva codebase-a.** Ili:
   - kalkulator zove javni, rate-limited endpoint na Django backend-u (`/api/public/tax-calculator`), ili
   - logika pravila živi kao deljeni paket (npr. mali TS/JS paket sa verzionisanim pravilima) koji koriste i marketing sajt i app.

   Ovo direktno štiti princip iz Pausalac.md sekcije 46/112 — da se regulatorna pravila ne kopiraju na više mesta.
7. Deployment: SSG output na CDN (Vercel/Netlify/Cloudflare Pages) ili isti VPS/Docker infra gde je i ostatak sistema — zavisi šta već koristite za app.

### Handoff marketing → app
- Svaki CTA na sajtu vodi na `https://app.pausalac.rs/register?plan=X&utm_...`.
- App na registraciji čita `plan` parametar i predlaže ga korisniku umesto da ga pita od nule (blueprint princip 4.3 — automation, minimalno ponavljanje unosa).

### SEO minimum
- Server-rendered/prerendered HTML (Nuxt SSG rešava ovo automatski).
- `sitemap.xml` i `robots.txt` (Nuxt modul `@nuxtjs/sitemap`).
- OG tagovi i structured data (Organization, FAQPage za cenovnik/FAQ, Article za blog).
- Srpski ćirilica/latinica: blueprint (109) kaže primarni jezik je srpski latinica — dovoljno je latinica za MVP, ali ostaviti i18n arhitekturu otvorenu (Nuxt i18n modul), tačno kako blueprint traži da se ne hardkoduju stringovi.

---

## 6. Šta NE raditi na sajtu (direktno iz vaših dokumenata)

- **Ne izmišljati testimonijale ili brojke korisnika** dok ih nema — to je isti princip kao "Do not fake features" (Pausalac.md 123) i "Do not use mock data in production" (124), samo primenjen na marketing sadržaj. Lažni social proof je i etički problem i rizik za brend paušalne/finansijske aplikacije.
- **Ne obećavati integracije koje ne postoje** (SEF, fiskalizacija, bankarski izvodi) kao da već rade — ako ih najavljuješ, jasno označi "uskoro", ne prikazuj ih kao gotove funkcije.
- **Ne praviti cheesy dizajn** — isto pravilo kao za app (118): bez preteranih ilustracija, bez gamifikacije, bez motivacionih slogana. Sajt treba da odiše istim "calm and competent" osećajem kao dashboard.
- **Ne kopirati layout/copy sa pausal.rs** — koncepte (cenovnik sa paketima, blog, kalkulator) je ok imati jer su to standardne poslovne funkcije sajta, ali sopstvena struktura, ton i vizuelni jezik.

---

## 7. Kritika i pitanja za dosadašnji razvoj aplikacije

Nisam imao pristup vašem VS Code repozitorijumu, pa ovo nije code review — ovo je lista stvari koje vredi proveriti sa vašim parnjakom u VS Code-u, izvedenih direktno iz onoga što vaš sopstveni master prompt zahteva. Predlažem da mu prosledite ovu listu kao brzi self-check pre nego što se site razvoj počne oslanjati na app.

1. **Financial event/ledger sloj (blueprint 15)** — da li postoji centralni "izvor istine" (npr. `FinancialEvent` model: `InvoiceCreated`, `InvoicePaid`, itd.) iz kog se izvode dashboard, KPO i limiti? Ovo je arhitektonski najkritičniji deo celog proizvoda — ako dashboard, KPO i limiti računaju direktno iz `Invoice` tabele na 3 različita mesta, garantovano ćete dobiti neusaglašene brojeve čim se pojavi prvi edge case (storno, delimično plaćanje, izmena posle plaćanja).
2. **Decimal vs float (46)** — proveriti da li su svi novčani iznosi `Decimal`/`NUMERIC` na backend-u i da li frontend ne radi matematiku nad njima kao JS float pre slanja nazad.
3. **Rules engine za limite/poreze (16)** — da li su granice (6M, 8M/365 dana, procenti upozorenja) hardkodovane u kodu ili žive kao verzionisana konfiguracija sa godinom važenja? Ovo je bitno jer se ova pravila realno menjaju iz godine u godinu — ako su hardkodovana, svaka izmena zakona znači deployment umesto admin izmene.
4. **Audit trail (4.5, 111)** — da li svaka izmena finansijskog podatka beleži ko/kada/staru-novu vrednost, ili je to nešto što je ostavljeno "za kasnije"? Ovo je lakše ugraditi sada nego naknadno na postojeće tabele.
5. **Attention Center kao agregacija, ne kao notification feed** — proveriti da li je ovo implementirano kao poseban servis koji objedinjuje događaje iz više domena (invoices, limits, obligations, sef, documents) u jednu prioritizovanu listu, ili je trenutno "lista poslednjih notifikacija" — blueprint eksplicitno traži prvo, ne drugo (sekcija 9).
6. **Da li dashboard, KPO i limiti zaista dele isti izvor podataka** (pitanje 1 ponovljeno namerno) — ovo je toliko često mesto gde projekti ovog tipa greše da zaslužuje eksplicitnu proveru pre nego što se doda još feature-a na vrh.
7. **Status quo naspram MVP redosleda (129)** — gde se trenutno nalazite u odnosu na predloženi redosled (Auth → Company → Clients → Invoice model → ... → Dashboard → Limits → KPO)? Ako je dashboard rađen pre nego što su limiti i KPO servisi stabilni, moguće je da dashboard trenutno prikazuje privremene/nepovezane brojeve koje će trebati refaktorisati.
8. **Definition of Done checklista (122)** — da li se ona zaista primenjuje po feature-u (loading/empty/error state, testovi, audit), ili se preskače pod pritiskom da se ide dalje? Vredi pitati direktno, jer ovo je tačka gde AI-asistirani razvoj najčešće "prečicuje" kada dobije zahtev za novi feature pre nego što je prethodni zaista završen.

Ako mi podeliš trenutnu strukturu repozitorijuma (folder tree, ključni modeli) ili odgovore na gornja pitanja, mogu dati konkretniji, code-level review umesto ovog checklist pristupa.

---

## 8. Predloženi redosled rada na sajtu

1. Design tokeni + osnovni layout (header/footer/navigacija) — deljivi sa app-om.
2. Landing page (`/`) — najveći ROI, prva stvar koju svi vide.
3. `/cenovnik` — potreban čim počneš da primaš prve korisnike.
4. Auth handoff sa app-om (CTA dugmad, query parametri).
5. `/funkcionalnosti` — detaljnija stranica, može ići paralelno sa app razvojem.
6. `/baza-znanja` + 3-5 startnih članaka — SEO se gradi sporo, što pre počneš to bolje.
7. `/alati` (kalkulatori) — jak organic-traffic magnet, ali zahteva da rules-engine bude stabilan u app-u prvo (da ne dupliraš logiku koja će se menjati).
8. `/za-racunovodje` — kad app strana za računovođe (accountant panel) bude dovoljno zrela da je pokažeš.
9. `/o-nama`, `/kontakt`, pravne strane — brzo, nisu blokirajuće.

---

Reci mi ako želiš da uđem dublje u bilo koji deo — npr. da napravim konkretan wireframe/HTML skicu landing page-a, detaljan copy za hero sekciju, ili Tailwind config sa tačnim tokenima iz blueprinta.
