# S1-ZW: Statischer Portabilitaetsabschluss und aktiver T0-Preflight

## Abschluss von S1-ZV

Die enge Rohbytekorrektur ist statisch geschlossen. Die sieben
`.gitattributes`-Regeln gelten weiterhin exakt. Alle 60 JSON-Reports und die
sechs gebundenen Browserassets liegen im Arbeitsbaum und im Git-Index als LF
vor. S1-ZW oeffnet diesen Bestand nicht erneut und veraendert weder Inhalte
noch Digests.

## T0-Umfang

Der aktive Schnelltest besteht aus genau sechs Modulen und 46 Testmethoden:

- aktive Engineering-Oberflaechengrenze: 15;
- aktiver Feldzustandsvertrag: 3;
- aktuelle Architektur-API: 3;
- MCM-Neuronenschicht: 11;
- Browser-Payload-Quelle: 6;
- Browser-Payload-Smoke: 8.

Die sechs Quelldigests und ihre Reihenfolge sind im maschinenlesbaren Vertrag
gebunden. `numpy` und `cv2` sind vorhanden. Die fehlenden optionalen
Abhaengigkeiten `pytest` und PyAV werden fuer T0 nicht benoetigt und duerfen
nicht nachinstalliert werden.

## Wirkungsgrenze

T0 ist ein technischer, synthetischer Test und nicht vollstaendig
zustandsfrei. Freigegeben sind lokale Neuronen- und Feldprimitive,
Temporaerdateien, isolierte Python-Importprozesse und injizierte
Playwright-Fakes. Nicht enthalten sind Netzwerkzugriffe, ein reales
Browserbinary, Produktionspersistenz, geschlossene Forschungspfade oder eine
oeffentliche API-Aenderung.

## Ausfuehrungsvertrag

Im naechsten Schritt darf der exakt gebundene `unittest`-Befehl einmal
ausgefuehrt werden. Erfolg erfordert Exitcode 0 und genau 46 Tests. Bei einer
Abweichung wird weder repariert noch wiederholt; zuerst ist der Befund statisch
zu klassifizieren. Breite Discovery, optionale Abhaengigkeitstests,
geschlossene Historie und private Engineeringtests bleiben ausgeschlossen.

In S1-ZW wurde kein Testmodul und keine Feldfunktion ausgefuehrt. Der Befund
ist nur ein statischer Ausfuehrungspreflight und kein Feld- oder
Memory-Ergebnis.

## Naechster Schritt

S1-ZX fuehrt genau den gebundenen T0-Befehl einmal aus und dokumentiert
Exitcode, Testzahl, Laufzeit und Abweichungen. Es gibt im selben Schritt weder
Retry noch Reparatur.

Maschinenlesbarer Vertrag:
[S1ZW_STATISCHER_PORTABILITAETSABSCHLUSS_UND_AKTIVER_T0_PREFLIGHT_V1.json](S1ZW_STATISCHER_PORTABILITAETSABSCHLUSS_UND_AKTIVER_T0_PREFLIGHT_V1.json).
