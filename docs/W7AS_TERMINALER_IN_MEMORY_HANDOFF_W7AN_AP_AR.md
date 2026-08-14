# W7-AS: Terminaler In-Memory-Handoff W7-AN nach W7-AP und W7-AR

## Status

W7-AS ist als private terminale Uebergabe implementiert. Es wurde kein
realer W7-AN-Lauf gestartet und kein Zahlenresultat erzeugt.

## Zweck

Der erste reale W7-AN-Nachweis erzeugte den kanonischen R1/R2/R4-Container
nur im Arbeitsspeicher. Nach Abschluss der technischen Containerpruefung
wurde das Objekt verworfen, weil W7-AP und W7-AR damals noch nicht
existierten.

W7-AS schliesst diese Luecke. Nach dem naechsten vollstaendigen Lauf wird der
Container innerhalb derselben Speicherlebenszeit in fester Reihenfolge
weitergereicht:

```text
36 bestaetigte W7-AN-Phasen
-> einmalige W7-AN-Containerfinalisierung
-> W7-AP-Rohdistanzkomposition
-> W7-AR-Numerikauswertung
-> ein terminales digestgebundenes Endobjekt
```

## Vorbedingungen

Der Handoff akzeptiert nur:

- einen vollstaendigen W7-AN-Koordinator mit genau 36 Phasenbelegen;
- drei kanonische Primaer- und drei digestgleiche Gegenlaufresultate;
- einen noch nicht finalisierten W7-AN-Container;
- den W7-AO-Vertragsdigest `14455f15...067dc`;
- den W7-AQ-Vertragsdigest `66717c7b...86ee3`;
- die bestehenden kanonischen CAP-, Handoff- und Rohkontrasteingaben.

## Terminale Semantik

W7-AS ruft keine `advance`-Phase auf. Es fuehrt keine Feldintegration aus.
Es finalisiert nur einen bereits vollstaendig aufgebauten Koordinator und
reicht dessen Objekt direkt an W7-AP und W7-AR weiter.

Nach einem erfolgreichen Handoff wird das Endobjekt am Koordinator gebunden.
Nach einem Fehler wird eine terminale Fehlerbindung gesetzt. In beiden
Faellen ist ein zweiter Versuch mit demselben Koordinator gesperrt. Dadurch
kann kein teilweise weiterverarbeiteter Abschluss wiederverwendet werden.

## Endobjekt

Das Endobjekt haelt im Arbeitsspeicher:

- den kanonischen W7-AN-Container;
- die vollstaendige W7-AP-Distanzkomposition;
- das vollstaendige W7-AR-Numerikergebnis;
- die W7-AN-, W7-AO-, W7-AP-, W7-AQ- und W7-AR-Digestkette;
- genau 36 vorgelagerte Phasenbelege als Anzahlbindung.

`persisted`, `field_function_decision_allowed` und `memory_claim_allowed`
bleiben `false`.

## Persistenz- und Evidenzgrenze

Der Handoff enthaelt keinen Datei-, Report-, Browser- oder Runnerpfad. Er
schreibt keine Zwischenwerte. Auch ein spaeter konvergiertes Ergebnis waere
nur ein technischer Numerikbefund und ersetzt keine W7-L-Funktionsbaseline.

## Verifikation

Der schnelle W7-AN-bis-W7-AS-Verbund besteht mit `77 tests, OK`. Die sieben
W7-AS-Tests pruefen die feste Reihenfolge W7-AN/W7-AP/W7-AR, die komplette
Digestkette, Vorbedingungsstopp, terminale Fehlersperre, Einmaligkeit,
Manipulationsschutz, private API und fehlende Ausfuehrungs-/Persistenzpfade.

## Naechster Schritt

Die technische Vorbereitung fuer den realen In-Memory-Gesamtlauf ist damit
abgeschlossen. Als W7-AT kann derselbe bereits nachgewiesene 36-Phasen-Lauf
erneut ausgefuehrt und sein Abschluss unmittelbar ueber W7-AS ausgewertet
werden. Erwartete Laufzeit nach dem letzten realen Nachweis: rund 76 Minuten.
