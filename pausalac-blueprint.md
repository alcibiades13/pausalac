PRODUCT BLUEPRINT
SaaS platforma za srpske paušalne preduzetnike
Radni koncept: moderan poslovni sistem za paušalce + platforma za računovodstvenu firmu
Verzija 1.0 • 13.09.2026.
1. Executive summary
Proizvod je web + mobile-first SaaS za srpsko tržište koji paušalcu objedinjuje fakturisanje, naplatu, KPO, praćenje limita, poreske obaveze, dokumente i relevantne državne/poslovne integracije. Ključna razlika nije broj funkcija, već sposobnost sistema da korisniku stalno odgovara na četiri pitanja: Koliko sam zaradio? Koliko mi je ostalo do limita? Šta moram da uradim? Da li postoji nešto zbog čega treba da reagujem?
Strateška prednost klijenta je postojeća računovodstvena firma. Zato proizvod treba od početka projektovati kao dva povezana proizvoda: korisnički sistem za paušalca i operativni command center za računovođu.
Pozicioniranje: „Tvoj paušal, na autopilotu.“ To znači automatizaciju i pravovremene informacije, a ne obećanje da sistem samostalno donosi poresko-pravne odluke.
2. Product principles
    • Jedan unos → više automatski ažuriranih evidencija.
    • Action-first UX: korisnik vidi šta treba da uradi, ne samo podatke.
    • Bez računovodstvenog žargona bez objašnjenja.
    • Mobile-first za svakodnevne radnje; desktop za masovni rad i administraciju.
    • Transparentnost: svaka važna finansijska promena je objašnjiva i auditabilna.
    • Regulatorna pravila su verzionisana konfiguracija, ne hard-coded logika.
    • Modularni monolit pre mikroservisa.
    • Premium, miran i profesionalan UI; bez prenatrpanog admin-template izgleda.
3. Ciljne persone
3.1 Paušalac
Freelancer, konsultant, developer, dizajner, zanatlija ili drugi preduzetnik koji želi da radi svoj posao bez stalnog razmišljanja o administraciji.
3.2 Napredni paušalac
Ima veći broj klijenata, devizne fakture, ponavljajuću naplatu i želi analitiku i automatizaciju.
3.3 Računovođa
Vodi više klijenata i želi centralni pregled rokova, limita, dokumenata, grešaka i komunikacije.
3.4 Accounting admin
Upravlja korisnicima, paketima, pravilima, integracijama, sadržajem i operativnim podešavanjima.
4. Core value proposition
Aplikacija ne treba da bude samo „alat za fakture“. Ona treba da bude lični poslovni kontrolni centar paušalca.
    • Dashboard odmah pokazuje finansijsko stanje i prioritete.
    • Limiti se ne prikazuju samo kao procenti, već se tumače.
    • Obaveze se pretvaraju u konkretne akcije.
    • Plaćena faktura automatski pokreće relevantne evidencije.
    • Računovođa može da prati klijente bez ručnog prebacivanja između sistema.
    • Promene propisa se komuniciraju kroz „šta ovo znači za mene?“ sadržaj.
5. Information architecture
Glavna mobilna navigacija: Početna | Fakture | + | Finansije | Više
Desktop navigacija: Dashboard | Fakture | Klijenti | Kasa | KPO | Finansije | Obaveze | Dokumenti
Globalna brza akcija (+): Nova faktura | Fiskalni račun | Profaktura | Avans | Novi klijent | Novi trošak
6. Ekrani i funkcionalnosti
6.1 Dashboard
    • Status poslovanja: zeleno / pažnja / kritično.
    • Promet YTD i poređenje.
    • 6M limit i relevantni 8M/365-day indikator.
    • Neizmirene fakture i iznos potraživanja.
    • Sledeća poreska obaveza.
    • Lista „zahteva tvoju pažnju“.
    • Brze akcije.
6.2 Fakture
    • Kreiranje, pregled, izmena i storno.
    • PDF generisanje i slanje.
    • Statusi: nacrt, izdata, poslata, viđena, delimično plaćena, plaćena, kasni, stornirana.
    • Devizne fakture i evidentiranje relevantnog kursa.
    • Ponavljajuće fakture.
    • QR podaci za plaćanje.
    • Kasnije: SEF integracija.
6.3 Klijenti
    • Profil klijenta, kontakt i poslovni podaci.
    • Istorija faktura.
    • Ukupno fakturisano, naplaćeno i otvoreno potraživanje.
    • Nova faktura iz profila.
    • Ponavljajuća saradnja.
6.4 Naplata
    • Praćenje dospelih i nedospelih faktura.
    • Automatsko označavanje kašnjenja.
    • Podsetnik klijentu.
    • Kasnije: uparivanje bankovnih izvoda.
6.5 Limiti
    • 6M godišnji promet.
    • 8M/365-day relevantno praćenje.
    • Procenat iskorišćenja i preostali iznos.
    • Istorija i projekcija.
    • Upozorenja na 70/85/95% ili prema podesivim pravilima.
    • „Šta ako?“ kalkulator.
6.6 KPO
    • Automatsko formiranje iz relevantnih događaja.
    • Pregled i korekcije uz audit trail.
    • PDF/Excel izvoz.
    • Pretraga i filtriranje.
6.7 Obaveze
    • Poreski kalendar.
    • Iznos, rok i status.
    • Kopiranje relevantnih podataka za uplatu.
    • Podsetnici.
    • Objašnjenje „zašto ovo plaćam?“.
6.8 Dokumenti
    • Poreska rešenja, fakture, KPO, SEF, fiskalni računi, ugovori i ostalo.
    • Dokumenti koji zahtevaju pažnju.
    • Bezbedno skladištenje i audit.
6.9 Integracije
    • SEF.
    • NBS kurs.
    • Fiskalizacija / PURS u kasnijoj fazi.
    • Banke / izvodi u kasnijoj fazi.
    • Webshop/API integracije u kasnijim fazama.
6.10 Knowledge base
    • Vodiči za paušalce.
    • Kratka objašnjenja propisa.
    • Interaktivni test samostalnosti.
    • Poreski i poslovni kalkulatori.
    • Aktuelne promene sa jasnim datumom i izvorom.
7. Signature features
7.1 Business health
Na početnoj strani korisnik dobija jedinstven status: „Sve je u redu“, „Potrebna pažnja“ ili „Potrebna akcija“, uz konkretan razlog.
7.2 Limit intelligence
Sistem ne prikazuje samo 2.840.000 / 6.000.000, već objašnjava koliko je ostalo, trend, projekciju i posledice scenarija.
7.3 Attention center
Jedna lista sa najvažnijim otvorenim stvarima: kasna faktura, poreski rok, limit, SEF greška, dokument ili poruka računovođe.
7.4 Accountant connection
„Moj računovođa“ postaje stalna veza između SaaS proizvoda i računovodstvene usluge.
8. User journey
    1. Landing page → pregled vrednosti → trial.
    2. Registracija → unos PIB-a i osnovnih podataka.
    3. Onboarding wizard → firma, banka, delatnost, SEF/fiskalizacija, preferencije.
    4. Dashboard → sistem inicijalno izračunava stanje i obaveze.
    5. Dodavanje prvog klijenta → prva faktura.
    6. Slanje fakture → praćenje statusa.
    7. Uplata → automatska evidencija i relevantno ažuriranje KPO/limita.
    8. Notifikacije → korisnik dobija samo akcije koje zahtevaju pažnju.
    9. Računovođa → povezuje se i dobija dozvoljeni pristup.
    10. Upgrade → trial se završava i korisnik bira paket.
9. MVP scope
MVP mora biti dovoljno kompletan da korisnik može realno da vodi svakodnevnu administraciju, ali bez pokušaja da odmah pokrije svaki edge case.
    11. Auth, kompanije i profili.
    12. Dashboard.
    13. Klijenti.
    14. Fakture + PDF + email.
    15. Praćenje naplate.
    16. QR / payment podaci.
    17. KPO.
    18. 6M i 8M/365-day monitoring.
    19. Poreski kalendar i obaveze.
    20. Notifikacije.
    21. Dokumenti.
    22. Osnovni accountant panel.
    23. Admin panel.
    24. Audit log.
    25. Subscription + trial.
10. V2
    • SEF integracija.
    • Devizne fakture + automatizovani NBS kurs.
    • Ponavljajuće fakture.
    • Troškovi.
    • Napredna analitika.
    • Test samostalnosti.
    • Računovođa komunikacija.
    • Napredne mobilne funkcije.
11. V3
    • Fiskalizacija.
    • Bank statement matching.
    • Open banking gde je opravdano.
    • API/webhooks.
    • Automatizovane radnje.
    • AI analiza i forecasting.
    • Napredni accounting automation.
12. Pricing strategy
Ne planirati permanentni free tier. Umesto toga koristiti ograničen free trial dovoljan da korisnik unese firmu, napravi prve fakture i vidi vrednost proizvoda.
    • Starter: približno 1.000–1.500 RSD/mesečno.
    • Professional: približno 1.500–2.500 RSD/mesečno.
    • Business/Advanced: približno 2.500–3.500+ RSD/mesečno, u zavisnosti od integracija i automatizacije.
    • Accounting paket: mogućnost da računovodstvena firma uključi aplikaciju u svoju uslugu.
Konačne cene i granice paketa treba odrediti tek nakon feature matrix-a i procene troškova integracija.
13. Accounting platform
Računovođa dobija centralni pregled svih klijenata.
    • Broj klijenata i status.
    • Klijenti kojima je potrebna pažnja.
    • Limit alerts.
    • Poreski rokovi.
    • Dokumenti koji nedostaju.
    • SEF/fiskalizacija greške.
    • Poruke i zahtevi klijenata.
    • Izveštaji.
    • Role-based pristup.
Primer prioriteta: 108 klijenata bez problema, 14 zahteva pažnju, 4 kritična.
14. Technical architecture
14.1 Frontend
    • Vue 3 + TypeScript.
    • Nuxt 4 za web/marketing sloj gde je opravdano.
    • Tailwind CSS sa sopstvenim design tokenima i komponentama.
    • Mobile-first responsive UI.
    • Capacitor kao kandidat za iOS/Android wrapper.
14.2 Backend
    • Django + Django REST Framework.
    • PostgreSQL.
    • Redis.
    • Celery/background jobs.
    • S3-compatible object storage.
    • REST API, uz mogućnost kasnijeg javnog API-ja.
14.3 Architecture style
Modularni monolit. Domeni: accounts, companies, invoices, clients, payments, kpo, limits, taxes, documents, sef, fiscalization, notifications, analytics, subscriptions, audit.
14.4 Integration layer
SEF, PURS/fiskalizacija i NBS moraju biti izolovani iza jasnog integration layer-a. Promena državnog API-ja ne sme zahtevati promenu cele aplikacije.
15. Financial data architecture
Uvesti centralni financial event/ledger koncept. Relevantni događaji uključuju InvoiceCreated, InvoiceSent, InvoicePaid, InvoiceCancelled, FiscalReceiptCreated i FiscalReceiptCancelled. Dashboard, KPO, limiti i analitika treba da se izvode iz konzistentnog izvora podataka, uz mogućnost rekonstrukcije istorije.
Sve finansijske izmene moraju imati audit trail: ko, kada, šta je promenjeno, prethodna i nova vrednost.
16. Rules engine
Poreska i regulatorna pravila ne treba hard-code-ovati u različite delove aplikacije. Pravilo treba da bude verzionisano i da sadrži godinu/period važenja, izvor, datum stupanja na snagu i status odobrenja.
Primeri pravila: godišnji limit, rolling 365-day prag, rokovi, ograničenja poreske osnovice i druga pravila koja se mogu menjati.
17. Security & privacy
    • HTTPS svuda.
    • Encrypted secrets i zaštita API credentials.
    • RBAC.
    • Audit logs.
    • Rate limiting.
    • Bezbedno object storage skladište.
    • Backup i disaster recovery plan.
    • Monitoring i alerting.
    • MFA kao opcija, a za osetljive administratorske akcije razmotriti obavezni MFA.
    • Minimalan pristup podacima po roli.
18. Design system
Vizuelni cilj: moderna fintech/productivity estetika, ozbiljna ali ne hladna; mnogo whitespace-a, jasna tipografija i funkcionalna upotreba boja.
    • Primary: Deep Navy #172033.
    • Background: Off White #F7F8FA.
    • Primary action: Indigo #4F46E5.
    • Success: #16A34A.
    • Warning: #D97706.
    • Danger: #DC2626.
    • Secondary text: #64748B.
    • Border: #E2E8F0.
    • Font: Inter.
    • Ne koristiti boje dekorativno kada imaju funkcionalno značenje.
19. Mobile strategy
    • Primarni mobile flows: nova faktura, pregled limita, pregled obaveza, status naplate, notifikacije, dokumenti.
    • Desktop flows: masovni rad, KPO, analitika, accountant panel, administracija.
    • Touch targets, sticky primary actions, bottom navigation i minimalan broj koraka.
    • Capacitor za store distribuciju, uz native pluginove samo gde su potrebni.
20. Notifications
    • Push + email + in-app.
    • Prioriteti: critical, attention, informational.
    • Ne slati sve događaje; grupisati i prikazati „X stvari zahtevaju tvoju pažnju“.
    • Korisnik može podesiti kanale i deo učestalosti.
21. AI roadmap
AI nije MVP feature. Kada sistem već ima kvalitetne podatke, AI može da radi nad njima: analiza pada prihoda, objašnjenje promena, projekcije, odgovori na pitanja o sopstvenim podacima i priprema nacrta komunikacije. Za poreska pitanja AI mora prikazivati osnovu/izvor i jasno označiti informativni karakter.
22. Content & trust
Svaki regulatorni sadržaj treba da ima datum ažuriranja, izvor i jasnu razliku između činjenice, procene i preporuke. Korisniku treba objasniti „šta ovo znači za mene“, umesto samo preneti zakonski tekst.
23. Competitive positioning
Pausal.rs, Paušalko i Fiksno potvrđuju da tržište očekuje fakture, KPO, limite, poreske obaveze, SEF/fiskalizaciju i druge poslovne funkcije. Naš proizvod ne treba da pobedi prostim brojanjem feature-a. Diferencijacija je u UX-u, centralnom „attention“ modelu, kvalitetu automatizacije i direktnoj vezi sa računovodstvenom firmom.
Pre developmenta treba napraviti detaljan feature matrix konkurencije: postojeće funkcije, UX kvalitet, pricing, ograničenja, integracije, onboarding, mobile iskustvo i praznine koje naš proizvod može da iskoristi.
24. Product metrics
    • Activation: korisnik završi onboarding i izda prvu fakturu.
    • Time to first invoice.
    • Broj izdatih faktura po aktivnom korisniku.
    • Procenat faktura koje postanu naplaćene.
    • Monthly active users.
    • Retention nakon 30/90 dana.
    • Trial → paid conversion.
    • Broj aktivnih accountant-client veza.
    • Broj uspešno automatizovanih radnji.
    • Broj kritičnih grešaka / neusaglašenih evidencija.
25. Definition of done za MVP
    • Svaki core financial flow ima testove.
    • Promene podataka su auditabilne.
    • Dashboard, KPO i limit računica koriste konzistentne izvore.
    • Critical integration failures su vidljive korisniku i adminu.
    • Responsive ponašanje je testirano na modernim desktop i mobile browserima.
    • Capacitor build pipeline je pripremljen za Android/iOS.
    • Backup/restore procedura je dokumentovana i testirana.
    • Regulatorna pravila imaju verziju i izvor.
    • Postoji staging okruženje odvojeno od produkcije.
    • Postoji monitoring i error tracking pre javnog lansiranja.
26. Pre-development deliverables
    26. Competitive feature matrix.
    27. Final product requirements document.
    28. Sitemap + navigation model.
    29. Low-fidelity wireframes za sve MVP ekrane.
    30. High-fidelity design system i ključni screenovi.
    31. Database ERD.
    32. API specification.
    33. Permissions matrix.
    34. Integration contracts.
    35. Rules-engine specification.
    36. Notification matrix.
    37. Analytics/event taxonomy.
    38. Security checklist.
    39. MVP backlog sa prioritetima i acceptance criteria.
    40. Development milestones.
27. Recommended development order
    41. Discovery + competitive matrix.
    42. Design system + core UX flows.
    43. Auth/company/onboarding.
    44. Core domain model + audit.
    45. Clients + invoices.
    46. Payments/status + dashboard.
    47. Limits + KPO.
    48. Obligations + notifications.
    49. Documents.
    50. Accountant panel.
    51. Subscriptions/trial.
    52. Integration layer + first external integration.
    53. QA, security, performance, mobile/Capacitor.
    54. Closed beta sa stvarnim paušalcima i računovođama.
    55. Public launch.
28. Product north star
Korisnik ne treba da otvara aplikaciju zato što „mora da vodi administraciju“. Treba da je otvori zato što je to najbrži način da sazna da li je njegov posao u redu.
North Star: „Za manje od 10 sekundi korisnik može da razume finansijsko stanje, sledeću obavezu i eventualni problem koji zahteva njegovu pažnju.“