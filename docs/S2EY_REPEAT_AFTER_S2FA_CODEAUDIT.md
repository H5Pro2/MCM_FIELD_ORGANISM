# S2-EY: Statischer Wiederholungsaudit nach S2-FA

## Befund

**STATIC_REPEAT_CODE_AUDIT_BLOCKED**

Der S2-FA-Quellstand wurde nach der privaten Korrekturimplementierung gegen
S2-EZ gelesen. Drei Korrekturpunkte sind statisch nachvollziehbar umgesetzt;
die vollstaendige native Trace-Abnahme bleibt an einer Quellbindungsfrage
offen. Das ist ein Code-/Vertragsbefund, kein fehlgeschlagener Plattformlauf.

## Verbleibender Blocker

**EY-B02-ABI: Das native Rename-Layout ist nicht eindeutig quellgebunden.**

In `_s2ex_recorder_trace.py:547` versucht der Decoder die beiden Layouts
`(4, 8, 12)` und `(8, 16, 20)` und akzeptiert das zum Buffer passende Layout.
Damit wird zwar ein vollstaendiger No-Replace-Puffer geprueft, jedoch nicht
nachgewiesen, dass gerade dieses Layout zur gebundenen Prozess-ABI gehoert.

S2-EZ verlangt die Auswertung anhand der fest gebundenen Quellen-/Runtime-ABI.
Die geerbte RuntimeIdentity bindet Interpreterpfad und -hash, Version,
Plattform sowie Abhaengigkeiten. Der Decoder leitet daraus aber noch keinen
eindeutigen Layoutselektor ab. Auch eine Host-Maschinenbezeichnung ersetzt
keine implementierte Bindung des Prozesslayouts.

Erforderlich ist eine genaue statische Herkunfts- und Abnahmeregel fuer
einen einzigen Layoutselektor. Zuerst ist zu klaeren, ob die vorhandenen
unveraenderlichen Runtimebelege dazu ausreichen. Falls nicht, benoetigt
die kleinste notwendige Bindungsergaenzung eine gesonderte Freigabe.
Kein neuer Wert, kein Host-Default und keine Plattformausfuehrung wurden
zur vermeintlichen Schliessung dieser Luecke erfunden.

## Teilabnahme

| Punkt | Statischer Befund |
| --- | --- |
| EY-B01 | Pfadargumente werden vor der numerischen Handleauswertung getrennt; die API-Slotlisten und Handle-Generationen sind lesend gebunden. |
| EY-B02 | Originalpaare, Datei-/Bytebelege, Phasen, Quellen und Abbrueche sind implementiert; die ABI-Auswahl verhindert die Gesamtabnahme. |
| EY-B03 | Kontrollschema, F-Referenzen und Reihenfolge der Kontrollabnahme vor dem eigenen Spoolabschluss sind umgesetzt. Die gemeinsame native Abnahme bleibt von EY-B02 abhaengig. |
| EY-B04 | Echter nativer Closefehler beendet den Proxy ohne angewendete Injektion; sein Fehler bleibt beim nativen Kindaufruf. |

Die p09-/p11-Nachpruefungen lesen die vollstaendigen finalen beziehungsweise
Markerbytes mit Identitaetsbindung. Sie reparieren keinen Flush und heben
den gescheiterten Subjektstatus nicht auf. Kein solcher Pfad wurde aufgerufen.

## Pruefbelege und Grenzen

- Fuenf von fuenf geaenderten Modulen sind syntaktisch per AST parsebar.
- Die JSON-Begleitdatei bindet die exakten Quellen, Rohbytes und Git-Blobs.
- Ausserhalb der fuenf privaten Recorder-Module ist kein Paketcode geaendert.
- Test-, Tool- und Reportbaeume sowie TSPM-1, PPB-1, API, Snapshot und Feldpfad
  sind unveraendert.
- Keine Tests, Projektimporte, Projektfunktionen, Plattformaufrufe,
  Rechteerhoehungen oder Matrixzellen wurden ausgefuehrt.
- Die Ausfuehrungssperre bleibt False, die Menge gepruefter Bindings leer.
  Die sechs gebundenen Studienausgabepfade bleiben abwesend.

Syntax und Quellabgleich sind keine Funktions-, Persistenz- oder
Plattformgarantie. Der Audit behauptet keine vollstaendige Tracekorrektheit
und keinen Memory- oder Feldbefund. Auch nach Schliessung des Restpunkts
bleiben konkrete Quellen-, Runtime-, Eltern-, Budget- und
Einmaligkeitsbindung vor einer Ausfuehrung gesondert erforderlich.

**RUECKMELDUNG ERFORDERLICH:** Fuer den naechsten Schritt wird ausschliesslich
ein enger statischer ABI-Bindungsvertrag vorgeschlagen. Noch keine erneute
Codeaenderung, Testausfuehrung, Plattformpruefung oder Matrix freigeben.

**WEITER:** Am besten geht es jetzt mit der eindeutigen statischen Bindung
des nativen Prozesslayouts und anschliessend einer gezielten Decoderkorrektur
mit erneutem S2-EY-Audit weiter.
