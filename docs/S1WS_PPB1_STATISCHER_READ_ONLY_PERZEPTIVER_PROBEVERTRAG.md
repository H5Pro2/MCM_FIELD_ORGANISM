# S1-WS: Statischer read-only perzeptiver Probevertrag

## Auftrag und Grenze

S1-WS trennt die spaetere Wiedererkennung methodisch von der schreibenden
Zustandsbildung. Der Vertrag beschreibt ausschliesslich eine private
read-only Probe gegen einen bereits gebildeten PPB-1-Zustand.

Es wurde keine Probe implementiert oder ausgefuehrt. Zustandsmaschine,
Referenzkern, Feldsnapshot, Produktionspfad und oeffentliche API bleiben
unveraendert. Semantische Labels, Woerter, Feldrueckwirkung und reale
Audio-/Videolaeufe sind ausgeschlossen.

## Probeinput

Eine spaetere Probe muss Bank-, Konfigurations-, Zustands- und
Identitaetsdigest sowie Modalitaet, Geometrie und geordnete Traeger binden.
Der Probeinput besteht ausschliesslich aus einem spaeteren normalisierten,
reduzierten Rezeptorzustand und dessen Digest. Audio- oder Bildrohdaten und
semantische Rollen sind nicht zulaessig.

Die Probe muss kausal nach dem letzten im Bankzustand gebundenen Kontakt
liegen. Sie darf selbst keinen akzeptierten Bank- oder Lebenszyklusschritt
erzeugen.

## Zulaessige Vergleichsmenge

Nur belegte und stabilisierte private Plaetze sind fuer die
Wiedererkennungspruefung zulaessig. Freie oder noch nicht stabilisierte
Plaetze werden nicht als spaeter abrufbarer Wahrnehmungszustand behandelt.

Die Probe darf weder einen Platz verfallen lassen noch ersetzen oder seine
Zulaessigkeit veraendern. Ablauf und Kapazitaetsersatz bleiben ausschliesslich
Aufgabe eines spaeteren schreibenden Lebenszyklusschritts.

## Vergleich und read-only Befund

Der Vertrag verwendet die vorhandene dimensionsnormalisierte L1-Distanz und
die bereits gebundene Matchschwelle der privaten Bank. Unter den zulaessigen
Plaetzen entscheidet die kleinste Distanz; bei Gleichstand die
lexikographisch kleinere Platz-ID. Ein Abstand auf der Schwelle gilt als
Match, ein groesserer Abstand nicht.

Der read-only Befund bindet nur Identitaeten, Digests, Anzahl zulaessiger
Plaetze, Matchentscheidung, ausgewaehlte Platz-ID, Distanz und den Digest des
ausgewaehlten Prototyps. Er enthaelt weder Prototypwerte noch Semantik,
Feldwirkung oder Nachzustand.

## Unveraenderlichkeitsvertrag

Vor und nach einer spaeteren Probe muessen Bankzustands- und
Identitaetsdigest identisch sein. Folgende Aenderungen bleiben exakt null:

- akzeptierte Schritte und Stuetzung;
- letzte Auswahlzeit und Prototypwerte;
- Stabilisierung, Ablauf und Ersatz;
- Referenz- und Lebenszyklusaufrufe;
- Dateioperation, Feldrueckwirkung und Retry.

Jede Digest-, Anatomie- oder Kausalabweichung stoppt ohne Befund. Jede
verdeckte Zustandsaenderung oder erreichte Advance-, Datei-, Feld-, Semantik-
oder Produktionsfunktion verwirft einen bereits gebildeten Befund und stoppt
den Probeabschnitt.

## Falsifikation und Status

Eine spaetere Implementierung muss insbesondere deterministisch sein,
Schwellenrand und Gleichstand korrekt behandeln und auch bei wiederholter
Probe keinerlei Stuetzung aufbauen oder Ablauf verzoegern. Jeder versteckte
Schreib- oder Advance-Aufruf beendet den Probeansatz.

Der Vertragsdigest lautet:

```text
909d3dc3d01ec3b94b53f0c770e615364e08ecb0b91f3aaefc72daf3aa834559
```

`10 von 10` rein statische Vertragstests bestehen. Sie laden nur die
JSON-Struktur; keine Probe- oder Zustandsfunktion wird importiert oder
ausgefuehrt.

S1-WS laesst eine private read-only Probe nur fuer eine spaetere
Implementierungsfreigabe zu. Der Vertrag bestaetigt weder Abruffunktion noch
Memory-Faehigkeit.

## Naechster Schritt

S1-WT ist als rein statischer Implementierungspreflight vorgesehen. Er muss
vor jedem Probe-Code klaeren, welche vorhandenen reinen Distanz-,
Validierungs- und Digestrollen ohne Aufruf von `advance_ppb1_bank` verwendet
werden koennen. Keine Implementierung oder Ausfuehrung waehrend dieses
Preflights.

## Grundlagen

- [S1-WR statischer Zustandslebenszyklus-Audit](S1WR_PPB1_STATISCHER_ZUSTANDSLEBENSZYKLUS_AUDIT.md)
- [Maschinenlesbarer S1-WS-Vertrag](S1WS_PPB1_READ_ONLY_PERZEPTIVER_PROBEVERTRAG_V1.json)
