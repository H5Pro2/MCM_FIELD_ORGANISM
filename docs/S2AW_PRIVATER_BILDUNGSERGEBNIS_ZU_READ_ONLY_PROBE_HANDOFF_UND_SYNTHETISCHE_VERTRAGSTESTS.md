# S2-AW: Privater Bildungsergebnis-zu-Probe-Handoff

## Umsetzung

S2-AW implementiert den privaten Anschluss zwischen dem vollstaendigen
S2-AR-Bildungsergebnis und der bestehenden S1-WU-read-only Probe in
`mcm_field_organism._ppb1_active_batch_formation_probe_handoff`.

Das Modul bindet Bildungsergebnis, urspruengliche Formation-Huelle und Profil
erneut gegeneinander. Beide Modalitaetszustaende muessen mindestens einen
stabilisierten berechtigten Platz enthalten. Eine zweite Huelle liefert genau
ein disjunktes und kausal spaeteres Probeframe fuer Audio und Video.

Der Partitionsdigest wird vor den Probeaufrufen gebildet. Danach wird die
vorhandene Probe je einmal fuer Audio und Video aufgerufen. Nur beide Befunde
gemeinsam ergeben ein Handoffergebnis. Die Bankdigests muessen vor und nach
den Probeaufrufen identisch sein.

## Synthetische Abnahme

Das fokussierte S2-AW-Testmodul wurde einmal ausgefuehrt. Alle 9 Tests
bestanden in der von `unittest` gemeldeten Laufzeit von 0,117 Sekunden.

Die Tests erzeugten acht authentische private S2-AR-Formationsergebnisse. Die
stabilisierten Fixtures durchliefen je drei Audio- und drei Video-
Bildungsschritte. Geprueft wurden positive und negative spaetere Proben,
Quellabweichungen, fehlende Stabilisierung, zeitliche Ueberlappung,
Mehrframe-Proben, ein Fehler beim zweiten Probeaufruf, Digestmanipulation und
die privaten Systemgrenzen.

Drei Handoffs lieferten vollstaendige Ergebnisse: zwei positive
Zwei-Modalitaetsbefunde und einen negativen Zwei-Modalitaetsbefund. Sechs
ungueltige oder injiziert fehlerhafte Versuche endeten ohne Handoffergebnis.

## Grenze

S2-AW zeigt technisch, dass ein tatsaechlich gebildeter und stabilisierter
privater PPB-1-Zustand spaeter gegen getrennte Audio- und Videoeingaben
read-only geprueft werden kann. Positive und negative Befunde veraendern den
Zustand nicht.

Dieser Befund vergleicht keine Baseline und betrifft keine Feldwirkung,
Produktion oder oeffentliche API. Er ist deshalb kein Nachweis eines
MCM-spezifischen Vorteils und kein Nachweis einer eigenstaendigen MCM-Memory.

Der naechste Schritt ist S2-AX: ein statischer Implementierungs-, Digest-,
read-only Atomaritaets- und Grenzenaudit ohne erneute Ausfuehrung.

Maschinenlesbarer Receipt:
[S2AW_PRIVATER_BILDUNGSERGEBNIS_ZU_READ_ONLY_PROBE_HANDOFF_UND_SYNTHETISCHE_VERTRAGSTESTS_V1.json](S2AW_PRIVATER_BILDUNGSERGEBNIS_ZU_READ_ONLY_PROBE_HANDOFF_UND_SYNTHETISCHE_VERTRAGSTESTS_V1.json).
