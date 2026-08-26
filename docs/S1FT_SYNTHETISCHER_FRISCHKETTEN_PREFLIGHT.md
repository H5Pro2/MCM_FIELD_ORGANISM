# S1-FT: Synthetischer Frischketten-Preflight

## Umsetzung

S1-FT implementiert den S1-FS-Preflight ausschliesslich mit typisierten
synthetischen Objekten. Gebunden werden:

- die sechs frischen S1-FI-Formationseingaben;
- der unveraenderte S1-FP-Probevertrag und seine Probequelle;
- alle 30 r2/r4/r8-Probe-Slots mit ihrer exakten Zustandsrolle;
- die zwoelfstufige S1-FS-Ausfuehrungsreihenfolge;
- alle acht Bestandteile der atomaren Rueckgabe;
- 45 geplante Aufrufe und maximal 28.000 Feldschritte;
- ein ausdruecklich synthetischer RAM-Snapshot.

Die Rueckgabehuelle enthaelt nur Schemadigests. Sie enthaelt keine beobachteten
Werte, kein Laufresultat und keine Feldschritte.

## Abnahme

Mit 8 GiB synthetisch freiem RAM bestehen alle zehn Preflight-Gates. Mit nur
3 GiB schliesst der Preflight kontrolliert mit
`SYNTHETIC_FRESH_CHAIN_PREFLIGHT_FAILED_CLOSED`. Fehlende Probe-Slots,
veraenderte Zustandsrollen oder eine vorgetaeuschte beobachtete Rueckgabe
werden bereits durch die typisierten Objekte abgewiesen.

Der positive Ausgang lautet:
`SYNTHETIC_FRESH_CHAIN_PREFLIGHT_PASSED_REAL_RUNNER_AND_AUTHORIZATION_ABSENT`.

## Grenze

Der RAM-Wert ist eine Fixture und keine Messung des aktuellen Rechners. Vor
einem spaeteren Lauf waere ein neuer realer Snapshot unmittelbar vor dem
ersten Formation-Arm erforderlich. S1-FT implementiert keinen Realrunner,
erzeugt keine Besitzerautorisierung, fuehrt keinen Feldschritt aus und
persistiert nichts. Es entsteht kein Memory-, Feldzeit-, Reaktivierungs-,
Organisations- oder KI-Nachweis.

## Bester naechster Schritt

S1-FU sollte statisch den fehlenden Realrunner-Anschluss kartieren: Welche
vorhandenen Formation-, Capture-, Probe- und Auswertungsadapter koennen
unveraendert wiederverwendet werden, und welche neue Koordination fehlt fuer
die 45-Aufruf-Kette? Noch keine Runnerimplementierung, Besitzerautorisierung
oder Ausfuehrung.
