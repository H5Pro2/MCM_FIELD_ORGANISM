# W7-AC: Implementierung des Observer-Siebenpfad-Verbrauchers

## Entscheidung

`SEPARATE_MAIN_AND_PROBE_OBSERVER_CONSUMER_IMPLEMENTED`

W7-AC implementiert den W7-AB-Vertrag als isolierte In-Memory-
Obserververarbeitung auf den vorhandenen W7-AA-P0-Produktionen. P0 wird
nicht neu erzeugt oder veraendert. Es wurde kein Report und kein formaler
Forschungslauf erstellt.

## 1. Optionale additive W7-P-Autorisierung

Der vorhandene W7-P-Kompositor akzeptierte zuvor nur Quelldigests aus dem
urspruenglichen W7-M-Inventar. W7-AC erweitert ihn optional um denselben
W7-W-Autorisierungsvertrag, den W7-R bereits verwendet.

Ohne Vertrag bleibt W7-P fuer additive Digests geschlossen. Mit Vertrag
werden Matrix, Quelldigest, Pfad und Intervall erneut geprueft. Die
W7-R-Uebergabe `compose_w7r_observer_driver` reicht diese optionale Bindung
weiter. Bestehende Aufrufe und vorhandene W7-M-Quellen bleiben unveraendert.

## 2. Implementierter Umfang

Das Modul `mcm_field_organism/w7ac_observer_seven_path_consumer.py` erzeugt:

- 67 einmalig komponierte W7-P-Treiber fuer 32 Haupt- und 35
  Probeproduktionen;
- 21 getrennte LEAK-/SAT-/NORM-Hauptketten;
- 96 Hauptobserverfortsetzungen;
- 105 passive Modell-/Pfadcheckpoints;
- 105 gleichpfadige Observerprobehuellen und Probeaeste;
- Modellreihenfolge-, Haupt-/Probereihenfolge-, Checkpoint- und
  P0-Unveraenderlichkeitskontrollen;
- 21 Observerpfadverbrauchsdigests und einen Gesamtverbrauchsdigest.

Alle Hauptketten enden bei Tick 8.

## 3. Gleichpfadige Probehuelle

Die vorhandene `branch_w7t_observer_state`-Funktion bleibt unveraendert. Fuer
Proben wird der W7-T-Zustand desselben Pfads tief kopiert und durch den
vorhandenen Zustandskonstruktor validiert. Eine externe Huelle bindet Pfad,
Modell, Checkpoint, Quellzustandsdigest und `returns_to_main = false`.

Am Kopierpunkt sind Zustandsdigest und Latenz gleich, waehrend Zustands- und
Baselineobjekte getrennt sind. Der Probeendzustand wird nur im Probeast
gebunden.

## 4. Modell- und NORM-Trennung

LEAK, SAT und NORM erhalten fuer dieselbe P0-Produktion dasselbe
Treiberobjekt. Ihre Anfangs-, Haupt-, Checkpoint- und Probezustaende bleiben
modellgetrennt.

NORM setzt seinen nichtnormalisierten Leaky-Latentzustand fort. Die
normalisierte `observer_output_trace` bleibt externe Ausgabe und wird nicht
als naechster Zustand verwendet. Alle Messfelder behalten ausschliesslich
`observer_`-Rollen.

## 5. Gegenkontrollen

Die AB-Ketten werden zusaetzlich in umgekehrter Modellreihenfolge
verarbeitet. Die 21 rollenbezogenen Pfaddigests bleiben unveraendert.

An AB/Checkpoint 0 werden LEAK-Haupt- und Probeast in beiden Reihenfolgen
aus unabhaengigen Kopien verarbeitet. Ihre Fortsetzungsdigests bleiben je
Rolle gleich. Passive Checkpointerzeugung und gesamte Obserververarbeitung
lassen den W7-AA-Gesamtverbrauchsdigest unveraendert.

## 6. Gebundener Gesamtverbrauchsdigest

```text
8c3c296ddbb911346fa649a9e7529f9be86abb67444b4041ee76c8745d778ad7
```

Der Digest bindet den unveraenderten W7-AA-Verbrauch, 21 kanonisch geordnete
Observerpfadverbrauchsdigests und die Gegenkontrollen. Er enthaelt keine
Pfadrangfolge oder Interpretation.

## 7. Verifikation

Die neue W7-AC-Suite enthaelt 15 Tests und besteht mit:

```text
Ran 15 tests
OK
```

Der breitere W7-Verbund besteht mit:

```text
Ran 101 tests
OK
```

Geprueft wurden 21 Rollenketten, 105 Probeaeste, Startticks,
Treibergleichheit, Kontinuitaet, tiefe Zustandskopien, passive Checkpoints,
W7-AA-Bindung, NORM-Latenz, reine Observermessrollen, additive
Autorisierungssperren, Gegenkontrollen, Determinismus und
Manipulationsablehnung.

W7-AC wird weder aus dem Paketwurzelmodul noch aus `current_api` exportiert.

## 8. Aussagegrenze

W7-AC ist die technische Ausfuehrung externer Erklaerungsbaselines. Die
Observerwerte wurden nicht zwischen Pfaden bewertet und beeinflussen keinen
Feldzustand. Daraus folgen keine Feldfunktion, kein Memory, keine Feldzeit,
Organisation, Topologie, Semantik, Selbstregulation oder KI.

## 9. Naechster Schritt

W7-AD soll statisch den ersten gekoppelten CAP-Siebenpfad-Verbrauch binden.
P0 und die W7-AC-Observer bleiben dort unveraenderliche Gegenbaselines.
Haupt- und Probe-M-Zustaende muessen strikt getrennt und kapazitaetserhaltend
fortgesetzt werden. Noch keine gekoppelte Ausfuehrung, kein Browser, Report
oder Forschungslauf.
