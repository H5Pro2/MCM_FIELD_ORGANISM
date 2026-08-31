# S2-IE - Wiederholungsaudit nach S2-IF

## Status

`S2IE_REPEAT_AUDIT_PASSED_PRIVATE_IMPLEMENTATION_ELIGIBLE`

Der vollstaendige S2-IE-Funktions-, Lauf- und Auswertungsplan wurde gegen den
S2-IF-Korrekturvertrag erneut statisch geprueft.

S2-IF-Vertragsdigest:

```text
ebe1cf840414edd9a1f90231694ce0f6ba544b5fa05be253e15e7bf0a60856b9
```

Es wurden keine Projektmodule importiert, keine Tests ausgefuehrt und keine
Rezeptor-, Speicher-, Projektions-, Signal- oder Baselinefunktion aufgerufen.

## Korrekturwirkung

Die einzige blockierende Quellenueberbindung des urspruenglichen S2-IE-Plans
ist geschlossen:

```text
ContextRetrievalProbe
    -> nativer vollstaendiger S2-FS-Probedigest
    -> S2-GC/S2-GI-A/B-Befunde

MaskedSignalProbe
    -> nativer MaskedVisualProbe-Digest
    -> S2-IC-Anwendbarkeit und Konfliktsignal
```

Beide Rollen besitzen eigene Quellen-IDs, eigene native Digests und eigene
typisierte Huellendigests. Sie sind ausschliesslich ueber den vorgebildeten
Fallplandigest Geschwister. Keine Rolle wird aus Befund, Digest oder Ergebnis
der anderen rekonstruiert.

Die unzulaessige Gleichheitspruefung

```text
two_area_bundle.probe_digest == masked_signal_probe.probe_digest
```

ist nicht Bestandteil des korrigierten Vertrags. Stattdessen sind zwei
getrennte Relationen vollstaendig materialisiert:

```text
two_area_bundle.probe_digest
    == context_retrieval_probe.function_probe_digest

signal_input.probe_digest
    == masked_signal_probe.masked_visual_probe_digest
```

Der Bundledigest bleibt zugleich Elternbeleg des Signaleingangs. Damit sieht
S2-IC weiterhin nur ein validiertes A/B-Bundle und genau eine maskierte
Signalprobe, ohne die vorgelagerte Kandidatenbildung zu wiederholen.

## Materialisierbarkeit der Rollenformen

Alle benoetigten Werte existieren in den vorhandenen qualifizierten privaten
Artefakten:

- S2-FS-read-only bindet den nativen vollstaendigen Probedigest;
- S2-GC und S2-GI erhalten und verifizieren diesen Digest;
- `MaskedVisualProbe` bindet Werte, feste Maske, Quelle und eigenen Digest;
- ReceptorReceipts liefern getrennte Bild-, Wert-, Quellen- und
  Konfigurationsdigests;
- S2-IC bindet den nativen maskierten Probedigest und den S2-GI-Bundledigest;
- Signal und Direktbaseline besitzen getrennte ownerfreie Inputs und interne
  Einmalowner.

Die neuen S2-IF-Huellen referenzieren diese Werte nur. Sie erfinden keine
Provenienz, betten keine Vollobjekte ein und verlangen keine Speicherabfrage.

## Reale Geschichten und Statusfaelle

Die sechs S2-IE-Geschichten bleiben unveraendert erreichbar:

| Geschichte | Formationen | Statischer Endzustand |
| --- | ---: | --- |
| h-c | 4 | A und B tragen P1 |
| h-x0 | 5 | A=V0, B=V1 |
| h-x1 | 5 | A=V1, B=V0 |
| h-sa | 1 | A=P11, B abwesend |
| h-sb | 13 | A fuer P1 abwesend, B=P1 stabil |
| h-n | 10 | A und B fuer P11 abwesend |
| **Gesamt** | **38** |  |

Die acht Funktionsfaelle bleiben vollstaendig und exklusiv:

```text
c01 CONSISTENT
c02 CONFLICT
c03 CONFLICT, gespiegelt
c04 SINGLE_SOURCE aus A
c05 SINGLE_SOURCE aus B
c06 NO_CONTEXT
c07 NO_APPLICABLE_CONTEXT
c08 NO_APPLICABLE_CONTEXT, gespiegelt
```

Z0 und Z1 werden nur als maskierte Signalproben gebildet. Sie koennen daher
die zuvor mit Q0 beziehungsweise Q1 abgerufenen A/B-Kandidaten weder
entfernen noch neu auswaehlen. Genau dadurch ist der doppelte sichtbare
Konflikt technisch erreichbar, ohne die Kontextabruflogik zu umgehen.

## Owner- und Atomaritaetsaudit

Je Fall existiert genau ein Dual-Probe-Fallowner, der vor beiden Armaufrufen
direkt bindet:

- Fallplan;
- Retrieval-Probenhuelle und nativen Retrieval-Probedigest;
- Signal-Probenhuelle und nativen MaskedVisualProbe-Digest;
- S2-GI-Bundle;
- Signalinput;
- Baselineinput.

Signal und Baseline behalten jeweils ihren eigenen qualifizierten internen
S2-IC-Owner. Diese Kindowner koennen nicht die Dual-Probe-Autorisierung
ersetzen. Beide Armresultate bleiben lokal, bis der Fallowner sie gemeinsam
abnimmt und genau einmal `CONSUMED` oder `FAILED` erreicht.

Ein Armfehler, Quellenbruch oder Owner-Reuse erzeugt keinen regulaeren
Fallbeleg. Teilcommit und zweite Transition sind ausgeschlossen.

## Operations- und Ereignisaudit

Die sieben bestehenden Operationen jedes Fallblocks wurden neu geordnet, aber
nicht erweitert:

```text
SIGNAL_PROBE_RECEPTOR
MASKED_SIGNAL_PROBE_PROJECT
DUAL_PROBE_AND_ARM_INPUTS_BIND
SIGNAL_INVOKE
BASELINE_INVOKE
DUAL_PROBE_CASE_OWNER_COMMIT
CASE_EVIDENCE_SEAL
```

Die fruehere separate Baselineinputbindung ist in der atomaren dritten Stufe
enthalten. Dadurch bleiben alle S2-IE-Grenzen unveraendert:

```text
Erfolg:          183 Operationen / 366 Ereignisse
maximaler Fehler: 185 Operationen / 370 Ereignisse
```

Die Operationsbereiche `ie-op-001..183` bleiben lueckenlos. Innerhalb der
acht Fallbereiche `ie-op-115..170` besitzt jeder Fall weiterhin exakt sieben
Operationen. Jede Operation besitzt genau ein START-/RESULT-Paar.

## Ressourcen- und Ledgeraudit

Die vorhandenen Funktionsbudgets bleiben unveraendert:

- 52 reale visuelle Rezeptoranalysen;
- 38 Composite-Formationen;
- 6 S2-FS-read-only-Proben;
- je 6 S2-GC- und S2-GI-Projektionen;
- je 8 Signal- und Direktbaselineaufrufe;
- S2-FS gesamt `23530/20592/2340` fuer Schreibwoerter, Distanz- und
  Kontrollterme.

S2-IF fuegt pro Fall nur die explizit gebundene Quellenpruefarbeit hinzu. Der
achtfaellige Gesamtumfang ist exakt:

```text
Fallplanvalidierungen             8
typisierte Probevalidierungen    16
Quellenbindungen                 16
ReceptorReceipt-Pruefungen       16
Konfigurationsbindungen          16
Kontextprobe-Relationen           8
Signalprobe-Relationen            8
Bundle-Kontextrelationen          8
Arminputrelationen               16
Kontextwertreferenzen           208
Signalpositionsvalidierungen    144
Digestvalidierungen             312
Owneruebergaenge                  8
neue Digestoperationen           64
Speicher-/Lernaufrufe             0
```

Das S2-IC-Ledger bleibt davon getrennt und unveraendert. Signal und Baseline
erhalten weiterhin identische funktionale Budgets.

## Groessenaudit

Die S2-IF-Vollhuellen wurden mit maximalen gueltigen IDs, Digests,
Positionen und Tickwerten nachgerechnet:

| Form | Bytes | Grenze | bestanden |
| --- | ---: | ---: | --- |
| Fallplan | 1145 | 2048 | ja |
| Retrieval-Probenhuelle | 1186 | 1792 | ja |
| Signal-Probenhuelle | 1264 | 1792 | ja |
| Dual-Probe-Bindung | 1259 | 2048 | ja |
| Quellenledger | 654 | 1536 | ja |
| Owner-Vorzustand | 913 | 1792 | ja |
| Owner-Nachzustand | 1005 | 1792 | ja |
| Fallbeleg | 2090 | 3584 | ja |
| Fehlerursache | 809 | 1536 | ja |
| ErrorReceipt | 660 | 1536 | ja |

Alle Formen bleiben unter 4095 Byte. Die kleinste Reserve betraegt 528 Byte.
Bestehende Receptor-, Formation-, S2-FS-, S2-GC-, S2-GI- und S2-IC-Grenzen
bleiben unveraendert.

## Nichtzirkularitaet und Evaluation

Der korrigierte Graph besitzt drei unabhaengige Wurzeln:

1. ExecutionPlan und Fallplan;
2. Retrieval- und Signalquelle als Geschwister;
3. unabhaengiger EvaluationPlanSeal.

Der Ausfuehrungsgraph ist vorwaertsgerichtet:

```text
CasePlan -> RetrievalProbe -> A/B-Bundle
CasePlan -> MaskedSignalProbe
A/B-Bundle + MaskedSignalProbe -> ArmInputs
ArmInputs -> Signal / Baseline
beide Resultate -> atomarer Fallbeleg
```

Erst `EvaluationRunBinding` verbindet das vollstaendige
ExecutionEvidencePackage mit dem EvaluationPlanSeal. Kein Fallplan,
Probeobjekt, Bundle, Arminput, Owner oder Funktionsresultat enthaelt Sollstatus
oder Zielwerte.

Der Digestgraph ist damit vollstaendig azyklisch. Insbesondere bindet keine
Probe den Digest oder Befund der jeweils anderen.

## Entscheidungen

`NOT_EVALUABLE` bleibt auf technische und methodische Verletzungen begrenzt,
einschliesslich Rollenvertauschung, Quellenbruch, Teilcommit,
Read-only-Verletzung oder unvollstaendiger Aufzeichnung.

Eine gueltige, aber falsche Statusentscheidung ist eine funktionale
Falsifikation und bleibt auswertbar. Die Direktbaseline bleibt der
verbindliche Erklaerungsvergleich.

Der maximal zulaessige positive Befund bleibt:

```text
S2IE_REAL_TWO_AREA_STATUS_FUNCTION_VALID_DIRECT_COMPARISON_EXPLAINS
```

## Auditentscheidung und Freigabegrenze

| Pruefpunkt | Befund |
| --- | --- |
| getrennte typisierte Probenrollen | bestanden |
| eigene Quellen und Digests | bestanden |
| keine Probeableitung | bestanden |
| gemeinsame Zugehoerigkeit nur ueber Fallplan | bestanden |
| Evaluation getrennt | bestanden |
| atomarer Owner bindet beide Proben | bestanden |
| reale Erreichbarkeit aller fuenf Statuswerte | bestanden |
| Spiegelung asymmetrischer Faelle | bestanden |
| Operations- und Ereigniszahlen | bestanden |
| Ledgers und Funktionsbudgets | bestanden |
| Artefaktgroessen | bestanden |
| Digestgraph und Nichtzirkularitaet | bestanden |
| S2-ID-Logik unveraendert | bestanden |

S2-IE ist nach S2-IF statisch bestanden und privat implementierungsfaehig.
Diese Entscheidung gibt noch keine Codeaenderung, Tests oder Ausfuehrung frei.

Der naechste zulaessige Schritt ist die getrennt freizugebende enge
Quellenkorrektur sowie die private S2-IE-Fixture-, Runner-, Recorder- und
Verifikatorimplementierung. Ein realer Funktionslauf bleibt bis nach einer
fokussierten neutralen Qualifikation der getrennten Zwei-Proben-Bindung
gesperrt.
