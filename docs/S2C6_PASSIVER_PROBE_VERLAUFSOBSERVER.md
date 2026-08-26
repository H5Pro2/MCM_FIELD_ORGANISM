# S2-C6: Passiver Probe-Verlaufsobserver

Stand: 2026-08-07

Status: `S2C6_PASSIVE_PROBE_TRACE_OBSERVER_BOUND`

Skalare Distanz: nicht berechnet

Vollmatrix: gesperrt

Forschungslauf: nein

## Zweck

S2-C6 bindet fuer die in S2-C4 und S2-C5 aufgebauten r1.a- und N8-Pfade
einen identischen passiven Beobachtungssupport waehrend Probe P:

```text
r1.a oder N8
-> externe S/H-Angleichung
-> identische Probe P
-> passive S/H-Kopie an jedem echten Rezeptorabschluss
-> fluechtige unveraenderliche In-Memory-Spur
```

Der Observer berechnet keine Distanz und trifft keine Entscheidung.

## Kanonischer Support

Die vorhandenen transienten B0- und B2-Integratoren stellen bereits
observerseitige Zustandskopien nach jedem abgeschlossenen Rezeptorereignis
bereit. S2-C6 verwendet ausschliesslich diese bestehende Grenze.

Probe P besitzt 31 eindeutige Abschlusszeitpunkte:

```text
8.10 s, 8.11 s, ..., 8.40 s
```

Auditive und visuelle Abschluesse am selben Tick werden vor der Beobachtung
gemeinsam angewendet. Es werden keine kuenstlichen Zwischenticks und keine
nachtraeglich interpolierten Werte erzeugt.

## Ergebnisvertraege

`S2ProbeTraceSample` enthaelt nur:

- einen kanonischen Abschluss-Tick;
- 84 Aktivierungswerte S;
- 84 Nachhallwerte H.

`S2ProbeTrace` bindet Welt-, Modell-, Probe- und Snapshot-Digests sowie die
geordneten fluechtigen Samples. `S2ProbeTracePair` akzeptiert nur die feste
Reihenfolge `r1.a` und `n8` im selben B0- oder B2-Modellarm mit identischem
Probeplan und identischen Ticks.

L wird an dieser Observergrenze nicht ausgegeben. Die kopierten Vektoren sind
unveraenderliche Tupel; eine Rueckwirkung in die Feldfortschreibung ist nicht
moeglich.

## Technische Einbindung

`observe_s2c6_probe_pair`:

- akzeptiert nur eine abgeschlossene r1.a- und N8-Bildung;
- verlangt denselben B0- oder B2-Arm und dieselbe Kopplung;
- fuehrt denselben externen S/H-Abgleich wie C4/C5 aus;
- verwendet denselben kanonischen Probeplan P;
- prueft Observer-Ticks gegen die echten Probe-Abschlussgruppen;
- persistiert keine Vektoren, Medien oder Ergebnisse.

Der interne optionale Observer des B0/B2-Einzelbatchpfads erhaelt nur Kopien.
Ohne Observer bleibt der bisherige C2- bis C5-Pfad unveraendert.

## Technische Pruefung

`tests/test_s2c6_probe_trace_observer.py` bindet:

1. exakt 31 geordnete gemeinsame Probe-Ticks;
2. unveraenderte 84-Orte-S/H-Anatomie in jedem Sample;
3. exakt gleiche Enddigests beobachteter und unbeobachteter C4/C5-Pfade;
4. digest- und wertgenaue Reproduktion der fluechtigen Spuren;
5. Abwesenheit von Metrik, Distanz und Entscheidung;
6. Abweisung unterschiedlich modellierter Paare.

```text
neue S2-C6-Suite:                  6 passed
gesamter relevanter Testverbund:  105 passed, 13 subtests passed
Python-Kompilation:               bestanden
```

Die bekannte Pytest-Cachewarnung hat keinen Einfluss auf die Ergebnisse.

## Aussagegrenze

S2-C6 zeigt nur, dass r1.a und N8 passiv am selben realen Probe-Support
beobachtet werden koennen, ohne ihren technischen Endzustand zu veraendern.
Es wurde weder geprueft noch behauptet, dass ihre S/H-Spuren verschieden
sind.

Es folgen keine Aussagen zu Praegung, Memory, relativer Feldzeit, innerem
Kontext, Wiedererkennung, Semantik, Organisation, Selbstregulation oder KI.

## Entscheidung

```text
gemeinsamer Probe-Support:         gebunden
31 echte Abschlusszeitpunkte:      gebunden
S/H-Anatomie:                      84/84 je Sample
Observerpassivitaet:               bestanden
B0/B2-Reproduktion:               bestanden
skalare D_S-/D_H-Distanz:         nein
D_L-Distanz:                       nein
Vollmatrix:                        gesperrt
Forschungslauf:                    nein
```

## Bester naechster Schritt

S2-C7 und S2-C8 binden inzwischen Einpaardistanzen und C1. Als naechstes
schliessen S2-C9 bis S2-C16 die A/B-Referenz bis zur kanonischen
End-to-End-Komposition. Der S2-Zwischenentscheid verweist als naechsten
Schritt auf den statischen S1-C-Kandidatenvertrag. Noch keine Entscheidung,
Vollmatrix, Persistenz oder Laufnummer.
