# Vertrag des multimodalen Musterprüfers

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

## 2. Feldfenster

Ein synthetisch oder später real erzeugter Feldzustand trägt:

- Modalität und Feldidentität,
- Feldgeometrie,
- gemeinsame Uhrkennung,
- Beginn und Ende des Zustandsfensters,
- lokale Trägerkennungen,
- Aktivierungs- und Nachhalllage.

Der Prüfer erzeugt diese Feldrollen nicht. Er darf nur die vom Verteiler
erhaltene Konstellation lesen.

## 3. Zeitrelation

- Ein einzelner Feldzustand bildet eine unimodale Konstellation.
- Mehrere zeitlich überlappende Zustände bilden eine gemeinsame Konstellation.
- Nicht überlappende Zustände bleiben als zeitlich getrennt markiert.

Zeitliche Trennung darf nicht als multimodale Gleichzeitigkeit ausgegeben
werden.

## 4. Prüfergebnis

Zulässig sind ausschließlich:

- vorhandene Modalitäten,
- Modalitätsdigests,
- gemeinsame oder getrennte Zeitrelation,
- tatsächliches Überlappungsfenster,
- Anzahl lokaler Träger,
- Digest der vollständigen unveränderten Konstellation.

Nicht zulässig sind Ähnlichkeitsscore, Cluster, Gewinner, Aufmerksamkeit,
Bedeutung, Objekt, Ereignis oder gewünschtes Muster.

## 5. Kernprüfung

```text
gleiche Feldlagen in anderer Reihenfolge
-> gleicher Konstellationsdigest

Änderung nur der auditiven Feldlage
-> nur auditiver Teildigest und Gesamtdigest ändern

Änderung nur der visuellen Feldlage
-> nur visueller Teildigest und Gesamtdigest ändern
```

## 6. Bester nächster Schritt

Der Prüfer wird zunächst mit synthetischen Feldlagen geprüft. Reale
multimodale Evidenz bleibt geschlossen, bis Audio- und Video-In sowie ihre
sensorspezifischen MCM-Felder tatsächlich vorhanden sind.
