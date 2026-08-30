# S2-GT: Private Laufhuelle und statischer Codeaudit

Stand: 2026-08-30

## Auftrag und Grenze

S2-GT materialisiert die in S2-GL, S2-GN und S2-GR gebundene private
Laufhuelle. In diesem Schritt wurden keine neuen Module importiert, keine
Tests ausgefuehrt, keine Verzeichnisse angelegt und keine Rezeptor-, Speicher-,
Koordinator-, Verbraucher- oder Auswertungsfunktion aufgerufen.

Der Hauptschalter bleibt fest geschlossen:

```text
MAIN_EXECUTION_ENABLED = False
```

## Genau vier private Module

| Rolle | Datei | SHA-256 |
| --- | --- | --- |
| literale Fixtures und Registrybindung | `tools/_s2gt_private_fixture_registry.py` | `bdab04c57764d98d0cc449f98c246c55d7789620b56990778e0ea671bc39038c` |
| geschlossener privater Runner | `tools/_s2gt_private_runner.py` | `d166a488fc56eca69b2b161f75d2503148e4319c854a285fe090020da6f25a77` |
| append-only Recorder | `tools/_s2gt_private_append_only_recorder.py` | `f9e9b204eabf1d63291f2f6c933c92e00ba01f8c0f64e3ee6184adfbad3ae51c` |
| unabhaengiger read-only Verifikator | `tools/_s2gt_private_result_verifier.py` | `53d4ba7bf8853ac6a765053da0700a54021f1764bbd086150234aea5099b6378` |

Der Verifikator verwendet ausschliesslich die Python-Standardbibliothek. Er
importiert weder Runner oder Recorder noch Rezeptor-, Memory-, Koordinator-
oder Feldmodule.

## Gebundener Funktionsumfang

Das Fixturemodul enthaelt literal:

- 25 erzeugbare `uint8`-Bildfixtures mit 18 ortsgebundenen Kanalwerten;
- 14 synthetische auditive 4-von-8-Rezeptorzustaende;
- vier neutrale Geschichten `h01..h04` mit je 13 Schritten;
- vier getrennte Vollproben und eine gemeinsame maskierte Verbraucherprobe;
- sieben neutrale Armbindungen;
- die vier digestgebundenen S2-GR-Registries.

Die Bildfixtures wurden statisch und ohne Modulimport erneut zu jeweils
28.800 Rohbytes materialisiert. Alle 25 SHA-256-Werte stimmen mit S2-GL
ueberein.

Der Runner bildet die Registryfolge ohne dynamische Operationserzeugung ab:

```text
1 RUN_PREPARE
52 FORMATION_RECEPTOR_ANALYSIS
52 COMPOSITE_FORMATION
4 CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS
4 COMPOSITE_READ_ONLY_PROBE
1 CONSUMER_RECEPTOR_ANALYSIS
1 MASKED_PROBE_BIND
4 S2GC_PROJECTION
4 S2GI_PROJECTION
7 ARM_EXECUTION
1 EXECUTION_EVIDENCE_SEAL
1 EVALUATION_RUN_BIND
4 PURE_EVALUATION
3 Erfolgsabschlussoperationen
= 139 Operationen
= 278 START-/RESULT-Ereignisse
```

`EvaluationPlanSeal` ist eine unabhaengige Wurzel. Weder ExecutionPlan noch
Reservierung oder die Operationen `op-0001..op-0131` enthalten seinen Digest.
Erst `op-0132` bindet vollstaendige Ausfuehrungsevidenz und vorab versiegelten
Auswertungsplan.

## Terminale und Ressourcen-Grenzen

- Vor einer erfolgreichen Reservierung ist nur `START_BLOCKED` ohne
  Laufverzeichnis moeglich.
- Nach Reservierung endet ein Fehler ueber genau drei registrierte
  Fehlerabschlussoperationen in `NOT_EVALUABLE`.
- Der Erfolgspfad endet ausschliesslich ueber `op-0137..op-0139` in
  `COMPLETE`.
- Erfolg und Fehler verwenden getrennte, exklusiv erzeugte Terminalpfade.
- Ueberschreiben, Fortsetzen und automatische Wiederverwendung sind nicht
  vorgesehen.
- Die Erfolgsgrenze bleibt `2.009.088` Bytes.
- Das groesste zulaessige Einzelpfadbudget bleibt `2.045.952` Bytes.

Die S2-GR-Registries wurden statisch erneut geprueft: 139 Erfolgszeilen, 140
Fehlerpfade, 16 neutrale Fehlercodes und ein maximales Einzelpfadbudget von
2.045.952 Bytes.

## Statischer Codeaudit

Bestanden wurden ausschliesslich nicht ausfuehrende Pruefungen:

- Python-AST fuer alle vier Module;
- keine Top-Level-Datei-, Prozess-, Rezeptor-, Speicher- oder Runneraufrufe;
- Standardbibliotheksisolation von Fixturemodul und Verifikator;
- geschlossener Hauptschalter und kein automatischer Moduleinstieg;
- 25/25 Rohbilddigests;
- Registryzaehlung, Operationsreihenfolge und Bytearithmetik;
- unveraenderte S2-FS-, S2-GC-, S2-GI- und S2-GK-Komponenten sowie
  unveraenderter Produktiv- und Feldcode;
- `git diff --check` ohne Befund.

Zwei waehrend des statischen Audits gefundene Huellefehler wurden vor dem
Abschluss eng korrigiert: die registrierte Fehlerterminalrolle lautet exakt
`terminal/failure`, und das ExecutionEvidencePackage bindet genau die
Operationsresultate `op-0001..op-0130` ohne interne Zusatzschluessel.

## Befund

```text
PASS_S2GT_PRIVATE_RUN_ENVELOPE_STATICALLY_MATERIALIZED
```

Dieser Befund bestaetigt ausschliesslich die statische Materialisierung. Er
qualifiziert weder Runner, Recorder oder Verifikator noch die 139-Operationen-
Ausfuehrung und erzeugt keinen Funktions- oder Memory-Befund.

## Naechster Schritt

Der naechste fachlich angemessene Schritt ist eine getrennt freizugebende,
neutrale technische Qualifikation der Laufhuelle mit kleinen Quellen. Der
S2-GT-Hauptlauf, die vier 13-Schritt-Geschichten und jede funktionale
Auswertung bleiben bis dahin gesperrt.
