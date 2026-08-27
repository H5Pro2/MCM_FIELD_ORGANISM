# S2-FA: Private Recorder-Korrekturimplementierung

## Status

**PRIVATE_CORRECTIONS_IMPLEMENTED_STATIC_AUDIT_BLOCKED**

Ausgangscommit: `0503ebf67128a9fc91426bd214a05b8e994d88e3`.
Umgesetzt wurden ausschliesslich die vier S2-EZ-Korrekturen in den fuenf
bestehenden privaten Recorder-Modulen. Es gibt keine neuen Module oder Tests.
Der anschliessende S2-EY-Audit ist wegen einer verbleibenden
ABI-Quellbindungsfrage noch nicht bestanden.

## Implementierter Umfang

- EY-B01: Pfad-APIs bleiben ausserhalb der numerischen Handleauswertung.
  Der Leser trennt Pfadrollen, geoeffnete Handles und API-Ausgabeslots.
- EY-B02: Ein rein lesender Decoder prueft Originalaufrufpaare,
  Handle-Lebenszyklen, Dateiidentitaeten, vollstaendige Bytepruefungen,
  Quellen, Phasenpflichten und Fallabbrueche. Positive Marker allein reichen
  nicht mehr. Die gebundenen p09-/p11-Lesbarkeitsnachpruefungen sind ergaenzt.
  Die Auswahl des nativen Rename-Layouts ist jedoch noch nicht ausreichend
  quellgebunden; dieser Punkt bleibt offen.
- EY-B03: Die Kontroll-Datenform ist geschlossen. Ihre lesende Abnahme liegt
  vor dem eigenen, nichtrekursiven Spool-Flush, Byteabgleich und Close.
  Die bestehende F-Referenz trennt S2-EW-Isolation und S2-EZ-Recorderformat.
- EY-B04: Ein echter nativer p12-Closefehler erzeugt kein INJECTION-Ereignis
  und keinen injected_error. Erst erfolgreicher nativer Close erlaubt den
  vorregistrierten eingespeisten Fehler.

Die neuen Decoder verarbeiten ausschliesslich uebergebene Originalbytes
und unveraenderliche Vertragswerte. Sie rufen weder die Fixture noch das
Dateibackend auf. Die zusaetzlichen Dateioperationen in der Fixture sind
nur die bereits in S2-EZ gebundenen lesenden p09-/p11-Nachpruefungen;
sie wurden nicht ausgefuehrt.

## Statische Pruefung

Alle fuenf geaenderten Python-Dateien lassen sich mit `ast.parse` lesen.
`git diff --check` ist bestanden. Quellen-, Rohbyte- und kanonische
LF-Digests stehen in der JSON-Begleitdatei. Die bestehende CRLF-Darstellung
der privaten Module wurde beibehalten; Git-Blobwerte sind separat erfasst.

Es gab keine Projektimporte, ausgewerteten Projekt-Syntaxbaeume,
Testausfuehrungen, Zustandsaufrufe, Plattformaufrufe, Rechteerhoehungen
oder Matrixzellen. Statische Syntaxkorrekturen waehrend der Bearbeitung
sind keine Testlaeufe und erhalten keine Laufnummer.

TSPM-1, PPB-1, oeffentliche API, Snapshot, Feldpfad, bestehendes Dateibackend
und Vergleichsrunner bleiben unveraendert. Test-, Tool- und Reportbaeume
bleiben unveraendert. Die Ausfuehrungssperre und die leere Liste abgenommener
Bindings bleiben erhalten; die sechs Studienausgabepfade sind abwesend.

## Anschluss

Der unmittelbar anschliessende rein statische Audit ist in
[S2-EY nach S2-FA](S2EY_REPEAT_AFTER_S2FA_CODEAUDIT.md) dokumentiert.
Er erteilt keine Plattform- oder Testfreigabe. Die ABI-Auswahl darf nicht
stillschweigend aus einem passenden Tracepuffer geraten werden.

**WEITER:** Am besten geht es jetzt mit einem gesondert freizugebenden,
engen statischen Vertrag zur eindeutigen nativen ABI-Quellbindung weiter.
