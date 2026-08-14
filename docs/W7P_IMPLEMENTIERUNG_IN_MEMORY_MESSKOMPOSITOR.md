# W7-P: Implementierung des In-Memory-Messkompositors

## Entscheidung

`ROLE_SEPARATED_MEASUREMENT_COMPOSITOR_IMPLEMENTED`

W7-P implementiert den in W7-O gebundenen Messkompositor als isoliertes
Modul. Er fuehrt keinen A/B-Feldpfad aus, startet keine Hauptmatrix und
schreibt weder Browser- noch Forschungsreports.

## Implementierter Umfang

Das Modul
`mcm_field_organism/w7p_measurement_compositor.py` stellt bereit:

- einen unveraenderlichen, an W7-M-Matrix- und Quelldigests gebundenen
  P0-S-Treiber;
- atomare P0-S-Abschlusszustande und linksgehaltene Treibersegmente;
- getrennte Datentypen fuer Feld-, Observer- und CAP-Ressourcenmessungen;
- reine LEAK-/SAT-/NORM-Komposition ueber die vorhandenen W7-N-Kerne;
- dimensionslose Lebenszyklusprofile mit eigenem Modellnenner;
- eine feste Observer-Erklaerungsreihenfolge `LEAK > SAT > NORM`.

Der Treiber nimmt nur bereits berechnete P0-S-Abschlusszustande entgegen.
W7-P leitet diese Zustaende nicht selbst aus Rezeptorereignissen ab und
entwickelt keinen Feldzustand fort. Dadurch bleibt die Komposition von der
noch nicht gestarteten Hauptmatrix getrennt.

## Rollensperren

Die Implementierung erzwingt:

- Feldmessungen nur fuer CAP, P0, LIN, F3, CONST-V, MOB, ETA0, KAPPA0 und
  SIGN;
- Observermessungen nur fuer LEAK, SAT und NORM;
- das Praefix `observer_` fuer alle Observermessrollen;
- M-, Freikapazitaets- und Bilanzrollen ausschliesslich fuer CAP;
- identische Treiberdigests fuer vergleichbare Observerausgaben;
- keine Epsilonersetzung bei einem unaufgeloesten Profilnenner;
- Uebereinstimmung von Modellklasse und Messflaeche.

## Zeitvertrag

P0-S-Abschlusszustande muessen eindeutig und streng zeitlich geordnet sein.
Ein Abschluss am Tick `t` veraendert erst das Segment ab `t`. Das davor
liegende Segment verwendet den zuletzt vollstaendig abgeschlossenen Zustand.
Mehrere Ereignisse derselben Abschlussgrenze muessen bereits atomar zu genau
einem P0-S-Zustand zusammengefuehrt worden sein; doppelte Ticks werden
abgelehnt.

## Technische Abnahme

Der fokussierte W7-P-Bestand besteht mit:

```text
11 tests, OK
```

Der erweiterte relevante Verbund aus W7-P, W7-N, W7-M, den
kapazitaetsbegrenzten Kopplungs- und Runtimepfaden, F3- und
Baselinekopplungen, K2-B-Vertraegen sowie API-/Architekturverbrauchern
besteht mit:

```text
106 tests, OK
```

Geprueft wurden insbesondere Linkshaltung, Atomizitaet, W7-M-Bindung,
Determinismus, ein gemeinsamer Observertreiber, Rollensperren,
CAP-Exklusivitaet, Profilnormalisierung, unaufgeloeste Nenner,
Erklaerungspraezedenz und fehlender Export aus `current_api`.

## Unveraenderte Grenzen

Unveraendert blieben:

- `mcm_field_organism.__init__` und `current_api`;
- Produktionsruntime und Snapshot-Schemata;
- Browser-, Video-, Audio- und Rezeptorpfade;
- Reports und Forschungslaeufe;
- Lauf 197 und die einmalige W6-I-Ausfuehrung.

W7-P belegt technische Rollenreinheit und reproduzierbare Komposition. Es
belegt keine Feldfunktion, kein Memory, keine Ressourcenwiederverwendung,
keine Feldzeit, Organisation, Semantik, Selbstregulation oder KI.

## Naechster Schritt

W7-Q muss statisch binden, wie aus den bereits eingefrorenen W7-M-
Rezeptorabschlussgruppen genau ein gemeinsamer P0-S-Abschlusszustand pro
Grenze entsteht. Der Vertrag muss Gleichzeitigkeit, Anfangszustand,
Neuronreihenfolge, P0-Parameter, Zeitintervall und Digestbindung festlegen.
Noch keine Implementierung, Hauptmatrix, Browserausfuehrung oder
Forschungsauswertung.
