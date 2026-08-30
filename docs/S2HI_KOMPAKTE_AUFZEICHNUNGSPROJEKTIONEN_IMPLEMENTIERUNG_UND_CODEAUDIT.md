# S2-HI: Kompakte Aufzeichnungsprojektionen und statischer Codeaudit

Status: `S2HI_IMPLEMENTED_STATIC_CODE_AUDIT_PASSED_NEUTRAL_QUALIFICATION_REQUIRED`

## Grenze

S2-HI implementiert ausschliesslich die drei in S2-HE bis S2-HG gebundenen
kompakten Aufzeichnungsprojektionen:

1. `CompactCompositeFormationReceiptV1`;
2. `CompactS2GCProjectionReceiptV1`;
3. `CompactS2GIProjectionReceiptV1`.

Geaendert wurden nur der private S2-GT-Runner und der unabhaengige read-only
Verifikator. Recorder, Registry, Fixtures, B4, TSPM-1, PPB-1, S2-GC, S2-GI,
Verbraucher, Baseline, Auswerter, API, Snapshot und Feldpfad bleiben
unveraendert.

Es wurden keine Projektmodule importiert, keine Tests ausgefuehrt und keine
Rezeptor-, Speicher-, Projektions- oder Kontextfunktion aufgerufen. Der
Hauptschalter bleibt `False`. S2-HC bleibt dauerhaft `NOT_EVALUABLE`.

## Implementierte Aufzeichnungsgrenze

Jede der drei Rollen verwendet nun dieselbe Trennung:

```text
vollstaendiges validiertes In-Memory-Funktionsresultat
  -> reine kompakte Aufzeichnungsprojektion
  -> kanonische Groessenpruefung
  -> append-only Receipt

vollstaendiges In-Memory-Funktionsresultat
  -> unveraendert an den funktionalen Nachfolger
```

Die kompakte Projektion ersetzt das Funktionsresultat nicht. Der Runner prueft
die Objektidentitaet und den semantischen Ergebnisdigest vor und nach der
Receiptbildung. Kein Nachfolger rekonstruiert Werte oder Zustaende aus einem
Digest.

## Formation

Alle 52 `COMPOSITE_FORMATION`-Operationen verwenden
`_record_compact_formation`. Die Projektion erhaelt:

- den Digest des unmittelbar zugehoerigen kompakten ReceptorReceipts;
- den vollstaendigen Step-, Komponenten-, Ledger- und Ownerbezug;
- `owner_prestate_digest` exakt aus
  `B4TSPM1StepReceipt.owner_prestate_digest`;
- Generation, Vor- und Nachzustand sowie die atomare Owner-Endlage;
- einen eigenen `projection_digest`.

Der vollstaendige `B4TSPM1StepResult.poststate` bleibt im Runner und wird
unveraendert fuer die naechste Formation oder Probe verwendet. Der kompakte
Receipt-Digest der vorangehenden Formation wird im START der naechsten
Formation derselben Geschichte gebunden.

Der unabhaengige Verifikator berechnet aus der kompakten Form erneut:

- Ressourcenledger;
- Composite-Nachzustandsdigest;
- Step-Receipt-Digest;
- Owner-Nachzustandsdigest;
- Step-Result-Digest;
- Projektionsdigest.

## S2-GC

Alle vier `S2GC_PROJECTION`-Operationen verwenden
`_record_compact_s2gc`. Das vollstaendige `PerceptualContextBundle` bleibt der
unveraenderte In-Memory-Eingang von S2-GI.

Die Aufzeichnung bindet insbesondere:

```text
sequence_digests = (
    ValidatedB4ShortSequenceEvidence.evidence_digest,
    B4ShortSequenceFinding.finding_digest,
)
```

Der erste Digest stammt aus exakt dem Sequence-Evidence-Objekt, das dem
S2-GC-Projektor uebergeben wurde. Der zweite Digest stammt aus dem daraus
erzeugten Finding. Eine Rekonstruktion aus Status, Fixture oder Sollwert findet
nicht statt.

Der Verifikator liest das gebundene vorausgehende
`B4TSPM1ReadOnlyFinding`-Artefakt und berechnet daraus erneut:

- Komponenten-, Kandidaten- und Rollenfindings;
- Sequence-Evidence- und Sequence-Finding-Digest;
- Ressourcenledger und Bundledigest;
- alle parallelen Rollen- und Komponentenlisten.

Der S2-GI-START bindet sowohl den semantischen `bundle_digest` als auch den
Artefaktdigest des kompakten S2-GC-Receipts.

## S2-GI

Alle vier `S2GI_PROJECTION`-Operationen verwenden
`_record_compact_s2gi`. Der vollstaendige `TwoAreaContextBundle` bleibt der
unveraenderte In-Memory-Eingang fuer Kontextverbraucher und direkte Baseline.

Die Projektion erhaelt getrennte A- und B-Befunde, stabile B-Komponenten,
Quellen- und Wertedigests, Ledger, Zustandsbindung und den eigenen
Projektionsdigest. Sie speichert keine vollstaendigen Komponentenwerte.

Der Verifikator bindet die Projektion an das konkrete kompakte S2-GC-
Elternartefakt und berechnet A-Finding, B-Finding, Zweibereichsledger und
Bundledigest erneut. Jeder kontextnutzende Arm-START bindet anschliessend den
semantischen Zweibereichsdigest und den zugehoerigen kompakten S2-GI-
Artefaktdigest.

## Fail-Closed-Regeln

Die Implementierung stoppt vor einer gueltigen Aufzeichnung bei:

- falschem Operationstyp, History- oder Quellenordinal;
- fehlendem, fremdem oder ungueltigem Elternartefaktdigest;
- abweichender Owner-, Vorzustands-, Probe- oder Quellenbindung;
- unvollstaendigen oder unterschiedlich langen parallelen Listen;
- ungueltigen Digestformen;
- abweichenden Ledger-, Finding-, Bundle- oder Projektionsdigests;
- fehlender Nachfolgerbindung;
- Ueberschreitung einer Rollen- oder Registrygrenze.

Die Fehlercodeentscheidung bleibt unveraendert. Groessenueberschreitungen
bleiben `E008`; registrierte phasenunpassende Fehler bleiben `E002`; nur
unregistrierte oder sonstige Ausnahmen werden `E009`.

## Statischer Groessenabgleich

Die implementierten Datentypfelder stimmen exakt mit den im S2-HF-
Wiederholungsaudit gebundenen Feldern ueberein. Der Recorderumschlag und seine
kanonische ASCII-Serialisierung sind unveraendert. Die 60 Registryoperationen
verteilen sich unveraendert auf 52 Formation-, vier S2-GC- und vier S2-GI-
Receipts.

| Rolle | Anzahl | Implementiertes Maximum | Grenze |
| --- | ---: | ---: | ---: |
| Formation | 52 | 2.801 Byte | 2.801 Byte |
| S2-GC | 4 | 3.174 Byte | 3.174 Byte |
| S2-GI | 4 | 2.977 Byte | 2.977 Byte |

Jede Rolle wird zusaetzlich gegen 3.200 Byte und gegen die unveraenderte
4.096-Byte-Registryrolle geprueft. Die kleinste effektive Registryreserve
bleibt 921 Byte.

## Budgets, Gate und Codegrenzen

Unveraendert bleiben:

```text
MAX_SUCCESS_PATH_BYTES = 2.009.088
MAX_FAILURE_PATH_BYTES = 2.045.952
MAX_RUN_PATH_BYTES     = 2.045.952
MAIN_EXECUTION_ENABLED = False
```

Der statische Audit hat bestaetigt:

- keine generische Vollobjektaufzeichnung fuer die drei Rollen verbleibt;
- genau 60 spezialisierte Registryoperationen sind gebunden;
- Runner- und Verifikatorfeldmengen sind identisch;
- alle neuen Digestkanten zeigen vorwaerts;
- keine Importzeitwirkung oder automatische Ausfuehrung wurde eingefuehrt;
- die ausgeschlossene Bootstrap-Datei wurde nicht beruehrt.

## Entscheidung

Die drei kompakten Aufzeichnungsprojektionen sind implementiert und der rein
statische Codeaudit ist bestanden.

Status:

`S2HI_IMPLEMENTED_STATIC_CODE_AUDIT_PASSED_NEUTRAL_QUALIFICATION_REQUIRED`

Dies ist noch kein technischer Laufbefund und kein Kontextfunktionsbefund. Als
naechster Schritt ist ausschliesslich eine getrennt freizugebende neutrale
Qualifikation der drei Projektoren, ihrer Groessengrenzen, Eltern- und
Nachfolgerbindungen sowie ihrer Fail-Closed-Wege zulaessig. Ein neuer
Kontextfunktionslauf bleibt gesperrt.
