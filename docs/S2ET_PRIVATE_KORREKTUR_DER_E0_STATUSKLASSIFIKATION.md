# S2-ET: Private Korrektur der E0-Statusklassifikation

## Umfang

**PRIVATE_STATUS_CORRECTION_IMPLEMENTED**

Ausgangscommit: `39bdc1be19bf743c17d6c999c06b1282a0613db4`.
Die ausdrueckliche S2-ET-Freigabe wird ausschliesslich fuer ES-B01 umgesetzt.
Keine Laufnummer; keine Tests, Projektfunktions- oder Plattformaufrufe.

Genau drei bestehende require-Aufrufe erhalten als drittes Argument
`BLOCKED_PLATFORM_PREREQUISITE`:

| Datei und Zeile | Bestehende Ablehnungsbedingung |
| --- | --- |
| `_s2er_publication_records.py:223` | Plattformkontext, Eltern und Publisherquellen zwischen W/F/B/C nicht anwendbar. |
| `_s2er_publication_records.py:232` | Host-/Runtimekontext passt nicht zu P/S. |
| `_s2er_windows_files.py:137` | Native Elternidentitaet passt nicht zum vorab abgenommenen Beleg. |

Die Bedingungen, Meldungen und ihre Reihenfolge bleiben identisch.
Es wird kein neuer Fehlercode eingefuehrt und kein Beleg akzeptiert,
der zuvor abgewiesen wurde.

## Unveraenderte Grenzen

Der Owner `_s2er_file_publication.py` bleibt bytegleich. Sein bestehender
Ausnahmezweig uebernimmt den Plattformstatus nur bei fehlender Reservierung.
Nach begonnener Reservierung bleibt FAILED beziehungsweise nach
Renameversuch ABORTED_INCOMPLETE massgeblich. Es gibt keinen Retry.

Nicht abgenommene Plattformberichte, offene Gates, unvollstaendige
Fallbefunde und ein fehlender unabhaengiger Zulassungskontext werden
bereits mit dem Plattform-Voraussetzungscode abgewiesen; diese Stellen
bleiben unveraendert. Allgemeine Schema-/Digest-/Bindungsfehler werden
nicht pauschal umklassifiziert. Native Fehler, insbesondere Fehler 5,
behalten ihre bestehende Behandlung.

Keine Aenderung an E0-E8, Dateioperationen, Flushes, Umbenennung, Marker,
kanonischen Datenformen oder Digestverfahren. TSPM-1, PPB-1,
bestehender Kern, Runner, API, Snapshot und Feldpfad bleiben unveraendert.

Die Quellhashes der zwei geaenderten privaten Module aendern sich
notwendigerweise. Der JSON-Beleg bindet diese neuen Identitaeten.
Fruehere Vertrags-/Implementierungsbelege werden nicht umgeschrieben;
spaetere Plattformbelege muessen den korrigierten Quellstand binden.

## Statische Verifikation

AST- und Syntaxpruefung ohne Projektimport oder Auswertung:
Werden ausschliesslich die drei hinzugefuegten Fehlercode-Argumente
aus einer AST-Kopie entfernt, ist sie mit dem jeweiligen Ausgangs-AST
identisch. Die Kopie wird nicht ausgefuehrt und nicht gespeichert.

Alle 20 direkten S2-ER-Vorgaengerquellen und alle 21 S2-EL-Quellen
stimmen weiterhin in Rohbytes und Git-Blobs. Beide Freigabeflags sind
False; keine Studienreservierung oder Ergebnisdatei wurde erzeugt.

**WEITER:** Die nachgelagerte statische Abnahme steht im separaten
S2-ES-Wiederholungsbericht nach S2-ET. Diese Implementierung allein
erteilt keine Test-, Plattform- oder Matrixfreigabe.
