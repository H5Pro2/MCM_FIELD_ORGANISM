# Pruefplan: Erhaltung unter Zwischenreizen und Kapazitaetsdruck

**Status: statischer Aufgaben- und Pruefplan mit privaten Fixtures,
read-only Inhaltsadaptern und acht bestandenen fokussierten Adaptertests. Kein
Runner und keine Hauptausfuehrung.**
Grundlage sind der bestaetigte
[Kurzzeit-Sequenzbefund](../reports/tspm1_functional/sequence-confirmation-20260829-01/BEFUND.md),
der unveraenderte B4-Kern und die private TSPM-1-/PPB-1-Architektur.

## 1. Getrennte Fragen

Der Versuch darf zwei Funktionen nicht zusammenwerten:

1. **Inhaltserhaltung:** Ist ein einzelner Zielzustand nach Zwischenreizen
   read-only abrufbar? Bei TSPM-1 werden Fast-Slot und Slow-PPB-1 getrennt
   ausgewiesen. Ein Slow-Abruf darf einen Fast-Verlust nicht verdecken.
2. **Folgenerhaltung:** Laesst sich die urspruengliche Reihenfolge allein aus
   den gespeicherten Zustandsfeldern rekonstruieren? Labels, Laufplan,
   Sollfolge, Ereignisjournal und Digestketten sind keine Abrufquellen.

Ein Inhaltsabruf ist kein Folgenabruf. Umgekehrt darf fehlende Folgenordnung
nicht als Scheitern der Inhalts-Memory ausgelegt werden.

## 2. Vorgelagerte Repraesentierbarkeitspruefung

### B4

B4 besitzt neun FIFO-Eintraege. Jeder belegte Eintrag traegt Werte und einen
tatsaechlich beim Zustandsuebergang geschriebenen `formation_index`. Solange
alle vier verschiedenen Zielwerte N1 bis N4 vorhanden sind, darf ein privater
read-only Folgenpruefer sie anhand dieser Indizes ordnen. Fehlt ein Zielwert
oder existiert keine eindeutige Eins-zu-eins-Zuordnung, lautet der Befund
`ORDER_UNAVAILABLE_MISSING_OR_AMBIGUOUS_CONTENT` und nicht geraten.

### TSPM-1

Die bestehende Konfiguration bleibt unveraendert:

Technische Quellen sind
[`_tspm1_s2dr_private_comparison.py`](../mcm_field_organism/_tspm1_s2dr_private_comparison.py),
[`_tspm1_private.py`](../mcm_field_organism/_tspm1_private.py) und
[`_ppb1_reference.py`](../mcm_field_organism/_ppb1_reference.py).

- Fast: drei gemeinsame AV-Slots, Matchschwellen 0,2/0,2,
  Aktualisierungsfaktor 0,5, Konsolidierung ab Support 2 und Ablauf nach acht
  Expositionen ohne Auswahl;
- Slow: PPB-1 auditiv mit Kapazitaet 8, Schwelle 0,02 und Ablauf 256;
  visuell mit Kapazitaet 4, Schwelle 0,01 und Ablauf 64; Stabilisierung jeweils
  ab Support 3;
- Fast-Slots tragen Werte, Support, `last_selected_step` und
  Konsolidierungszaehler. Slow-Slots tragen Prototyp, Support und den letzten
  PPB-Selektionsschritt. Die beiden Modalitaeten sind getrennte Banken.

Das reicht fuer aktuelle Inhalte und begrenzte Aktualitaetsordnung, aber nicht
fuer eine vollstaendige beliebige Viererfolge: Fast kann hoechstens drei
verschiedene AV-Inhalte gleichzeitig halten; Slow speichert nur die letzte
Auswahl eines Prototyps und die Konsolidierungsreihenfolge, nicht alle
urspruenglichen Expositionen. Generation, Parent-, State-, Receipt- und
Expositionsdigests sind nicht invertierbare Identitaetsbelege und duerfen
nicht als Folgenhistorie dekodiert oder als Klassifikationsschluessel benutzt
werden. Globale letzte Ticks sind keine Zeitmarken je Inhalt.

Damit nimmt TSPM-1 in diesem Plan vollstaendig am Inhaltsvergleich teil. Fuer
die Viererfolge wird statisch `NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE`
protokolliert; es wird kein Folgenoperator aufgerufen. Eine spaetere neue
Reihenfolgekoordinate oder ein Uebergangstraeger ist nicht Bestandteil dieses
Plans.

## 3. Gemeinsame Wahrnehmungswerte

Auditiv erhalten alle Expositionen unveraendert acht Nullwerte. Visuell werden
dieselben 3-x-2-Zellbilder wie im bestaetigten Sequenzlauf verwendet:

| ID | H-Positionen | Sechs Zellwerte |
| --- | --- | --- |
| N1 | 013 | 200, 200, 40, 200, 40, 40 |
| N2 | 014 | 200, 200, 40, 40, 200, 40 |
| N3 | 015 | 200, 200, 40, 40, 40, 200 |
| N4 | 023 | 200, 40, 200, 200, 40, 40 |
| D1 | 024 | 200, 40, 200, 40, 200, 40 |
| D2 | 025 | 200, 40, 200, 40, 40, 200 |
| D3 | 034 | 200, 40, 40, 200, 200, 40 |
| D4 | 035 | 200, 40, 40, 200, 40, 200 |
| D5 | 123 | 40, 200, 200, 200, 40, 40 |
| D6 | 124 | 40, 200, 200, 40, 200, 40 |
| D7 | 125 | 40, 200, 200, 40, 40, 200 |

Alle Bilder haben dieselbe Gesamthelligkeit und dasselbe Histogramm. Je zwei
verschiedene Masken unterscheiden sich in mindestens zwei Zellen; ihr
kleinster visueller Abstand ist `160/765` und liegt ueber `44/765`.

`44/765` bleibt die gemeinsame, technisch vorgegebene funktionale
Auswertungsschwelle fuer gespeicherte visuelle Werte. Sie ersetzt nicht die
internen, bereits gebundenen TSPM-1-/PPB-1-Matchschwellen; deren native
Entscheidungen werden unveraendert und separat berichtet. Eine Abweichung
zwischen nativer Auswahl und gemeinsamer Funktionsauswertung ist ein Ergebnis.

Jede Exposition verwendet einen fortlaufenden Ein-Tick-Zeitraum. Beide Arme
erhalten bytegleich dieselben Rezeptorwerte, Ticks und Probevektoren. Die IDs
N1 bis D7 existieren nur im Versuchsplan und Recorder; kein Speicher- oder
Abrufoperator erhaelt sie.

## 4. Sechs begrenzte Geschichten

Jede Arm-/Geschichts-Zelle beginnt aus einem frischen Zustand. Es gibt zwei
Arme (`B4`, `TSPM1`) und sechs Geschichten, insgesamt zwoelf unabhaengige Zellen.

Eine passende TSPM-1-Exposition ruft PPB-1 nicht beim ersten Fast-Eintrag auf.
Die zweite passende Exposition erzeugt den Slow-Prototyp mit Support 1, die
dritte erhoeht ihn auf 2 und die vierte auf 3. Erst Support 3 ist fuer die
vorhandene S1-WU-Probe zulaessig. Die folgenden Tabellen binden die kumulative
PPB-Aufrufzahl **je Modalitaet**; jeder Konsolidierungsschritt ruft auditiv und
visuell genau einmal auf.

### U und V: unverdichtet gegen verdichtet

- U: `N1, N1, D1, D2, D3, D4`
- V: `N1, N1, N1, N1, D1, D2, D3, D4`

U und V unterscheiden sich nur durch zwei zusaetzliche N1-Bestaetigungen vor
dem identischen Druck D1-D4. N1 wird in U nach Schritt 2, 4, 5 und 6, in V
nach Schritt 4, 6, 7 und 8 read-only geprobt.

| Geschichte/Schritt | Input | N1 im Fast-Slot | PPB-Aufrufe kumulativ | N1-Slow-Support | stabil | Slow-Ersetzung | gebundenes Ereignis |
| --- | --- | --- | ---: | ---: | --- | --- | --- |
| U1 | N1 | ja | 0 | 0 | nein | nein | `FAST_CREATED` |
| U2 | N1 | ja | 1 | 1 | nein | nein | `FAST_UPDATED`, erster PPB-Create |
| U3 | D1 | ja | 1 | 1 | nein | nein | `FAST_CREATED` |
| U4 | D2 | ja | 1 | 1 | nein | nein | `FAST_CREATED`, Fast voll |
| U5 | D3 | nein | 1 | 1 | nein | nein | `FAST_REPLACED`, N1 verloren |
| U6 | D4 | nein | 1 | 1 | nein | nein | weitere Fast-Ersetzung |
| V1 | N1 | ja | 0 | 0 | nein | nein | `FAST_CREATED` |
| V2 | N1 | ja | 1 | 1 | nein | nein | `FAST_UPDATED`, erster PPB-Create |
| V3 | N1 | ja | 2 | 2 | nein | nein | `FAST_UPDATED`, PPB-Match |
| V4 | N1 | ja | 3 | 3 | ja | nein | `FAST_UPDATED`, PPB stabil |
| V5 | D1 | ja | 3 | 3 | ja | nein | `FAST_CREATED` |
| V6 | D2 | ja | 3 | 3 | ja | nein | `FAST_CREATED`, Fast voll |
| V7 | D3 | nein | 3 | 3 | ja | nein | `FAST_REPLACED`, N1 verloren |
| V8 | D4 | nein | 3 | 3 | ja | nein | weitere Fast-Ersetzung |

Gebundene Gegenprognose nach Fast-Verlust: U darf keinen stabilisierten
Slow-N1-Abruf liefern; V soll N1 aus beiden stabilen PPB-1-Modalitaeten liefern.
Ein anderer Befund bleibt ein Ergebnis und wird nicht durch die Tabelle ersetzt.
B4 erhaelt dieselben Geschichten und dient als unveraenderte FIFO-Referenz.

### C: stabilisierter Slow-Inhalt unter Kapazitaetsdruck

`N1 x4, N2 x4, N3 x4, N4 x4, D1 x4, D2 x4`

N1 bis N4 werden vor dem ersten Distraktor jeweils durch vier tatsaechliche
Expositionen stabilisiert. Erst danach erzeugen D1 und D2 Slow-Druck. Die
visuelle PPB-Bank besitzt Kapazitaet 4. Die auditive Bank sieht stets Nullwerte;
ihr gemeinsamer Prototyp ist ab dem dritten PPB-Aufruf stabil.

| Schritt | Input | Fast-Ereignis / Fast-Verlust | PPB-Aufrufe kumulativ | visueller PPB-Schritt | stabiler visueller Slow-Bestand | Slow-Ersetzung |
| ---: | --- | --- | ---: | --- | --- | --- |
| 1 | N1 | `FAST_CREATED` | 0 | keiner | - | nein |
| 2 | N1 | `FAST_UPDATED` | 1 | N1 Create, Support 1 | - | nein |
| 3 | N1 | `FAST_UPDATED` | 2 | N1 Match, Support 2 | - | nein |
| 4 | N1 | `FAST_UPDATED` | 3 | N1 Match, Support 3 | N1 | nein |
| 5 | N2 | `FAST_CREATED` | 3 | keiner | N1 | nein |
| 6 | N2 | `FAST_UPDATED` | 4 | N2 Create, Support 1 | N1 | nein |
| 7 | N2 | `FAST_UPDATED` | 5 | N2 Match, Support 2 | N1 | nein |
| 8 | N2 | `FAST_UPDATED` | 6 | N2 Match, Support 3 | N1,N2 | nein |
| 9 | N3 | `FAST_CREATED` | 6 | keiner | N1,N2 | nein |
| 10 | N3 | `FAST_UPDATED` | 7 | N3 Create, Support 1 | N1,N2 | nein |
| 11 | N3 | `FAST_UPDATED` | 8 | N3 Match, Support 2 | N1,N2 | nein |
| 12 | N3 | N1 `FAST_EXPIRED`; N3 `FAST_UPDATED` | 9 | N3 Match, Support 3 | N1,N2,N3 | nein |
| 13 | N4 | `FAST_CREATED` im freien Slot | 9 | keiner | N1,N2,N3 | nein |
| 14 | N4 | `FAST_UPDATED` | 10 | N4 Create, Support 1 | N1,N2,N3 | nein |
| 15 | N4 | `FAST_UPDATED` | 11 | N4 Match, Support 2 | N1,N2,N3 | nein |
| 16 | N4 | N2 `FAST_EXPIRED`; N4 `FAST_UPDATED` | 12 | N4 Match, Support 3 | N1,N2,N3,N4 | nein |
| 17 | D1 | `FAST_CREATED` im freien Slot | 12 | keiner | N1,N2,N3,N4 | nein |
| 18 | D1 | `FAST_UPDATED` | 13 | D1 Create, Support 1 | N2,N3,N4 | ja: N1 |
| 19 | D1 | `FAST_UPDATED` | 14 | D1 Match, Support 2 | N2,N3,N4 | nein |
| 20 | D1 | N3 `FAST_EXPIRED`; D1 `FAST_UPDATED` | 15 | D1 Match, Support 3 | N2,N3,N4,D1 | nein |
| 21 | D2 | `FAST_CREATED` im freien Slot | 15 | keiner | N2,N3,N4,D1 | nein |
| 22 | D2 | `FAST_UPDATED` | 16 | D2 Create, Support 1 | N3,N4,D1 | ja: N2 |
| 23 | D2 | `FAST_UPDATED` | 17 | D2 Match, Support 2 | N3,N4,D1 | nein |
| 24 | D2 | N4 `FAST_EXPIRED`; D2 `FAST_UPDATED` | 18 | D2 Match, Support 3 | N3,N4,D1,D2 | nein |

Nach Schritt 16, 17, 18, 20, 21, 22 und 24 werden N1 bis N4 sowie D1 und D2
read-only geprobt. Damit liegen Proben vor, unmittelbar vor, an und nach beiden
Slow-Ersetzungen. Der Fast-Verlust in C entsteht bei den Schritten 12, 16, 20
und 24 durch Ablauf; die Schritte 13, 17 und 21 belegen danach jeweils einen
freien Slot mit `FAST_CREATED`. Die visuelle Slow-Ersetzung bleibt davon
unabhaengig: N1 wird beim ersten D1-PPB-Schritt 18 und N2 beim ersten
D2-PPB-Schritt 22 ersetzt. Fast, auditives Slow und visuelles Slow bleiben
getrennt.

### A: Fast-Ablauf ohne vorherige Kapazitaetsersetzung

`N1 x4, D1 x2, D2 x2, D1, D2, D1, D2, D1`

Neben N1 existieren nur D1 und D2. Damit bleiben alle drei Fast-Slots belegt,
ohne N1 durch einen vierten Inhalt zu ersetzen. N1 wird nach Schritt 11, 12
und 13 read-only geprobt.

| Schritt | Input | N1 im Fast-Slot | PPB-Aufrufe kumulativ | relevanter Slow-Stand | Slow-Ersetzung | gebundenes Ereignis |
| ---: | --- | --- | ---: | --- | --- | --- |
| 1 | N1 | ja | 0 | N1 absent | nein | `FAST_CREATED` |
| 2 | N1 | ja | 1 | N1 Support 1 | nein | `FAST_UPDATED` |
| 3 | N1 | ja | 2 | N1 Support 2 | nein | `FAST_UPDATED` |
| 4 | N1 | ja | 3 | N1 Support 3, stabil | nein | `FAST_UPDATED` |
| 5 | D1 | ja | 3 | N1 stabil | nein | `FAST_CREATED` |
| 6 | D1 | ja | 4 | D1 Support 1 | nein | `FAST_UPDATED` |
| 7 | D2 | ja | 4 | D2 absent | nein | `FAST_CREATED`, Fast voll |
| 8 | D2 | ja | 5 | D2 Support 1 | nein | `FAST_UPDATED` |
| 9 | D1 | ja | 6 | D1 Support 2 | nein | `FAST_UPDATED` |
| 10 | D2 | ja | 7 | D2 Support 2 | nein | `FAST_UPDATED` |
| 11 | D1 | ja | 8 | D1 Support 3, stabil | nein | `FAST_UPDATED` |
| 12 | D2 | nein | 9 | D2 Support 3, N1 weiter stabil | nein | N1 `FAST_EXPIRED` vor Update |
| 13 | D1 | nein | 10 | N1 weiter stabil | nein | `FAST_UPDATED` nach Ablauf |

N1s `last_selected_step` bleibt 4; vor Schritt 12 gilt `12 - 4 = 8` und damit
die unveraenderte Fast-Ablaufgrenze. B4 verdraengt bei Schritt 10 bis 13
nacheinander die vier N1-Eintraege; der letzte geht erst bei Schritt 13
verloren. Ablauf, FIFO-Verdraengung und Slow-Erhaltung bleiben dadurch
unterscheidbar.

### S1 und S2: Folgenordnung unter FIFO-Druck

- S1: `N1, N2, N3, N4, D1, D2, D3, D4, D5, D6, D7`
- S2: `N1, N3, N2, N4, D1, D2, D3, D4, D5, D6, D7`

Diese Geschichten bleiben unveraendert. Nach Schritt 4, 9, 10 und 11 werden
N1 bis N4 einzeln geprobt und die Folgenrepraesentierbarkeit bewertet. Schritt
9 ist B4 voll ohne Verdraengung, Schritt 10 die erste und Schritt 11 die zweite
FIFO-Verdraengung. S1 und S2 haben gleiche Inhalte, Laenge, Ticks,
Distraktoren, Anfang und Abschluss; nur N2/N3 sind vertauscht.

| Schritt | S1/S2-Input | TSPM-1-Fast-Ereignis | Fast-Verlust | PPB-Aufrufe | Slow-Support/Stabilitaet/Ersetzung |
| ---: | --- | --- | --- | ---: | --- |
| 1 | N1 / N1 | `FAST_CREATED` | - | 0 | keiner |
| 2 | N2 / N3 | `FAST_CREATED` | - | 0 | keiner |
| 3 | N3 / N2 | `FAST_CREATED` | - | 0 | keiner |
| 4 | N4 / N4 | `FAST_REPLACED` | N1 | 0 | keiner |
| 5 | D1 / D1 | `FAST_REPLACED` | N2 / N3 | 0 | keiner |
| 6 | D2 / D2 | `FAST_REPLACED` | N3 / N2 | 0 | keiner |
| 7 | D3 / D3 | `FAST_REPLACED` | N4 | 0 | keiner |
| 8 | D4 / D4 | `FAST_REPLACED` | D1 | 0 | keiner |
| 9 | D5 / D5 | `FAST_REPLACED` | D2 | 0 | keiner |
| 10 | D6 / D6 | `FAST_REPLACED` | D3 | 0 | keiner |
| 11 | D7 / D7 | `FAST_REPLACED` | D4 | 0 | keiner |

Alle visuellen Inhalte sind nativ ausserhalb der Fast-Matchschwelle. Deshalb
gibt es in S1/S2 keinen PPB-Aufruf und keinen Slow-Prototyp. B4 darf fuer die
Folgenentscheidung ausschliesslich aktuell gespeicherte Werte und
`formation_index` nutzen. TSPM-1 erhaelt dieselben Geschichten und
Inhaltsproben, aber gemaess Abschnitt 2 keinen kuenstlichen Folgenpruefer.

## 5. Read-only Proben und Auswertung

Alle Proben muessen Vor- und Nachzustandsdigest als identisch nachweisen.
Aufgezeichnet werden je Ziel und Checkpoint:

- gemeinsame L1-Entscheidung mit exakt `44/765`;
- tatsaechlich zurueckgegebene Werte und Abweichung zum Ziel;
- B4-Slot und `formation_index` oder `ABSENT`;
- TSPM-1-Fast-Status, Slot, Distanzen und Werte;
- TSPM-1-Slow-Status getrennt fuer auditiv und visuell, PPB-Slots,
  Distanzen, Prototypwerte und Stabilitaetsstatus;
- zusammengesetzter nativer TSPM-1-Kontext, ohne dass dieser die getrennten
  Fast-/Slow-Ergebnisse ersetzt.

Inhaltsklassen: `FAST_ONLY`, `SLOW_ONLY`, `FAST_AND_SLOW`, `B4_PRESENT`,
`ABSENT`, `WRONG_RETURN` und `NATIVE_FUNCTIONAL_DISAGREEMENT`.

Folgenklassen: `ORDER_RECONSTRUCTED`,
`ORDER_UNAVAILABLE_MISSING_OR_AMBIGUOUS_CONTENT` und
`NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE`. Eine Ergebnis-Solltabelle darf
nur nach dem read-only Befund auswerten; sie ist keine Eingabe.

## 6. Ereignisse, Ressourcen und Fairness

Vollstaendig zu erfassen sind:

- B4 `APPENDED` und `EVICTED_AND_APPENDED`;
- TSPM-1 `FAST_CREATED`, `FAST_UPDATED`, `FAST_REPLACED`, abgelaufene und
  ersetzte Slotdigests;
- Konsolidierungsberechtigung, -status und atomarer PPB-1-Abschluss;
- auditive und visuelle PPB-1-Ereignisse `CREATED`, `MATCHED`, `REPLACED`
  sowie Ablauf;
- Vor-/Nachzustaende, Owner, Quellen, Ticks, Receipts und native Kosten.

Beide Arme erhalten dieselben oberen Grenzen; ungenutztes Budget wird nicht
als Vorteil umgedeutet:

- maximal 269 logische 64-Bit-Woerter Zustand;
- maximal 293 funktionale Schreibwoerter und 234 L1-Terme je Exposition;
- maximal 234 L1-Terme und null Schreibwoerter je Inhaltsprobe;
- fuer einen zulaessigen Vierer-Folgenvergleich maximal 416 funktionale plus
  416 unabhaengig validierende L1-Terme und null Schreibwoerter.

Native Verbraeuche bleiben zusaetzlich sichtbar: insbesondere B4 maximal 255
logische Woerter und 27 Schreibwoerter je Bildung gegen TSPM-1 maximal 269
logische Woerter und 293 Schreibwoerter je Bildung. Recorder-, Hash- und
Sollauswertungsarbeit wird separat berichtet und keinem Arm als Speicher
zugerechnet.

Der korrigierte statische Gesamtumfang ist:

- sechs Geschichten mal zwei Arme: zwoelf frische Arm-/Geschichts-Zellen;
- 73 Expositionen je Arm, insgesamt **146 Expositionen**;
- U/V: 16 N1-Inhaltsproben ueber beide Arme;
- C: 84 Inhaltsproben auf N1-N4/D1/D2 ueber beide Arme;
- A: 6 N1-Inhaltsproben ueber beide Arme;
- S1/S2: 64 Inhaltsproben ueber beide Arme;
- insgesamt **170 exakte read-only Inhaltsproben**;
- 16 Folgenrepraesentierbarkeitsbefunde. Bei TSPM-1 sind acht davon reine
  statische Statusausgaben ohne Folgenoperator;
- 32 TSPM-1-PPB-Aufrufe je Modalitaet: U 1, V 3, C 18, A 10,
  S1/S2 0; insgesamt 64 modale PPB-Aufrufe.

Bei einer spaeteren Aufzeichnung mit je einem Start-/Ergebnispaar fuer
Bildanalyse und Zustandsoperation ergeben sich vorab **316 Bildanalysen** und
**1296 verkettete Ereignisse**: 146 Expositionen mal vier, 170 Inhaltsproben
mal vier und 16 Folgenstatus mal zwei. Diese Ereignisform darf vor einer
Implementierung nicht erweitert oder zusammengezogen werden, ohne die
Gesamtzahl neu zu binden. Ein Folgenstatus verwendet die vier bereits am
selben Checkpoint gebundenen Probevektoren und loest keine weitere
Bildanalyse aus.

Gemeinsame Maximalbudgets und native Kosten werden getrennt summiert:

- oberes Schreibbudget: 146 mal 293 = 42778 funktionale Schreibwoerter;
- nativer Bildungsverbrauch: B4 73 mal 27 = 1971 und TSPM-1 maximal
  73 mal 293 = 21389, zusammen maximal 23360 Schreibwoerter;
- oberes Inhaltsprobenbudget: 170 mal 234 = 39780 L1-Terme, null
  Probeschreibwoerter;
- oberes Folgenbudget: 16 mal 416 = 6656 funktionale plus 6656 unabhaengig
  validierende L1-Terme. Nur acht B4-Befunde duerfen diese Rechnung nativ
  nutzen; die acht TSPM-1-Statusbefunde verbrauchen null Folgen-L1-Terme.

Keine Intensitaets-, Rausch- oder Tempovariation wird gleichzeitig untersucht.

## 7. Entscheidungsregeln und Grenzen

Der spaetere Bericht beantwortet getrennt:

1. Unterscheiden sich U und V nach Fast-Verlust genau durch fehlende gegen
   stabilisierte Slow-Erhaltung?
2. Wie lange bleiben N1 bis N4 in B4 erhalten?
3. Wann verliert TSPM-1 einen Inhalt im Fast-Bereich, und bleibt er im
   Slow-Bereich abrufbar?
4. Welche nativen Ablauf-, Konsolidierungs- und Verdraengungsereignisse
   erklaeren den jeweiligen Befund?
5. Bis zu welchem FIFO-Druck kann B4 die gespeicherte Viererfolge aus seinen
   eigenen Eintraegen rekonstruieren?
6. Bleibt TSPM-1 auf Inhaltserhaltung begrenzt, ohne dass daraus ein
   negativer Gesamtbefund abgeleitet wird?

Ein Zwei-Zeitskalen-Vorteil liegt nur vor, wenn ein Ziel nach belegtem
Fast-Verlust aus Slow korrekt read-only abrufbar bleibt. B4-Folgenerfolg gilt
nur, wenn alle Inhalte und ihre gespeicherten Indizes vorhanden sind. Native
Komplexitaet, Digests oder Konsolidierungsflags sind allein kein Erfolg.

Technische oder methodische Verletzungen ergeben `NOT_EVALUABLE`. Fachlich
falsche, fehlende oder widerspruechliche Abrufe bleiben Ergebnisse. Keine
automatische Wiederholung, Teilfortsetzung oder Parameteranpassung.

Der Plan fuegt keine neue Reihenfolgekoordinate, keinen Uebergangstraeger und
keine externe Historie hinzu. Er prueft keine Semantik, Episodenbildung,
Langzeitverdichtung oder MCM-Feldwirkung. Erst nach einem spaeteren Befund
waere getrennt zu entscheiden, ob ein begrenzter Wahrnehmungsuebergangs- oder
Folgentraeger als neue Engineeringfunktion begruendet ist.

## 8. Freigabegrenze

Umgesetzt sind ausschliesslich die privaten
[`_retention_capacity_fixtures.py`](../tools/_retention_capacity_fixtures.py)
und
[`_retention_capacity_read_only.py`](../tools/_retention_capacity_read_only.py).
Die Fixtures binden die sechs Geschichten, Werte, Ticks, Checkpoints, Budgets
und erwarteten Ereignisorte als Pruefmetadaten. Der Adapter liest B4 nur aus
belegten Slots, Werten und `formation_index`; fuer TSPM-1 besitzt er genau eine
native read-only Probestelle und inspiziert danach nur den bereits validierten,
unveraenderten Zustand. Fast, auditives Slow, visuelles Slow, native Schwellen
und die gemeinsame Funktionsschwelle `44/765` bleiben getrennt.

Die statische Codepruefung bestaetigt ASCII-Syntax, eng begrenzte Importe,
genau eine native TSPM-1-Probestelle sowie null Advance-, Datei-, Runner- oder
Veroeffentlichungsaufrufe im Adapter. `_values` akzeptiert nur exakte numerische
Tupel ohne Bool oder String; B4 verlangt genau `min(accepted_count, 9)` belegte
Slots und das vollstaendige aktuelle FIFO-Indexfenster.

Genau acht fokussierte Tests mit neutralen synthetischen Skalaren wurden einmal
mit `python -m unittest -v tests.test_retention_capacity_private_adapters`
ausgefuehrt: `8/8`, Exit-Code 0, terminal `OK`. Ein vorheriger Pytest-Aufruf
endete wegen des nicht installierten Pakets vor Sammlung und fuehrte null Tests
aus. Nicht freigegeben sind weitere Tests, Runner, Ergebnisablage oder die
`146/170/16`-Hauptausfuehrung. B4, TSPM-1, PPB-1, API, Snapshot und Feldpfad
bleiben unveraendert. Alte Lauf- und Matrixeinstiege bleiben gesperrt.
