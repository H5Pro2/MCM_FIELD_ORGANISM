# S2-DL: Statischer TSPM-1-Negativtestvertrag

## Auftrag und Grenze

S2-DL materialisiert ausschliesslich die 16 in S2-DJ gebundenen
Negativtestklassen fuer die private S2-DK-Korrektur. Der Vertrag legt
Fixtures, Einzelmutationen, erwartete Fehler, Ownerzustand,
PPB-1-Aufrufbudget und Atomaritaetsorakel fuer eine spaetere getrennte
Ausfuehrung fest.

Es wurden keine Projektmodule importiert, keine Testdatei angelegt, keine
Zustands- oder Probefunktion aufgerufen und kein Test ausgefuehrt. TSPM-1,
PPB-1, API, Snapshot und Feldpfad bleiben unveraendert.

## Gebundene Quellen

Die spaetere Testimplementierung muss exakt diese Quellen verwenden:

- S2-DJ-Vertragsdigest:
  `64238dab052f5df30ce4fa85ab36e33dc2773d15e7275caa3a41321658293895`;
- S2-DK-Implementierungsdigest:
  `ddcbe4a8f9fbac903b4b03822c9c7a47eb89d19adc1f42ed380545dc1e93efcc`;
- korrigierter privater TSPM-1-Quelldigest:
  `c33ea3fdbc399b88e1416e91f8421f362060de1e368817e3673a93c522013252`;
- unveraenderter S2-DH-Testdigest:
  `836bd2a6ed663590eb2bcbe17442d2bc2e9bab8f2032c34208953dae50b3865d`.

Eine Digestabweichung sperrt Implementierung und Ausfuehrung vollstaendig.
Es ist unzulaessig, die erwarteten Orakel an einen abweichenden Codezustand
anzupassen.

## Gemeinsame Fixtureanatomie

Die spaetere private Testdatei erhaelt genau vier deterministische
Fixturefamilien:

1. `PRIORITY`: gueltige Konfiguration, frischer oder einmal fortgeschrittener
   Composite-Zustand, gebundene Exposition beziehungsweise Probe und ein
   einmaliger Owner;
2. `RELATION`: gueltige Quellen mit privaten digestkonsistenten
   Datentraegern, bei denen genau eine Kreuzfeldbeziehung falsch ist;
3. `PPB_RESULT`: konsolidierungsberechtigter Fast-Vorzustand und lokal
   ersetzte PPB-1-Rueckgabe, ohne PPB-1-Code zu aendern;
4. `ATOMICITY`: konsolidierungsberechtigter Zustand, gueltiges erstes lokales
   PPB-1-Ergebnis und ungueltiges oder fehlschlagendes zweites Ergebnis.

Alle Frames bleiben synthetisch, endlich, streng zeitgeordnet und stammen aus
den vorhandenen S2-DH-Hilfsformen. Fuer malformed exakte Datentraeger darf
eine testprivate Bypass-Hilfe ausschliesslich `object.__new__` und
`object.__setattr__` verwenden. Sie darf keine Projektvalidierung reparieren,
keinen Produktionspfad aufrufen und keine neue Zustandsmechanik erzeugen.

Jeder Test besitzt genau eine primaere Mutation. Kontrollwerte, die nur zum
Erreichen des Zielvalidators erforderlich sind, muessen aus derselben
gueltigen Ausgangsfixture stammen.

## Gemeinsame Orakel

Fuer Ownerpfade gilt, sofern unten nicht anders gebunden:

- aeusserer Fehler: `TSPM1_ATTEMPT_FAILED`;
- innerer Fehler im terminalen Owner: der fallbezogen gebundene Code;
- Owner: `FAILED`, `attempt_count=1`, `use_count=0`, `generation=1`;
- kein `TSPM1StepResult`, kein Receipt und kein Composite-Nachzustand;
- autorisierter Composite-Vorzustandsdigest bleibt bitgleich;
- zweiter Aufruf desselben Owners: `TSPM1_OWNER_TERMINAL`;
- keine Aenderung an einem PPB-1-Vorzustandsobjekt.

Direkte Konstruktor- und read-only-Faelle besitzen keinen Owner. Sie muessen
den gebundenen inneren Fehler direkt liefern und duerfen keinen Nachzustand
erzeugen.

## P01 bis P04: Fail-Closed-Prioritaet

### P01: Falscher Expositionstyp vor ungueltigem Composite

- Fixture: `PRIORITY`, autorisierter Owner, malformed exakter
  Composite-Datentraeger und `object()` statt Expositionshuelle.
- Mutation: nur der Aufrufwert der Expositionsrolle besitzt den falschen Typ;
  der malformed Composite dient ausschliesslich als konkurrierender
  nachrangiger Fehler.
- Erwarteter innerer Code: `TSPM1_INVALID_TYPE_OR_SCHEMA`.
- PPB-1-Aufrufe: null.

### P02: Owner-Autorisierung vor Composite-Inhalt

- Fixture: `PRIORITY`, exakte Typen, Owner autorisiert einen anderen
  Composite-Digest; der uebergebene exakte Composite ist zusaetzlich
  digestinkonsistent.
- Primaere Mutation: Owner-/Aufruf-Composite-Digestabweichung.
- Erwarteter innerer Code: `TSPM1_OWNER_AUTHORIZATION_MISMATCH`.
- PPB-1-Aufrufe: null.

### P03: Owner-Autorisierung vor Quellenprovenienz

- Fixture: `PRIORITY`, exakte Typen, Owner autorisiert einen anderen
  Expositionsdigest; die uebergebene exakte Exposition besitzt zusaetzlich
  eine fremde Envelope-Mitgliedschaft.
- Primaere Mutation: Owner-/Aufruf-Expositionsdigestabweichung.
- Erwarteter innerer Code: `TSPM1_OWNER_AUTHORIZATION_MISMATCH`.
- PPB-1-Aufrufe: null.

### P04: Falscher Probehuellentyp vor Composite-Inhalt

- Fixture: `PRIORITY`, gueltige Konfiguration, malformed exakter Composite
  und `object()` statt Probehuelle.
- Erwarteter direkter Code: `TSPM1_INVALID_TYPE_OR_SCHEMA`.
- Distanz-, S1-WU- und PPB-1-Aufrufe: null.

## R05 bis R12: Relationale Datentraeger

### R05: Match und Konfliktflag

- Fixture: digestkonsistenter `TSPM1FastTransitionCandidate` mit
  `FAST_UPDATED` und `partial_association_conflict=true`.
- Erwarteter direkter Code: `TSPM1_ATOMIC_RESULT_REQUIRED`.
- Kein Owner und keine PPB-1-Aufrufe.

### R06: Support und Konsolidierungsberechtigung

- Fixture: gueltiger konsolidierungsberechtigter Fast-Vorzustand; der lokal
  ersetzte Kandidat besitzt den korrekten Nachsupport, aber
  `consolidation_eligible=false` und einen dazu neu berechneten Eigendigest.
- Erwarteter innerer Code: `TSPM1_ATOMIC_RESULT_REQUIRED`.
- PPB-1-Aufrufe: null, weil die Kandidatenabnahme vor PPB-1 liegt.

### R07: Ablauf-, LRU- oder Restslotrelation

- Fixture: gueltiger Ersatzfall; der lokal ersetzte Kandidat verwendet einen
  nicht minimalen LRU-Slot oder veraendert genau einen nicht ausgewaehlten
  Restslot und besitzt einen dazu passenden Eigendigest.
- Gebundene Variante: nicht minimaler LRU-Slot; keine zweite Variante im
  selben Test.
- Erwarteter innerer Code: `TSPM1_ATOMIC_RESULT_REQUIRED`.
- PPB-1-Aufrufe: null.

### R08: Commit mit falschem Primaerereignis

- Fixture: digestkonsistentes `TSPM1TransitionReceipt` mit `COMMITTED`, zwei
  formal vollstaendigen PPB-1-Rollen und `FAST_CREATED`.
- Erwarteter direkter Code: `TSPM1_ATOMIC_RESULT_REQUIRED`.

### R09: Ineligible Receipt mit PPB-1-Rollen

- Fixture: digestkonsistentes Receipt mit `NOT_ELIGIBLE` und genau einer
  nichtleeren PPB-1-Readout- oder Stabilitaetsrolle.
- Gebundene Mutation: auditiver Readoutdigest nicht leer.
- Erwarteter direkter Code: `TSPM1_ATOMIC_RESULT_REQUIRED`.

### R10: Slow-Kontext ohne zwei positive Slow-Befunde

- Fixture: digestkonsistentes `TSPM1ReadOnlyFinding` mit
  `SLOW_PPB1_CONTEXT`, auditiv `SLOW_RECOGNIZED` und visuell
  `SLOW_NOT_RECOGNIZED`.
- Erwarteter direkter Code: `TSPM1_ATOMIC_RESULT_REQUIRED`.

### R11: Fast-Kontext ohne Fast-Match

- Fixture: digestkonsistentes Finding mit `FAST_ASSOCIATIVE_CONTEXT` und
  `fast_recognized=false`, alle Fast-Ergebnisfelder leer.
- Erwarteter direkter Code: `TSPM1_ATOMIC_RESULT_REQUIRED`.

### R12: Step-Result mit Owner-/Receipt-Abweichung

- Fixture: einzeln gueltige Composite-, Receipt- und Ownerformen; der Owner
  autorisiert einen anderen Expositionsdigest als das Receipt. Der
  Resultdigest wird fuer diese falsche Kombination kanonisch neu berechnet.
- Erwarteter direkter Code: `TSPM1_ATOMIC_RESULT_REQUIRED`.
- Kein Ergebnisobjekt darf den Konstruktor verlassen.

## B13 bis B15: Symmetrische PPB-1-Ergebnisabnahme

Alle drei Faelle patchen ausschliesslich die im privaten TSPM-1-Modul
gebundene lokale Referenz auf `advance_ppb1_bank`. Der PPB-1-Kern und seine
Dateien bleiben unveraendert. Der Fast-Zustand ist vor Aufruf bereits
konsolidierungsberechtigt.

### B13: Auditiver Ergebnistyp oder Konfigurationsdigest

- Gebundene Mutation: der auditive Aufruf liefert einen exakten
  `PPB1StepResult`, dessen Readout einen fremden Konfigurationsdigest bindet;
  alle anderen Rollen sind formal gueltig und digestkonsistent.
- Der visuelle Aufruf liefert sein gueltiges lokales Ergebnis.
- Erwarteter innerer Code: `TSPM1_ATOMIC_RESULT_REQUIRED`.
- PPB-1-Aufrufreihenfolge und Anzahl: `auditory`, `visual`; exakt zwei.

### B14: Auditive Vorzustands-, Eingabe- oder Nachzustandsbindung

- Gebundene Mutation: nur der auditive `readout.input_digest` wird auf einen
  fremden gueltigen Digest gesetzt; Readout und Step-Result werden
  digestkonsistent rekonstruiert.
- Visuelles Ergebnis bleibt gueltig.
- Erwarteter innerer Code: `TSPM1_ATOMIC_RESULT_REQUIRED`.
- PPB-1-Aufrufe: exakt zwei in auditiv-visueller Reihenfolge.

### B15: Visuelle Symmetrie

- Auditives Ergebnis bleibt gueltig.
- Gebundene Mutation: nur der visuelle `readout.prestate_digest` wird auf
  einen fremden gueltigen Digest gesetzt; die Rueckgabe bleibt formal und
  digestkonsistent.
- Erwarteter innerer Code: `TSPM1_ATOMIC_RESULT_REQUIRED`.
- PPB-1-Aufrufe: exakt zwei in auditiv-visueller Reihenfolge.

## A16: Atomarer Zweitfehler und Retry-Sperre

- Fixture: konsolidierungsberechtigter Zustand und gueltiges lokales
  auditives PPB-1-Ergebnis.
- Mutation: der visuelle PPB-1-Aufruf wirft eine testprivate Ausnahme, bevor
  ein visuelles Ergebnis entsteht.
- Erwarteter innerer Code: `TSPM1_ATOMIC_RESULT_REQUIRED`.
- PPB-1-Aufrufreihenfolge: `auditory`, `visual`; exakt zwei Versuche.
- Weder das gueltige auditive Lokalergebnis noch Fast-Kandidat,
  Composite-Nachzustand oder Receipt werden ausgegeben.
- Owner endet terminal `FAILED`; ein Retry liefert
  `TSPM1_OWNER_TERMINAL` und erzeugt keinen weiteren PPB-1-Aufruf.

## Testdatei und feste Anzahl

Eine spaetere Freigabe darf genau eine neue private Testdatei anlegen:

`tests/test_tspm1_s2dm_negative_contract.py`

Sie enthaelt genau 16 Testmethoden mit den IDs `P01` bis `P04`, `R05` bis
`R12`, `B13` bis `B15` und `A16`. Parametrisierung, die mehrere Mutationen in
einer Methode verbirgt, ist ausgeschlossen. Die bestehenden elf direkten
S2-DH-Tests bleiben unveraendert.

## Spaetere Ausfuehrungsreihenfolge

Nach einer separaten Freigabe gilt fail-closed:

1. Quelldigests und Testmethodenzahl statisch pruefen;
2. genau die 16 neuen Negativtests einmal ausfuehren;
3. nur bei 16 von 16 bestandenen Tests die elf bestehenden direkten
   TSPM-1-Tests gemeinsam mit den 16 neuen Tests ausfuehren;
4. nur bei 27 von 27 bestandenen direkten TSPM-1-Tests die 49 bestehenden
   PPB-1-, S1-WU- und Rezeptorregressionen hinzunehmen;
5. Abschluss nur bei 76 von 76 bestandenen fokussierten Tests.

Kein automatischer Retry, keine Vollsuite und keine reale oder produktive
Ausfuehrung sind Teil dieses Budgets. Der erste Fehler stoppt die jeweilige
Stufe und sperrt jede Abschlussentscheidung.

## Entscheidung

`PASS_TSPM1_STATIC_NEGATIVE_TEST_MATERIALIZATION_AND_EXECUTION_CONTRACT`

Alle 16 Negativtests sind eindeutig, endlich und nicht ueberlappend
materialisiert. S2-DL implementiert oder bestaetigt keinen Test. Die S2-DK-
Korrektur bleibt bis zur getrennt freigegebenen Ausfuehrung statisch und
nicht abschliessend abgenommen.

## Naechster Schritt

S2-DM kann nach separater ausdruecklicher Freigabe ausschliesslich die eine
gebundene Testdatei mit den 16 Faellen implementieren und die dreistufige
fokussierte Folge `16 -> 27 -> 76` genau einmal ausfuehren. TSPM-1, PPB-1,
API, Snapshot und Feldpfad muessen dabei unveraendert bleiben.
