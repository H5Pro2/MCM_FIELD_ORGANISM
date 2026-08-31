# S2-IL: Gemeinsame neutrale Einmalqualifikation

## Status

`QUALIFICATION_FAILED_FAILURE_ARTIFACT_PROVENANCE`

Die Qualifikation wurde genau einmal unter
`s2il-joint-qualification-20260831-01` ausgefuehrt. Es erfolgten keine
Korrektur und keine Wiederholung.

## Ergebnis

- 29 Tests wurden erreicht.
- 28 Tests bestanden.
- Ein Test schlug fehl.
- Exit-Code: `1`.
- Die 14 aktuellen S2-ID-Pruefungen bestanden.
- Sechs der sieben Laufhuellentests bestanden.
- Alle acht neuen Parent-Set-Pruefungen bestanden.
- Alle zehn gebundenen Quellhashes waren vor und nach dem Lauf identisch.
- Es wurden keine realen Geschichten und keine Memory-Zustandsfunktionen
  ausgefuehrt.

Der Status
`S2GT_PRIVATE_RUNNER_RECORDER_VERIFIER_QUALIFICATION_VALID` wird nicht
gesetzt. Der reale Fuenf-Status-Funktionslauf bleibt gesperrt.

## Bestaetigter Teilbefund

Die S2-IK-Projektion bestand innerhalb dieses Laufs folgende neutrale
Pruefungen:

- kanonische Bildung und unabhaengige Rekonstruktion aller 76
  Mehr-Eltern-Operationen;
- unveraenderte Null- und Ein-Eltern-Projektion;
- fail-closed bei doppelten, fehlenden, fremden und zeitlich spaeteren
  Eltern;
- `ie-op-171` mit maximaler Owner-ID exakt `814` Byte;
- Einhaltung der gebundenen Huelle fuer `ie-op-171` bis `ie-op-183`;
- Registrybindung `183/366`.

Dieser Teilbefund ersetzt die fehlgeschlagene Gesamtqualifikation nicht.

## Fehlerbefund

Fehlgeschlagen ist
`test_21_complete_and_not_evaluable_are_exclusive`. Der Test erzeugt nach
erfolgreicher Verzeichnisreservierung einen neutralen Fehlerabschluss. Der
Recorder erreicht dabei terminal `NOT_EVALUABLE` und erzeugt keinen
`COMPLETE`-Marker.

Der read-only Verifikator meldet jedoch zusaetzlich:

`reservation or manifest is unreadable`

Statische Ursache:

- `AppendOnlyRunRecorder.reserve` schreibt Reservierung und Manifest als
  Ergebnis der ersten registrierten Operation unter deren Zielpfad;
- der fruehe Fehlerpfad veroeffentlicht danach die beiden Fehlerartefakte;
- `verify_run_read_only` verlangt vor der Fehlerpfadauswertung eigenstaendige
  Dateien `reservation.json` und `manifest.json`;
- diese Belegformen stimmen fuer den fruehen `NOT_EVALUABLE`-Pfad nicht
  ueberein.

Damit ist die terminale Fehlerprovenienz der Laufhuelle noch nicht gemeinsam
qualifiziert. Dies ist kein Fehler der Parent-Set-Projektion und kein
Memory-Funktionsbefund.

## Belege

Die vollstaendigen Belege liegen unter:

`reports/s2il/s2il-joint-qualification-20260831-01/`

Enthalten sind Testausgabe, Exit-Code, Vorher-/Nachher-Quellhashes,
Hashvergleich und maschinenlesbarer Qualifikationsstatus.

## Grenze

Eine Korrektur oder neue Qualifikation benoetigt eine neue ausdrueckliche
Freigabe und eine neue Qualifikations-ID. Der reale Fuenf-Status-Lauf bleibt
gesperrt.
