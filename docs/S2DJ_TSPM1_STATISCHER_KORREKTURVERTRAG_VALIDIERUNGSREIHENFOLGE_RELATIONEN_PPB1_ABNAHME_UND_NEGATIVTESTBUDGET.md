# S2-DJ: Statischer TSPM-1-Korrekturvertrag

## Auftrag und Grenze

S2-DJ schliesst auf Vertragsebene ausschliesslich die vier in S2-DI
festgestellten Luecken:

1. verbindliche Fail-Closed-Pruefreihenfolge;
2. vollstaendige relationale Ergebnisvalidierung;
3. explizite und symmetrische PPB-1-Ergebnisabnahme;
4. endliches Negativtestbudget fuer eine spaetere getrennte Freigabe.

Es wurden keine Projektmodule importiert, keine Zustands- oder Probefunktion
aufgerufen, keine Tests ausgefuehrt und keine Implementierung geaendert.
PPB-1, API, Snapshot und Feldpfad bleiben unveraendert.

## K1: Verbindliche Abbruchreihenfolge des Koordinators

`TSPM1CoordinatorOwner.consume_once` muss genau diese Prioritaet einhalten:

1. nicht blockierenden Owner-Lock erwerben; andernfalls `TSPM1_OWNER_BUSY`
   ohne Statusaenderung;
2. terminalen Ownerstatus pruefen; andernfalls `TSPM1_OWNER_TERMINAL` ohne
   neuen Versuch;
3. exakte Typen von Konfiguration, Composite-Vorzustand und Expositionshuelle
   pruefen;
4. TSPM-1-Schema, Vertragsdigests und gemeinsame Konfigurationsbindung
   pruefen;
5. Owner-Autorisierung atomar gegen Konfigurationsdigest,
   Composite-Vorzustandsdigest und Expositionsdigest pruefen;
6. Composite- und Fast-Vorzustand einschliesslich der zwei PPB-1-
   Vorzustaende pruefen;
7. Objektidentitaet, Envelope-Mitgliedschaft und alle Provenienz- und
   Quelldigests der Exposition pruefen;
8. Modalitaet, Geometrie, Traegerordnung und Dimensionen pruefen;
9. gemeinsame Feldfensterueberlappung sowie Fast- und PPB-1-Quellclocks und
   Endticks pruefen;
10. lokalen Fast-Kandidaten berechnen und gegen K3 abnehmen;
11. nur bei Konsolidierungsberechtigung beide PPB-1-Schritte lokal berechnen
    und gegen K4 abnehmen;
12. Composite-Nachzustand gegen Fast- und beide PPB-1-Ergebnisse pruefen;
13. Receipt gegen alle direkten Quellen und den Nachzustand pruefen;
14. Unveraendertheit von Konfiguration, Vorzustand und Exposition bestaetigen;
15. Resultdigest aus Nachzustand, Receipt und Owner-Nachzustandsprojektion
    ohne `committed_result_digest` bilden;
16. Owner genau einmal auf `CONSUMED` setzen und das vollstaendige Step-Result
    pruefen.

Nach Schritt 2 wird der Owner vor jeder weiteren Pruefung intern
`IN_PROGRESS`, `attempt_count=1`. Jeder Fehler aus den Schritten 3 bis 16
endet terminal mit `FAILED`, `use_count=0`, `generation=1`, innerem Fehlercode
und Fehlerdigest. Nach aussen entsteht nur `TSPM1_ATTEMPT_FAILED`. Ein Retry
bleibt gesperrt.

Owner-Autorisierung darf fuer ihre Prioritaetspruefung nur die nach exakter
Typpruefung vorhandenen drei Digestfelder lesen. Eine inhaltliche Composite-
oder Quellenvalidierung vor diesem Vergleich ist verboten.

## K2: Verbindliche Abbruchreihenfolge der read-only Probe

`probe_tspm1_read_only` muss genau diese Reihenfolge verwenden:

1. exakte Typen von Konfiguration, Composite-Zustand und Probehuelle;
2. Schema, Vertragsdigests und Konfigurationsbindung;
3. Composite-, Fast- und beide PPB-1-Zustaende;
4. Objektidentitaet, Envelope-Mitgliedschaft und Provenienz der Probe;
5. Modalitaet, Geometrie, Traegerordnung und Dimensionen;
6. Feldfensterueberlappung, Quellclocks und strikt spaetere Endticks;
7. Fast-Distanzen und gemeinsamer Fast-Match;
8. je vorhandener Slow-Bank hoechstens ein S1-WU-Aufruf und Abnahme des
   Befunds;
9. Kontextentscheidung und relationale Findingvalidierung nach K6;
10. Unveraendertheit aller drei Bankdigests und des Composite-Digests;
11. Ausgabe genau eines digestgebundenen read-only Findings.

Keine Distanz und kein S1-WU-Aufruf darf vor Abschluss von Schritt 6
stattfinden. Die Probe besitzt keinen Owner und erzeugt keinen Nachzustand.

## K3: Fast-Kandidatenidentitaet

Ein lokaler `TSPM1FastTransitionCandidate` ist nur gueltig, wenn alle
folgenden Beziehungen zum gebundenen Fast-Vorzustand, zur Konfiguration und
zur aktuellen Exposition gleichzeitig gelten:

- Nachzustandszaehler ist exakt Vorzustandszaehler plus eins;
- Slot-IDs, Kapazitaet und Reihenfolge bleiben exakt erhalten;
- Fast-Konfigurationsdigest, Bank-ID und beide Quellclocks stimmen;
- beide letzten Endticks stammen aus den zwei aktuellen Originalframes;
- Ablaufdigests entsprechen genau den nach Slot-ID geordneten faelligen
  Vorzustandsslots und diese Slots enthalten keinen alten Zustand mehr;
- genau ein Primaerereignis liegt vor.

Fuer `FAST_UPDATED` gilt zusaetzlich:

- der ausgewaehlte Vorzustandsslot ist belegt;
- beide Distanzen sind endlich, in `[0,2]` und innerhalb ihrer Schwellen;
- Auswahl entspricht exakt der gebundenen Dreifachrangfolge;
- `partial_association_conflict` ist zwingend `false`;
- beide Komponenten folgen exakt der gebundenen Updateformel;
- Support und letzter Auswahlschritt sind exakt fortgeschrieben;
- `consolidation_eligible` gilt genau dann, wenn der Nachsupport die
  Konsolidierungsgrenze erreicht hat;
- kein Ersatzdigest ist vorhanden.

Fuer `FAST_CREATED` und `FAST_REPLACED` gilt zusaetzlich:

- es existiert kein gemeinsamer Match;
- beide Matchdistanzen sind im Kandidaten leer;
- Support ist eins, Konsolidierungszahl null und letzter
  Konsolidierungsexpositionsdigest leer;
- `consolidation_eligible` ist `false`;
- das Konfliktflag ist genau dann wahr, wenn mindestens eine Modalitaet zu
  mindestens einem verbleibenden Slot passt, aber kein gemeinsamer Match
  existiert;
- `FAST_CREATED` verwendet den kleinsten freien Slot und keinen
  Ersatzdigest;
- `FAST_REPLACED` verwendet den kleinsten LRU-Rang und bindet exakt den
  Digest des verworfenen vollständigen Slots.

Alle nicht ausgewaehlten und nicht abgelaufenen Slots bleiben bitgleich.

## K4: Explizite PPB-1-Ergebnisabnahme

Bei `consolidation_eligible=false` gilt:

- kein `advance_ppb1_bank`-Aufruf;
- beide PPB-1-Nachzustaende sind dieselben unveraenderten Vorzustandsobjekte;
- keine PPB-1-Readout- oder Stabilitaetsrolle im Receipt.

Bei `consolidation_eligible=true` gilt:

- Primaerereignis ist zwingend `FAST_UPDATED`;
- genau ein auditiver und danach genau ein visueller PPB-1-Aufruf;
- Argumente sind exakt die gebundenen PPB-1-Konfigurationen, die zwei
  Composite-Vorzustaende und die zwei aktuellen Originalframe-Objekte;
- jedes Ergebnis besitzt den exakten `PPB1StepResult`-Typ und genau einen
  exakten `PPB1Readout` sowie `PPB1BankState`;
- Readout-Bank, Modalitaet und Konfigurationsdigest stimmen mit der jeweiligen
  gebundenen PPB-1-Konfiguration;
- Readout-Vorzustandsdigest stimmt mit dem jeweiligen PPB-1-Vorzustand;
- Readout-Eingabedigest stimmt mit dem jeweiligen gebundenen
  PPB-1-Eingabeprojektionsdigest der Exposition;
- Readout-Nachzustandsdigest stimmt mit dem validierten Ergebnisnachzustand;
- Nachzustand hat exakt einen akzeptierten PPB-1-Schritt mehr, dieselbe
  Quellclock und den Endtick des aktuellen Originalframes;
- beide Ergebnisse werden vollstaendig abgenommen, bevor Fast-
  Konsolidierungszaehler, Composite-Zustand oder Receipt materialisiert
  werden.

Jeder Typ-, Rollen- oder Digestunterschied verwirft beide lokalen Ergebnisse.
Es entsteht kein Composite-Nachzustand, kein Receipt und kein Result.

## K5: Konsolidierungs-, Composite- und Receiptidentitaet

Der Fast-Konsolidierungscommit ist nur fuer einen nach K3 gueltigen,
berechtigten Kandidaten erlaubt. Er aendert ausschliesslich im ausgewaehlten
Fast-Slot:

- `consolidation_count := consolidation_count + 1`;
- `last_consolidation_exposure_digest := aktuelle exposure_digest`.

Alle anderen Fast-Felder bleiben bitgleich zum Kandidatennachzustand.

Das Composite-Ergebnis ist nur gueltig, wenn:

- Generation exakt Vorzustandsgeneration plus eins ist;
- Parentdigest exakt der Composite-Vorzustandsdigest ist;
- letzter Expositionsdigest exakt der aktuelle Expositionsdigest ist;
- Fast-Nachzustand exakt dem abgenommenen Fast-Ergebnis einschliesslich
  optionalem Konsolidierungscommit entspricht;
- beide PPB-1-Nachzustaende bei Commit exakt K4 entsprechen und sonst
  bitgleich zu ihren Vorzustaenden sind.

Das Receipt muss Konfigurationsdigest, Owner-Autorisierungsvorzustandsdigest,
Expositionsdigest, Composite-Vorzustandsdigest und Fast-Kandidatendigest
bitgleich aus den direkten Quellen uebernehmen. Ferner gilt:

- `COMMITTED` genau dann, wenn der Kandidat berechtigt und beide PPB-1-
  Ergebnisse nach K4 bestanden sind;
- `COMMITTED` erfordert `FAST_UPDATED`, beide Readoutdigests und beide
  unabhaengigen Stabilitaetsbooleans;
- `NOT_ELIGIBLE` erfordert leere PPB-1-Readout- und Stabilitaetsrollen;
- Primaerereignis, Konfliktflag, Ablaufdigests, Ersatzdigest und Slot-ID sind
  exakt die Werte des Fast-Kandidaten;
- alle drei Nachzustandsdigests und der Composite-Nachzustandsdigest stimmen
  mit dem ausgegebenen Composite-Zustand.

## K6: Read-only-Findingidentitaet

Ein `TSPM1ReadOnlyFinding` ist nur gueltig, wenn:

- Konfigurations-, beobachteter Composite- und Probe-Digest exakt den
  direkten Eingaben entsprechen;
- ein positiver Fast-Befund genau einen gueltigen Slotdigest, Slot-ID und
  zwei endliche Distanzen innerhalb der Schwellen bindet;
- ein negativer Fast-Befund alle vier Fast-Ergebnisfelder leer laesst;
- `SLOW_UNAVAILABLE` genau fuer einen frischen PPB-1-Zustand gilt und keinen
  Findingdigest traegt;
- `SLOW_RECOGNIZED` beziehungsweise `SLOW_NOT_RECOGNIZED` exakt dem
  jeweiligen abgenommenen S1-WU-Befund entspricht und dessen Digest bindet;
- `SLOW_PPB1_CONTEXT` genau zwei positive Slow-Befunde voraussetzt;
- `FAST_ASSOCIATIVE_CONTEXT` mindestens einen nicht positiven Slow-Befund
  und einen positiven gemeinsamen Fast-Befund voraussetzt;
- `NO_COMPLETE_CONTEXT` mindestens einen nicht positiven Slow-Befund und
  keinen positiven gemeinsamen Fast-Befund voraussetzt.

Die Kontextquelle ist damit eine abgeleitete, nicht frei waehlbare Rolle.

## K7: Step-Result- und Owneridentitaet

Ein `TSPM1StepResult` ist nur gueltig, wenn:

- Receipt-Nachzustandsdigest und Composite-Nachzustandsdigest gleich sind;
- Receipt-Konfigurationsdigest und Composite-Konfigurationsdigest gleich
  sind;
- Owner-Autorisierung Konfiguration, Composite-Vorzustand und Exposition des
  Receipts exakt bindet;
- Ownerstatus `CONSUMED`, Versuch/Nutzung/Generation `1/1/1` und Fehlerrollen
  leer sind;
- Resultdigest exakt aus Composite-Nachzustand, Receipt und der
  Owner-Nachzustandsprojektion ohne `committed_result_digest` entsteht;
- erst danach der Owner denselben Resultdigest als
  `committed_result_digest` bindet.

Fehlerpfade duerfen keinen dieser Ergebnisdatentraeger ausgeben.

## K8: Endliches spaeteres Negativtestbudget

Eine spaetere getrennte Implementierungsfreigabe darf genau die bestehenden
elf TSPM-1-Tests erhalten und folgende 16 Negativtests ergaenzen:

1. falscher Expositionstyp hat Vorrang vor ungueltigem Composite;
2. Owner-Autorisierungsmismatch hat Vorrang vor ungueltigem Composite;
3. Owner-Autorisierungsmismatch hat Vorrang vor Quellenprovenienzfehler;
4. falscher Probehuellentyp hat Vorrang vor ungueltigem Composite;
5. `FAST_UPDATED` mit Konfliktflag wird verworfen;
6. Fast-Kandidat mit falscher Support-/Berechtigungsrelation wird verworfen;
7. Candidate-Nachzustand mit falschem Ablauf-, LRU- oder Slotrest wird
   verworfen;
8. `COMMITTED` mit anderem Primaerereignis wird verworfen;
9. `NOT_ELIGIBLE` mit PPB-1-Rollen wird verworfen;
10. Slow-Kontext ohne zwei positive Slow-Befunde wird verworfen;
11. Fast-Kontext ohne positiven Fast-Befund wird verworfen;
12. Step-Result mit Owner-/Receipt-Quellenabweichung wird verworfen;
13. auditives PPB-1-Ergebnis mit falschem Typ oder Konfigurationsdigest wird
    atomar verworfen;
14. auditives PPB-1-Ergebnis mit falschem Vorzustands-, Eingabe- oder
    Nachzustandsdigest wird atomar verworfen;
15. dieselben PPB-1-Fehlerklassen werden fuer die visuelle Seite symmetrisch
    atomar verworfen;
16. jeder Fehler nach einem lokal gueltigen ersten PPB-1-Ergebnis publiziert
    nichts und macht den Owner terminal ohne Retry.

Diese 16 Tests bilden ein festes Zusatzbudget. Weitere Testfaelle oder neue
Funktionspfade benoetigen eine neue Freigabe. In S2-DJ wird keiner dieser
Tests implementiert oder ausgefuehrt.

## Entscheidung

`PASS_TSPM1_STATIC_CORRECTION_CONTRACT_FOUR_GAPS_FULLY_BOUND`

DI-B1 bis DI-B4 sind auf Vertragsebene vollstaendig und materialisierbar
geschlossen. Der Befund korrigiert noch keinen Code und nimmt S2-DH noch
nicht abschliessend ab.

TSPM-1 bleibt eine private technische Memory-Komponente. API, Snapshot,
Feldpfad, Produktion und eine MCM-spezifische Feldinterpretation bleiben
ausgeschlossen.

## Naechster Schritt

S2-DK kann nach separater ausdruecklicher Freigabe ausschliesslich die
K1-bis-K7-Validator- und Reihenfolgekorrekturen im privaten TSPM-1-Modul
implementieren. PPB-1, bestehende Tests und alle oeffentlichen oder
feldbezogenen Pfade muessen unveraendert bleiben. Die 16 gebundenen
Negativtests und jede Testausfuehrung benoetigen danach eine weitere getrennte
Freigabe.
