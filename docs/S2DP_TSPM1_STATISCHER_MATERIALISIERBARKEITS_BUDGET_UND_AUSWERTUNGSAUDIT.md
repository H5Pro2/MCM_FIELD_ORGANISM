# S2-DP: Statischer TSPM-1-Materialisierbarkeits- und Budgetaudit

## Auftrag und Grenze

S2-DP prueft ausschliesslich den statischen S2-DO-Vertrag auf eindeutige
Materialisierbarkeit, faire Budgets, Comparatorordnung, Reduktionsgrenzen
und vollstaendige Quellen- und Ergebnisbindungen.

Es wurden keine Projektmodule importiert, keine Zustandsfunktion aufgerufen,
keine Tests oder Vergleiche ausgefuehrt und keine Implementierung geaendert.
TSPM-1, PPB-1, API, Snapshot, Feldpfad und Produktion bleiben unveraendert.

## Gepruefte Vertragsoberflaeche

Der S2-DO-Artefaktdigest
`431fa352d0a32789af72531f34bdd6b2462fcee8f43b026db47bb39fb1ddade2`
ist kanonisch gueltig. Das Artefakt enthaelt:

- sechs einfache Baselinearme;
- eine generische Zwei-Ebenen-Reduktionskontrolle;
- sieben Pflichtgeschichten;
- neun Budgetachsen;
- zwoelf getrennte Messrollen;
- vier zulaessige Endentscheidungen.

Die Funktionsfrage ist nicht zirkulaer formuliert: Erfolg wird nicht aus
einem TSPM-1-internen Digest, Slotnamen oder Konsolidierungsstatus abgeleitet.
Auch die generische Reduktionskontrolle sperrt bereits jede MCM-spezifische
Interpretation.

Diese Punkte genuegen jedoch noch nicht fuer eine eindeutige spaetere
Fixture- oder Runnerimplementierung.

## Bestandene Teilpruefungen

Folgende Bindungen sind statisch ausreichend:

1. Die Funktionsrollen Aufnahme, Haltedauer, Konsolidierung, Konflikt,
   Verdraengung und read-only Abruf sind getrennt benannt.
2. Fast- und Slow-Abruf duerfen nicht zu einem gemeinsamen internen Befund
   verschmolzen werden.
3. No-Memory, PPB-1, adaptive Prototypbank, Nachhall und kurzfristiger
   Zustand sind als getrennte Baselineklassen vorhanden.
4. Jede Geschichte beginnt aus einem frischen unabhaengigen Zustand.
5. Replay, Feldintegration und semantische Zusatzinformation sind
   ausgeschlossen.
6. `METHOD_INVALID`, Baselineerklaerung, Kandidatenfehler und technischer
   Vorteil sind getrennte Endentscheidungen.

## Materialisierungsblocker

### DP-B01: Keine feste Vergleichskonfiguration

S2-DO verwendet `K`, `C` und `E` symbolisch. Der vorhandene S2-DH-Testhelper
zeigt zwar eine moegliche Konfiguration mit `K=3`, `C=2`, `E=8`, bindet sie
aber nicht als S2-DO-Vergleichsquelle. Ebenso fehlen die zwei konkreten
PPB-1-Konfigurationen, Profil-, Geometrie- und Traegerdigests.

Ohne genau eine quellgebundene Konfiguration sind Matrixgroesse,
Zustandsbudget, Ablaufzeitpunkt und Konsolidierungszahl nicht endlich
bestimmt.

### DP-B02: Geschichten sind nicht literal materialisiert

`A:X`, `A:Y`, `B:X`, Stoerer, Negativprobe und nahe Probe besitzen keine
konkreten Audio-/Video-Vektoren, Timed Frames, Feldfenster oder
Provenienzhüllen. Begriffe wie `hinreichend getrennt`, `mindestens E` und
`ausserhalb mindestens einer Schwelle` lassen mehrere gueltige Payloads und
Ablauflaengen zu.

Vor Code muessen fuer H1 bis H7 exakte Expositions- und Probeindizes,
Vektoren, Distanzmargen, erwartete Matchrelationen und Quellhuellen gebunden
werden.

### DP-B03: PPB-Direktbudget widerspricht der allgemeinen Schreibgrenze

`PPB_DIRECT` soll jeden Originalframe erhalten. Gleichzeitig duerfen alle
Baselines hoechstens dieselbe Zahl von Zustandsschreibvorgaengen wie TSPM-1
verwenden. TSPM-1 ruft PPB-1 jedoch nur bei
konsolidierungsberechtigten Expositionen auf.

Damit ist `PPB_DIRECT` entweder eine bewusst schreibstaerkere Oberbaseline
oder ein budgetgleicher Arm, aber nicht beides. Seine Ergebnisrolle und sein
Ausschluss aus einer budgetgleichen Erfolgsentscheidung muessen eindeutig
festgelegt werden.

### DP-B04: B2, B3 und B4 besitzen keine eindeutige Mechanik

Fuer die adaptive Online-Prototypbank fehlen genaue gemeinsame
Matchdistanz, Update-, Ablauf- und Ersatzregeln. Fuer den Nachhall fehlen
Abschwaechungsregel und Probeoperator. B4 laesst die Wahl zwischen FIFO und
Ring offen.

Der vorhandene Projektbestand stellt keine einzelne bereits gebundene
Implementierung bereit, die diese drei Rollen ohne neue Entscheidung exakt
erfuellt. Jede Rolle benoetigt vor Implementierung genau eine reine
Zustandsform und Uebergangsspezifikation.

### DP-B05: Ressourcenledger ist nicht zaehlbar

`Gesamtbudget fuer skalare Werte, Slotmetadaten und Zustandsdigests` legt
nicht fest:

- ob Provenienz- und Sicherheitsdigests als funktionale Speicherkapazitaet
  zaehlen;
- wie Float-, Integer-, Boolean- und Stringrollen in Bits umgerechnet
  werden;
- ob unbesetzte Slots voll zaehlen;
- wie Audio- und Videodimensionen summiert werden;
- ob Baselineverwaltungsdaten und Kandidaten-Owner gleich behandelt werden.

Ohne kanonisches Ledger kann Budgetgleichheit weder vorab berechnet noch
spaeter fail-closed validiert werden.

### DP-B06: Operationsbudget ist kandidatenabhaengig

Die erlaubte Zahl von Schreibvorgaengen und Distanzbewertungen wird mit
`hoechstens wie TSPM-1` beschrieben. TSPM-1-Aufrufe haengen jedoch von
Matches, Ablauf und Konsolidierung innerhalb der spaeteren Geschichte ab.

Ein erst nach dem Kandidatenlauf bekanntes Baselinebudget waere zirkulaer.
Erforderlich sind aus der festen Fixture vorab berechnete Obergrenzen oder
ein kandidatenunabhaengiges gemeinsames Operationsledger.

### DP-B07: Comparator- und Tie-Regeln sind nicht vollstaendig

Die gerichtete Gegenprognose verlangt einen kombinierten Vorteil in H1, H3,
H4 und H5 sowie keine hoehere Fehlakzeptanz. Nicht festgelegt sind:

- exakte boolesche Passbedingungen je Metrik;
- Reihenfolge bei Gleichstand;
- Umgang mit einem Vorteil in einer und einem Nachteil in einer anderen
  Geschichte;
- Auswahl der `staerksten einfachen Baseline`;
- Vorrang zwischen Kandidatenfehler, Baselineerklaerung und
  `METHOD_INVALID`.

Eine eindeutige lexikographische Entscheidungsfolge und eine vollstaendige
Wahrheitstabelle fehlen.

### DP-B08: Quellen-, Zell- und Ergebnisformen fehlen

Der Vertrag bindet noch keine Matrixzell-IDs, Konfigurations- und
Fixturedigests, Baseline-Vor- und Nachzustandsformen, read-only Findings,
Budgetreceipts oder einen atomaren Gesamtresultattyp. Auch die Abbildung von
R0 auf TSPM-1-Ereignisse und Ausgaben ist nicht definiert.

Ohne diese Formen koennten Teilresultate, vertauschte Baselineausgaben oder
stale Proben nicht eindeutig fail-closed verworfen werden.

## Auditentscheidung

`STOP_TSPM1_COMPARISON_MATERIALIZATION_EIGHT_BINDINGS_OPEN`

S2-DO besitzt eine fachlich sinnvolle und falsifizierbare Funktionsfrage,
ist aber noch nicht eindeutig implementierbar. Der Stopp betrifft die
Versuchs- und Budgetmaterialisierung, nicht die bereits abgeschlossene
private TSPM-1-Implementierung.

Es entsteht weder ein positiver noch ein negativer TSPM-1-Funktionsbefund.
Insbesondere ist aus diesem Audit keine Memory- oder MCM-spezifische
Wirksamkeit ableitbar.

## Naechster Schritt

S2-DQ kann nach separater Freigabe ausschliesslich einen statischen
Korrektur- und Materialisierungsvertrag fuer DP-B01 bis DP-B08 erstellen.
Er muss genau eine Konfiguration, literale H1-bis-H7-Payloads, eindeutige
B2-/B3-/B4-Regeln, zwei getrennte PPB-Direktrollen, ein kanonisches
Ressourcen- und Operationsledger, eine Comparatorwahrheitstabelle sowie
vollstaendige Zell-, Receipt- und Ergebnisformen binden.

Implementierung, Test- oder Vergleichsausfuehrung und Feldintegration bleiben
bis zu einem spaeter bestandenen Wiederholungsaudit gesperrt.
