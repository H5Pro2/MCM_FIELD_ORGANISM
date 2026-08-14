# Z1: technische Quellenarme und Pfadmetrik

Stand: 2026-08-06

> **Aktueller Status:** Dieses Dokument beschreibt den technischen
> Zwischenstand vor der Ausfuehrung. Lauf 195 ist inzwischen
> [`TECHNICALLY_UNDECIDABLE`](forschung/LAUF_195_Z1_FELDTRAJEKTORIEN_KOVARIANZAUDIT.md)
> abgeschlossen.

## Status

Die technische Grundlage der
[Z1-Vorregistrierung](Z1_FELDTRAJEKTORIEN_KOVARIANZAUDIT_VORREGISTRIERUNG.md)
ist implementiert und getestet. Es wurde kein Feldarm ausgefuehrt, kein
Ergebnis ausgewertet und kein Lauf 195 erzeugt.

## Implementierte Bausteine

### Gebundene Quellenarme

`mcm_field_organism/mcm_f3_z1_source.py` erzeugt ohne Feldfortschreibung:

- Referenz und rein technisch halbierte Vorschlagsschritte;
- exakte Zeitdehnung mit Faktor 2;
- exakte Zeitkompression mit Faktor 0,5;
- modalitaetsweise Wertumkehr auf unveraendertem Zielzeitraster;
- feste Vierblockpermutation `0,3,2,1`;
- eine unabhaengige kontrollierte AV-Quelle;
- feste Sequenz- und Ausfuehrungsdigests fuer alle sieben Arme.

Alle Arme tragen 101 reduzierte Ereignisse in 91 gemeinsamen
Abschlussgruppen. Nur `A.partitioned` verdoppelt die technischen
Vorschlagsschritte von 91 auf 182, ohne die Rezeptorsequenzen zu veraendern.

### Passiver Observer

`mcm_field_organism/mcm_f3_z1_trajectory.py` enthaelt einen append-only
Observer fuer vollstaendige S-, H- und M-Vektoren. Er kopiert Runtimearrays,
fordert streng steigende Ticks und besitzt keinen Schreibpfad zur Runtime.

### Reine Pfadmetrik

Das gleiche Modul implementiert getrennt fuer S, H und M:

- kumulative euklidische Pfadlaenge;
- Normierung auf `q = 0..1`;
- lineare Abtastung auf 101 festen Punkten;
- skalierte L-inf-Distanz zur Referenzbahn;
- die vorregistrierte numerische Huelle
  `max(1e-12, 4 * D(2n, 4n))`.

Weltsekunden, Tickzahl und Beobachtungspunktzahl gehen nicht als
Sachmesswert in die Pfaddistanz ein.

## Technische Korrekturen vor jeder Ausfuehrung

Der statische API-Abgleich zeigte zwei unmoegliche Annahmen der ersten
Vorregistrierungsfassung:

1. Der Spektralrezeptor erzeugt nach seinem Anlauf aus 100 Audiohops 91
   reduzierte Audioabschluesse, nicht 100.
2. Eine vollstaendige Umkehr gemeinsamer Abschlussgruppen und die zuerst
   genannte Blockfolge waren bei unterschiedlichen Modalitaetsraten nicht
   bijektiv auf dasselbe Raster abbildbar.

Vor jeder Messung wurden deshalb die modalitaetsweise Wertumkehr und die
inventargleiche Blockfolge `0,3,2,1` festgelegt. Diese Korrekturen veraendern
keinen Befund, weil noch kein Z1-Feldlauf stattgefunden hatte.

## Technische Pruefung

Bestanden sind:

- 13 neue Tests fuer Quellenarme, Zeitabbildung, Reihenfolgenkontrollen,
  deterministische Digests, Observer und Pfadmetrik;
- insgesamt 34 fokussierte Z1-, F3-Runtime-, B3-, E3- und K2-B-Tests;
- Paketimport und oeffentliche Z1-API;
- Python-Kompilation der Runtime und Tests.

## Nicht implementiert

- der gebundene Mehrarmrunner und die n/2n/4n-Aufgabenmatrix sind inzwischen
  [technisch implementiert](Z1_TECHNISCHER_F3_B3_MEHRARMRUNNER.md), aber nicht
  real ausgefuehrt;
- keine Forschungsentscheidungs- und Ergebnisserialisierung;
- keine Ergebnisdatei und kein Lauf 195.

## Aussagegrenze

Die Implementierung zeigt nur, dass der vorregistrierte Quellen- und
Messvertrag technisch darstellbar ist. Sie belegt keine Teilungsinvarianz,
Zeitkovarianz, Ordnungssensitivitaet, relative Feldzeit, Memory, Organisation,
Topologie, Semantik, Selbstregulation oder KI.

## Bester naechster Schritt

Die reine Z1-Entscheidungs- und Serialisierungsschicht implementieren und mit
synthetischen Paketen testen. Danach die reale Paketfunktion genau einmal als
Lauf 195 ausfuehren.
