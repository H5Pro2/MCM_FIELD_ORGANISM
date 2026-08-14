# S2-C16: Kanonische n=8-A/B-End-to-End-Komposition

Stand: 2026-08-07

Status: `S2C16_N8_AB_CANONICAL_COMPOSITION_BOUND`

Schwelle: nein

Forschungsentscheidung: nein

Forschungslauf: nein

## Zweck

S2-C16 schliesst die bisher einzeln gebundenen technischen Referenzbausteine
zu genau einem kanonischen In-Memory-Pfad:

```text
r8.a/c8.a und r8.b/c8.b
-> B0 oder lineares B2
-> externe S/H-Angleichung
-> identische Probe P
-> D_pair_A(8) und D_pair_B(8)
-> C14-A/B-Skalarcontainer
-> D_world_pair(8)
```

Die Funktion `compose_s2c16_n8_ab_reference()` akzeptiert ausschliesslich
`b0` oder `b2`. Sie schreibt keine Datei und vergibt keine Laufnummer.

## Gebundene Provenienz

`S2C16N8ABCanonicalComposition` bindet:

- die Digests der beiden A- und beiden B-Weltplaene;
- die typisierten A8- und B8-Paarergebnisse;
- den daraus erzeugten C14-Container;
- die daraus erzeugte C15-Distanz;
- einen kanonischen Digest der gesamten Komposition.

Der Ergebnistyp weist inkonsistente Modellarme, Quellskalare oder eine
unterbrochene Container-Digest-Kette ab.

## Technische Pruefung

`tests/test_s2c16_n8_ab_end_to_end.py` prueft fuenf Invarianten:

1. Der vollstaendige B0-Pfad bleibt fuer beide Paarwerte und
   `D_world_pair(8)` exakt null.
2. Der aktive lineare B2-Pfad liefert endliche und digestgenau
   reproduzierbare technische Werte.
3. Vier getrennte kanonische Weltplan-Digests bleiben gebunden.
4. Paarwerte, Container und Distanz besitzen eine geschlossene Provenienz.
5. Entscheidung, Schwelle und Weltspezifitaetsrolle fehlen.

```text
neue S2-C16-Suite:                 5 passed
direkter S1-B/S2-Testverbund:    115 passed
Python-Kompilation:               bestanden
```

Die Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen Testcache und
nicht die geprueften Vertrage.

## Aussagegrenze

C16 zeigt, dass die vorhandene lineare Referenz technisch durchgaengig und
reproduzierbar zusammengesetzt werden kann. Es zeigt nicht Memory,
Feldzeitverdichtung, Praegung, Weltspezifitaet, innere Organisation,
Semantik, Selbstregulation oder KI. Ein endlicher B2-Abstand ist weiterhin
nur ein technischer Referenzwert der fest definierten linearen L-Kopplung.

## Bester naechster Schritt

Der [S2-Zwischenentscheid](S2_ZWISCHENENTSCHEID_NACH_C16.md) ist gebunden.
Der statische
[S1-C-Zulassungsvertrag](S1C_ZULASSUNGSVERTRAG_MINIMALER_NICHTLINEARER_LOKALER_SUBSTRATKANDIDAT.md)
ist ebenfalls gebunden. S1-D reduziert die gepruefte MCM-spezifische
Naturannahme auf eine Relaxationsbaseline. S1-E begruendet keine zweite
lokale Variable und bestimmt verteilte kausale Nichtseparierbarkeit als
offene Feldanforderung. Als naechstes folgt ihr statischer
S1-F-Zulassungsvertrag. Noch keine Implementierung, Vollmatrix oder Laufnummer.
