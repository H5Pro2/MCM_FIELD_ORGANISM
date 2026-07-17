# Vertrag des multimodalen Musterprüfers

> **Historischer Architekturstand:** Der nachgeschaltete Musterprüfer ist kein
> Bestandteil der aktuellen Runtime. Alle Docks wirken heute direkt in
> [einem gemeinsamen Feld](024_GEMEINSAMES_MCM_FELD_ARCHITEKTUR.md).

## 1. Zweck

Der Musterprüfer beobachtet den Ausgang des modularen MCM-Verteilers. Er prüft,
ob die angedockten sensorspezifischen MCM-Feldlagen als gemeinsame
Konstellation erhalten bleiben:

```text
auditiver MCM-Feldzustand --\
                            -> passive multimodale Konstellation
visueller MCM-Feldzustand --/   MCM-Verteiler -> Musterprüfer
```

Die Konstellation selbst ist das geprüfte Muster. Es wird keine Musterklasse
und keine innere Bezeichnung erzeugt.

## 2. Nachgelagerte Resonanzgrenze

Eine mögliche Resonanz zu Sprache oder gemeinsame innere Bezeichnung darf erst
den Ausgang der multimodalen Feldkonstellation als Ganzes erhalten. Sie gehört
nicht in das auditive, visuelle oder taktile Einzelfeld.

`Multimodal` bedeutet dabei nicht, dass immer mehrere Sinnesfelder anwesend
sein müssen. Eine gültige Konstellation kann auch nur ein vorhandenes Feld
tragen und dennoch später in denselben gemeinsamen Resonanzraum eintreten.

Dieser Resonanzraum ist noch keine aktive Runtime-Komponente. Insbesondere
existieren keine Wortliste, Musterklasse, feste Bezeichnung oder programmierte
Semantik.

## 3. Feldfenster

Ein synthetisch oder später real erzeugter Feldzustand trägt:

- Modalität und Feldidentität,
- Feldgeometrie,
- gemeinsame Uhrkennung,
- Beginn und Ende des Zustandsfensters,
- lokale Trägerkennungen,
- Aktivierungs- und Nachhalllage.

Der Prüfer erzeugt diese Feldrollen nicht. Er darf nur die vom Verteiler
erhaltene Konstellation lesen.

## 4. Zeitrelation

- Ein einzelner Feldzustand bildet eine unimodale Konstellation.
- Mehrere zeitlich überlappende Zustände bilden eine gemeinsame Konstellation.
- Nicht überlappende Zustände bleiben als zeitlich getrennt markiert.

Zeitliche Trennung darf nicht als multimodale Gleichzeitigkeit ausgegeben
werden.

## 5. Prüfergebnis

Zulässig sind ausschließlich:

- vorhandene Modalitäten,
- Modalitätsdigests,
- gemeinsame oder getrennte Zeitrelation,
- tatsächliches Überlappungsfenster,
- Anzahl lokaler Träger,
- Digest der vollständigen unveränderten Konstellation.

Nicht zulässig sind Ähnlichkeitsscore, Cluster, Gewinner, Aufmerksamkeit,
Bedeutung, Objekt, Ereignis oder gewünschtes Muster.

## 6. Kernprüfung

```text
gleiche Feldlagen in anderer Reihenfolge
-> gleicher Konstellationsdigest

Änderung nur der auditiven Feldlage
-> nur auditiver Teildigest und Gesamtdigest ändern

Änderung nur der visuellen Feldlage
-> nur visueller Teildigest und Gesamtdigest ändern
```

## 7. Bester nächster Schritt

Der Prüfer wird zunächst mit synthetischen Feldlagen geprüft. Reale
multimodale Evidenz bleibt geschlossen, bis Audio- und Video-In sowie ihre
sensorspezifischen MCM-Felder tatsächlich vorhanden sind.
