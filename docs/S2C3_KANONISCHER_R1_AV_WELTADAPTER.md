# S2-C3: Kanonischer r1.a-AV-Weltadapter

Stand: 2026-08-07

Status: `S2C3_CANONICAL_R1_AV_ADAPTER_BOUND`

Probe P: nicht ausgefuehrt

Vollmatrix: gesperrt

Forschungslauf: nein

## Zweck

S2-C3 bindet erstmals genau eine kanonische S2-Bildungsgeschichte aus der
Vorregistrierung an den transienten B0/B2-Einzelbatchpfad:

```text
r1.a
-> prozedurale kontrollierte Audio-/Videowelt
-> vorhandene neutrale Rezeptorreduktion
-> gemeinsame zeitversetzbare Ereigniszeitlinie
-> drei phasengrosse Transient-Batches
-> B0 oder B2
```

Andere Welten, Probe P, Interventionen und Auswertung bleiben gesperrt.

## Zeitversetzbare AV-Reduktion

`reduce_controlled_test_world_sequences` reduziert eine
`ControlledAudioVideoTestWorld` mit einem geprueften gemeinsamen Startoffset.
Der Offset muss gleichzeitig aus vollstaendigen Audiohops, Videoframes und
Organismusticks bestehen.

Die Funktion:

- erzeugt Audio und Video nur prozedural im Arbeitsspeicher;
- verwendet die vorhandenen neutralen Audio- und Videorezeptoren;
- erhaelt die getrennten Rezeptorgeometrien;
- schreibt keine Samples, Frames, Pixel oder Rezeptorfolgen;
- veraendert kein Feld.

## Gebundener r1.a-Plan

`prepare_s2c3_r1_receptor_plan` akzeptiert ausschliesslich `r1.a` und bindet:

- den kanonischen Weltdigest;
- zwei Digests der reduzierten auditiven und visuellen Sequenzen;
- gemeinsamen Takt und Tickrate;
- einen geprueften Startoffset;
- drei lueckenlose Phasenschritte;
- den Horizont von exakt 8.0 s;
- die vollstaendige Zahl reduzierter Quellenstuetzpunkte.

Ein direkt konstruiertes Planobjekt wird gegen Welt-, Sequenz-, Phasen- und
Horizontvertrag erneut validiert.

## B0/B2-Einzelweltpfad

`advance_s2c3_r1_world` baut das bestehende gemeinsame AV-Feld mit 84
Feldorten auf und akzeptiert nur:

```text
B0: vorhandener schneller transienter Neutralpfad
B2: transienter S1-B-Pfad mit rho=8 und g=0.25/s
```

Der technische B2-Nullarm `g=0` ist nur als Abnahmekontrolle zulaessig.
Feldantwortzeit `1.0 s` und Nachhallzeit `0.5 s` sind fest; andere Werte
werden vor der Weltfortschreibung abgewiesen.

Jeder reduzierte Quellenstuetzpunkt muss durch den vorhandenen Handoff genau
einmal einem Batch zugeordnet werden. Das Ergebnis enthaelt nur Digests,
Support- und Batchzahlen sowie den In-Memory-Feldzustand. Es persistiert
nichts.

## Technische Pruefung

`tests/test_s2c3_r1_world_adapter.py` bindet:

1. deterministischen Weltplan und korrekten Zeitoffset;
2. B0-Digestgleichheit zum vorhandenen kontrollierten Phasenpfad;
3. exakte Fastprojektionsgleichheit von B2 mit `g=0` und B0;
4. digestgenaue Reproduktion des aktiven B2-Pfads;
5. Abweisung aller nicht registrierten Modellarme.

Ergebnisse:

```text
neue S2-C3-Suite:                  5 passed
fokussierter C2/C3/AV-Verbund:    16 passed
gesamter betroffener Testverbund: 82 passed, 9 subtests passed
Python-Kompilation:               bestanden
```

Die bestehende Pytest-Cachewarnung bleibt ohne Einfluss auf die Ergebnisse.

## Aussagegrenze

S2-C3 hat `r1.a` technisch als kontrollierte Testwelt durch B0 und B2
fortgeschrieben. Das ist noch kein Forschungsversuch zur spaeteren
Feldwirkung, weil folgende Teile fehlen:

```text
externe S/H-Angleichung
identische Probe P
N8-Gegenbaseline
L-Tausch und L-Neutralisierung
skalare D_L-, D_S- und D_H-Auswertung
```

Der aktive B2-Endzustand ist nur ein technischer Zwischenzustand. Aus ihm
werden keine Begriffe wie Praegung, Memory, Feldzeit, Wiedererkennung oder
Organisation abgeleitet.

## Entscheidung

```text
r1.a-AV-Reduktion:                gebunden
gemeinsamer Zeitoffset:           gebunden
vollstaendiger Ereignis-Handoff:  bestanden
B0-Bestandsvergleich:             bestanden
B2-Nullarm:                       bestanden
B2-Reproduktion:                 bestanden
Probe P:                          nein
Gegenbaseline N8:                 nein
Forschungsmetrik:                 nein
Vollmatrix:                       gesperrt
Forschungslauf:                   nein
```

## Bester naechster Schritt

S2-C4 bis S2-C8 binden inzwischen Angleichung, Probe P, N8, Observer,
Einpaardistanzen und C1; S2-C9 bis S2-C16 schliessen die A/B-Referenz bis zur
kanonischen End-to-End-Komposition. Der S2-Zwischenentscheid verweist als
naechsten Schritt auf den statischen S1-C-Kandidatenvertrag. Noch keine
Forschungsentscheidung oder Vollmatrix.
