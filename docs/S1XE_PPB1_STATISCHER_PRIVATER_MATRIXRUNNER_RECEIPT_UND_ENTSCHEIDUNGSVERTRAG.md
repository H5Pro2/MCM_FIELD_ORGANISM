# S1-XE: Statischer privater Matrixrunner-, Receipt- und Entscheidungsvertrag

## Auftrag und Grenze

S1-XE bindet den vollstaendigen privaten Ablauf vor jeder Runner-
Implementierung. Es werden weder Materialisierer, PPB-1-Bildung, Probe,
Baseline noch eine der 60 registrierten Zellen ausgefuehrt.

## Korrektur des Bildungsbypasses

Der in S1-XC direkt materialisierte stabile PPB-1-Zustand ist nur eine
erwartete Vorlage. Er ist kein Ergebnis ausgefuehrter Zustandsbildung.
Ein spaeterer Runner muss deshalb fuer Audio und Video jeweils:

1. einen leeren Zustand mit `initial_ppb1_bank_state` erzeugen;
2. die drei gebundenen Frames `0-1`, `1-2`, `2-3` mit
   `advance_ppb1_bank` ausfuehren;
3. die Ereignisfolge `CREATED, MATCHED, MATCHED` erhalten;
4. den gebildeten Zustand vollstaendig gegen die S1-XC-Vorlage pruefen;
5. bei jeder Abweichung vor der ersten Probe stoppen.

Damit sind exakt sechs PPB-1-Bildungsschritte vorregistriert. Die Vorlage
darf die echte Bildung nicht ersetzen.

## Gebundener Runnerablauf

Nach erfolgreicher Bildung werden Kandidaten- und Baselinevorzustaende
eingefroren. Die 60 Zellen laufen ausschliesslich in der vorhandenen Ordnung:

```text
2 Modalitaeten x 6 Systeme x 5 Probearten = 60 Zellen
```

Erlaubte Aufrufe:

| Rolle | Funktion | Anzahl |
|---|---|---:|
| Materialisierung | `materialize_s1xc_fixture_registry` | 1 |
| leerer Kandidatenzustand | `initial_ppb1_bank_state` | 2 |
| Kandidatenbildung | `advance_ppb1_bank` | 6 |
| Kandidatenprobe | `probe_s1wu_perceptual_state` | 10 |
| Baselineprobe | `probe_s1xc_baseline_read_only` | 50 |

Jede Zelle verwendet den exakt gebundenen Plan und einen unabhaengigen,
wertgleichen eingefrorenen Vorzustand. Fehlende, doppelte, umgeordnete oder
wiederholte Zellen machen den gesamten Ablauf methodisch ungueltig.

## Receipts und Atomaritaet

Jedes Zellreceipt bindet Plan, Befund, Distanz, Erkennungsentscheidung,
Vorher-/Nachherdigest, Identitaets- oder Nullrolle, Provenienz und
Informationsbudget. Prototypwerte und Rohhistorie duerfen nicht im Receipt
stehen.

Ein Matrixreceipt ist nur bei 60 einzeln validierten Zellreceipts erlaubt.
Teilresultate duerfen weder aggregiert noch interpretiert werden. Ein Fehler
liefert keine Funktions- oder Baselineentscheidung.

## Vorregistrierte Entscheidung

Der Kandidat besteht nur, wenn beide Bildungen die Vorlage erreichen und
alle zehn Kandidatenzellen ihre gebundene Positiv-/Negativprognose bei
unveraendertem Zustand erfuellen.

Eine Baseline erklaert den Kandidaten nur, wenn dieselbe Baseline alle zehn
Audio-/Video-Proben in Erkennungsentscheidung und Distanz reproduziert.
Metadaten duerfen berichtet, aber nicht zur kuenstlichen Ungleichheit
verwendet werden. Ein Mischen verschiedener Baselines ist verboten.

Fuer die Nullvektor-Fixture bleibt vorregistriert:

```text
TECHNICAL_MEMORY_FUNCTION_PASS_BASELINE_EXPLAINED
```

Dies ist eine erwartete technische Grundfunktionsentscheidung und kein
Nachweis einer MCM-spezifischen Memory.

## Reproduzierbare Bindung

Vertragsdigest:

```text
eb501a103ec40dc9234e946553afb554279089ed2381a03011daa91f9db7731c
```

`12 von 12` statische Vertragstests bestehen. Ausgefuehrte Matrixzellen: `0`.

## Naechster Schritt

S1-XF darf den privaten Runner und die Receipt-Datentypen implementieren,
aber nur mit einer kleinen synthetischen Ersatzmatrix testen. Die
registrierte 60-Zellen-Matrix, Ergebnisentscheidung, Feld und Produktion
bleiben geschlossen.

## Grundlagen

- [S1-XD Abschlussaudit](S1XD_PPB1_STATISCHER_QUELL_DIGEST_EXPORT_UND_NICHTAUSFUEHRUNGSAUDIT.md)
- [Maschinenlesbarer S1-XE-Vertrag](S1XE_PPB1_STATISCHER_PRIVATER_MATRIXRUNNER_RECEIPT_UND_ENTSCHEIDUNGSVERTRAG_V1.json)
