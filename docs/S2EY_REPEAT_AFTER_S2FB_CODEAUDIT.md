# S2-EY: Statischer Wiederholungsaudit nach S2-FB

## Ergebnis

**STATIC_REPEAT_CODE_AUDIT_PASSED_EXECUTION_LOCKED**

Im freigegebenen Layoutumfang wurde keine verbleibende Vertragsabweichung
identifiziert. EY-B02-ABI ist statisch geschlossen. Das ist eine Code- und
Vertragsabnahme, keine ausgefuehrte Trace-, Plattform- oder Funktionspruefung.

## Abgleich

| Punkt | Statischer Befund |
| --- | --- |
| EY-B01 | Pfad-/Handletrennung bleibt unveraendert erhalten. |
| EY-B02-ABI | Genau ein Descriptor; Runtime-/Encoder-/Originalbytebindung; kein Layoutversuch anhand des Puffers. |
| EY-B02 | Offener Layoutrest geschlossen; sonstige Originalbeleg-, Phasen- und Fallregeln unveraendert. |
| EY-B03 | Geschlossenes Kontrollschema und lesende Abnahme vor eigenem Spoolabschluss unveraendert. |
| EY-B04 | Echte und eingespeiste p12-Closefehler bleiben getrennt. |

`_bound_native_layout` verlangt den kanonischen Originalbeleg, den festen
Layoutdigest, dieselbe RuntimeIdentity und beide unveraenderten Encoderquellen.
Der Originalbeleg und der S2-FB-Vertrag muessen in der unabhaengig geprueften
Leseliste vorhanden sein. Die Binding-Identitaet enthaelt die neuen Bytes;
ein anderer Beleg kann keine alte Binding-Abnahme wiederverwenden.

Die Encoder deklarieren dieselbe geordnete Struktur aus Byteflag, nativer
Handle-/Pointergroesse, uint32-Laenge und WCHAR-Namen. Fuer das explizit
gebundene Profil sind Strukturumfang 24 und Namensoffset 20 getrennt.
Die statische Auswertung liest lediglich diese Deklarationen. Sie konstruiert
keine ctypes-Struktur und misst keine Offsets eines realen Prozesses.

Der Decoder prueft das gesamte Original gegen die einzige kanonische
Darstellung des gebundenen Ziels. Eine andere Feldlage, falsche Laenge,
Padding, Root, Terminator, unvollstaendige Zeichen oder Restbytes passen
nicht zu diesem Vergleich. Die native Rollenfortsetzung liegt weiterhin
hinter dieser Pruefung und dem erfolgreichen Originalreturn.

## Belege

Die JSON-Begleitdatei bindet die fuenf gelesenen Recorderquellen sowie beide
Encoder. Fuenf von fuenf Recorderdateien sind AST-parsebar. Descriptor,
Layoutdigest, Vertragsdigest, Rohdatei-Hash und Encoder-SourceRefs wurden
mit Standardbibliotheksfunktionen an literalen Daten abgeglichen.
`git diff --check` ist bestanden.

Nur zwei private Codemodule sind geaendert. Native Encoder, Fixture und
Supervisor bleiben bytegleich. TSPM-1, PPB-1, API, Snapshot, Feldpfad sowie
Test-, Tool- und Reportbaeume bleiben unveraendert. Die sechs gesperrten
Studienausgabepfade sind abwesend.

## Weiterhin offen

Die konkrete Prozess-/Layoutbeobachtung und ihre unabhaengige Abnahme liegen
nicht vor. Das neue Belegschema ist kein solcher Beobachtungsbefund.
Ein Digest bestaetigt Integritaet, nicht die Wahrheit einer ABI-Angabe.
Vor einer Ausfuehrung muss der externe Abnehmer die Originalherkunft fuer
die genaue Runtime, ihre Abhaengigkeiten und Encoderquellen pruefen.

Es wurden weder Tests noch Projektfunktionen, Plattformaufrufe, Matrixzellen
oder Rechteerhoehungen ausgefuehrt. Es wurde kein Launcher, Prozessbeleg,
neues F oder freigegebenes Binding erstellt. `_PLATFORM_EXECUTION_RELEASED`
bleibt `False`, `_REVIEWED_BINDINGS` bleibt leer.

Die statische Abnahme ersetzt keine spaetere ausdrueckliche Einmallauffreigabe.
Sie behauptet keine gemessene Persistenz, komplette Laufzeitkorrektheit,
Memory-Funktion oder Feldwirkung.

**WEITER:** Am besten geht es jetzt mit S2-FC als statischem Preflight der
konkreten Quellen-, Runtime-, Layoutbeleg- und Einmaligkeitsbindung weiter.
Tests und Plattformausfuehrung bleiben dabei gesperrt.
