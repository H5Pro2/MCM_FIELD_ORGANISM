# S1-WW: Statischer Bildungs- und Probe-Funktionsvertrag

## Auftrag und Grenze

S1-WW beschreibt erstmals den vollstaendigen privaten technischen Grundpfad
als pruefbare Memory-Funktion:

```text
reduzierte Wahrnehmung
-> begrenzte Zustandsbildung
-> Stabilisierung und Belegbindung
-> eingefrorener Bankzustand
-> kausal spaetere read-only Probe
-> Positiv-/Negativentscheidung ohne Zustandsaenderung
```

Der Vertrag implementiert und startet diesen Ablauf nicht. Feldwirkung,
Semantik, oeffentliche API, Snapshot und Produktion bleiben ausgeschlossen.
Eine technische Memory-Funktion wird pruefbar beschrieben, aber noch nicht
nachgewiesen.

## Bildung und Belegbindung

Audio und Video bleiben getrennte Modalitaeten mit eigenen privaten Banken.
Jede beginnt aus einem gueltigen leeren Zustand und erhaelt exakt
`stable_after` gebundene reduzierte Bildungsexpositionen desselben
Zielmusters oder einer vorab festgelegten engen Variation.

Der terminale Bildungsschritt muss genau einen Zielplatz stabilisieren. Ein
Beleg bindet Bank-, Konfigurations-, Identitaets-, Vor- und
Nachzustandsdigest, Platz- und Prototypdigest, Stuetzung, letztes
Kontaktende und den Digest der Bildungsgeschichte. Rohhistorie und
Prototypwerte gehoeren nicht in den Beleg.

## Eingefrorener Probevorzustand

Jede Probe startet vom exakt gleichen stabilisierten Bankdigest und derselben
Zustandsidentitaet. Rekonstruktion aus einer Zusammenfassung,
Zwischenschritte und vorherige Proben sind unzulaessig. Dadurch koennen
Probeart und Reihenfolge den Zustand nicht veraendern.

## Fuenf Probearten

Der Vertrag bindet pro Modalitaet:

1. exaktes Positiv bei Distanz null;
2. nahes Positiv echt innerhalb der Matchschwelle;
3. Positiv exakt auf der Matchschwelle;
4. nahes Negativ mit vorab gebundener Marge ausserhalb der Schwelle;
5. weiter entferntes Negativ.

Die ersten drei muessen erkannt, die letzten beiden abgewiesen werden. Jede
Probe nutzt ausschliesslich S1-WU, einen kausal spaeteren reduzierten
Rezeptorzustand und den eingefrorenen Bankzustand. Nachzustand, Advance und
Zugriff auf die Bildungshistorie sind verboten.

## Unveraenderlichkeit

Nach jeder Probe muessen Bank- und Identitaetsdigest exakt dem Vorzustand
entsprechen. Schritt, Stuetzung, Auswahlzeit, Prototyp, Stabilisierung,
Ablauf, Ersatz und wiederholte Probeakkumulation bleiben null.

## Gegenbaselines

Neben PPB-1 werden fuenf Baselines gebunden:

- No-Memory mit nur der aktuellen Probe;
- Replay als obere Informationskontrolle mit der vollstaendigen reduzierten
  Bildungsgeschichte;
- eine statische Ein-Prototyp-Bank ohne Lebenszyklus;
- ein begrenzter gleitender beziehungsweise Nachhallzustand;
- Distanz zum letzten reduzierten Bildungsvektor.

Alle vergleichbaren Systeme sehen dieselbe Bildungsgeschichte, denselben
Gap und dieselben Proben. Wo Distanz und Schwelle verwendet werden, sind sie
identisch. Speicherrollen und gespeicherte Skalarwerte muessen offengelegt
werden. Replay wird wegen seines groesseren Informationszugriffs nicht als
gleiches Speicherbudget ausgegeben.

Die minimale statische Matrix enthaelt `2 Modalitaeten mal 6 Systeme mal 5
Probearten = 60` Zellen. Ihre Ausfuehrungszahl bleibt null.

## Entscheidungen

`TECHNICAL_MEMORY_FUNCTION_PASS` verlangt stabilisierte Bildung, drei
korrekte Positiv- und zwei korrekte Negativentscheidungen, deterministische
Digestbefunde, vollstaendige Unveraenderlichkeit und fehlenden Rohhistorien-
oder Advance-Zugriff.

Jede gegenteilige Funktionsbedingung ergibt
`TECHNICAL_MEMORY_FUNCTION_FAIL`.

Erst danach wird getrennt entschieden, ob eine Baseline alle
Funktionsausgaben erklaert. Eine Baselineerklaerung hebt den technischen
Funktionspass nicht auf; sie sperrt lediglich eine besondere Interpretation.
Auch ein nicht erklaerter Engineeringunterschied ist noch kein Nachweis
einer MCM-spezifischen Memory.

Fairness-, Digest-, Informations- oder Matrixfehler haben Vorrang und ergeben
`METHOD_INVALID_STOP_WITHOUT_FUNCTION_DECISION`.

## Reproduzierbare Bindung

Vertragsdigest:

```text
d37006947a0b71be113519b4204b742b9c459a2cdc2e0bb755f4888f0f9143da
```

`12 von 12` statische Vertragstests bestehen. Sie laden nur die
maschinenlesbare Vertragsstruktur; weder Bildung, Probe noch Baseline wird
ausgefuehrt.

## Naechster Schritt

S1-WX ist als rein statischer Vollstaendigkeits-, Fairness- und
Nichtzirkularitaetsaudit des S1-WW-Vertrags vorgesehen. Er muss insbesondere
pruefen, dass Probeerwartungen vorab gebunden, Baselineinformationen fair
getrennt und Funktionspass, Baselineerklaerung und Methodenungueltigkeit
nicht zirkulaer vermischt sind. Noch keine Fixture-, Matrix- oder
Feldausfuehrung.

## Grundlagen

- [S1-WV statischer Probe-Abschlussaudit](S1WV_PPB1_STATISCHER_READ_ONLY_PROBE_ABSCHLUSSAUDIT.md)
- [Maschinenlesbarer S1-WW-Vertrag](S1WW_PPB1_VOLLSTAENDIGER_BILDUNGS_UND_PROBE_FUNKTIONSVERTRAG_V1.json)
