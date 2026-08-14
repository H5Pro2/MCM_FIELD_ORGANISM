# W3-B: current_api Restore-Fortsetzungspruefung

Stand: 2026-08-09

Entscheidung: `CURRENT_API_RESTORED_CONTINUATION_EXACT`

Implementierung: technischer Test

Formaler Forschungslauf: nein

## Auftrag

W3-B prueft ueber `current_api`, ob ein restauriertes neutrales Feld bei
exakt derselben spaeteren reduzierten Rezeptorfolge dasselbe Endfeld wie der
ununterbrochene Pfad erzeugt.

## Pruefaufbau

Der bestehende Fassade-only Consumertest wurde um folgenden Pfad erweitert:

```text
erster kontrollierter AV-Abschnitt
-> Feld F1
-> Snapshot S1
-> Restore R1

zweiter kontrollierter AV-Abschnitt
-> reduzierte Sequenzen Q2

F1 + Q2 -> ununterbrochenes Endfeld
R1 + Q2 -> restauriertes Endfeld
```

Der zweite Abschnitt wird einmal kontrolliert aufgenommen. Seine exakt
gleichen reduzierten Sequenzobjekte werden fuer beide Fortsetzungspfade
verwendet. Damit vermischt der Vergleich keine erneute Quellenaufnahme oder
abweichende Threadzeit mit der Restore-Frage.

## Kontrollen

- Der Test importiert weiterhin nur aus
  `mcm_field_organism.current_api`.
- Der zweite Abschnitt enthaelt zehn auditive und zwei visuelle reduzierte
  Zustaende.
- Der Snapshot des ersten Feldes bleibt nach der ununterbrochenen Fortsetzung
  unveraendert.
- Ununterbrochenes und restauriert fortgesetztes Endfeld besitzen denselben
  Snapshot-Digest.
- F3-Referenzarm und Live-Sensorik werden nicht verwendet.

## Verifikation

```text
119 passed
350 subtests passed
Python-Kompilierung erfolgreich
Projektimporte im Consumertest: nur mcm_field_organism.current_api
Enddigest ununterbrochen == Enddigest restauriert
```

Pytest meldet weiterhin die bestehende Cache-Warnung fuer `.pytest_cache`.
Sie beeinflusst die bestandenen Tests nicht.

## Verwendete Quellen

- W3-A-Consumertest;
- `advance_audio_video_receptor_sequences` aus `current_api`;
- Snapshot- und Restore-Vertrag des neutralen gemeinsamen Feldes;
- kontrollierte synthetische Audio- und Videofolgen.

## Aussagegrenze

W3-B belegt technische Zustandskontinuitaet unter identischer bereits
reduzierter Fortsetzung. Snapshot/Restore bleibt Runtime-Serialisierung und
ist kein MCM-Memory. Der Test belegt kein Lernen, keine Feldzeit,
Organisation, Semantik, Selbstregulation oder KI. Es wurde kein Browser
gestartet und keine Kamera, kein Live-Mikrofon oder andere physische Sensorik
aktiviert. Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

W3-C bindet dieselbe Fortsetzungspruefung an die echte serialisierte
Fassadengrenze:

1. Der erste Snapshot wird mit `to_json()` in Text serialisiert.
2. Nur `SharedMCMFieldSnapshot.from_json()` darf daraus den Restorezustand
   rekonstruieren.
3. Derselbe zweite reduzierte Abschnitt wird auf ununterbrochenem und aus JSON
   restauriertem Feld fortgesetzt.
4. Serialisierter Snapshot, dekodierter Snapshot und beide Endfelder muessen
   digestidentisch zu ihren jeweiligen Kontrollen sein.
5. Projektimporte bleiben auf `current_api` begrenzt; Forschungsclaims und
   Live-Sensorik bleiben ausgeschlossen.

## Spaeterer Umsetzungsstand W3-C

W3-C ist am 2026-08-09 umgesetzt worden. Der erste Snapshot wird kanonisch zu
JSON serialisiert, daraus neu dekodiert und erst danach restauriert. Snapshot-
und Endfelddigests bleiben gegenueber den jeweiligen Kontrollen identisch. Der
aktuelle Verbund besteht mit `120 passed` und 350 Subtests.
