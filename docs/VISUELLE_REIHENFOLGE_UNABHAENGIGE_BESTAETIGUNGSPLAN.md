# Unabhaengige Bestaetigung kurzer visueller Folgen

**Status: Plan, Korrekturtest und einmalige unabhaengige Bestaetigung
abgeschlossen.** Grundlage des Plans ist `af1be2f`.
Der [Fehlversuch](../reports/tspm1_functional/sequence-20260829-01/BEFUND.md)
bleibt dauerhaft `NOT_EVALUABLE`. Seine Dateien werden nicht ergaenzt,
repariert oder als funktionaler Befund verwendet.

## 1. Unabhaengige Bildauswahl vor jeder Ausfuehrung

Unveraendertes Profil: 120 x 80 RGB, 3 x 2 Zellen, je 40 x 40 Pixel,
drei gleiche Kanalwerte pro Zelle und 18 ortsgebundene visuelle Werte.
Auditiv bleiben acht Werte null. Zellpositionen werden zeilenweise mit
0 bis 5 nummeriert.

Die Auswahlregel ist vollstaendig deterministisch:

1. Verwende ausschliesslich den Grauwert 40 fuer `L` und 200 fuer `H`.
2. Erzeuge alle 20 Masken mit genau drei `H`- und drei `L`-Zellen.
3. Stelle jede Maske als aufsteigende Dreierkombination ihrer H-Positionen dar
   und sortiere diese Kombinationen lexikografisch.
4. Entferne die vier Anordnungen des Fehlversuchs: `012`, `135`, `045`, `345`.
   Das ist nur eine Neuheitsgrenze; keine dortige Entscheidung geht ein.
5. Waehle aus der verbleibenden Liste unveraendert die ersten vier Masken:
   `013`, `014`, `015`, `023`.

Damit sind vorab gebunden:

| Zustand | H-Positionen | Obere Zeile | Untere Zeile |
|---|---|---|---|
| N1 | 0, 1, 3 | 200, 200, 40 | 200, 40, 40 |
| N2 | 0, 1, 4 | 200, 200, 40 | 40, 200, 40 |
| N3 | 0, 1, 5 | 200, 200, 40 | 40, 40, 200 |
| N4 | 0, 2, 3 | 200, 40, 200 | 200, 40, 40 |

Alle vier haben dasselbe Histogramm, je drei Werte 40 und 200, und dieselbe
globale Kanalhelligkeit `120/255`. Keine Anordnung und kein Intensitaetspaar
stammt aus dem Fehlversuch. Die externe Kennung N1 bis N4 gelangt weder in
Rezeptorwerte noch Bank oder Abruffunktion.

Je zwei Masken unterscheiden sich in mindestens zwei Zellen. Bei Kontrast
160 ist ihr kleinster konstruktiver mittlerer visueller L1-Abstand `160/765`.
Der Abstand eines Zustands zu seiner globalen +/-8-Variante ist `8/255`.
Damit liegt die vorgesehene positive Seite unter und die negative Seite ueber
dem unveraenderten `44/765`. Diese Rechnung ist eine Vorbedingung, kein neuer
Messbefund. Spaeter muessen die tatsaechlichen Rezeptorwerte und alle 4 x 4
Paarabstaende aus jeder Probe aufgezeichnet und unabhaengig nachgerechnet werden.

## 2. Unveraenderte Folgenaufgabe

Zwei frische B4-Banken:

| Episode | Bildungsfolge bei Delta 0 | Gegenfolge |
|---|---|---|
| E1 | N1, N2, N3, N4 | N1, N3, N2, N4 |
| E2 | N1, N3, N2, N4 | N1, N2, N3, N4 |

Gleiche vier Inhalte, Haeufigkeiten und Folgenlaenge; gleicher Anfang N1 und
Abschluss N4. Nur die beiden Mittelpositionen sind vertauscht. Technisches
Zeitraster und Reihenfolge bleiben wie vorregistriert: ein Frame-Tick pro Bild,
Bildung bei 0 bis 3; die sechs Vier-Bild-Proben beginnen bei 4, 8, 12, 16,
20 und 24. Keine reale Laufzeit wird zur Abrufinformation.

Je Episode: Original 0, Gegenfolge 0, Original -8, Gegenfolge -8,
Original +8, Gegenfolge +8. Der Offset gilt innerhalb einer Folge global und
einheitlich. Kein Clipping, lokales Rauschen, variables Tempo oder Wechsel des
Offsets innerhalb einer Folge.

Unveraendert bleiben:

- B4-Kern und Indexableitung `prestate.accepted_count + 1`;
- vier tatsaechliche fortgesetzte Bildungen je Episode;
- `probe_visual_sequence_read_only` und eine gemeinsame 4-x-4-Abstandstabelle;
- GEORDNET mit ausschliesslich gespeicherten Bildungsindizes;
- REIHENFOLGEBLIND ohne Index-, Slot-, Zeit- oder Versuchskennung;
- auditive Schwelle 0.2 und visuelle L1-KAL-Schwelle exakt `44/765`;
- eindeutige Eins-zu-eins-Inhaltszuordnung, read-only Bank und Rueckgabe
  gespeicherter Originalwerte nur bei geordneter Annahme;
- Erfolgskriterien: GEORDNET sechs richtige Annahmen und sechs richtige
  Abweisungen; REIHENFOLGEBLIND zwoelf diagnostische Inhaltsannahmen.

Die deskriptiven Entscheidungen aus `sequence-20260829-01` duerfen weder
Schwelle, Regeln, Bilder, erwartete Klassen noch Kosten veraendern. Der neue
Lauf prueft dieselbe Funktion mit neuen Eingaben; er repariert den alten nicht.

## 3. Fokussierte Validatorpruefung vor dem Hauptlauf

Der korrigierte Verweis `spatial.empty_payload()` ist noch nicht dynamisch
qualifiziert. Vor einer neuen Hauptausfuehrung ist **genau ein neuer kleiner
Korrekturtest** vorgesehen. Die alten acht Tests werden nicht wiederholt.

Der Test verwendet ein temporaeres, eigenes Verzeichnis und keine N1-N4-Bilder.
Er fuehrt keinen Rezeptor, B4-Uebergang, Folgenpruefer, alten Runner oder
Matrixpfad aus. Er prueft den tatsaechlichen Abschlussweg:

1. die vom Record-Inspector verwendete Initialzustandsfunktion ruft
   `spatial.empty_payload()` auf und liefert die vollstaendige leere
   Neun-Platz-Form;
2. ein minimales versiegeltes Start-/Ergebnis-Ereignispaar wird vollstaendig
   geschrieben und als verkettetes Journal gelesen;
3. ein kleines Manifest und ein Ergebnis mit Journalhash werden neu angelegt;
4. `result.json` und das daran gebundene `terminal.json` werden ueber denselben
   lokalen atomaren Publikationshelfer veroeffentlicht;
5. ein separater read-only Mini-Validator prueft Formen, Digests, Hash,
   Exit-Code 0 und terminales `OK` und liefert `COMPLETE`;
6. fehlender Abschluss, falscher Digest oder Wiederverwendung des Verzeichnisses
   muss fail-closed stoppen.

Dazu darf der Inspector nur so refaktoriert werden, dass die korrigierte
Initialzustandsfunktion von Hauptinspektion und Mini-Test gemeinsam verwendet
wird. Die fachliche Folgenfunktion, Schwellen, Vergleichsregeln und B4 bleiben
unveraendert. Der kleine Test ist ein Infrastrukturbeleg, kein Sequenzbefund.

Vorgesehene Qualifikations-ID:
`sequence-confirmation-validator-20260829-01`. Nur ein vollstaendig
gespeicherter Test mit Exit-Code 0 und `COMPLETE` oeffnet die bedingte
Hauptfreigabe. Bei Testfehler oder unvollstaendiger Aufzeichnung bleibt die
Hauptausfuehrung geschlossen; keine automatische Testwiederholung.

## 4. Neue Einmalgrenze und Hauptumfang

Vorgesehene neue Lauf-ID: `sequence-confirmation-20260829-01`.
Vor dem ersten Bild werden Quellen, korrigierter Code, Runtime, Plan,
Autorisation, Auswahlregel, vier Bilder, Folgen, Schwellen, Budgets,
Validatorbeleg und erwartete Dateiformen byte- und digestgebunden.

Hauptumfang bleibt exakt:

- **56 Bildanalysen**: acht Bildungsbilder und 48 Probebilder;
- **acht B4-Bildungen** aus frischen Banken;
- **zwoelf Folgeproben**;
- **24 read-only Sichtentscheidungen**;
- 152 verkettete Start-/Ergebnisereignisse;
- 232 funktionale Schreibwoerter;
- 4992 funktionale und 4992 live validierende L1-Terme;
- neun Plaetze, vier belegt, maximal 255 logische Bankwoerter;
- je Folgeprobe dieselbe einmal berechnete Abstandstabelle fuer beide Sichten.

Das neue Laufverzeichnis muss vor Start fehlen. Seine exklusive Erzeugung
verbraucht die Einmalfreigabe auch bei Fehlern. Vollstaendige Ereignisse,
`result.json`, `terminal.json`, Exit-Code 0 und eine anschliessende reine
Belegpruefung sind fuer einen auswertbaren Lauf notwendig. Fachlich falsche
Abrufe bleiben Ergebnisse; Quellen-, Index-, Eindeutigkeits- oder
Aufzeichnungsfehler ergeben `NOT_EVALUABLE`. Keine Wiederholung,
Teilfortsetzung, nachtraegliche Publikation oder Parameteranpassung.

Die reine Belegpruefung darf keine Rezeptor-, Bildungs-, Abruf- oder
Matrixfunktion aufrufen. Nach Abschluss wird der neue Einstieg gesperrt.
Der alte Fehlversuch behaelt `failure.json` und `diagnostic.json`; dort werden
keine `result.json` oder `terminal.json` angelegt.

## 5. Aussagegrenze und Abschluss

Bei regulaerem Erfolg waeren getrennt zu berichten:

1. korrekte Rezeptorfolge und Tickordnung;
2. erhaltene Werte und Bildungsindizes 1 bis 4 in B4;
3. geordnete Annahme beziehungsweise Abweisung bei 0 und +/-8;
4. diagnostische Inhaltsgleichsetzung durch REIHENFOLGEBLIND;
5. Rueckgabewerte, Bankunveraendertheit, Paarabstaende und Kosten.

Ein Erfolg waere ein begrenzter technischer Kurzzeit-Sequenzabruf durch
explizite Bildungsreihenfolge. Er waere kein selbststaendiges Segmentieren,
Episoden- oder Sequenzlernen, keine Vorhersage, Tempo-Invarianz,
Langzeitverdichtung, Semantik oder MCM-Feldwirkung.

Die Refaktorierung, genau ein Korrekturtest und die danach separat freigegebene
Einmalausfuehrung sind abgeschlossen. Der zugehoerige
[Befund](../reports/tspm1_functional/sequence-confirmation-20260829-01/BEFUND.md)
bleibt auf den begrenzten technischen Kurzzeit-Sequenzabruf beschraenkt.
B4, Einzelbildabruf, TSPM-1, PPB-1, API, Snapshot und Feldpfad blieben
unveraendert. Der Lauf-Gate ist wieder gesperrt; keine Wiederholung.
