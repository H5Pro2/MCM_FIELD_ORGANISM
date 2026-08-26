# W1-V: Ereignisdichte und technische Ressourcenlast

Stand: 2026-08-09

Entscheidung: `W1V_FIELD_ENDPOINT_INVARIANT_ACROSS_BOUND_EVENT_DENSITIES`

Forschungslauf: nein

Realer Browser gestartet: nein

Adaptive Regulation implementiert: nein

## Auftrag

W1-V trennt technische Ereignisarbeit von Feldamplitude. Drei feste
Ereignisdichten durchlaufen jeweils denselben einsekundigen AV-Horizont:

| Dichte | Unterstuetzung | Ereignisse je Modalitaet | AV-Ereignisse gesamt |
|---|---:|---:|---:|
| density_10_hz_per_modality | 0.1 s | 10 | 20 |
| density_100_hz_per_modality | 0.01 s | 100 | 200 |
| density_1000_hz_per_modality | 0.001 s | 1000 | 2000 |

Jede Dichte wird mit zwei Eingabearmen und fuenf Wiederholungen aus einem
frischen 26-Neuronen-Feld ausgefuehrt:

- `0.0`: exakte Nullkontaktkontrolle;
- `0.1`: identische gleichmaessige nichtnullige Dauerbelastung.

Das ergibt sechs aggregierte Beobachtungen aus 30 technischen
Runtime-Ausfuehrungen. Ein Browser, reale Sensorik und Ergebnisdateien werden
nicht verwendet.

## Deterministisches Arbeitsinventar

| Dichte | AV-Ereignisse | Abschlussgruppen | lokal projizierte Kontakte | Proposal-Batches |
|---|---:|---:|---:|---:|
| 10 Hz je Modalitaet | 20 | 10 | 260 | 1 |
| 100 Hz je Modalitaet | 200 | 100 | 2600 | 1 |
| 1000 Hz je Modalitaet | 2000 | 1000 | 26000 | 1 |

Zwischen kleinstem und groesstem Arm wachsen Quellereignisse und lokal
projizierte Kontakte jeweils exakt um Faktor `100`. Die Feldgeometrie, der
Organismushorizont, die Proposal-Batchanzahl und die Kontaktamplitude bleiben
unveraendert.

## Feldendpunkte

Die Nullkontaktarme enden bei allen Dichten exakt mit Aktivierungs-L1,
Aktivierungs-Linf und Afterimage-Linf `0.0`. Ihre vollstaendigen
Snapshot-Digests sind bitgleich.

Im aktiven Arm betraegt Aktivierungs-Linf:

| Dichte | Aktivierungs-Linf | Delta-Linf zur 10-Hz-Referenz |
|---|---:|---:|
| 10 Hz je Modalitaet | 0.06321205588285593 | 0.0 |
| 100 Hz je Modalitaet | 0.06321205588285551 | 4.440892098500626e-16 |
| 1000 Hz je Modalitaet | 0.06321205588285356 | 2.400857290751901e-15 |

Die 100-fache Ereignisarbeit erzeugt damit innerhalb der gebundenen
Toleranz `1e-12` weder zusaetzliche Feldaufnahme noch einen anderen aktiven
Feldendpunkt.

## Deskriptive Laufzeit

Eine beispielhafte lokale Messung ergab folgende Median-Wandzeiten fuer die
reine Feldruntime:

| Dichte | Nullkontakt | aktiver Kontakt |
|---|---:|---:|
| 10 Hz je Modalitaet | 0.0088770 s | 0.0085225 s |
| 100 Hz je Modalitaet | 0.0464759 s | 0.0464805 s |
| 1000 Hz je Modalitaet | 0.4464525 s | 0.4314473 s |

Diese Zeiten sind umgebungs- und lastabhaengige Diagnostik. Sie sind keine
Abnahmeschwelle und gehen nicht in die Feldentscheidung ein. Deterministisch
gebunden sind nur Ereignis-, Gruppen-, Kontakt- und Batchinventare.

## Abnahme

Der erweiterte Feldverbund besteht mit `79 passed` und 4 Subtests. Geprueft
sind beide Dichtearme, exakte Arbeitsinventare, wiederholbare Endpunkte,
Nullkontaktinvarianz, aktive Dichteinvarianz, geordnete deskriptive
Zeitmessungen, fehlende adaptive Rollen sowie W1-R bis W1-U, Feldruntime,
Substrat, gemeinsamer Feldverteiler und aktuelle Architektur-API.

## Aussagegrenze

W1-V beobachtet innerhalb der gebundenen Matrix keinen technischen
Ressourcenabbruch und keine dichteabhaengige Feldverfaelschung. Dies ist kein
Nachweis unbegrenzter Kapazitaet. Speicherbedarf, konkurrierende Prozesse,
Live-Sensortransport, Browser-Jitter und Dichten oberhalb 1000 Hz je
Modalitaet wurden nicht untersucht.

Der Befund begruendet keine Selbstregulation, Wahrnehmung, Feldzeit,
Praegung, Memory, Organisation, Semantik oder KI. Eine technische
Eingangsbegrenzung waere zudem noch keine organismische Selbstregulation.

## Bester naechster Schritt

W1-W schliesst die Regulationsvorpruefung formal gegen den bestehenden
E0-Vertrag ab. W1-R bis W1-V werden in einer Evidenztabelle den notwendigen
Ausloesern Feldgrenze, Kontrastverlust, Erholungsfehler und
Ressourcenverletzung gegenuebergestellt. Da keiner dieser Ausloeser im
gebundenen Bereich vorliegt, bleibt adaptive Regulation geschlossen. Danach
kehrt die Hauptarbeit zur offenen Substrat- und Memory-Grundlagenfrage
zurueck, statt weitere kuenstliche Regulationsmechanik zu erzeugen.
