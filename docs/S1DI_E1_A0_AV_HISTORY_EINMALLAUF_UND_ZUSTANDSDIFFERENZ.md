# S1-DI: E1-A0-AV-History-Einmallauf und Zustandsdifferenz

## Status

Der in S1-DH registrierte kanonische AB/BA-History-Versuch wurde nach
vollstaendiger synthetischer Executorabnahme und finaler Vorpruefung genau
einmal ausgefuehrt. Der Lauf ist erfolgreich atomar veroeffentlicht. Eine
Wiederholung ist gesperrt. Es wurde keine eingefrorene Probe ausgefuehrt.

## Implementierung

```text
mcm_field_organism/e1_a0_av_history_one_shot_execution.py
tests/test_e1_a0_av_history_one_shot_execution.py
```

Der Executor bleibt privat. Vor dem kanonischen Lauf bestanden 5 fokussierte
Executor- und 127 relevante Verbundtests.

## Einmalnachweis

```text
execution_id       e1.a0-av-history.s1di.once.v1
technical_status   E1_A0_AV_HISTORY_STATES_PRODUCED
contract_digest    bce53a59cdc4afff5b88fe36ecd891a94b00167169e9b502abf0949eac9a1224
result_digest      7fe242f667ff77b9c4e79e5800c890ab37d269c68ff6b52fccf12224645348d9
report_sha256      831e535b0193d0bce03081545c5bda6bb4cc5655fd8b32cf77daa8a1b2fc9d1a
```

Ergebnisdatei:

```text
reports/e1_a0_av_history_s1di_once_v1.json
```

Nach erfolgreicher Veroeffentlichung fehlen Versuchsnachweis und Sperrdatei.
Die vorhandene Ergebnisdatei sperrt jeden weiteren Start desselben Vertrags.

## Pflichtkontrollen

Beide Quellenarme bestehen vollstaendig:

| Arm | Supports | zugeordnet | P0 == A0 | Ressourcenfehler | Rueckwirkung |
|---|---:|---:|---|---:|---|
| AB | 220 | 220 | exakt | 0.0 | vollstaendig aus |
| BA | 220 | 220 | exakt | 0.0 | vollstaendig aus |

Weitere bestaetigte Grenzen:

- AB und BA tragen dasselbe S1-DE-Payload-, Support-, Zeitslot-, Masse- und
  Energieinventar;
- beide E1-Endzustaende verwenden dasselbe Inventar aus 145 Kanten;
- historische S/H-Felder, Restore-Snapshots und Probeobjekte fehlen im
  Ergebniscontainer;
- der kanonische Produzenten-, Konfigurations- und Quelldigest stimmt mit
  S1-DH ueberein;
- die E1-Rueckwirkung war waehrend beider Historien deaktiviert.

## Rohmetriken

Der Einmallauf ergibt:

```text
D_state         0.000830161044915372
D_total_binding 0.00037698677602994446
```

Damit sind `b_AB` und `b_BA` im ausgefuehrten technischen Modell nicht
identisch. Die reine zeitliche Reihenfolge desselben reduzierten
AV-Frameinventars fuehrt unter A0 zu unterschiedlichen E1-Endlagen.

Dies ist ein begrenzter technischer Fortschritt: S1-DE hat nur die Ordnung
veraendert, P0/A0 ist in beiden Armen bitgenau und E1 konnte das historische
S/H-Feld nicht rueckwirkend veraendern.

## Noch offene Numerikgrenze

S1-DC verlangt fuer eine spaetere Probeentscheidung einen
`D_state_refinement`-Vergleich. Der S1-DI-Einmallauf hat bewusst nur die
registrierte kanonische Aufloesung ausgefuehrt und keinen zweiten
Verfeinerungsarm erzeugt. Wegen des Wiederholungsverbots darf dieser fehlende
Rest nicht nachtraeglich durch einen erneuten kanonischen History-Lauf
beschafft werden.

Die positive Zustandsdifferenz darf deshalb noch nicht als numerisch
verfeinerter Forschungsbefund oder als Freigabe der S1-DC-Probe ausgegeben
werden. Sie ist ein reproduzierbar gebundener Rohbefund genau dieses einen
technischen Laufs.

## Aussagegrenze

S1-DI zeigt eine order-spezifische technische E1-Endzustandsdifferenz auf
der kontrollierten AV-Geometrie. Es zeigt noch keine spaetere Feldwirkung,
keine Rekonstruktion und kein Vergessen. Der Lauf belegt kein MCM-Memory,
keinen inneren Kontext, keine Semantik, Organisation, Topologie,
Selbstregulation oder KI.

## Bester naechster Schritt

S1-DJ fuehrt einen rein statischen Evidenz- und Anschlussaudit des
veroeffentlichten S1-DI-Ergebnisses durch. Er muss insbesondere klaeren, wie
die fehlende S1-DC-Numerikgrenze ohne verbotene Wiederholung behandelt wird:
entweder durch eine bereits vorhandene analytische Fehlerobergrenze des
Integrators oder durch eine enger begrenzte technische Probeaussage, die
keinen verfeinerten Zustandsbefund voraussetzt. Bis zu diesem Audit bleibt
die eingefrorene AV-Probe gesperrt.

S1-DJ ist inzwischen abgeschlossen. Eine globale analytische Ersatzschranke
liegt nicht vor; der volle S1-DC-Befund bleibt gestoppt. Freigegeben ist nur
die statische Vorbereitung einer engeren zustandskonditionierten
Transferpruefung. Siehe
`S1DJ_E1_A0_AV_HISTORY_EVIDENZ_UND_ANSCHLUSSAUDIT.md`.
