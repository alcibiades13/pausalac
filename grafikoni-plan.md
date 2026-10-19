# Plan: Grafikoni i vizualizacije u aplikaciji

Referenca za implementaciju — bazirano na `Pausalac.md` (master prompt) i `pausalac-blueprint.md`. Cilj: dodati grafikone tamo gde stvarno pomažu razumevanju finansijskog stanja, bez da aplikacija postane "admin template pretrpan karticama i grafikonima" (blueprint 4.8) — to je eksplicitna zabrana koju treba imati na umu kroz ceo ovaj rad, ne samo kao formalnost.

---

## 0. Pravilo pre svega ostalog: grafikon ne sme biti sopstveni izvor istine

Ranije smo identifikovali da je najveći arhitektonski rizik u projektu ako dashboard, KPO i limiti računaju iz tri različita mesta. Grafikoni su tačno mesto gde se taj rizik najlakše ponovi — lako je napisati "brz" agregacioni upit u frontend-u ili u posebnom endpoint-u koji zaobiđe već postojeći `LimitService`/financial event sloj.

**Pravilo**: svaki grafikon mora povlačiti podatke iz **postojećih domain servisa** (`LimitService`, `InvoiceService`, KPO agregacije), ne iz novog, paralelnog upita napravljenog "samo za chart". Backend endpoint za grafikon je tanak wrapper oko iste logike koja već hrani dashborad karticu/KPO tabelu, ne nova implementacija te logike.

---

## 1. Gde grafikoni idu (mapirano na blueprint sekcije)

| Lokacija | Grafikon | Zašto | Blueprint referenca |
|---|---|---|---|
| Dashboard | Promet — trend linija/area, YTD sa poređenjem prošlog perioda | Odgovara na "Koliko sam zaradio?" vizuelno, ne samo brojem | 8, Revenue sekcija |
| Dashboard / Limiti | Progress vizuelizacija 6M limita (i 8M/365-day) sa projekcijom | Signature feature "Limit intelligence" — ne samo procenat, nego trend + projekcija | 7.2, blueprint 105 |
| Limiti (detaljna strana) | Istorija po mesecima + projektovana linija do kraja godine | "Šta ako?" kalkulator treba vizuelni kontekst, ne samo tabelu brojeva | 6.5 |
| KPO | Mesečni pregled prihoda (bar chart) iznad tabele, kao rezime | Tabela ostaje primarna (auditabilnost), chart je samo brzi pregled | 6.6 |
| Naplata/Fakture | Mini status breakdown (naplaćeno / na čekanju / kasni) — donut ili horizontalni stacked bar | Brz vizuelni odgovor "da li neko duguje" | 6.4, 8 (Outstanding invoices) |
| Accountant panel | Distribucija klijenata po statusu (OK / pažnja / kritično) — stacked bar ili slično | Računovođa treba brz pregled 100+ klijenata, ne listu | 13 |
| Klijent detalj | (V2, opciono) Mala sparkline istorije fakturisanja po klijentu | Nije prioritet za MVP grafikone — dodati tek ako ima vremena | 6.3 |

**Ono što NE dobija grafikon u ovoj fazi**: Obaveze (poreski kalendar je lista/rok, ne serija podataka), Dokumenti (nema smisla), Klijenti lista (tabela je dovoljna).

---

## 2. Izbor biblioteke

Ovo zaslužuje pažljiviju odluku nego "ubaci Chart.js", jer default izgled većine chart biblioteka je tačno onaj "generički admin template" stil koji blueprint zabranjuje (4.8, 118) — debele mrežaste linije, default tooltip stilovi, boje koje ne prate vaš design token set.

**Preporuka: dva nivoa, u zavisnosti od grafikona.**

### A) Signature grafikoni (revenue trend, limit projekcija) — custom SVG komponente
Za grafikone koji nose brend i pojavljuju se na dashboard-u (dakle, prvi utisak proizvoda), preporučujem **bespoke Vue komponente pisane direktno u SVG-u**, uz `d3-scale` i `d3-shape` kao **samo matematičke/geometrijske helpere** (skaliranje osa, generisanje path-a za liniju/area), bez da se koristi ceo D3 rendering model. Ovo daje potpunu kontrolu nad izgledom (boje iz design tokena, tačan font, tačan spacing, tačan tooltip stil) i drži bundle mali.

Razlog za ovaj pristup umesto gotove biblioteke: dashboard grafikon je jedno od retkih mesta gde vizuelni identitet stvarno nosi utisak "premium fintech proizvod" vs. "još jedan SaaS template" — vredi uložiti par dana više u custom komponentu nego prihvatiti default izgled biblioteke.

### B) Sekundarni grafikoni (KPO bar chart, status breakdown, accountant distribucija) — lagana biblioteka
Za manje istaknute, jednostavnije grafikone, gde brzina implementacije je bitnija od jedinstvenog vizuelnog potpisa, preporučujem **ApexCharts** (`vue3-apexcharts`) — razumna default estetika koja se lako prilagođava temom, dobra dokumentacija, podržava sve standardne tipove (bar, donut, stacked). Alternativa je `unovis` (moderniji, Vue-first, malo strmija kriva učenja).

**Ne preporučujem** Chart.js kao default izbor ovde — radi posao, ali njegov "canvas rendering" pristup otežava fine detalje stilizacije (custom tooltip pozicioniranje, precizni border-radius na barovima) koje ćete verovatno hteti kasnije.

---

## 3. Backend — šta treba dodati

Svaki grafikon treba **agregiran** endpoint, ne sirove podatke koje frontend sam sabira (isto pravilo kao "PDF generation backend treba da bude authoritative" iz sekcije 108 master prompta — primenjeno ovde na agregacije).

Predlog endpoint-a (nazivi ilustrativni, prilagoditi postojećoj REST konvenciji):

```
GET /api/dashboard/revenue-series?period=ytd&granularity=month
→ [{ month: "2026-01", amount: "450000.00", currency: "RSD" }, ...]

GET /api/limits/6m/history?year=2026
→ { current: "2840000.00", limit: "6000000.00", history: [...], projection: [...] }

GET /api/limits/8m365/history
→ (analogno gornjem, rolling 365-day varijanta)

GET /api/kpo/monthly-summary?year=2026
→ [{ month: "2026-01", products: "0.00", services: "450000.00", total: "450000.00" }, ...]

GET /api/invoices/status-breakdown
→ { paid: "1200000.00", pending: "300000.00", overdue: "629500.00" }

GET /api/accountant/clients/status-distribution
→ { ok: 108, attention: 14, critical: 4 }
```

Svi ovi endpoint-i treba da **pozivaju postojeće servise** (`LimitService.get_history()`, `InvoiceService.get_status_breakdown()`, itd.), ne da pišu novu SQL/ORM logiku direktno u view/serializer sloju.

**Projekcija za limite** — pošto je "šta ako" kalkulator i projekcija linija već pomenuta funkcija u blueprintu (6.5), vredi da se logika projekcije (linearna ekstrapolacija na osnovu trenutnog tempa, ili prosek poslednjih N meseci) implementira **jednom, u `LimitService`**, i koristi i za dashboard karticu (tekstualni "na ovom tempu dostićićeš limit do X") i za grafikon (linija projekcije) — isti izvor, dva prikaza.

---

## 4. Frontend — komponente za napraviti

```
components/charts/
  RevenueTrendChart.vue       — custom SVG, area/line, dashboard
  LimitProgressChart.vue      — custom SVG, radijalni ili linearni progress + projekcija
  KpoMonthlyBarChart.vue      — ApexCharts bar, KPO strana
  InvoiceStatusBreakdown.vue  — ApexCharts donut/stacked bar
  ClientStatusDistribution.vue — ApexCharts stacked bar, accountant panel
  ChartEmptyState.vue         — deljena komponenta za "nema još podataka"
  ChartSkeleton.vue           — deljena loading komponenta (skeleton, ne spinner — konzistentno sa "calm" UI principom)
```

Svaka chart komponenta prima **već agregirane podatke** kao prop (iz API poziva preko postojećeg store/composable sloja za server state) — ne radi sopstveni fetch niti sopstvenu agregaciju iz sirovih faktura.

---

## 5. Stanja koja svaki grafikon mora imati (Definition of Done, sekcija 122 master prompta — primenjeno na grafikone)

- **Loading** — skeleton u obliku samog grafikona (npr. bledi placeholder bars/linije), ne generički spinner.
- **Empty** — kad korisnik nema dovoljno podataka (npr. nova firma, nula faktura). Ne prikazuj prazan/slomljen chart — prikaži smislenu poruku ("Prikazaćemo trend čim izdaš par faktura") uz opciono ilustrativni placeholder chart sa 0 vrednostima.
- **Error** — ako agregacioni endpoint padne, jasna poruka + retry, ne tihi prazan prostor.
- **Jedna tačka podataka** — edge case koji se lako zaboravi: linijski chart sa samo jednom tačkom ne sme da izgleda slomljeno (nema linije, samo tačka + osa).
- **Negativne/nula vrednosti** — proveriti da li skala grafikona i dalje ima smisla ako je npr. promet 0 ili je stornirana faktura napravila negativan mesec.

Nijedan chart ne sme koristiti mock/placeholder podatke u produkciji (master prompt 124) — ako podataka nema, ide empty state, ne izmišljeni brojevi.

---

## 6. Formatiranje — sitno, ali kritično za finansijski proizvod

- RSD formatiranje: `1.234.567,89 RSD` (tačka za hiljade, zarez za decimale — srpski standard), ne engleski `1,234,567.89`.
- Y-osa na chart-ovima treba skraćene oznake za velike brojeve (`2.8M` umesto `2800000`), ali **tooltip na hover/tap mora prikazati pun tačan iznos** — finansijski podatak se nikad ne zaokružuje bez mogućnosti da se vidi tačna vrednost.
- Datumi na X-osi: mesec skraćeno na srpskom (`Jan, Feb, Mar...` ili `jan, feb, mar` — dogovoriti konzistentno sa ostatkom aplikacije), ne engleski meseci.

---

## 7. Mobile

- Dashboard revenue chart i limit progress moraju raditi na uskom ekranu — najverovatnije znači: manje X-osa labela (npr. prikazati svaki drugi mesec), touch-friendly tooltip (tap, ne samo hover).
- KPO bar chart i accountant distribution grafikoni mogu ostati desktop-prioritetni (blueprint 4.7 — desktop je za "masovni rad, KPO, analitiku, računovođe"), ali ne smeju biti potpuno skriveni na mobilnom — minimalno, prikazati kao horizontalno scroll-abilan chart ili pojednostavljenu verziju.

---

## 8. Redosled implementacije

1. **Backend agregacioni endpoint-i** (revenue series, limit history+projekcija, KPO monthly, status breakdown) — proveriti da svi koriste postojeće servise.
2. **`LimitProgressChart`** (custom SVG) — najviši prioritet, jer je limit intelligence signature feature.
3. **`RevenueTrendChart`** (custom SVG) — dashboard, drugi po vidljivosti.
4. **Empty/loading/error shared komponente** (`ChartEmptyState`, `ChartSkeleton`) — napraviti pre nego što se doda treći/četvrti chart, da se ne duplira logika.
5. **`KpoMonthlyBarChart`** i **`InvoiceStatusBreakdown`** (ApexCharts) — brže za implementirati, niži rizik.
6. **`ClientStatusDistribution`** (accountant panel) — poslednje, jer accountant panel generalno dolazi kasnije u MVP redosledu (blueprint 129, stavka 16).

---

## 9. Testovi koje treba pokriti

- Agregacioni endpoint vraća tačne sume za poznat test dataset (uporediti sa ručno izračunatom vrednošću).
- Projekcija limita daje razuman rezultat na rubnim slučajevima (0 transakcija, 1 transakcija, tačno na limitu, preko limita).
- Frontend komponenta korektno renderuje empty state kad API vrati praznu seriju.
- Formatiranje RSD i datuma je tačno u snapshot/unit testu za par reprezentativnih vrednosti (uklj. veliki broj, 0, negativan broj ako je moguć).

---

Ovo je dovoljno konkretno da se prosledi direktno Claude Code-u kao radni zadatak — redosled u sekciji 8 može poslužiti kao lista taskova. Javi ako želiš da razradim konkretan izgled/wireframe `LimitProgressChart`-a pre nego što se pređe na kod, pošto je to najosetljiviji vizuelni element od svih navedenih.
