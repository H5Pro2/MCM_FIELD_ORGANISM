# MCM-Verteiler-Vertrag

> **Historischer Architekturstand:** Dieser Verteiler erhielt fertige
> Sinnesfelder und ist nicht der aktuelle `ReceptorDistributor`. Verbindlich
> ist der [Rezeptorvertrag](025_REZEPTORVERTRAG_UND_DOCKGRENZE.md).

## 1. Zweck

Der MCM-Verteiler ist ein offenes Modul, an das fertige sensorspezifische
MCM-Felder andocken:

```text
Hören  -> auditives MCM -> auditiver Dock --\
Sehen  -> visuelles MCM -> visueller Dock  ---> MCM-Verteiler
Fühlen -> taktiles MCM  -> taktiler Dock  --/
```

Der Verteiler kennt keine Mikrofone, Kameras oder Rezeptorformeln. Er erzeugt
selbst kein sensorspezifisches Feld und keine feste multimodale Fusion.

## 2. MCM-Dock

Jedes Sinnes-MCM registriert genau einen technischen Dock mit:

- eindeutiger Dockidentität,
- Modalität,
- erwarteter Feldgeometrie,
- gemeinsamer technischer Uhrkennung.

Neue Sinnesmodalitäten ergänzen einen neuen Dock. Bestehende Docks werden dafür
nicht verändert.

## 3. Angedockte Feldlage

Jede vom Sinnes-MCM übergebene Feldlage trägt nur:

- eindeutige Feld- und Schnappschussidentität,
- zugehörigen Dock,
- Modalität und Feldgeometrie,
- gemeinsame technische Uhrkennung,
- Beginn und Ende seines Zeitfensters,
- lokale MCM-Trägerkennungen,
- gegenwärtige Aktivierungs- und Nachhalllage.

Rohsensorik, Semantik, Wichtigkeit und Zielwerte sind verboten.

## 4. Verteilung

Der Verteiler nimmt pro Dock höchstens eine Feldlage für eine gemeinsame
Prüfrunde an. Er ordnet alle vorhandenen Feldlagen kanonisch nach Dock und
Modalität. Dadurch verändert die technische Ankunftsreihenfolge die verteilte
Konstellation nicht.

Ein einzelnes angedocktes Sinnes-MCM darf allein eine gültige Verteilung bilden.
Fehlende Docks werden nicht durch Nullvektoren ersetzt.

## 5. Nicht erlaubt

- Summieren oder Verketten der Feldwerte als behauptete Integration,
- globale Gewinner- oder Prioritätsregel,
- modalitätsübergreifende Skalierung,
- Rückschreiben an Sinnes-MCMs,
- Muster-, Objekt- oder Ereignisklassen,
- dauerhafte Feldspeicherung im Verteiler.

## 6. Fehlergrenze

Unbekannter Dock, falsche Modalität, doppelte Feldidentität, ungültiges
Zeitfenster, inkompatible Uhr oder falsche Geometrie blockieren die gesamte
Prüfrunde.

## 7. Ausgang

Der Ausgang ist eine verlustfreie verteilte MCM-Konstellation. Sie enthält die
einzelnen Feldlagen unverändert und kann vom multimodalen Musterprüfer gelesen
werden. Sie ist noch keine gemeinsame Feldwirkung.

## 8. Bester nächster Schritt

Der Verteiler wird mit synthetischen auditiven, visuellen und taktilen
MCM-Feldlagen geprüft. Reale Docks folgen erst, wenn die jeweiligen
sensorspezifischen MCM-Felder vorhanden sind.
