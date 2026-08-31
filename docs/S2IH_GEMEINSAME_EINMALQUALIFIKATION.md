# S2-IH gemeinsame Einmalqualifikation

## Grenze

S2-IH sollte den aktuellen S2-IC-Quellstand und die private S2-IG-Laufhuelle
in genau einem neutralen `unittest`-Aufruf qualifizieren. Vollstaendige
Memory-Geschichten, Formationen und der reale Fuenf-Status-Lauf blieben
gesperrt.

## Ergebnis

Status: `QUALIFICATION_FAILED_EVENT_LIMIT`

- Ein `unittest`-Aufruf wurde ausgefuehrt.
- Die 14 bestehenden S2-ID-Status-, Symmetrie- und Fehlerpruefungen bestanden.
- Die sieben neuen S2-IH-Testkoerper wurden nicht erreicht.
- Beim neutralen Aufbau des vollstaendigen `183/366`-Belegs trat `IG-E008`
  auf.
- Es gab keinen Retry und keine Hauptausfuehrung.
- Alle gebundenen Quellhashes waren vor und nach dem Lauf identisch.

## Ursache

`ie-op-171` (`EXECUTION_EVIDENCE_SEAL`) besitzt 14 registrierte
Elternoperationen. Bereits sein minimaler neutraler kanonischer
START-Beleg ist `1.550` Byte gross. Die unveraenderte Ereignisgrenze betraegt
`1.536` Byte. Die Laufhuelle kann daher ihren eigenen registrierten
Erfolgspfad nicht innerhalb der gebundenen Einzelgrenze materialisieren.

Das ist ein technischer Huelen- und Registrybefund. Es ist kein negativer
S2-IC-, Kontextsignal- oder Memory-Befund.

## Verbleibende Grenze

`S2IG_PRIVATE_RUNNER_RECORDER_VERIFIER_QUALIFICATION_VALID` und eine
aktuelle S2-IC-Gesamtqualifikation wurden nicht gesetzt. Der reale
Fuenf-Status-Funktionslauf bleibt gesperrt. Eine Korrektur der
Elternbelegprojektion oder Ereignisgrenze und eine neue Qualifikation
benoetigen eine eigene Freigabe und eine neue Qualifikations-ID.

Die vollstaendigen maschinenlesbaren Belege liegen unter
`reports/s2ih/s2ih-joint-qualification-20260831-01/`.
