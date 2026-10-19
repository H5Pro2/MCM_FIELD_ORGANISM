# PPB-KETTE-FEHLERBILANZ

## Bezug und Ergebnis

Statische Klärung zum bestehenden `STRUCTURE_CHAIN_EXTRACTION_PRESTART_STOP.md`.
Repository-HEAD: `537109994cf777f8d36cda617aafe12226806c25`.
Maßgeblich sind zusätzlich die gelesenen, noch unqualifizierten Arbeitsdateien
`reports/qualify_structure_chain_once.py` und `tools/_structure_ppb_chain.py`;
sie sind unversioniert im Arbeitsbaum. HEAD allein bindet sie nicht.
Fremde Änderungen und historische Belege bleiben erhalten.

**Die vollständige Fehlerreserve ist nicht statisch abgesichert.** Konkreter
unbeschränkter Bestandteil ist die freie Fehlerdiagnostik, nicht die Anzahl
der PPB-Übergänge. Deshalb kein neuer Qualifikationsaufruf.

## Endliche Struktur ist nicht gleich endliche Fehlerausgabe

`generate()` im Kettenmodul, Zeilen 39–71, begrenzt die Geschichte auf drei
Banken mit je drei Übergängen: höchstens zwölf Zustandsabbilder einschließlich
dreier Anfangszustände und neun vollständige Schrittbelege. Jeder Kontakt
enthält 288 Werte; eine Bank hat vier Slots. Der Fortschritt verweist auf
diese Ketten, statt weitere Übergänge zu erzeugen.

Nach erfolgreicher Fortschreibung wird der Postzustand bereits in Zeile 50
angehängt und der Zähler erhöht; erst nach Tabellenbildung folgt die
40.960-Byte-Prüfung in Zeile 61. Ein Fehlerpräfix kann daher den letzten
gültigen Postzustand ohne fertigen Schrittbeleg enthalten. Die Zustandsgrenze
ist an dieser Fehlerposition noch nicht erfolgreich geprüft. Die
1.048.576-Byte-Gesamtprüfung in Zeile 70 schützt den zurückgegebenen
Erfolgsrecord, ist aber keine vorangestellte Prüfung sämtlicher Fehlerpräfixe.
Die bloße Multiplikation der Reserven liefert deshalb keinen vollständigen
Fehlerobergrenzennachweis.

## Konkret unbeschränkte Bestandteile

1. `reports/qualify_structure_chain_once.py:165–168`: Der breite
   `except Exception` speichert `str(exc)` und `traceback.format_exc()`.
   Es gibt keine Bindung der Textlänge, der verketteten Ausnahmen oder der
   Tracebacktiefe. Neun fachliche Übergänge begrenzen diese Größen nicht.
   JSON-Escaping ist zusätzlich zu berücksichtigen. Die 8.192 Byte für
   `failure.json` sind eine Reserve, keine aus diesen Formaten abgeleitete
   Obergrenze. Auch feste eigene Fehlercodes begrenzen nicht sämtliche hier
   abgefangenen Bibliotheks-, Serialisierungs- und Dateifehler.
2. Derselbe Einstieg, Zeilen 112–123: stdout und stderr des vollständigen
   unittest-Prozesses gehen unverändert in `qualification.log`. Die
   4.096-Byte-Grenze wird erst danach gegen die Dateigröße geprüft.
   Fehlertexte, Assertiondarstellungen und Tracebacks sind nicht aus der
   Zahl zwölf der Prüfgruppen nach oben begrenzt. Vollständige Aufbewahrung
   ist vorgesehen, ein belegter maximaler Umfang jedoch nicht.

Es wurde keine zusätzliche Fehlerausgabe erzeugt. Weder Überschreitungen
dieser beiden Reserven noch eine konkrete fehlende historische Zahl werden
als Messwert behauptet. Festgestellt ist die fehlende statische Absicherung.

## Abschlussalternativen

Der Fehlerpfad kann nach Veröffentlichung von `record.json` und sogar
`verification.json` erreicht werden. Dann werden zusätzlich `partial.json`
und `failure.json` gespeichert. Record und Präfix dürfen nicht pauschal als
Alternativen abgezogen werden; physische Mehrfachablage bleibt mitzuzählen.

Bei erfolgreicher Veröffentlichung der Auswertung endet der try-Block.
Ein nachfolgender Fehler im finally-Block kann trotzdem mit vorhandener
`evaluation.json` auftreten, ohne den dort nicht mehr erreichbaren except-
Abschluss zu erzeugen. `save()` (Zeilen 30–35) schreibt außerdem zunächst
eine temporäre Datei; bei Schreib-/Umbenennungsfehlern kann diese verbleiben.
Die bekannte Erfolgs-/Fehleraufteilung ist somit kein vollständiger Beweis
für alle Dateifehlerabschlüsse. Der spätere `run()` prüft zudem alle CAPS
zusammen, während `prepare()` und `bind()` Alternativen bilden.

## Stopp

Historische Vorbilanz unverändert: Erfolg 3.247.500 Byte, Fehleralternative
4.296.076 Byte, Überschreitung 101.772 Byte gegenüber 4.194.304 Byte.
Das sind die dokumentierten Reservensummen des Vorabstopps, keine neu
gemessene oder jetzt garantierte vollständige Fehlerhülle.

Eine kleinere Präfixreserve würde die unbeschränkten Diagnostikbestandteile
nicht beseitigen. Unter den Vorgaben vollständiger Logs und unveränderter
Grenzen liegt daher keine tragfähige Vorbedingung für den Testaufruf vor.
Keine Kürzung, Auslagerung, Verpackungsstufe oder Ersatzreserve vorgenommen.
Alle zwölf Prüfungen bleiben unausgeführt; keine reale PPB-Folge, keine
Projektimporte, Rezeptoranalyse oder historische Prüfungswiederholung.
