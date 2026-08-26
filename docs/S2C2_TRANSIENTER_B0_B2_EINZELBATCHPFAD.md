# S2-C2: Transienter B0/B2-Einzelbatchpfad

Stand: 2026-08-07

Status: `S2C2_TRANSIENT_B0_B2_BATCH_BOUND`

Audiovisuelle Vollmatrix: gesperrt

Forschungslauf: nein

## Zweck

S2-C2 schliesst die technische Luecke zwischen asynchronen reduzierten
Rezeptorabschluessen und der S1-B-Referenzmechanik fuer genau einen
vorbereiteten Batch.

Der Pfad trifft keine Forschungsentscheidung und fuehrt keine der elf
kanonischen S2-Bildungsgeschichten aus.

## Implementierte Transient-S1-B-Semantik

`advance_s1b_reciprocal_shared_field_transient` verarbeitet dieselben
`TransientNeuronInputSet`-Objekte wie der bestehende schnelle Neutralpfad.

Innerhalb eines Batches gilt:

```text
zwischen Rezeptorabschluessen:
    exakte gekoppelte S/H/L-Fortschreibung

am Rezeptorabschluss:
    endliche lokale Aufnahme wirkt nur auf S
    H bleibt am Impuls unveraendert
    L bleibt am Impuls unveraendert

danach:
    gemeinsame S/H/L-Fortschreibung bis zum naechsten Abschluss
```

Die freie B2-Entwicklung verwendet dieselbe kapazitaetsgewichtete skalierte
S/L-Matrix wie S1-B. H wird aus den gemeinsamen S/L-Eigenmoden exakt
fortgeschrieben. Der Nullarm `g=0` delegiert unveraendert an den bestehenden
schnellen Transient-Pfad und haengt nur den unveraenderten L-Zustand wieder
an.

Observer erhalten ausschliesslich Kopien von S, H und L. Sie werden von der
Runtime nicht gelesen.

## Einzelbatch-Bruecke

`advance_s2_controlled_receptor_batch` akzeptiert derzeit genau:

```text
B0 -> vorhandener schneller transienter Feldpfad
B2 -> neuer transienter S1-B-Feldpfad
```

Andere Modellarme werden vor jeder Fortschreibung abgewiesen. Das Ergebnis
`S2ControlledBatchResult` enthaelt nur:

- Modelladresse;
- Start-Layer-Digest;
- Endsnapshot-Digest;
- Zahl lokaler reduzierter Kontakte;
- den unveraenderten resultierenden In-Memory-Feldzustand.

Es enthaelt keine Forschungsmetrik, keine Entscheidung, keine Lauf-ID und
keinen Schreibpfad.

## Unabhaengige Punktkontaktreferenz

`apply_s2_reference_point_contacts` bildet denselben endlichen lokalen
Rezeptorimpuls unabhaengig auf `S2ReferenceState` ab. Nur S wird veraendert;
H und L bleiben exakt gleich. Damit kann ein aktiver transienter B2-Batch
gegen die bereits getrennte Pade-13-B2-Referenz geprueft werden.

## Technische Pruefung

Die neue Suite `tests/test_s2c2_transient_batch.py` bindet vier Kontrollen:

1. B0 ist digestgleich zum bestehenden schnellen Transient-Pfad.
2. B2 mit `g=0` ist in seiner Fastprojektion digestgleich zu B0.
3. Aktives B2 stimmt ueber dieselben asynchronen Ereignisse innerhalb
   `2e-12` mit der unabhaengigen Pade-13-Referenz ueberein.
4. Aktives B2 ist innerhalb `2e-12` gegen grobe und feine Batchteilung
   invariant.

Ergebnisse:

```text
neue S2-C2-Suite:                  4 passed
fokussierter B0/B2/S2-Verbund:    25 passed
gesamter betroffener Testverbund: 70 passed, 9 subtests passed
Python-Kompilation:               bestanden
```

Die bestehende Pytest-Cachewarnung bleibt ohne Einfluss auf die Ergebnisse.

## Verbleibende Grenze

Der Batchpfad ist noch nicht mit dem kanonischen S2-Weltplan verdrahtet.
Insbesondere fehlt noch die technische Funktion:

```text
ControlledAudioVideoTestWorld
-> frische prozedurale Audio-/Videoquellen
-> vorhandene neutrale Rezeptorreduktion
-> gemeinsame Ereigniszeitlinie mit festem Offset
-> vorbereitete Transient-Batches
-> B0/B2-Einzelbatchpfad
```

Darum wurde noch keine Bildungsgeschichte `r1.a` bis `n8` und keine Probe P
durch B0 oder B2 gefuehrt. Die Tests verwenden nur kleine kontrollierte,
bereits reduzierte auditive und visuelle Ereignisfolgen.

Eine `S2ReferenceMeasurement` waere an diesem Stand noch unzulaessig, weil
sie Bildung, S/H-Angleichung, Intervention, Probe und Gegenvergleich gemeinsam
benoetigt. S2-C2 erzeugt deshalb bewusst nur ein technisches Batchresultat.

## Aussagegrenze

S2-C2 weist nur die technische Gleichheit und Teilungsstabilitaet des
Einzelbatchpfads nach. Es bestehen keine Befunde zu Weltgeschichte,
Wiederholung, Dauerkontakt, Praegung, Memory, relativer Feldzeit,
Organisation, Topologie, Semantik, Selbstregulation oder KI.

## Entscheidung

```text
B0-Transient-Bruecke:             gebunden
B2-Transient-S1-B:                gebunden
Nullpfadgleichheit:               bestanden
unabhaengige B2-Referenz:         bestanden
Batchteilungsinvarianz:           bestanden
kanonischer AV-Weltadapter:       offen
S2ReferenceMeasurement:           noch nicht zulaessig
Vollmatrix:                       gesperrt
Forschungslauf:                   nein
```

## Bester naechster Schritt

S2-C3 implementieren: genau einen kanonischen `ControlledAudioVideoTestWorld`
ohne Persistenz in reduzierte, zeitversetzbare Rezeptorbatches ueberfuehren
und zunaechst nur `r1.a` technisch durch B0 und B2 fortschreiben. Noch keine
Probe, keine Vollmatrix und keine Forschungsentscheidung.
