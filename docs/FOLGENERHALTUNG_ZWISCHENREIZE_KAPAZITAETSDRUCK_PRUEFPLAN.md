# Pruefplan: Erhaltung unter Zwischenreizen und Kapazitaetsdruck

**Status: statischer Aufgaben- und Pruefplan. Keine Implementierung und keine
Ausfuehrung.** Grundlage sind der bestaetigte
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

## 4. Vier begrenzte Geschichten

Jede Arm-/Geschichts-Zelle beginnt aus einem frischen Zustand. Es gibt zwei
Arme (`B4`, `TSPM1`) und vier Geschichten, insgesamt acht unabhaengige Zellen.

### C: Zwei-Zeitskalen-Inhalt unter Kapazitaetsdruck

`N1, N1, N2, N2, N3, N3, N4, N4, D1, D1, D2, D2`

Read-only Inhaltsproben auf N1 bis N4 nach den Schritten:

| Schritt | gebundene Grenze |
| --- | --- |
| 6 | Fast-Kapazitaet drei gefuellt, noch vor N4 |
| 7 | erste TSPM-1-Fast-Ersetzung durch N4 |
| 8 | nach Fast-Grenze; N4-Konsolidierungsangebot abgeschlossen |
| 9 | B4 exakt voll; TSPM-1-Slow visuell noch mit N1-N4 |
| 10 | erste B4-Verdraengung und erste visuelle Slow-Ersetzung durch D1 |
| 12 | nach der Grenze; D2 konsolidiert und weitere Verdraengung erfolgt |

Die Tabelle bindet erwartete Ereignisorte aus den unveraenderten Kapazitaeten,
nicht erwartete Abruferfolge. Fast- und Slow-Befunde werden je Ziel getrennt.

### A: Ablauf ohne Fast-Kapazitaetsersetzung des Zielslots

`N1, N1, D1, D1, D2, D2, D1, D2, D1, D2, D1`

Nur N1 wird nach Schritt 9, 10 und 11 geprobt. Da neben N1 nur D1 und D2 die
drei Fast-Slots belegen, kann N1 bis zur nativen Acht-Expositions-Ablaufgrenze
nicht durch einen vierten Inhalt ersetzt werden. Schritt 9 liegt davor,
Schritt 10 an der Fast-Ablaufgrenze und Schritt 11 danach. Gleichzeitig liegt
B4 bei Schritt 9 an seiner Kapazitaet, verdraengt bei Schritt 10 die erste und
bei Schritt 11 die zweite N1-Bildung. Der Slow-N1-Befund bleibt separat.

### S1 und S2: Folgenordnung unter FIFO-Druck

- S1: `N1, N2, N3, N4, D1, D2, D3, D4, D5, D6, D7`
- S2: `N1, N3, N2, N4, D1, D2, D3, D4, D5, D6, D7`

Nach Schritt 4, 9, 10 und 11 werden N1 bis N4 einzeln geprobt und die
Folgenrepraesentierbarkeit bewertet. Schritt 9 ist B4 voll ohne Verdraengung,
Schritt 10 die erste und Schritt 11 die zweite FIFO-Verdraengung. S1 und S2
haben gleiche Inhalte, Laenge, Ticks, Distraktoren, Anfang und Abschluss;
nur N2/N3 sind vertauscht.

B4 darf fuer die Folgenentscheidung ausschliesslich aktuell gespeicherte Werte
und `formation_index` nutzen. TSPM-1 erhaelt dieselbe Geschichte und alle
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

Der statische Gesamtumfang ist gebunden auf 90 Expositionen in acht frischen
Arm-/Geschichts-Zellen, 118 exakte read-only Inhaltsproben und 16
Folgenrepraesentierbarkeitsbefunde. Bei TSPM-1 sind diese 16 Befunde reine
statische Statusausgaben ohne Folgenoperator. Keine Intensitaets-, Rausch-
oder Tempovariation wird gleichzeitig untersucht.

## 7. Entscheidungsregeln und Grenzen

Der spaetere Bericht beantwortet getrennt:

1. Wie lange bleiben N1 bis N4 in B4 erhalten?
2. Wann verliert TSPM-1 einen Inhalt im Fast-Bereich, und bleibt er im
   Slow-Bereich abrufbar?
3. Welche nativen Ablauf-, Konsolidierungs- und Verdraengungsereignisse
   erklaeren den jeweiligen Befund?
4. Bis zu welchem FIFO-Druck kann B4 die gespeicherte Viererfolge aus seinen
   eigenen Eintraegen rekonstruieren?
5. Bleibt TSPM-1 auf Inhaltserhaltung begrenzt, ohne dass daraus ein
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

Freigegeben ist nur dieser statische Plan. Nicht freigegeben sind Adapter,
Fixtures, Tests, Zustandsaufrufe, Runner, Dateiablage oder Ausfuehrung. B4,
TSPM-1, PPB-1, API, Snapshot und Feldpfad bleiben unveraendert. Alte Lauf- und
Matrixeinstiege bleiben gesperrt.
