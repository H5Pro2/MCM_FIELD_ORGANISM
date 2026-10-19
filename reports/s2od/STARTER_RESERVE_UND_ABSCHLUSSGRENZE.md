# Starterreserve korrigiert; neue Abschlussgrenze festgestellt

Stand: 2026-09-11. Rein statische Vorprüfung, **0 Testaufrufe**,
keine native Sitzung und keine Payloadverarbeitung. Der bisherige
Vorabstopp und die ursprüngliche Vorbereitung bleiben unverändert erhalten.

## Prospektive Reservebindung

Die ausdrücklich freigegebene lokale Starterreserve beträgt jetzt **6.720 Byte**
statt 4.096 Byte. Sie ist keine Erhöhung einer Runtime-, Memory-, Metadaten-
oder Gesamtgrenze.

- Datei: `reports/s2od/start_terminal_basic_once.py`
- Tatsächliche Dateigröße: **6.720 Byte**
- SHA-256: `e8b18cb55a7cce4787c4bf59cfc00e62902307a9e38bf88a2b33a625ea8deb85`
- Code unverändert gegenüber dem dokumentierten Starterentwurf.
- Geltung: kommende Anschlussqualifikation und neue finale Laufbindung;
  keine rückwirkende Änderung der historischen 4.096-Byte-Vorbereitung.

Damit ist die bisherige lokale Quellenüberschreitung geschlossen.

## Neue konkrete Überschreitung

Die vollständige Auswertung passt nicht in ihre bisherige Einzelbindung:

| Teil | Gebunden bzw. vorhanden |
| --- | ---: |
| Starterprüfung `ASSESSMENT_LIMIT` | 3.000 Byte |
| Gemeinsamer Abschlussansatz `@evaluation` | 3.000 Byte |
| Vorhandene vollständige OB-Auswertung allein | 3.229 Byte |
| Überschreitung bereits ohne neue Anzeigehülle | 229 Byte |

Quellstellen: [Starter](start_terminal_basic_once.py), Zeilen 128–130,
und [gemeinsamer Sitzungseinstieg](../../tools/_s2oc_bound_session.py), Zeile 12.
Der Starter bettet das Ergebnis der unveränderten OB-Auswertungsfunktion unter
`functional` ein und ergänzt sieben Anzeigehashes, sieben Vergleichsergebnisse
sowie `verification_calls_by_starter`. Er prüft die gesamte Form gegen 3.000 Byte.

Die gelesene Vergleichsdatei ist
`reports/s2ob/caller-av-basic-20260910-01/evaluation.json`:
3.229 Byte, SHA-256
`5e5739256bc00462ec98cfc9ebccb5ecb29e9558e1e83d448866e1a1edd9e35e`.
Das ist eine vorhandene historische Dateigröße, **kein neu gemessener
Benutzerlauf und keine erneut ausgeführte Funktionsauswertung**.
Die zusätzliche Anzeigehülle ist in den 3.229 Byte noch nicht enthalten.
Eine vollständige Erfolgsform in der bereits belegten Gestalt ist damit nicht
durch die 3.000-Byte-Reserve abgedeckt. Die tatsächliche künftige Ausgabegröße
ist weiterhin unbekannt; insbesondere wird keine universelle Obergrenze aus
diesem einen historischen Ergebnis abgeleitet.

## Konsequenz für die Qualifikation

Status bleibt **PRECONDITION_BLOCKED**, diesmal an einer anderen konkreten
Belegklasse. Es wird kein Testaufruf gestartet und kein Anschlussnachweis
behauptet. Native neutrale Payloads wurden noch nicht erzeugt. Test-/Aufruf-
und Abschlussbelege sind noch nicht zu einer tragfähigen finalen Gesamtbindung
zusammengeführt; die frühere passende Vorbilanz ersetzt das nicht.

Die kleinste zusammenhängende Korrekturrichtung ist ein ausdrücklich gebundener
Ansatz für die vollständige Auswertung einschließlich Anzeigeabgleich im
versuchsspezifischen Anschluss: Größe vorab begrenzen und denselben Betrag in
Vorstart, Clientverifikation und Abschlussbilanz zählen. Nicht nur die Assertion
ändern, keine notwendige Auswertung kürzen und keine alten Belege umklassifizieren.
Die 65.536-Byte-Metadaten- und 4.194.304-Byte-Gesamtgrenze bleiben unverändert.

Die aktuelle Freigabe erhöht ausschließlich die Starterquellenreserve.
Eine weitere Reserveänderung wurde nicht eigenmächtig vorgenommen. Die neue
Abschlussüberschreitung wird entsprechend der ausdrücklich genannten
Stoppbedingung vorgelegt. Gates bleiben `False`; realer Benutzerlauf gesperrt.
