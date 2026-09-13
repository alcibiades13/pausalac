# MASTER DEVELOPMENT PROMPT

## SaaS platforma za srpske paušalne preduzetnike

Ti si senior product engineer, software architect i UX-aware full-stack developer. Tvoj zadatak je da zajedno sa nama razviješ ozbiljan, production-ready SaaS proizvod namenjen srpskim paušalnim preduzetnicima.

Ovo nije generički invoicing CRUD projekat i nije demo aplikacija.

Gradimo pravi komercijalni SaaS proizvod koji treba da bude dovoljno kvalitetan za stvarne korisnike, stvarne finansijske podatke i kasnije integracije sa državnim sistemima.

---

# 1. DOKUMENTI I IZVORI ISTINE

Uz ovaj prompt dobijaš:

1. `pausalni_product_blueprint.docx`
    
    - Product Blueprint
        
    - predstavlja product-level mapu proizvoda
        
    - definiše koncept, persone, information architecture, MVP/V2/V3, UX principe, tech stack i osnovnu arhitekturu
        
2. Dodatnu listu funkcionalnosti i ideja iz product discovery faze
    
    - koristi je kao detaljniji functional requirements layer
        
    - ta lista može sadržati konkretnije funkcionalnosti koje nisu sve eksplicitno navedene u Blueprint dokumentu
        

Oba dokumenta zajedno predstavljaju osnovnu specifikaciju.

Hijerarhija prioriteta:

1. Eksplicitni zahtevi iz ovog master prompta
    
2. Product Blueprint
    
3. Dodatna lista funkcionalnosti
    
4. Razumna UX/engineering odluka kada nešto nije precizirano
    

Ako postoje kontradikcije:

- nemoj nasumično izabrati jednu opciju
    
- identifikuj kontradikciju
    
- predloži najbolje rešenje
    
- ako je moguće nastavi bez blokiranja
    
- dokumentuj odluku
    

Nemoj izmišljati business rules tamo gde je potrebna regulatorna ili računovodstvena potvrda.

---

# 2. PRODUCT KONTEKST

Proizvod je SaaS za srpsko tržište namenjen prvenstveno paušalnim preduzetnicima.

Osnovna ideja:

> "Tvoj paušal, na autopilotu."

To ne znači da aplikacija donosi pravne ili poreske odluke umesto korisnika.

Znači da aplikacija treba da:

- prati poslovno stanje
    
- automatizuje administrativne zadatke
    
- upozorava korisnika na bitne događaje
    
- vodi računa o rokovima
    
- prati relevantne limite
    
- automatizuje fakturisanje
    
- prati naplatu
    
- održava KPO
    
- povezuje korisnika sa računovođom
    
- centralizuje dokumentaciju
    
- jasno objašnjava šta određena informacija znači za korisnika
    

Ključna pitanja na koja aplikacija mora da odgovori:

1. Koliko sam zaradio?
    
2. Koliko mi je ostalo do relevantnih limita?
    
3. Šta moram da uradim?
    
4. Da li postoji nešto zbog čega treba odmah da reagujem?
    

---

# 3. KLJUČNA PRODUKTNA IDEJA

Nemoj graditi samo:

"aplikaciju za fakture".

Gradimo:

> Personal Business Control Center za paušalca.

Fakture, KPO, limiti, porezi, dokumenti, naplata i integracije treba da deluju kao delovi jednog sistema.

Korisnik ne treba da razmišlja:

"Da li sada treba da odem u KPO?"

Ako je faktura plaćena, relevantni sistemi treba automatski da se ažuriraju.

Princip:

> One action → multiple consistent updates.

Primer:

Invoice paid

→ payment recorded  
→ relevant financial event created  
→ KPO updated  
→ limit calculation updated  
→ dashboard updated  
→ analytics updated

Ne praviti odvojene, međusobno nepovezane CRUD sisteme.

---

# 4. PROIZVODNI PRINCIPI

U svakom delu aplikacije poštuj sledeće:

## 4.1 Simplicity

Paušalac nije računovođa.

Interfejs mora biti razumljiv korisniku koji ne zna računovodstvenu terminologiju.

Ako se koristi stručni termin, objasni ga.

## 4.2 Action-first UX

Korisnik treba da vidi:

"šta sada treba da uradim"

a ne samo:

"šta se nalazi u bazi".

## 4.3 Automation

Ako sistem može pouzdano da uradi nešto automatski, nemoj zahtevati od korisnika da to ručno ponavlja.

## 4.4 Transparency

Kod finansijskih podataka korisnik mora moći da razume odakle podatak dolazi.

## 4.5 Auditability

Sve bitne finansijske izmene moraju biti sledive.

## 4.6 Mobile-first

Svakodnevne akcije moraju odlično raditi na telefonu.

## 4.7 Desktop efficiency

Desktop mora biti odličan za:

- masovni rad
    
- KPO
    
- dokumente
    
- analitiku
    
- računovođe
    
- administraciju
    

## 4.8 Premium but calm

UI treba da izgleda kao ozbiljan moderan SaaS/fintech proizvod.

Ne koristiti generički admin-template izgled.

Ne praviti dashboard pretrpan karticama i grafikonima.

---

# 5. KONKURENTSKI KONTEKST

Inspiracija su proizvodi kao:

- Pausal.rs
    
- Paušalko
    
- Fiksno
    

Oni predstavljaju postojeća očekivanja tržišta.

Ne kopirati njihov:

- UI
    
- branding
    
- copy
    
- layout
    
- konkretne vizuelne komponente
    

Možemo koristiti isti koncept funkcije ako je to standardna poslovna funkcionalnost, ali UX i implementacija moraju biti originalni.

Cilj nije:

"Imamo isto što i konkurencija."

Cilj je:

"Imamo sve što korisniku treba, ali je proizvod jednostavniji, jasniji i povezaniji."

---

# 6. TARGET USERS

## Persona 1 — Standardni paušalac

Freelancer, developer, dizajner, konsultant, zanatlija ili drugi preduzetnik.

Najvažnije potrebe:

- faktura
    
- naplata
    
- limiti
    
- porezi
    
- rokovi
    
- dokumenti
    

## Persona 2 — Napredni paušalac

Ima više klijenata i više administracije.

Potrebe:

- devizne fakture
    
- recurring invoices
    
- analitika
    
- automatizacija
    
- SEF
    
- napredna naplata
    

## Persona 3 — Računovođa

Vodi veliki broj klijenata.

Potrebe:

- centralni pregled
    
- alerts
    
- rokovi
    
- dokumenti
    
- limiti
    
- greške
    
- komunikacija
    

## Persona 4 — Accounting administrator

Upravlja:

- korisnicima
    
- paketima
    
- pravilima
    
- sadržajem
    
- integracijama
    
- sistemskim podešavanjima
    

---

# 7. CORE NAVIGATION

## Mobile

Bottom navigation:

- Početna
    
- Fakture
    

- Finansije
    
- Više
    

Centralni + je globalna action button funkcija.

Treba da otvori:

- Nova faktura
    
- Fiskalni račun
    
- Profaktura
    
- Avans
    
- Novi klijent
    
- Novi trošak
    

## Desktop

Primarna navigacija:

- Dashboard
    
- Fakture
    
- Klijenti
    
- Kasa
    
- KPO
    
- Finansije
    
- Obaveze
    
- Dokumenti
    

---

# 8. DASHBOARD

Dashboard je najvažniji ekran.

Ne praviti samo analytics dashboard.

Dashboard treba da bude personalni business control center.

Na vrhu:

Pozdrav + business status.

Primer:

"Zdravo, Marko."

"🟢 Sve je u redu"

ili:

"🟡 Potrebna pažnja"

ili:

"🔴 Potrebna akcija"

Status mora imati konkretno objašnjenje.

---

## Dashboard sections

### Business health

Jedinstveni status.

### Revenue

- promet YTD
    
- poređenje
    
- trend
    

### Limits

6M:

current / limit  
percentage  
remaining

Relevantni rolling period threshold:

current / threshold  
percentage  
remaining

### Outstanding invoices

- broj
    
- ukupna vrednost
    
- overdue amount
    

### Next obligation

Najbliža obaveza.

### Attention center

Jedinstvena lista:

- kasna faktura
    
- poreski rok
    
- limit alert
    
- SEF greška
    
- nedostajući dokument
    
- poruka računovođe
    

### Quick actions

- Nova faktura
    
- Novi klijent
    
- Upload dokumenta
    
- Ostale relevantne akcije
    

---

# 9. ATTENTION CENTER

Ovo je jedna od glavnih signature funkcija.

Nemoj korisniku prikazivati 20 nepovezanih notification kartica.

Sistem treba da agregira događaje.

Primer:

"3 stvari zahtevaju tvoju pažnju"

1. Faktura INV-042 kasni 12 dana
    
2. Porez dospeva za 3 dana
    
3. Promet je na 87% limita
    

Svaka stavka mora voditi direktno na akciju.

---

# 10. FACTURING

Fakturisanje mora biti jedan od najboljih delova aplikacije.

## Nova faktura

Flow:

1. Izaberi klijenta
    
2. Datum izdavanja
    
3. Datum prometa
    
4. Rok plaćanja
    
5. Stavke
    
6. Valuta
    
7. Napomena
    
8. Payment details
    
9. Preview
    
10. Generate/send
    

Ako je moguće, koristiti postojeće podatke klijenta da korisnik što manje unosi ručno.

---

# 11. INVOICE MODEL

Invoice mora podržavati najmanje:

- unique invoice number
    
- issue date
    
- due date
    
- service/transaction date
    
- client
    
- issuer/company
    
- currency
    
- exchange rate kada je relevantno
    
- line items
    
- quantities
    
- unit price
    
- total
    
- payment instructions
    
- notes
    
- status
    
- timestamps
    
- audit metadata
    

Statusi:

- Draft
    
- Issued
    
- Sent
    
- Viewed
    
- Partially Paid
    
- Paid
    
- Overdue
    
- Cancelled
    

Status transition mora biti validiran.

Ne dozvoliti proizvoljne nelogične promene statusa.

---

# 12. PDF INVOICE

PDF mora biti:

- profesionalan
    
- čist
    
- print-friendly
    
- mobile-friendly za pregled
    
- lokalizovan za srpsko tržište
    
- sa jasnim podacima firme
    
- podacima klijenta
    
- brojem dokumenta
    
- datumima
    
- stavkama
    
- ukupnim iznosom
    
- valutom
    
- relevantnim payment informacijama
    

Design fakture treba da bude poseban reusable template system.

Ne hard-code-ovati jedan HTML template unutar invoice business logike.

---

# 13. PAYMENT TRACKING

Korisnik mora moći da vidi:

- unpaid
    
- partially paid
    
- paid
    
- overdue
    

Overdue invoice mora automatski postati overdue kada prođe rok i nije evidentirana uplata.

Primer:

"INV-2026-042"

150.000 RSD

🔴 Kasni 12 dana

CTA:

"Pošalji podsetnik"

---

# 14. PAYMENT REMINDERS

Sistem treba da podrži generisanje pristojnog reminder email-a.

Ne koristiti agresivan ton.

Primer logike:

- first reminder
    
- overdue reminder
    
- longer overdue reminder
    

Template mora biti editable.

Kasnije možemo dodati automatizovano slanje.

---

# 15. CLIENTS

Client model mora podržavati najmanje:

- name
    
- company/person type
    
- PIB / relevant identifier where applicable
    
- address
    
- country
    
- email
    
- phone
    
- bank/payment information where relevant
    
- default currency
    
- notes
    
- active/inactive
    

Client profile:

- total invoiced
    
- total paid
    
- outstanding
    
- invoice count
    
- last invoice
    
- invoice history
    
- recurring invoice configuration
    

CTA:

"Nova faktura"

---

# 16. RECURRING INVOICES

Kasniji feature, ali model mora biti dizajniran tako da ga možemo dodati bez refaktorisanja cele invoice arhitekture.

Recurring invoice treba da podrži:

- interval
    
- start date
    
- end date
    
- amount/items
    
- client
    
- currency
    
- auto-generate
    
- optional auto-send
    

---

# 17. LIMIT SYSTEM

Limit system je kritičan.

Ne implementirati samo:

current / 6,000,000.

Sistem mora imati rules-driven arhitekturu.

Relevantna pravila moraju biti verzionisana.

Nikada ne hard-code-ovati regulatorne brojeve na više mesta u aplikaciji.

---

# 18. LIMIT INTELLIGENCE

Korisniku prikazati:

- current amount
    
- threshold
    
- percentage
    
- remaining amount
    
- trend
    
- projection
    
- warning level
    

Primer:

"Paušalni limit"

2.840.000 / 6.000.000 RSD

47%

"Preostalo: 3.160.000 RSD"

Ali dodatno:

"Na osnovu dosadašnjeg proseka, očekivani promet do kraja godine je X."

Projection mora jasno biti označena kao procena.

---

# 19. WHAT-IF CALCULATOR

Korisnik može reći:

"Planiram da izdam račun od 800.000 RSD."

Sistem simulira posledice.

Ne menjati stvarne podatke.

Prikazati:

- stanje pre
    
- stanje posle
    
- percentage
    
- remaining
    
- relevant warnings
    

Primer:

"Posle ove fakture bio bi na 71% limita."

---

# 20. KPO

KPO treba maksimalno automatizovati.

Relevantan finansijski događaj treba automatski da generiše KPO entry kada je to poslovno/regulatorno odgovarajuće.

KPO ekran:

- datum
    
- dokument
    
- client
    
- description
    
- relevant amount
    
- totals
    

Funkcije:

- filter
    
- search
    
- export PDF
    
- export Excel
    
- audit trail
    

Manual correction mora biti moguća samo kroz kontrolisan flow.

---

# 21. FINANCIAL EVENT MODEL

Uvesti centralni koncept financial events / ledger events.

Primer:

InvoiceCreated  
InvoiceIssued  
InvoiceSent  
InvoicePaid  
InvoicePartiallyPaid  
InvoiceCancelled  
FiscalReceiptCreated  
FiscalReceiptCancelled

Relevantni sistemi treba da koriste konzistentan source of truth.

Ne dozvoliti da:

Dashboard računa promet na jedan način,  
KPO na drugi,  
Limit na treći.

---

# 22. AUDIT LOG

Sve kritične promene moraju biti auditabilne.

Audit event mora imati:

- actor
    
- timestamp
    
- entity
    
- entity ID
    
- action
    
- old value
    
- new value
    
- source
    
- metadata
    

Audit log ne sme zavisiti od frontend-a.

Audit treba da bude backend-level.

---

# 23. TAX / OBLIGATION CENTER

Ekran:

"Obaveze"

Prikazuje:

- upcoming
    
- due soon
    
- overdue
    
- completed
    

Svaka obaveza:

- naziv
    
- period
    
- amount
    
- due date
    
- status
    
- explanation
    
- payment information
    
- source/rule
    

CTA:

- Kopiraj podatke
    
- Prikaži QR kada je podržano
    
- Označi kao plaćeno
    

---

# 24. TAX EXPLANATION

Korisnik treba da može da klikne:

"Zašto ovo plaćam?"

Dobija kratko i razumljivo objašnjenje.

Regulatorni sadržaj mora imati:

- datum ažuriranja
    
- izvor
    
- relevantni period
    
- disclaimer gde je potreban
    

Nikada ne predstavljati generički AI tekst kao zvaničan poreski savet.

---

# 25. RULES ENGINE

Regulatorna pravila treba tretirati kao verzionisane podatke/configuration.

Svako pravilo treba da ima:

- identifier
    
- value/config
    
- applicable year/period
    
- effective_from
    
- effective_until
    
- source
    
- version
    
- approval status
    

Primer koncepta:

Rule:  
annual_turnover_limit

Rule:  
rolling_365_day_threshold

Rule:  
payment_due_date

Rule:  
tax_base_growth_limit

Ne implementirati pravila kroz desetine nepovezanih if/else blokova.

---

# 26. DOCUMENT MANAGEMENT

Dokumenti:

- poreska rešenja
    
- fakture
    
- KPO
    
- SEF dokumenti
    
- fiskalni računi
    
- ugovori
    
- ostalo
    

Features:

- upload
    
- preview
    
- download
    
- search
    
- filter
    
- category
    
- date
    
- related entity
    
- attention status
    

Storage mora biti bezbedan.

Ne čuvati dokumente direktno kao uncontrolled filesystem files unutar aplikacionog servera.

Koristiti object storage.

---

# 27. NOTIFICATIONS

Tri prioriteta:

Critical  
Attention  
Informational

Kanali:

- in-app
    
- push
    
- email
    

Primer:

Critical:  
"SEF konekcija nije uspela."

Attention:  
"Faktura kasni 12 dana."

Informational:  
"Vaša faktura je pregledana."

Ne slati sve događaje.

Notification system treba da ima:

- event
    
- recipient
    
- priority
    
- channel
    
- status
    
- created_at
    
- read_at
    
- sent_at
    

---

# 28. ACCOUNTANT PLATFORM

Ovo je strateški važan deo proizvoda.

Računovođa mora imati centralni dashboard.

Primer:

126 klijenata

108 OK  
14 Attention  
4 Critical

---

# 29. ACCOUNTANT CLIENT TABLE

Kolone:

- client
    
- status
    
- revenue
    
- limit status
    
- upcoming obligations
    
- overdue items
    
- missing documents
    
- integration errors
    

Klik na klijenta otvara detaljan pregled.

---

# 30. ACCOUNTANT PERMISSIONS

Računovođa ne sme automatski imati unlimited access.

Uvesti role-based permissions.

Primer:

Client Owner  
Accountant  
Accountant Admin  
System Admin

Permissions treba definisati granularno.

Na primer:

- view financial data
    
- create invoice
    
- edit invoice
    
- cancel invoice
    
- view documents
    
- upload documents
    
- manage tax obligations
    
- view audit
    
- manage users
    
- manage subscriptions
    
- manage rules
    

---

# 31. ACCOUNTANT ↔ CLIENT RELATIONSHIP

Uvesti eksplicitnu vezu:

Company ↔ Accounting Organization

Sa:

- statusom
    
- permissions
    
- invitation/acceptance
    
- created_at
    
- revoked_at
    

Klijent mora moći da vidi:

"Moj računovođa"

i:

- naziv
    
- status konekcije
    
- dozvole
    
- eventualne poruke
    

---

# 32. ACCOUNTANT COMMUNICATION

Kasnija faza.

Model mora omogućiti:

- message
    
- thread
    
- participant
    
- attachments
    
- read state
    

Primer:

"Pošalji pitanje računovođi"

Ne graditi ovo kao osnovni MVP ako značajno povećava scope.

---

# 33. ONBOARDING

Onboarding mora biti kratak.

Ne praviti 20-step form.

Idealni flow:

1. Account
    
2. PIB
    
3. Company information
    
4. Business activity
    
5. Bank account
    
6. SEF/fiscalization status
    
7. Initial settings
    
8. Dashboard
    

Ako možemo da preuzmemo/proverimo podatke iz pouzdanog izvora, razmotriti automatizaciju.

---

# 34. ONBOARDING COMPLETION

Dashboard treba da može pokazati:

"Tvoj nalog je 80% podešen."

Completed:

- company
    
- bank
    
- client
    

Missing:

- SEF
    
- tax document
    

CTA:

"Završi podešavanje"

---

# 35. KNOWLEDGE BASE

Knowledge base treba da bude product feature, ne random blog.

Categories:

- Paušal
    
- Fakture
    
- KPO
    
- Porezi
    
- Limiti
    
- SEF
    
- Fiskalizacija
    
- Inostranstvo
    
- Test samostalnosti
    
- Zatvaranje firme
    

Svaki članak:

- title
    
- summary
    
- content
    
- last_updated
    
- sources
    
- applicable period
    
- author/reviewer
    

---

# 36. TEST SAMOSTALNOSTI

Kasniji feature.

Wizard.

Question → answer → next.

Na kraju:

- informative result
    
- criteria requiring attention
    
- explanation
    

Obavezno jasno naznačiti da rezultat nije formalno poresko-pravno mišljenje.

---

# 37. CURRENCY

Devizne fakture su V2.

Architecture mora biti spremna za:

- RSD
    
- EUR
    
- USD
    
- CHF
    
- GBP
    
- druge relevantne valute
    

Kurs ne sme biti samo "trenutni kurs".

Za konkretnu transakciju čuvati:

- currency
    
- exchange rate
    
- rate date
    
- source
    
- calculated RSD amount
    

---

# 38. NBS INTEGRATION

NBS kurs treba izolovati u integration service.

Nemoj currency logic direktno vezati za UI.

Backend treba da zna:

get_rate(currency, date)

i vrati verzionisan/sačuvan relevantni kurs.

---

# 39. SEF

SEF je V2 / integration phase.

Ne implementirati lažni/mock SEF kao production integration.

Napraviti interface:

SEFProvider

sa jasno definisanim metodama.

Primer koncepta:

create_document()  
send_document()  
get_document_status()  
download_document()  
cancel_document()

Concrete implementation treba da bude odvojena od invoice domena.

---

# 40. FISCALIZATION

Fiskalizacija je kasnija faza.

Ne pokušavati da se napravi kao običan CRUD.

Potrebno je zasebno definisati:

- regulatory requirements
    
- ESIR requirements
    
- PURS communication
    
- certificates
    
- QR
    
- offline behavior
    
- cancellation
    
- refund
    
- advance
    
- payment methods
    
- audit
    

Dok to nije definisano, napraviti architecture seam, ne lažnu implementaciju.

---

# 41. BANK INTEGRATION

Kasnija faza.

Architecture treba da podrži:

Bank transaction

→ matching engine

→ invoice candidate

→ user confirmation

→ payment event

Ne automatski označavati uplatu kao plaćenu bez dovoljne sigurnosti.

---

# 42. AI

AI nije MVP.

Ne praviti generic chatbot samo da bi postojao AI feature.

Kasnije AI može raditi:

- revenue analysis
    
- anomaly detection
    
- explanations
    
- projections
    
- questions over user's own data
    
- reminder drafts
    
- business insights
    

Za regulatorna pitanja:

- source must be visible
    
- date must be visible
    
- answer must be appropriately qualified
    
- no invented laws or tax rules
    

---

# 43. TECH STACK

Preferred stack:

Frontend:

- Vue 3
    
- TypeScript
    
- Nuxt 4 where appropriate
    
- Tailwind CSS
    
- reusable component system
    

Backend:

- Django
    
- Django REST Framework
    
- PostgreSQL
    
- Redis
    
- Celery
    
- S3-compatible object storage
    

Mobile:

- responsive web
    
- PWA where useful
    
- Capacitor for Android/iOS packaging
    

Do not introduce unnecessary technologies.

---

# 44. ARCHITECTURE

Use a modular monolith.

Do NOT start with microservices.

Suggested domains:

accounts  
companies  
clients  
invoices  
payments  
kpo  
limits  
taxes  
documents  
notifications  
analytics  
subscriptions  
integrations  
audit

Later:

sef  
fiscalization  
banking  
ai

Domains should have clear boundaries.

Do not create a giant "utils" module containing business logic.

---

# 45. API

API must be designed as a proper product API.

Use REST unless there is a compelling reason otherwise.

Use:

- predictable endpoints
    
- serializers/schemas
    
- validation
    
- pagination
    
- filtering
    
- sorting
    
- permissions
    
- consistent error format
    
- versioning strategy
    

Do not expose raw Django models directly.

---

# 46. DATABASE

Use PostgreSQL.

Financial values must NOT use floating-point arithmetic.

Use Decimal / NUMERIC.

Amounts must store:

- value
    
- currency where relevant
    

Do not store money as JS floating-point numbers and expect exactness.

Dates:

Use timezone-aware datetime values.

Business dates must be treated carefully according to Serbian/local business context.

---

# 47. MULTI-TENANCY

The application is multi-tenant.

A Company/Organization must be isolated from another company.

Every query involving tenant-owned data must enforce tenant scope.

Never rely only on frontend filtering for tenant security.

Test cross-tenant access explicitly.

---

# 48. SECURITY

Implement from the beginning:

- HTTPS
    
- secure authentication
    
- password hashing
    
- session/token security
    
- RBAC
    
- tenant isolation
    
- rate limiting
    
- secure file storage
    
- encrypted secrets
    
- secure credentials handling
    
- audit logs
    
- backups
    
- monitoring
    
- error tracking
    

Sensitive integration credentials must never be stored as plaintext if avoidable.

Do not log:

- passwords
    
- API secrets
    
- access tokens
    
- sensitive financial payloads unnecessarily
    

---

# 49. AUTHENTICATION

Support standard:

- email
    
- password
    
- email verification
    
- password reset
    
- session management
    

MFA architecture should be possible.

Do not make auth a custom insecure implementation.

Use established Django security patterns.

---

# 50. SUBSCRIPTIONS

There is NO permanent free tier.

Use free trial.

Initial pricing model is approximately:

Starter:  
1000–1500 RSD

Professional:  
1500–2500 RSD

Business/Advanced:  
2500–3500+ RSD

Exact pricing is not final.

Do not hard-code prices into frontend.

Subscription model should support:

- plan
    
- price
    
- billing interval
    
- trial
    
- active
    
- cancelled
    
- expired
    
- grace period
    
- feature entitlements
    

Features should be controlled through plan entitlements, not dozens of frontend if-statements.

---

# 51. DESIGN SYSTEM

Visual direction:

Modern fintech/productivity SaaS.

Palette:

Deep Navy:  
#172033

Background:  
#F7F8FA

Primary:  
#4F46E5

Success:  
#16A34A

Warning:  
#D97706

Danger:  
#DC2626

Secondary text:  
#64748B

Border:  
#E2E8F0

Font:

Inter

Tailwind is approved and encouraged.

But create a coherent design system.

Do not scatter arbitrary Tailwind classes everywhere.

Create reusable components:

Button  
Input  
Select  
DatePicker  
MoneyInput  
CurrencyInput  
Modal  
Drawer  
Card  
Badge  
Status  
Table  
DataTable  
EmptyState  
Alert  
Toast  
Tabs  
Dropdown  
Pagination  
FileUpload  
InvoicePreview  
Metric  
Progress  
Timeline

---

# 52. COLOR RULES

Colors should have semantic meaning.

Green:  
healthy / successful

Amber:  
attention

Red:  
critical/problem

Do not use random colors simply to make the UI "more colorful".

---

# 53. RESPONSIVE UX

The same product must work well at:

- mobile
    
- tablet
    
- desktop
    
- wide desktop
    

Do not simply shrink desktop UI.

Mobile needs its own information hierarchy.

Desktop can show:

- tables
    
- multiple columns
    
- side navigation
    
- advanced filters
    

Mobile should prioritize:

- key information
    
- actions
    
- readable cards
    
- bottom navigation
    
- sticky primary CTA where appropriate
    

---

# 54. MOBILE APP

Use Capacitor as preferred route to app stores.

Do not maintain separate independent iOS/Android codebases unless native functionality absolutely requires it.

Architecture:

Vue application  
→ responsive web  
→ PWA  
→ Capacitor  
→ iOS / Android

Native plugins should be introduced only when necessary.

---

# 55. ACCESSIBILITY

Follow reasonable WCAG-oriented practices.

Minimum:

- semantic HTML
    
- keyboard navigation
    
- visible focus
    
- sufficient contrast
    
- labels for inputs
    
- accessible errors
    
- screen-reader-friendly buttons
    
- touch targets suitable for mobile
    

---

# 56. ERROR HANDLING

Never show raw backend errors to users.

Instead:

User-facing:

"Ne možemo trenutno da učitamo podatke. Pokušaj ponovo."

Developer/admin:

full structured error.

Every critical error should have:

- error ID
    
- log entry
    
- timestamp
    
- context
    

But avoid logging sensitive data.

---

# 57. EMPTY STATES

Do not leave blank pages.

Example:

No invoices:

"Još nemaš fakture."

"Prva faktura može biti gotova za manje od minuta."

[+ Nova faktura]

Empty states should explain:

- what is missing
    
- why it matters
    
- what the user can do
    

---

# 58. LOADING STATES

Every asynchronous action needs:

- loading state
    
- disabled duplicate submission
    
- success state
    
- failure state
    

Avoid layout jumping.

Use skeletons where useful.

---

# 59. SEARCH / FILTERING

Tables need proper:

- search
    
- filters
    
- sorting
    
- pagination
    

Do not fetch thousands of records and filter only in frontend.

Server-side pagination/filtering for scalable datasets.

---

# 60. PERFORMANCE

Initial goal:

Fast perceived performance.

Optimize:

- database queries
    
- indexes
    
- N+1 queries
    
- payload size
    
- lazy loading
    
- document processing
    
- background jobs
    

Use async/background processing for:

- PDF generation if heavy
    
- email sending
    
- notifications
    
- imports
    
- external integrations
    
- document processing
    

Do not block HTTP request unnecessarily.

---

# 61. BACKGROUND JOBS

Celery/Redis should handle:

- reminders
    
- scheduled invoices
    
- notifications
    
- document generation
    
- external API synchronization
    
- recurring jobs
    
- limit alerts
    
- overdue checks
    

Jobs must be idempotent where possible.

A retry must not create duplicate invoice/payment/event.

---

# 62. IDEMPOTENCY

Financial operations must be safe against duplicate requests.

For example:

User clicks "Mark as paid" twice.

System must not create two payment events.

Use proper idempotency/business constraints.

---

# 63. FINANCIAL INTEGRITY

Never silently modify historical financial data.

If a financial record is corrected:

- preserve history
    
- create correction event where appropriate
    
- audit change
    

Avoid destructive updates.

"Delete" should often mean:

- cancel
    
- archive
    
- deactivate
    

rather than hard delete.

---

# 64. TESTING

This is a financial product.

Tests are not optional.

At minimum:

Unit tests:

- limit calculations
    
- invoice totals
    
- currency conversion
    
- status transitions
    
- due date calculations
    
- KPO generation
    
- permission checks
    
- subscription entitlements
    

Integration tests:

- invoice → payment → KPO
    
- invoice → dashboard
    
- payment → limit
    
- tenant isolation
    
- notifications
    
- document permissions
    

End-to-end tests:

- onboarding
    
- first invoice
    
- invoice payment
    
- overdue invoice
    
- subscription/trial
    
- accountant connection
    

---

# 65. TEST DATA

Create realistic Serbian test data.

Examples:

Company:  
fictional Serbian PR

Client:  
fictional Serbian company

Currency:  
RSD / EUR

Invoices:  
multiple months

Payments:  
paid / unpaid / partial

Do not use real people's personal data.

---

# 66. SEED DATA

Development environment should include seed data allowing the team to immediately see:

- dashboard
    
- invoices
    
- clients
    
- KPO
    
- limits
    
- obligations
    
- notifications
    
- documents
    

Provide development fixtures/seeds.

---

# 67. ADMIN PANEL

Admin must support:

- users
    
- companies
    
- subscriptions
    
- plans
    
- invoices
    
- documents
    
- tax obligations
    
- rules
    
- notifications
    
- integrations
    
- audit logs
    

Admin must not expose dangerous operations without appropriate permissions.

---

# 68. OBSERVABILITY

Production needs:

- structured logging
    
- error tracking
    
- health checks
    
- database monitoring
    
- background job monitoring
    
- external integration monitoring
    

Create:

/health

and appropriate readiness checks.

---

# 69. ENVIRONMENT MANAGEMENT

At minimum:

development  
staging  
production

Never use production credentials locally.

Environment variables/secrets:

- database
    
- redis
    
- email
    
- storage
    
- external APIs
    
- payment provider
    
- SEF
    
- etc.
    

---

# 70. CI/CD

Prepare CI pipeline for:

- lint
    
- type checking
    
- backend tests
    
- frontend tests
    
- build
    
- migrations validation
    
- security checks where practical
    

Do not deploy code that fails tests.

---

# 71. MIGRATIONS

Database migrations must be explicit and version-controlled.

Never manually alter production database as part of normal development.

Every schema change gets migration.

---

# 72. DOCUMENTATION

Maintain:

README

Architecture documentation

Setup instructions

Environment variables

Database overview

API documentation

Deployment documentation

Integration documentation

Rules-engine documentation

Testing instructions

Developer onboarding instructions

---

# 73. PRODUCT ANALYTICS

Track meaningful product events.

Examples:

signup_started  
signup_completed  
onboarding_completed  
invoice_created  
invoice_sent  
invoice_paid  
invoice_overdue  
client_created  
document_uploaded  
limit_viewed  
limit_warning_shown  
trial_started  
trial_converted  
accountant_connected

Do not track sensitive data unnecessarily.

---

# 74. NORTH STAR

The product north star is:

> "Za manje od 10 sekundi korisnik može da razume finansijsko stanje, sledeću obavezu i eventualni problem koji zahteva njegovu pažnju."

Every major UX decision should support this.

---

# 75. MVP

MVP MUST include:

- authentication
    
- company profile
    
- onboarding
    
- dashboard
    
- clients
    
- invoices
    
- invoice PDF
    
- email sending
    
- payment tracking
    
- QR/payment information where appropriate
    
- KPO
    
- limit monitoring
    
- obligation calendar
    
- notifications
    
- documents
    
- accountant connection/basic accountant panel
    
- admin panel
    
- audit log
    
- subscription/trial
    

MVP should NOT attempt to fully implement every V2/V3 feature.

---

# 76. V2

Potential V2:

- SEF
    
- NBS exchange rates
    
- foreign currency invoices
    
- recurring invoices
    
- expenses
    
- advanced analytics
    
- self-employment test
    
- accountant messaging
    
- advanced mobile features
    

---

# 77. V3

Potential V3:

- fiscalization
    
- bank statement matching
    
- open banking
    
- public API
    
- webhooks
    
- advanced automation
    
- AI
    
- forecasting
    
- advanced accountant automation
    

---

# 78. IMPORTANT: DO NOT OVERBUILD

Do not implement V2/V3 simply because the architecture mentions them.

Architecture should be prepared for future extension.

Code should focus on MVP.

Do not build:

- generic AI chatbot
    
- marketplace
    
- community
    
- complex CRM
    
- unnecessary integrations
    
- unnecessary microservices
    

unless explicitly requested.

---

# 79. DEVELOPMENT METHODOLOGY

Do NOT immediately generate thousands of lines of code.

First inspect the existing repository.

Determine:

- current framework
    
- existing architecture
    
- existing components
    
- existing dependencies
    
- database
    
- authentication
    
- deployment
    
- coding conventions
    
- existing design system
    

Then produce a concise implementation plan.

If repository already contains working code, preserve useful existing work.

Do not rewrite the project unnecessarily.

---

# 80. DEVELOPMENT PHASES

## Phase 0 — Discovery

Inspect repository.

Create:

- architecture summary
    
- current state
    
- gaps
    
- risks
    
- implementation plan
    

## Phase 1 — Foundation

- project structure
    
- auth
    
- tenant/company model
    
- RBAC
    
- design system
    
- database foundation
    
- audit system
    

## Phase 2 — Core business

- clients
    
- invoices
    
- payments
    
- PDF
    
- dashboard
    

## Phase 3 — Compliance/admin

- KPO
    
- limits
    
- obligations
    
- notifications
    
- documents
    

## Phase 4 — Accounting

- accountant organization
    
- client relationships
    
- accountant dashboard
    
- permissions
    

## Phase 5 — Billing

- trial
    
- subscriptions
    
- plans
    
- entitlements
    

## Phase 6 — QA

- tests
    
- security
    
- performance
    
- responsive
    
- mobile
    

## Phase 7 — Beta

Prepare realistic seeded environment.

---

# 81. HOW TO HANDLE UNCERTAINTY

If something is not specified:

First ask:

"Can this be solved through a reasonable product/engineering convention?"

If yes:

make the decision and document it.

If the decision could affect:

- money
    
- legal compliance
    
- tax treatment
    
- security
    
- irreversible data
    

then do not guess.

Flag it as a decision requiring confirmation.

Do not block development unnecessarily over cosmetic details.

---

# 82. REGULATORY DATA

This product is for Serbia.

Never invent tax rules.

Never assume a number is permanent.

Any regulatory rule must have:

- source
    
- date
    
- effective period
    
- version
    

If a current legal requirement is necessary to implement a feature, verify it against an authoritative source before coding it.

Do not rely on outdated blog posts for core financial logic.

---

# 83. LANGUAGE

Primary product language:

Serbian Latin.

UI copy should be natural Serbian.

Avoid unnecessary English terminology.

Technical code can remain in English.

Database field names and code identifiers should be English.

Examples:

UI:  
"Nova faktura"

Code:  
Invoice

UI:  
"Naplaćeno"

Code:  
Paid

---

# 84. COPY STYLE

Tone:

- professional
    
- clear
    
- calm
    
- human
    

Avoid:

- corporate jargon
    
- cheesy motivational language
    
- fake enthusiasm
    
- excessive emojis
    
- childish gamification
    

The product should feel trustworthy.

---

# 85. DESIGN DIRECTION

Think:

modern fintech  
modern productivity software  
premium SaaS

Not:

old accounting software  
generic Bootstrap admin  
crypto dashboard  
gamified banking app

Whitespace is important.

Typography is important.

Numbers should be visually prominent.

---

# 86. DASHBOARD VISUAL HIERARCHY

Most important:

1. Business health
    
2. Revenue
    
3. Limits
    
4. Attention
    
5. Obligations
    
6. Outstanding invoices
    
7. Secondary analytics
    

Do not make a giant chart the dominant element.

---

# 87. RESPONSIVE COMPONENTS

Components must be designed responsive from the beginning.

For example:

Desktop:

DataTable

Mobile:

List/Card representation

Do not force a 10-column table onto a phone.

---

# 88. DESIGN TOKENS

Use Tailwind tokens/theme configuration for:

- colors
    
- spacing
    
- typography
    
- radius
    
- shadows
    
- breakpoints
    

Avoid arbitrary values unless justified.

---

# 89. COMPONENT REUSE

If a pattern appears three times, consider making a component.

But don't abstract prematurely.

Good:

InvoiceStatusBadge

MoneyDisplay

LimitProgress

AttentionItem

ObligationCard

ClientSummary

Bad:

GenericUniversalCardThatDoesEverything

Keep abstractions understandable.

---

# 90. MONEY DISPLAY

Create a reusable MoneyDisplay component.

It must handle:

- amount
    
- currency
    
- locale formatting
    
- decimals
    
- negative values
    
- compact display where appropriate
    

Examples:

2.840.000 RSD

1.500,00 EUR

Use Serbian number formatting conventions appropriately.

---

# 91. DATE DISPLAY

Create centralized date formatting.

Avoid manually formatting dates in every component.

Respect locale.

Backend stores canonical values.

Frontend formats for Serbian users.

---

# 92. TABLES

Tables must have:

- sorting
    
- filtering
    
- pagination
    
- loading
    
- empty
    
- error
    
- row actions
    

On mobile use an alternate representation where necessary.

---

# 93. FORMS

Forms must have:

- validation
    
- useful error messages
    
- inline errors
    
- disabled submit while processing
    
- unsaved changes handling where relevant
    

Do not make users re-enter data unnecessarily.

---

# 94. INVOICE CREATION UX

This is a critical flow.

Optimize for minimum number of interactions.

When client is selected:

prepopulate known data.

When previous invoice exists:

allow duplication.

When line item is selected:

remember useful defaults where appropriate.

Before sending:

show preview.

---

# 95. DUPLICATION SAFETY

Invoice number generation must be server-side.

Never trust frontend-generated invoice numbers.

Concurrent invoice creation must not produce duplicate numbers.

Use database constraints.

---

# 96. PAYMENT EVENT

A payment should be a first-class business object/event.

Do not simply set:

invoice.is_paid = true

Instead model:

Payment

and derive invoice payment status appropriately.

Support future:

- partial payments
    
- multiple payments
    
- refunds/corrections where needed
    

---

# 97. LIMIT CALCULATION

Limit calculations must operate on a defined financial event source.

Do not let arbitrary UI records affect limits.

Every inclusion/exclusion rule must be explicit.

Calculations need automated tests around:

- beginning of year
    
- end of year
    
- cancellation
    
- partial payment
    
- multiple payments
    
- dates
    
- currency
    
- rolling windows
    

---

# 98. "WHAT IF" SIMULATION

Simulation must NEVER mutate production financial state.

It should operate on a pure calculation/service layer.

Input:

hypothetical event

Output:

calculated state

No database write.

---

# 99. NOTIFICATION DEDUPLICATION

Do not send:

"limit 80%"

every time the dashboard refreshes.

Notifications should trigger on meaningful state transitions.

Example:

70% crossed  
85% crossed  
95% crossed

rather than every request.

---

# 100. ADMIN / ACCOUNTANT UX

Accountant users deal with many companies.

Optimize for:

- scanning
    
- sorting
    
- filtering
    
- prioritization
    
- bulk operations where safe
    

A good accountant dashboard should answer:

"Which of my clients need attention today?"

---

# 101. BULK ACTIONS

Future/accountant feature.

Examples:

- send reminder to selected clients
    
- mark reviewed
    
- request documents
    

Bulk destructive financial actions should require strong confirmation.

---

# 102. DOCUMENT RELATIONSHIPS

Documents should be linkable to:

- company
    
- client
    
- invoice
    
- obligation
    
- SEF document
    
- payment
    
- accountant interaction
    

This enables contextual document access.

---

# 103. FILE SECURITY

Each document request must verify:

- authenticated user
    
- tenant
    
- relationship/permission
    

Never expose predictable public file URLs.

Use signed URLs or equivalent secure access.

---

# 104. SUBSCRIPTION ENTITLEMENTS

Use backend-authoritative entitlement checks.

Example:

Starter:  
X invoices/month

Professional:  
Y invoices/month

Advanced:  
SEF  
recurring invoices  
advanced analytics

Exact limits are TBD.

Frontend may hide unavailable features for UX, but backend must enforce them.

---

# 105. TRIAL

Trial should allow enough use for the user to experience value.

Trial should NOT be so restrictive that user cannot:

- create company
    
- add clients
    
- issue invoices
    
- see dashboard
    
- experience limit tracking
    

Trial expiration flow:

- warning
    
- expiration
    
- grace period if desired
    
- upgrade
    

Do not silently delete data after trial.

---

# 106. DATA RETENTION

Define policy for:

- deleted accounts
    
- cancelled subscriptions
    
- invoices
    
- documents
    
- audit logs
    

Financial/audit data may need different retention than normal user preferences.

Do not implement arbitrary destructive deletion.

---

# 107. EMAIL SYSTEM

Create reusable email service.

Templates:

- email verification
    
- password reset
    
- invoice sent
    
- payment reminder
    
- payment confirmation
    
- obligation reminder
    
- subscription/trial
    
- accountant invitation
    

Use background jobs.

---

# 108. PDF SYSTEM

PDF generation should be deterministic and testable.

Do not generate PDFs manually in frontend.

Backend should own authoritative document generation.

---

# 109. INTERNATIONALIZATION

Primary language Serbian Latin.

Architecture should not make future localization impossible.

Avoid hard-coded UI strings in business logic.

---

# 110. API ERROR CONTRACT

Consistent structure.

Example conceptual response:

{  
"error": {  
"code": "INVOICE_ALREADY_PAID",  
"message": "Faktura je već označena kao plaćena.",  
"request_id": "..."  
}  
}

Frontend should map known errors to good UI.

---

# 111. DATABASE CONSTRAINTS

Use database-level constraints for critical integrity:

- unique invoice number per company
    
- valid foreign keys
    
- non-negative values where applicable
    
- valid statuses
    
- unique relationships
    

Do not rely only on application-level validation.

---

# 112. CRITICAL BUSINESS SERVICES

Business logic should live in explicit service/domain layers where useful.

Examples:

InvoiceService  
PaymentService  
LimitService  
KPOService  
NotificationService  
SubscriptionService  
DocumentService

Avoid putting complex business logic directly inside controllers/views.

---

# 113. FRONTEND STATE

Use appropriate state management.

Do not create one giant global store containing the entire application.

Separate:

- auth
    
- UI
    
- server state
    
- local form state
    

Use server-state caching where useful.

---

# 114. ROUTING

Routes should reflect information architecture.

Examples:

/dashboard

/invoices

/invoices/new

/invoices/:id

/clients

/clients/:id

/kpo

/limits

/obligations

/documents

/settings

/accountant

/admin

Mobile and desktop should use same logical routes unless there is a strong reason otherwise.

---

# 115. DEEP LINKS

Important objects should have stable URLs.

User should be able to open:

invoice  
client  
document  
obligation

directly.

---

# 116. GLOBAL SEARCH

Later feature.

Architecture should allow global search across:

- invoices
    
- clients
    
- documents
    
- obligations
    

Do not implement unless part of current sprint.

---

# 117. PRODUCT COPY EXAMPLES

Use language like:

"Preostalo do limita"

not:

"Remaining threshold utilization"

"Potrebna pažnja"

not:

"Warning state"

"Faktura kasni 12 dana"

not:

"Invoice overdue"

The product is Serbian-first.

---

# 118. DO NOT MAKE THE UI CHEESY

Avoid:

- motivational slogans inside dashboard
    
- excessive emojis
    
- fake congratulation screens
    
- gamification
    
- badges for ordinary actions
    
- unnecessary illustrations
    

The product should feel calm and competent.

---

# 119. COMPETITIVE ADVANTAGE

The product should win through:

1. Simplicity
    
2. Automation
    
3. Attention center
    
4. Limit intelligence
    
5. Accountant connection
    
6. Excellent mobile UX
    
7. Trust/transparency
    

Not simply number of features.

---

# 120. PRODUCT QUALITY BAR

Before considering any feature complete, ask:

- Is it simple?
    
- Is it correct?
    
- Is it secure?
    
- Is it mobile-friendly?
    
- Is it auditable?
    
- Does it integrate properly with existing business logic?
    
- Does it have loading/error/empty states?
    
- Does it have tests?
    
- Does it handle edge cases?
    
- Does it look like part of the same product?
    

If not, it is not finished.

---

# 121. ACCEPTANCE CRITERIA FORMAT

For each significant feature create:

### Goal

What problem does this solve?

### User

Who uses it?

### Flow

What happens step by step?

### Rules

What business rules apply?

### Edge cases

What can go wrong?

### Permissions

Who can access it?

### API

What endpoints/data are required?

### UI states

Loading  
Empty  
Error  
Success  
Disabled

### Tests

What must be tested?

---

# 122. DEFINITION OF DONE

A feature is done only when:

- frontend implemented
    
- backend implemented
    
- database/migrations complete
    
- permissions complete
    
- validation complete
    
- loading state complete
    
- empty state complete
    
- error state complete
    
- success state complete
    
- responsive UI complete
    
- tests complete
    
- audit requirements complete
    
- documentation updated where necessary
    

---

# 123. DO NOT FAKE FEATURES

Do not create buttons that say:

"Coming soon"

unless intentionally part of product design.

Do not create fake SEF integration.

Do not create fake tax calculations.

Do not create fake bank synchronization.

If functionality isn't implemented, don't pretend it is.

---

# 124. DO NOT USE MOCK DATA IN PRODUCTION

Seed/mock data may exist in development/staging.

Production must use real persisted data.

---

# 125. DEVELOPMENT COMMUNICATION

After each meaningful implementation phase, report:

1. What was implemented
    
2. What files/modules changed
    
3. Database changes
    
4. API changes
    
5. Tests added
    
6. Remaining issues
    
7. Decisions made
    
8. Known assumptions
    

Keep reports concise but concrete.

---

# 126. WHEN YOU FINISH A PHASE

Do not automatically jump to unrelated features.

Verify:

- tests
    
- lint
    
- build
    
- migration
    
- UX
    
- responsive behavior
    

Then continue to the next phase.

---

# 127. FIRST TASK

Before writing significant code:

1. Inspect the repository.
    
2. Inspect existing frontend.
    
3. Inspect existing backend.
    
4. Inspect package/dependency setup.
    
5. Inspect database.
    
6. Inspect authentication.
    
7. Inspect deployment.
    
8. Identify reusable components.
    
9. Compare current state with this product specification.
    
10. Produce an implementation plan.
    

Do not rewrite existing code without reason.

---

# 128. FIRST IMPLEMENTATION TARGET

If the repository is empty/new:

Build the foundation first:

1. Project structure
    
2. Docker/development environment if appropriate
    
3. Django backend
    
4. PostgreSQL
    
5. Redis
    
6. Celery
    
7. Vue/Nuxt frontend
    
8. Tailwind
    
9. shared design system
    
10. Authentication
    
11. Company/tenant model
    
12. RBAC
    
13. Audit infrastructure
    

Then proceed to core business flows.

---

# 129. CORE MVP IMPLEMENTATION ORDER

Follow this approximate order:

1. Auth
    
2. Company/onboarding
    
3. Clients
    
4. Invoice model
    
5. Invoice creation
    
6. Invoice PDF
    
7. Invoice sending
    
8. Payment tracking
    
9. Financial event layer
    
10. Dashboard
    
11. Limits
    
12. KPO
    
13. Obligations
    
14. Notifications
    
15. Documents
    
16. Accountant platform
    
17. Subscription/trial
    
18. Admin
    
19. QA
    
20. Mobile/Capacitor preparation
    

---

# 130. FINAL PRINCIPLE

Do not optimize for:

"How quickly can we produce lots of screens?"

Optimize for:

"How quickly can we create a coherent, trustworthy, useful product?"

The application should eventually feel like this:

A paušalac opens it.

Within seconds he knows:

- how much he earned
    
- how much he can still earn
    
- whether someone owes him money
    
- what he needs to pay
    
- what requires his attention
    

And if he needs to do something:

he can do it immediately.

That is the product.

Build toward that outcome consistently.