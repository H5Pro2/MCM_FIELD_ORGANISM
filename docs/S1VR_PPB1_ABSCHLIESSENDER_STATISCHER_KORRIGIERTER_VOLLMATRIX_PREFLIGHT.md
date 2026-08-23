# S1-VR: Abschliessender statischer korrigierter PPB-1-Vollmatrix-Preflight

## Auftrag und Grenze

S1-VR prueft den in S1-VQ implementierten korrigierten 528-Pfad-Plan
abschliessend statisch. Geprueft werden Elternplan, Korrekturplan,
Identitaetsrollen, Wiederholungspfade, Aufrufbudget, Ausfuehrungsgate und der
Anschluss an den reinen S1-VO-Auswerter.

S1-VR fuehrt keinen registrierten Pfad aus. Es gibt keine Feld-, Medien-,
API- oder Snapshotaenderung und keine Parameter-, Baseline- oder
Eignungsentscheidung.

## Gebundener Planstand

Der unveraenderte S1-VN-Elternplan besitzt weiterhin den Digest:

```text
35c1e589f749f1c1f1f24900f611fd43f8329d803a4b82ca94584d1925067ba3
```

Alle 384 R0-Pfade erhalten Familie, Parameter, Modalitaet, Fixture,
Aufrufzahl und Konfigurationsdigest bitgleich aus diesem Elternplan. Der
korrigierte Plan besitzt den Digest:

```text
f307363400ba66e53a49ec9cd21bc17973f93f240f3946eade2c6a7dbdcd1210
```

Sein gebundenes Budget lautet:

```text
Faelle:               528
PPB-Aufrufe:         9.476
Baselineaufrufe:    66.332
Gesamtaufrufe:      75.808
ausgefuehrte Aufrufe:    0
```

## Geschlossene S1-VO-Blocker

Die beiden in S1-VO erkannten methodischen Luecken sind technisch
geschlossen:

1. B01 bis B06 tragen getrennte Auswahl- und Schreibidentitaeten,
   Vorzustandsdigest sowie aktives Identitaetsinventar; B07 bleibt
   identitaetsfrei.
2. F04, F05 und F06 besitzen fuer jede Familie, jeden Parametersatz und jede
   Modalitaet einen unmittelbar folgenden R1-Frischpfad neben R0. Genau 144
   R1-Pfade sind vorhanden.

Die korrigierten Receipts binden ausserdem eine von der Pfad-ID unabhaengige
normalisierte Wiederholungsdarstellung und deren Digest.

## Neu erkannte Ergebnis-Pipeline-Luecken

Der korrigierte Plan darf dennoch noch nicht ausgefuehrt werden. S1-VR
findet drei voneinander getrennte Blocker:

### 1. Fehlende atomare Ergebnisversiegelung

`S1VQMatrixResult` traegt zwar Plan-Digest, Receipts, Aufrufzahl und
Wiederholungsvergleiche, validiert diese Rollen aber noch nicht atomar. Eine
kanonische Payload und ein Gesamtdigest fehlen. Dadurch ist noch nicht
gebunden, dass nur ein vollstaendiges, planrichtiges 528-Fall-Ergebnis die
Auswertungsgrenze erreicht.

### 2. Fehlende deterministische 528-zu-48-Verdichtung

Der S1-VO-Auswerter erwartet genau 48 Zusammenfassungen aus acht Familien,
drei Parametersaetzen und zwei Modalitaeten. Es gibt noch keinen gebundenen
Compositor, der aus den 528 Fallreceipts genau diese 48 Arme bildet. Ohne
diesen Anschluss waeren Fixtureauswahl, Diagnosezaehlung, Lebenszyklus- und
Wiederholungswertung nachtraeglich interpretierbar.

### 3. Identitaetskosten fehlen im Einfachheitsvergleich

Die korrigierten Baselines fuehren technische Identitaetsmetadaten. Der
bestehende S1-VO-Summary vergleicht bisher nur logische Werte und akzeptierte
Aufrufe. Die zusaetzliche Identitaetslast darf bei der Entscheidung, ob eine
Baseline einfacher ist, nicht unsichtbar bleiben.

## Implementierter Preflight

Das private Modul
[`_ppb1_s1vr_corrected_preflight.py`](../mcm_field_organism/_ppb1_s1vr_corrected_preflight.py)
prueft 16 Rollen. 13 Plan-, Budget-, Identitaets-, Wiederholungs-, Receipt-
und Gatepruefungen bestehen. Nur die drei vorstehend benannten
Ergebnis-Pipeline-Rollen bleiben gezielt falsch.

Die Entscheidung lautet:

```text
BLOCKED_RESULT_PIPELINE_CORRECTION_REQUIRED_NO_EXECUTION
```

Kanonischer Preflight-Digest:

```text
93c9bc7b092c0e947e5efd212e00c27cdc2096163b31ca7b20fc4065857e89e3
```

## Abnahme

Die S1-VR-Testdatei besteht mit `11 von 11` Tests. Zusammen mit dem privaten
PPB-Kern, Profilbinder, S1-VN, S1-VO, S1-VQ und der aktiven
Engineeringoberflaechen-Grenze bestehen `121 von 121` fokussierte Tests.

Geprueft werden insbesondere:

- exakte Eltern- und Korrekturplandigests;
- vollstaendige R0-Elternabbildung;
- 528 eindeutige Pfade und exakte Aufrufbudgets;
- Schliessung beider S1-VO-Blocker;
- normalisierte Wiederholungsreceiptrollen;
- das aktive Vollmatrixgate und null ausgefuehrte Aufrufe;
- die exakt drei neuen Ergebnis-Pipeline-Blocker;
- kanonische und deterministische Preflightausgabe;
- Abwesenheit aus Feldsnapshot, Root-Exports und `current_api`.

## Entscheidung

```text
S1_VR_PARENT_AND_CORRECTED_PLANS_ACCEPTED
S1_VR_BASELINE_IDENTITY_BLOCKER_CLOSED
S1_VR_F04_F05_F06_REPEAT_BLOCKER_CLOSED
S1_VR_528_CASE_AND_75808_CALL_BUDGET_ACCEPTED
S1_VR_RESULT_SEAL_MISSING
S1_VR_528_TO_48_COMPOSITOR_MISSING
S1_VR_IDENTITY_METADATA_BUDGET_MISSING
S1_VR_FULL_MATRIX_EXECUTION_BLOCKED
S1_VR_ZERO_REGISTERED_CALLS_EXECUTED
S1_VR_11_OF_11_NEW_TESTS_PASS
S1_VR_121_OF_121_COMBINED_FOCUSED_TESTS_PASS
```

S1-VR bestaetigt damit die korrigierte Versuchsgeometrie, aber noch nicht die
Ausfuehrungsreife der Ergebnispipeline. Es liegt weiterhin kein PPB-1-
Ausfuehrungs- oder Eignungsbefund vor.

## Genau ein naechster Schritt

Der einzige Anschluss ist:

```text
S1-VS - statischer Ergebnis-Pipeline-Korrekturvertrag
```

S1-VS muss vor jeder Implementierung festlegen:

- eine kanonische, atomar validierte 528-Fall-Ergebnisrolle;
- die einzige zulaessige Verdichtung der Fixtures in genau 48 S1-VO-Arme;
- die Ableitung jeder Lebenszyklus-, Diagnose-, Trennungs- und
  Wiederholungsmetrik aus konkreten Receiptrollen;
- eine endliche Identitaetsmetadaten-Groesse und ihre Rolle im
  Einfachheitsvergleich;
- Fail-Closed-Regeln fuer fehlende, doppelte oder inkonsistente Receipts.

S1-VS darf noch keine Implementierung und keine Matrixausfuehrung enthalten.

## Grundlagen

- [S1-VQ Identitaetsrollen und korrigierter Plan](S1VQ_PPB1_PRIVATE_IDENTITAETSROLLEN_UND_KORRIGIERTER_MATRIXPLANER.md)
- [S1-VP statischer Korrekturvertrag](S1VP_PPB1_STATISCHER_IDENTITAETS_UND_WIEDERHOLUNGSKORREKTURVERTRAG.md)
- [S1-VO reiner Auswerter und erster Preflight](S1VO_PPB1_REINER_AUSWERTER_UND_STATISCHER_VOLLMATRIX_PREFLIGHT.md)
