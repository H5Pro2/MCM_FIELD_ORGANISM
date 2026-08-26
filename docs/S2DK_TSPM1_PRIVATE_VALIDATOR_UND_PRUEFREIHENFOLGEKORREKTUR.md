# S2-DK: Private TSPM-1-Validator- und Pruefreihenfolgekorrektur

## Auftrag und Grenze

S2-DK implementiert ausschliesslich die in S2-DJ gebundenen privaten
Validator- und Pruefreihenfolgekorrekturen. Geaendert wurde nur
`mcm_field_organism/_tspm1_private.py`.

Nicht geaendert wurden PPB-1, bestehende Tests, oeffentliche API,
Paketexporte, Snapshot und Feldpfad. Es wurden keine Zustands- oder
Probefunktionen und keine Tests ausgefuehrt. Die 16 in S2-DJ gebundenen
Negativtests wurden weder implementiert noch ausgefuehrt.

## K1: Fail-Closed-Reihenfolge

Der private Koordinator prueft nun nach Lock und terminalem Ownerstatus:

1. exakte Typen von Konfiguration, Composite-Vorzustand und Exposition;
2. Konfigurations- und Vertragsbindung;
3. Owner-Autorisierung gegen Konfiguration, Composite-Digest und
   Expositionsdigest;
4. Composite- und Fast-Zustand;
5. Quellenidentitaet und Provenienz;
6. Modalitaet, Geometrie und Traegerordnung;
7. Feldfenster, Quellclocks und strikt spaetere Endticks;
8. Fast-Kandidat und alle folgenden Ergebnisrelationen.

Damit wird ein nicht autorisierter Aufruf verworfen, bevor der Inhalt eines
nicht autorisierten Zustands oder einer nicht autorisierten Quelle fachlich
validiert wird. Jeder Fehler nach Lockgewinn bleibt terminal und erzeugt
keinen Nachzustand.

Die read-only Probe prueft nun ebenfalls alle drei exakten Argumenttypen vor
Composite- oder Quelleninhalt. Distanzen und S1-WU-Aufrufe liegen erst hinter
Zustands-, Provenienz-, Geometrie- und Zeitpruefung.

## K2: Fast-Kandidatenabnahme

Der neue relationale Fast-Validator rekonstruiert aus Konfiguration,
Vorzustand und aktueller Exposition die vollstaendige erwartete Transition.
Er vergleicht:

- Expositionszaehler, Quellclocks und Endticks;
- Ablaufmenge und nach Slot-ID geordnete Ablaufdigests;
- gemeinsamen Zwei-Modalitaeten-Match und Dreifachrangfolge;
- Updateformel, Support, letzten Auswahlschritt und Berechtigung;
- Konfliktflag;
- kleinsten freien Slot oder deterministischen LRU-Ersatz;
- ausgewaehlten Slot, Ersatzdigest und alle unveraenderten Restslots.

Ein Kandidat mit gueltigem Eigendigest, aber falscher Beziehung zu seiner
Quelle, wird damit verworfen.

## K3: PPB-1-Ergebnisabnahme

Nach den weiterhin genau zwei direkten PPB-1-Aufrufen werden beide lokalen
Ergebnisse symmetrisch geprueft. Erforderlich sind:

- exakter `PPB1StepResult`-, `PPB1BankState`- und `PPB1Readout`-Typ;
- korrekte Bank, Modalitaet und Konfiguration;
- exakter Vorzustandsdigest;
- exakter Eingabeprojektionsdigest des aktuellen gebundenen Originalframes;
- exakter Nachzustandsdigest;
- genau ein weiterer akzeptierter Schritt;
- korrekte Quellclock und aktueller Endtick;
- Uebereinstimmung von Readout, ausgewaehltem Slot, Support,
  Prototypwerten und Stabilitaetsstatus.

Erst nach bestandener auditiver und visueller Abnahme wird der Fast-
Konsolidierungszustand lokal fortgeschrieben. Ein Unterschied auf einer Seite
verwirft beide lokalen Ergebnisse ohne Teilausgabe.

## K4: Composite-, Receipt- und Ownerrelationen

Der optionale Fast-Konsolidierungscommit darf nur den
Konsolidierungszaehler und letzten Expositionsdigest des ausgewaehlten Slots
aendern. Ein neuer Composite-Validator bindet Generation, Parentdigest,
Expositionsdigest, Fast-Zustand und beide PPB-1-Zustaende exakt an ihre
Vorgaenger und lokalen Ergebnisse.

Das Receipt wird gegen eine vollstaendig aus Owner-Vorzustand, Exposition,
Composite-Vorzustand, Fast-Kandidat, Konsolidierungsentscheidung, beiden
PPB-1-Readouts und Composite-Nachzustand abgeleitete Referenzform geprueft.

`TSPM1StepResult` erzwingt nun zusaetzlich:

- denselben Konfigurationsdigest in Receipt und Composite;
- dieselben autorisierten Konfigurations-, Vorzustands- und
  Expositionsdigests in Owner und Receipt;
- denselben Composite-Nachzustandsdigest in Receipt und Ergebnis.

Die azyklische Result-/Owner-Digestbildung bleibt unveraendert.

## K5: Read-only-Ergebnisrelationen

Ein Fast-Finding prueft jetzt endliche Distanzen in `[0,2]` und eine
deterministisch aus Fast- und Slow-Befunden abgeleitete Kontextquelle.
`SLOW_PPB1_CONTEXT`, `FAST_ASSOCIATIVE_CONTEXT` und `NO_COMPLETE_CONTEXT`
sind nicht mehr frei kombinierbar.

Die zwei vorhandenen S1-WU-Befunde werden auf exakten Typ, Probe-ID, Bank,
Modalitaet, Konfiguration, beobachteten Zustand und Eingabeprojektionsdigest
geprueft. Der abschliessende relationale Findingvalidator rekonstruiert den
rangbesten Fast-Match und prueft die Slow-Verfuegbarkeit gegen die beiden
PPB-1-Zustaende.

## Statische Integritaetspruefung

Der korrigierte Quelltext wurde ausschliesslich statisch als ASCII-Python-AST
geprueft. Er ist syntaktisch materialisierbar. Es bestehen weiterhin exakt
zwei direkte `advance_ppb1_bank`-Aufrufstellen mit den aktuellen auditiven
und visuellen Originalframes.

Der neue private Quelldigest lautet:

`c33ea3fdbc399b88e1416e91f8421f362060de1e368817e3673a93c522013252`

Der bestehende S2-DH-Testdigest und alle vier gebundenen PPB-1-Quelldigests
sind unveraendert. Ausser dem privaten TSPM-1-Modul wurde keine
Implementierungs- oder Testdatei geaendert.

## Entscheidung

`PRIVATE_TSPM1_CORRECTIONS_IMPLEMENTED_AWAITING_SEPARATE_NEGATIVE_TEST_CONTRACT`

Die vier S2-DI-Luecken sind gemaess S2-DJ im privaten Code korrigiert. Wegen
der ausdruecklichen Testsperre ist dies noch keine ausgefuehrte oder
abgeschlossene Implementierungsabnahme.

TSPM-1 bleibt eine private technische Memory-Komponente. Es gibt keine neue
Memory-Funktion, keine Feldintegration und keinen MCM-spezifischen
Feldmechanismusbefund.

## Naechster Schritt

S2-DL sollte ausschliesslich als statischer Materialisierungs- und
Ausfuehrungsvertrag fuer die 16 bereits in S2-DJ gebundenen Negativtests
erstellt werden. Er muss Fixtures, Mutationspunkte, erwartete Fehlercodes,
Atomaritaetsorakel und das spaetere Ausfuehrungsbudget festlegen. Noch keine
Testimplementierung oder Testausfuehrung.
