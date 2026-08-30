# S2-HF: Vollstaendiger Wiederholungsaudit nach S2-HG

Status: `S2HF_REPEAT_PASSED_COMPACT_PROJECTIONS_IMPLEMENTATION_ELIGIBLE`

## Grenze

Der Wiederholungsaudit prueft den S2-HE-Vertrag mit den zwei ausdruecklichen
S2-HG-Korrekturen. Es wurden keine Projektmodule importiert, keine Tests oder
Funktionen ausgefuehrt und keine Speicher-, Rezeptor-, Kontext- oder
Feldzustaende erzeugt. S2-HC bleibt dauerhaft `NOT_EVALUABLE`.

Der Audit gibt keinen Hauptlauf frei. Er stellt ausschliesslich fest, ob die
drei kompakten Aufzeichnungsprojektionen nach einer separaten Freigabe
implementiert und neutral qualifiziert werden koennen.

## Auditquellen

Statisch abgeglichen wurden:

- der S2-HE-Vertrag und sein Maschinenbeleg;
- der urspruengliche S2-HF-Audit und sein Maschinenbeleg;
- der S2-HG-Korrekturvertrag und sein Maschinenbeleg;
- die S2-GR-Operationsregistry;
- S2-GT-Runner, Recorder und Verifikator;
- S2-FS-Koordinator, S2-GC-Bundleprojektion und S2-GI-Zweibereichsprojektion;
- der reine S2-GJ-Auswerter.

Die kanonische Groessenform bleibt unveraendert: ASCII-JSON, sortierte
Schluessel, Trenner `,` und `:`, `ensure_ascii = true`, maximal 96 Zeichen
lange Owner-ID und genau ein abschliessendes LF.

## Materialisierung der zwei Korrekturen

### Owner-Vorzustand

Der Koordinator bildet `owner_prestate_digest` unmittelbar vor dem Wechsel
des Owners nach `IN_PROGRESS`. Exakt dieser Wert wird dem
`B4TSPM1StepReceipt` uebergeben und gehoert bereits zu dessen
Digestgrundlage. Die Rolle ist damit vor dem kompakten Formation-Receipt
verfuegbar, typisiert und quellgebunden.

Der Wert ist weder mit dem autorisierten Composite-Vorzustand noch mit dem
Owner-Nachzustand gleichgesetzt. Eine nachtraegliche Rekonstruktion ist nicht
erforderlich und nicht zulaessig.

### Sequenzevidenz

Der Runner erstellt je Geschichte ein konkretes
`ValidatedB4ShortSequenceEvidence` und uebergibt genau dieses Objekt an
`project_perceptual_context_bundle`. Der Projektor prueft dessen Digest vor
der Bundlebildung und bindet ihn als
`B4ShortSequenceFinding.source_evidence_digest`.

Die korrigierte S2-GC-Projektion zeichnet diesen vorhandenen Digest zusammen
mit dem daraus entstandenen Findingdigest in der typisierten positionalen
Rolle `sequence_digests` auf. Es wird kein Status, Referenzsatz oder Sollwert
zurueckgerechnet.

Beide Materialisierungspruefungen sind bestanden.

## Neuberechnung aller 60 Huellen

Die Neuberechnung umfasst die vollstaendige unveraenderte Recorderhuelle und
die jeweils korrigierte Projektionsform. Die 60 Einzeloperationen und ihre
kanonischen Bytegroessen sind im Maschinenbeleg einzeln aufgefuehrt.

### 52 Formation-Receipts

- 36 Schritte mit `B4_APPENDED`: je 2.788 Byte.
- 16 Schritte mit `B4_EVICTED_AND_APPENDED`: je 2.801 Byte.
- Maximum: 2.801 Byte.
- Reserve zu 3.200 Byte: 399 Byte.
- Reserve zu 4.095 Byte: 1.294 Byte.

Die Zunahme gegenueber S2-HE betraegt exakt 91 Byte je Huelle. Sie besteht
aus Komma, Feldname, Doppelpunkt, Anfuehrungszeichen und dem 64-stelligen
Digest. Der Zeilenabschluss bleibt unveraendert.

### Vier S2-GC-Receipts

| Operation | Form | Groesse |
| --- | --- | ---: |
| `op-0116` | stabile Vollform | 3.174 Byte |
| `op-0117` | stabile Vollform | 3.174 Byte |
| `op-0118` | stabile Vollform | 3.174 Byte |
| `op-0119` | `ABSENT_VALID` | 2.658 Byte |

Die positionsgebundene Substitution vergroessert jede Huelle exakt um 62
Byte. Das Maximum bleibt 26 Byte unter der zusaetzlichen 3.200-Byte-Grenze und
921 Byte unter der effektiven Registrygrenze.

### Vier S2-GI-Receipts

S2-GI ist von S2-HG nicht betroffen:

| Operation | Form | Groesse |
| --- | --- | ---: |
| `op-0120` | stabile Vollform | 2.977 Byte |
| `op-0121` | stabile Vollform | 2.977 Byte |
| `op-0122` | stabile Vollform | 2.977 Byte |
| `op-0123` | `ABSENT_VALID` | 2.509 Byte |

### Groessenergebnis

Alle 60 vollstaendigen Huellen bleiben unter 3.200 und 4.096 Byte. Das globale
Maximum betraegt 3.174 Byte; die kleinste Reserve zur effektiven
Registrygrenze betraegt 921 Byte. Die Summe der 60 konkret projizierten
Huellen betraegt 168.804 Byte.

Der Groessenaudit ist bestanden.

## Vollobjekttrennung

Die Korrekturen fuegen nur zwei 64-stellige Digests hinzu. Sie betten weder
Owner-, Composite-, B4-, TSPM-, PPB-1-, Sequence-Evidence-, Finding-, Bundle-
noch Zweibereichsobjekte ein.

- Formation reicht den vollstaendigen Nachzustand weiterhin nur im
  In-Memory-Funktionspfad weiter.
- S2-GC reicht das vollstaendige Bundle weiterhin nur an S2-GI weiter.
- S2-GI reicht das vollstaendige Zweibereichsbundle weiterhin an Verbraucher
  und Baseline weiter.
- Der Verifikator darf aus keinem Digest Werte oder Zustaende rekonstruieren.

Der Ausschluss indirekter Vollobjekteinbettung ist bestanden.

## Offline-Validierung

Mit S2-HG kann der unabhaengige Verifikator die zuvor blockierten Beziehungen
vollstaendig nachrechnen:

- Formation: Ressourcenledger, Owner-Nachzustand, Step-Receipt und
  Step-Result einschliesslich Owner-Vorzustand;
- S2-GC: Komponenten-, Kandidaten-, Rollen-, Sequenz-, Ledger- und
  Bundledigest einschliesslich exakter Sequenzevidenz;
- S2-GI: Bereichs-, Ledger- und Bundledigest.

Die direkten Elternartefakte liefern weiterhin die nicht duplizierten Werte
und Quellen. Der reine Auswerter erhaelt unveraendert alle benoetigten
Funktionsfelder aus den Armresultaten und der getrennten Zielwertfixture.

`HF-B01` und `HF-B02` sind geschlossen. Offline-Verifikatorversorgung und
Auswertungsversorgung sind bestanden.

## Quellen- und Digestgraph

Die beiden neuen Kanten sind vorwaertsgerichtet:

```text
Owner-Vorzustand
  -> Step-Receipt
  -> Step-Result
  -> kompakte Formation
  -> naechster Formation-START

Sequenzevidenz
  -> Sequenzfinding
  -> S2-GC-Bundle
  -> kompakte S2-GC-Projektion
  -> kompakte S2-GI-Projektion
  -> Armreceipt
  -> Evaluation
```

`projection_digest` schliesst sich selbst aus. Recorder-Artefaktdigests
entstehen erst nach der jeweiligen Projektion. Evaluation und Abschluss sind
keine Eltern des Ausfuehrungspfads. Es gibt keine Selbstkante, Rueckkante oder
Mehrdeutigkeit.

Quellen-, Owner-, Operations-, Receipt- und Nachfolgerbindungen sowie
Zyklenfreiheit sind bestanden.

## Budgets und Fehlerwege

Keine Registryobergrenze wird geaendert. Die gebundenen Pfadmaxima bleiben:

```text
MAX_SUCCESS_PATH_BYTES = 2.009.088
MAX_FAILURE_PATH_BYTES = 2.045.952
MAX_RUN_PATH_BYTES     = 2.045.952
```

Die tatsaechlich kompakteren Huellen liegen innerhalb der bereits reservierten
Einzelrollen. Erfolgspfad und Fehlerpfad bleiben exklusiv.

- Groessenverletzung: `E008`.
- Registrierter, aber phasenunpassender Fehler: `E002`.
- Unregistrierte oder sonstige Ausnahme: `E009`.

Budgetaddition und Fehlercodewege sind bestanden.

## Entscheidung

Der vollstaendige S2-HF-Wiederholungsaudit ist bestanden:

- beide fehlenden Digestrollen sind direkt materialisierbar;
- alle 60 kanonischen Vollhuellen sind neu berechnet und innerhalb der
  Grenzen;
- keine Vollobjekte werden erneut eingebettet;
- Offline-Verifikator und Auswerter erhalten alle benoetigten Rollen;
- der Digestgraph bleibt eindeutig und azyklisch;
- Budgets und Fehlercodewege bleiben unveraendert.

Status:

`S2HF_REPEAT_PASSED_COMPACT_PROJECTIONS_IMPLEMENTATION_ELIGIBLE`

Dies ist ausschliesslich die statische Voraussetzung fuer eine spaeter separat
freizugebende Implementierung der drei kompakten Aufzeichnungsprojektionen.
Keine Implementierung, Qualifikation oder Hauptausfuehrung ist durch diesen
Audit freigegeben oder erfolgt.
