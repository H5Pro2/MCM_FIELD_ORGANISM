# S2-FB: Private Layoutkorrektur

## Implementierung

Nach Bindung des statischen Layoutvertrags wurde ausschliesslich
`_s2ex_recorder_binding.py` und `_s2ex_recorder_trace.py` geaendert.

Die private Bindung prueft den kanonischen Layoutdescriptor, dessen Digest,
einen geschlossenen Originalbeleg, die zugehoerige RuntimeIdentity, die beiden
unveraenderten Encoderquellen und die exakten FileRefs in der Leseliste.
`native_layout_raw` ist Teil der gesamten Binding-Identitaet. Sein leerer
Initialwert ist nur ein Fehlend-Sentinel und wird abgewiesen, kein Default-ABI.

Der Decoder verwendet nur das gebundene Profil. Die fruehere Schleife ueber
zwei Layouts ist entfernt. Geprueft werden der unveraenderte originale
DWORD-Aufrufumfang und saemtliche Pufferbytes: Nullflag, sieben Paddingbytes,
Null-Root-Handle, Little-Endian-Laenge und das vollstaendige gebundene
UTF16LE-Rename-Ziel. Es gibt keine Praefixabnahme oder Restbytes.

Rollenwechsel, native Erfolgspruefung, Phasen, Actorrechte und Einmaligkeit
bleiben unveraendert. Der Encoder, die Fixture und der Supervisor bleiben
bytegleich. Es wurde kein neuer nativer Funktionsaufruf eingefuehrt.

## Statische Abnahme

Der S2-EY-Wiederholungsaudit nach S2-FB schliesst EY-B02-ABI im freigegebenen
Code-/Vertragsumfang. Die Quellenbelege stehen in dessen JSON-Begleitdatei.
Fuenf Recorder-Module wurden per AST gelesen; kein Projektmodul wurde
importiert, kein Projekt-Syntaxbaum ausgewertet und keine Funktion aufgerufen.

TSPM-1, PPB-1, API, Snapshot, Feldpfad, Tests, Tools und Reports bleiben
unveraendert. Die neue Herkunftshuelle ist keine oeffentliche Schnittstelle
und aendert weder F/B/Q/C noch RunBinding oder TraceEntry.

Der Vertrag selbst liegt in CRLF-Rohdarstellung bytegenau gebunden vor;
die beiden geaenderten Python-Dateien behalten ihre bisherige CRLF-Darstellung.
Der Audit nennt zusaetzlich kanonische LF-Hashes und Git-Blobidentitaeten.

## Keine Ausfuehrungsabnahme

Ein echter Herkunftsbeleg wurde nicht hergestellt. Seine spaetere unabhaengige
Abnahme muss die konkrete Prozess-ABI und Encoderuebereinstimmung feststellen.
Der neue Validator prueft die Bindung dieses Belegs, nicht die Wahrheit einer
beliebig eingereichten Behauptung. Die vorhandene Ausfuehrungssperre und die
leere Menge abgenommener Bindings bleiben deshalb bestehen.

Keine Tests, Plattformaufrufe, Matrixzellen oder Rechteerhoehung.
Keine neue Laufnummer und kein technischer Wirkungsbefund.

**WEITER:** Am besten geht es jetzt mit dem statischen Preflight der konkreten
Quellen-, Runtime-, Layoutbeleg- und Einmaligkeitsbindung fuer S2-EM weiter.
