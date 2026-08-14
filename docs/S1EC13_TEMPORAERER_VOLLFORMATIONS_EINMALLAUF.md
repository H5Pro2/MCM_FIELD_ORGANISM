# S1-EC13: Temporaerer Vollformations-Einmallauf

## Status

```text
FULL_PREPARED_FORMATION_EXECUTED_TEMPORARILY
ALL_FORMATION_CONTROLS_PASSED
CONVERGENCE_NONINCREASING
STOPP_FOR_DIRECT_PROBE_HANDOFF
NO_MEMORY_CLAIM
```

S1-EC13 fuehrte die vollstaendige vorbereitete AV-Formation fuer `r2`, `r4`
und `r8` genau einmal in einem persistenten, nicht-kanonischen
S1-EC3-Lebenszyklus aus. Vor dem Attempt und erneut nach dem Attempt bestand
derselbe S1-EC12-Ressourcenpreflight.

## Implementierung und Aufruf

```text
mcm_field_organism/e1_confirmation_full_formation_lifecycle.py
tests/test_e1_confirmation_full_formation_lifecycle.py
tools/run_e1_confirmation_full_formation_s1ec13_once.py

.venv/Scripts/python.exe -m tools.run_e1_confirmation_full_formation_s1ec13_once
```

Ein vorheriger direkter Dateiaufruf erreichte wegen fehlendem Python-
Modulpfad weder `main()` noch Laufordner, Vertrag, Lock oder Attempt. Er war
kein S1-EC13-Lauf. Der anschliessende Modulaufruf war der einzige gestartete
Lebenszyklus.

## Laufumfang

```text
Feldknoten                  84
E1-Kanten                  145
Formationsarme               5
Refinementstufen             3
Armlaeufe                    15
Armschritte              14.000
Laufzeit                  430,2 s
```

## Rohwerte

```text
AB/BA-Zustandsabstand:
r2 = 0.0008453023645430579
r4 = 0.000852954804258883
r8 = 0.0008568014728262579

Verfeinerungsrest ueber alle fuenf Arme:
r2 -> r4 = 0.000034885390053043374
r4 -> r8 = 0.00001736313599644745

convergence_nonincreasing = true
preflight_digest = 236f7d6a29c548149bf6663a9a2e3b8fd4f4d807032083c5b6547c51f536fb75
formation_digest = 8dbec067dc2ca07a462beb2c11f7b89917f07083b7696452ee6f897081915797
```

Der maximale stufengleiche Verfeinerungsrest sinkt ungefaehr um die Haelfte.
Der AB/BA-Zustandsabstand bleibt auf allen drei Stufen von null getrennt und
nimmt leicht zu. Das ist eine technische Formationsbeobachtung, kein
Memorybefund.

## Persistiertes Artefakt

```text
synthetic_runs/s1ec13_full_formation_once_v1/
  e1_confirmation_s1ec3_synthetic_once_v1.json

report_sha256 = 15932c1f3f6b493ebc090c6e2da5612dd3bc35e6f9aa012f416ef710ee54e48a
```

Der Bericht bindet Laufvertrag, Eingabemanifest und Formation-Digest. Nach
seiner verifizierten Publikation wurden Attempt und Lock entfernt.

## Kontrollen

- S1-EC12 bestand vor und waehrend des Attempts mit identischem Digest;
- alle 15 realen Arme wurden aus den vorbereiteten Planausgaben gespeist;
- Identitaets-, Ablations-, Objekttrennungs-, Feld- und Ressourcenkontrollen
  bestanden auf jeder Refinementstufe;
- vorbereitete Eingaben blieben unveraendert;
- 59 Post-Run-Regressionstests bestanden;
- S1-EA6 und der terminale S1-EB31-Attempt blieben unveraendert.

## Evidenz- und Fortsetzungsgrenze

Der generische S1-EC3-Bericht speichert nur den Formation-Digest, nicht den
vollstaendigen Ergebniscontainer oder die 15 gebildeten E1-Zustaende. Die
Rohwerte wurden terminal ausgegeben und hier protokolliert, aber die
Zustandsobjekte sind nach Prozessende nicht als pruefbarer Probe-Handoff
verfuegbar.

**STOPP fuer Wiederholung, direkte Probe oder nachtraegliche Rekonstruktion
von S1-EC13.** Der erfolgreiche Lauf darf nicht erneut gestartet werden. Aus
seinem Digest allein duerfen keine Zustandswerte zurueckgerechnet werden.

Der Befund belegt eine kontrollierte, numerisch verfeinerbare
Vollformation. Er belegt kein MCM-Memory, Lernen, Vergessen, Rekonstruktion,
Feldzeit, Organisation, Semantik, Selbstregulation oder KI.

## Bester naechster Schritt

S1-EC14 sollte statisch einen vollstaendigen Ergebnis- und
Zustandshandoff-Vertrag fuer eine neue temporaere Identitaet binden. Vor
jeder neuen Ausfuehrung muessen Rohmetriken, Formationsergebnisdigests und
die fuer eine spaetere eingefrorene Probe notwendigen E1-Zustaende atomar
im Bericht enthalten sein. Noch keine neue Formation und keine Probe.
