# S2-C: Technische Kernimplementierung des Referenzrunners

Stand: 2026-08-07

Status: `S2C_CORE_IMPLEMENTED_S2C2_BATCH_BOUND`

Vollmatrix: technisch blockiert

Forschungslauf: nein

## Zweck

S2-C setzt den gebundenen S2-B-Vertrag in drei voneinander getrennten
Produktionsmodulen um, ohne die audiovisuelle Vollmatrix auszufuehren.

## Implementierte Module

### `s2_reference_worlds.py`

Implementiert sind:

- elf kanonische achtsekundige Bildungsgeschichten;
- die getrennte 0.4-s-Probe P;
- exakt gepaarte Kontaktzeit und Kontaktschwerpunkte fuer Rn/Cn;
- 800 Audiohops und 80 Videoframes je Bildungsgeschichte;
- 40 Audiohops und vier Videoframes fuer P;
- sechs Modelladressen B0 bis B5;
- die feste L-Tausch-Involution;
- 152 eindeutige logische Aufgaben;
- ein kanonischer Inventardigest.

Die Tests bauen nur die prozeduralen Plaene und Digests. Sie oeffnen keine
Quellen und speisen keine Rezeptoren.

### `s2_reference_baselines.py`

Implementiert sind reine, weltunabhaengige S/H/L-Referenzfortschreibungen:

```text
B0  schneller Nullpfad mit exakt unveraendertem L
B1  einseitige lineare L-Spur
B2  unabhaengige lineare reziproke Referenz
B3  tanh-begrenzte Integration des exakten S-Zeitintegrals
B4  fester dimensionsloser Gain mit RK4-Teilungskontrolle 16/32
B5  lineare Rueckwirkungsablation
```

Lineare affine Systeme verwenden eine lokale Scaling-and-Squaring-
Pade-13-Matrixexponentialfunktion auf NumPy-Basis. B4 meldet seinen
Teilungsfehler als Skalar. Kein Modell liest Metriken oder Entscheidungen.

Diese Referenzen tragen absichtlich keinen Schema-3-Snapshot mit einem
falschen S1-B-Gleichungsnamen. Der reale B2-Pfad bleibt der vorhandene
S1-B-Zustand; die neue B2-Berechnung ist nur dessen unabhaengige spaetere
Gegenrechnung.

### `s2_reference_runner.py`

Implementiert sind:

- externe S/H-Angleichung bei unveraendertem L, Tick, Takt, Docks und
  letzter Verteilung;
- skalare Mess- und Kontrollvertraege;
- kanonische Zuordnung von Messung zu Aufgabe;
- Orchestrierung expliziter technischer Teilmengen;
- harte Ablehnung eines Aufrufs mit 152 Aufgaben;
- kanonische Paketbildung aus bereits vorliegenden 152 Skalarmessungen;
- Schema `mcm.s2.reference.packet.v1`;
- endliche JSON-Projektion ohne Rohdaten, Trajektorien, Lauf-ID oder
  Forschungsentscheidung.

Die Paketbildung fuehrt selbst keine Welt und kein Modell aus. Ein
Mess-Executor wird nur als explizite technische Abhaengigkeit angenommen.

## Technische Tests

Neu angelegt wurden:

```text
tests/test_s2_reference_worlds.py
tests/test_s2_reference_baselines.py
tests/test_s2_reference_runner.py
```

Ergebnisse:

```text
fokussierte S2-C-Suite:       17 passed
S1-B/Shared-Field-Regression: 43 passed, 9 subtests passed
kombinierte Abnahme:          60 passed, 9 subtests passed
Python-Kompilation:           bestanden
```

Es bleibt eine vorhandene Pytest-Cachewarnung, weil am Cachepfad bereits ein
inkompatibler Dateisystemeintrag existiert. Sie beeinflusst die Testresultate
nicht.

## In S2-C2 geschlossene technische Luecke

S2-C2 bindet inzwischen den transienten B0/B2-Einzelbatchpfad. Weiterhin
offen ist der kanonische AV-Weltadapter, der:

```text
eine kanonische ControlledAudioVideoTestWorld
-> frische prozedurale Quellen und neutrale Rezeptorreduktion
-> zeitversetzbare asynchrone Rezeptorbatches
-> zunaechst genau B0 und B2
```

verdrahtet. Bildung, Boundary-Angleichung, Intervention, Probe und
`S2ReferenceMeasurement` bleiben nachgelagert.

Der S1-B-Pfad besitzt jetzt eine gleichwertige Transient-Batch-Schnittstelle
und ist gegen Fastpfad, unabhaengige B2-Referenz und Batchteilung geprueft.

Ohne diese Bruecke waere ein angeblich fertiger Vollrunner nur eine
Orchestrierung von Ersatzmessungen. Das ist fuer einen Forschungslauf nicht
zulaessig.

## Aussagegrenze

S2-C weist keine Weltwirkung und keinen Unterschied zwischen Wiederholung
und Dauerkontakt nach. Die bestandenen Tests betreffen nur Vertraege,
Numerik-Fixtures, Zustandsisolation, Paketgrenzen und Regressionen.

Insbesondere bestehen keine Befunde zu Praegung, Memory, relativer Feldzeit,
Organisation, Topologie, Semantik, Selbstregulation oder KI.

## Entscheidung

```text
Weltplaene:                    implementiert
B0- bis B5-Referenznumerik:    implementiert
S/H-Angleichung:               implementiert
Aufgabeninventar:              implementiert
skalare Paketprojektion:       implementiert
152-Aufgaben-Sperre:           implementiert und getestet
transienter B0/B2-Executor:    implementiert
kanonischer AV-Weltadapter:    implementiert
Probe-P-Fortsetzung:           implementiert
reale Vollmatrix:              gesperrt
Auswertungsentscheidung:       nicht implementiert
Forschungslauf:                nein
```

## Bester naechster Schritt

S2-C4 bis S2-C8 binden r1.a/c1.a, N8, S/H-Angleichung, Probe P, Observer,
Einpaardistanzen und Identitaetskontrolle. S2-C9 bis S2-C16 schliessen die
A/B-Referenz bis zur kanonischen End-to-End-Komposition. Der
S2-Zwischenentscheid verweist als naechsten Schritt auf den statischen
S1-C-Kandidatenvertrag. Noch keine weitere Gegenbaseline, Vollmatrix oder
Ergebnisdatei.
