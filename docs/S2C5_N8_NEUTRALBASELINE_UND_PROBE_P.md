# S2-C5: N8-Neutralbaseline und Probe P

Stand: 2026-08-07

Status: `S2C5_N8_NEUTRAL_BASELINE_AND_PROBE_BOUND`

Vergleich mit r1.a: nicht ausgefuehrt

Vollmatrix: gesperrt

Forschungslauf: nein

## Zweck

S2-C5 bindet die bereits vorregistrierte N8-Gegenbaseline an denselben
technischen B0/B2-, S/H-Angleichungs- und Probe-P-Pfad wie S2-C4:

```text
N8 von 0.0 bis 8.0 s
-> externe Angleichung von S und H auf exakt null
-> L unveraendert erhalten
-> identische kanonische Probe P von 8.0 bis 8.4 s
-> getrennte Fortsetzung durch B0 oder B2
```

Es wird noch keine Distanz zu r1.a berechnet und keine Forschungsentscheidung
getroffen.

## Kanonischer N8-Plan

`prepare_s2c5_n8_receptor_plan` akzeptiert ausschliesslich die kanonische
Welt `n8`. Sie besteht aus genau einem neutralen achtsekundigen Phasenschritt.
Der Plan bindet:

- den kanonischen N8-Weltdigest;
- getrennte Digests der auditiven und visuellen Rezeptorfolge;
- den gemeinsamen S2-Organismustakt;
- genau einen Schritt von `0.0` bis `8.0 s`;
- 791 auditive und 80 visuelle, insgesamt 871 Quellenstuetzpunkte.

Alle Stuetzpunkte werden genau einmal einem Bildung-Batch zugeordnet. Samples,
Frames, Rezeptorfolgen und Feldtrajektorien werden nicht persistiert.

## Getrennte Ergebnisrollen

`S2ControlledN8Result` und `S2N8ProbeResult` sind eigene technische Rollen.
Sie koennen weder als r1.a-Bildung noch als r1.a-Probeergebnis an die
vorherigen Einstiegspunkte uebergeben werden. Damit bleiben Bildungsgeschichte
und Neutralbaseline trotz gemeinsamem Feldkern getrennt adressiert.

## B0/B2-Bildung und Probe

`advance_s2c5_n8_world` fuehrt N8 nur durch B0 oder B2. Der B2-Nullarm mit
`g=0` dient ausschliesslich der technischen Fastprojektionskontrolle. Der
aktive B2-Pfad verwendet unveraendert `rho=8` und `g=0.25/s`.

`advance_s2c5_n8_probe`:

- akzeptiert nur eine abgeschlossene N8-Bildung;
- setzt S und H extern exakt auf null;
- erhaelt L, Feldidentitaet, Docks und letzten Bildungstakt;
- verwendet exakt denselben Probeplan und Probe-Digest wie S2-C4;
- uebergibt alle 35 Probe-Stuetzpunkte genau einmal;
- liefert nur Digests, Supportzahlen und den fluechtigen In-Memory-Feldzustand.

## Technische Pruefung

`tests/test_s2c5_n8_probe_path.py` bindet:

1. deterministischen einphasigen N8-Plan und vollstaendigen Handoff;
2. exakte B0-Gleichheit mit dem bestehenden kontrollierten Phasenpfad;
3. exakte B0-Fastprojektionsgleichheit des B2-Nullarms vor und nach P;
4. digestgenaue Reproduktion des aktiven B2-Bildungs- und Probepfads;
5. denselben Probeplan fuer alle N8-Arme;
6. Typtrennung zwischen r1.a- und N8-Einstieg.

```text
neue S2-C5-Suite:                  6 passed
gesamter relevanter Testverbund:  99 passed, 13 subtests passed
Python-Kompilation:               bestanden
```

Die bekannte Pytest-Cachewarnung hat keinen Einfluss auf die Ergebnisse.

## Aussagegrenze

N8 ist jetzt technisch verfuegbar, aber noch nicht mit r1.a verglichen. Die
vorregistrierten Groessen `D_L`, `D_S(P)` und `D_H(P)` wurden nicht berechnet.
Insbesondere reicht ein Probe-Endzustand nicht aus, um das vorregistrierte
Maximum waehrend P abzubilden.

Es folgen keine Aussagen zu Praegung, Memory, relativer Feldzeit, innerem
Kontext, Wiedererkennung, Semantik, Organisation, Selbstregulation oder KI.

## Entscheidung

```text
N8-Bildung B0/B2:                 gebunden
einphasiger N8-Handoff:           bestanden
externe S/H-Angleichung:          gebunden
L-Erhaltung:                      bestanden
identische Probe P:               gebunden
B2-Nullarm gegen B0:              bestanden
aktive B2-Reproduktion:           bestanden
r1.a-N8-Vergleich:                nein
Probe-Verlaufsmetrik:             nein
Vollmatrix:                       gesperrt
Forschungslauf:                   nein
```

## Bester naechster Schritt

S2-C6 bis S2-C8 binden inzwischen Probe-Support, Einpaardistanzen und C1.
S2-C9 bis S2-C16 schliessen die A/B-Referenz bis zur kanonischen
End-to-End-Komposition. Der S2-Zwischenentscheid verweist als naechsten
Schritt auf den statischen S1-C-Kandidatenvertrag; keine Persistenz,
Vollmatrix, Entscheidung oder Laufnummer.
