# S2-FB: Statischer nativer Layoutvertrag

## Umfang

**STATIC_LAYOUT_CONTRACT_BOUND**

Dieser Vertrag schliesst ausschliesslich die Layoutbindung EY-B02-ABI aus
dem S2-EY-Audit nach S2-FA. Er bindet genau ein unterstuetztes natives Profil:
`windows-amd64-llp64`. Andere Profile werden nicht geraten oder ausprobiert.
Die nachfolgende private Decoderkorrektur ist durch den aktuellen Auftrag
mitfreigegeben, Tests und Plattformausfuehrung sind es nicht.

## Kanonisches Rename-Layout

| Feld | Typ | Offset | Umfang |
| --- | --- | --- | --- |
| replace | uint8, Wert 0 | 0 | 1 Byte |
| padding | Nullbytes | 1 | 7 Bytes |
| root | uint64, Wert 0 | 8 | 8 Bytes |
| name_length | uint32, little-endian | 16 | 4 Bytes |
| name | UTF16LE, exakter gebundener Zielpfad | 20 | name_length Bytes |

Das Profil bindet Zeiger mit acht Bytes, WCHAR mit zwei Bytes und native
Ausrichtung mit acht Bytes. Der feste Strukturumfang ist 24 Bytes; der
variable Name beginnt bereits bei Offset 20. Der Encoder allokiert
`max(24, 20 + name_length)`, uebergibt aber nur `20 + name_length` Bytes.
Allokationsumfang und uebergebener Umfang duerfen nicht verwechselt werden.

Die Laenge ist positiv, gerade und passt in uint32. Der uebergebene Puffer
enthaelt keinen Terminator und keinen nachfolgenden Rest. Abweichende Flags,
Paddingbytes, Root-Handles, Offsets, Laengen oder unvollstaendige Zeichen
werden durch den vollstaendigen Bytevergleich verworfen.

## Herkunft und Digest

Der Layoutdigest ist SHA-256 des kanonischen JSON-Layoutobjekts. Ein genau
definierter privater Originalbeleg `s2fb.native-layout-origin.v1` bindet ihn
an die vollstaendige RuntimeIdentity und die beiden unveraenderten Encoder-
Quellen. Seine geschlossene Datenform steht in der JSON-Begleitdatei.

`RecorderBinding` erhaelt nur die zusaetzliche unveraenderliche Bytes-Huelle
`native_layout_raw`. Die Originalbytes muessen als exakter FileRef bereits
in der unabhaengig geprueften Leseliste liegen. Ihr Quellpfad liegt im
gebundenen Repository und erhaelt nur eine bestehende dynamische source-Rolle.
Auch dieser Vertrag wird bytegenau in die vorhandene Leseliste gebunden.
Es entstehen keine neue feste Pfadrolle und kein neuer Schreibpfad.

Der Beleg darf nur die fuer den konkreten spaeteren Prozess unabhaengig
festgestellte ABI wiedergeben. Ein Hash beweist Unveraendertheit, nicht die
Richtigkeit einer ABI-Angabe. Die bestehende unabhaengige Startabnahme muss
diesen Originalbefund pruefen, bevor sie die gesamte Binding-Identitaet
abnimmt. Diese Identitaet enthaelt nun auch native_layout_raw. Ein Beleg aus
anderer Runtime oder anderen Encoderquellen darf nicht uebernommen werden.

Hier wird kein solcher Prozessbeleg erzeugt, kein Messverfahren ausgefuehrt
und keine Vertrauensregistrierung installiert. Fehlende Belege sperren den
Zugang. Hostbezeichnung, Versionszeichenfolge oder ein zufaellig passender
Tracepuffer ersetzen die Herkunft nicht.

## Encoder, Decoder und Rollen

Die beiden vorhandenen Encoder bleiben unveraendert. Ihre Feldreihenfolge,
Datentypen, Nullinitialisierung und uebergebene Bytezahl werden statisch
gegen das Profil abgeglichen. Die konkreten Quelldigests sind im Vertrag
gebunden; geaenderte Encoder erfordern eine neue Abnahme.

Der Decoder verwendet ausschliesslich die gebundenen Offsets. Er vergleicht
die gesamten Originalbytes mit der kanonischen Darstellung des bereits
gebundenen Rename-Ziels. Er rekonstruiert keinen fehlenden Originalaufruf
und akzeptiert keinen lediglich dekodierbaren Praefix.

Es gelten unveraendert nur die 28 bestehenden Renamekanten und deren
Actor-, Handle-, Phasen- und Einmaligkeitsregeln. Quellen, Verzeichnisse,
Spools, Reservierungen und Marker werden keine Rename-Quellen. p13 bleibt
lesend; p05 behaelt seinen gebundenen nativen Fehlerfall. Ein erfolgreicher
nativer Return wechselt die Rolle, ein fehlgeschlagener nicht.

## Fail-Closed und Grenze

Fehlende oder nicht unterstuetzte ABI-Herkunft blockiert mit
`BLOCKED_PLATFORM_PREREQUISITE`. Abweichende Formen, Digests, Quellen oder
Puffer werden mit den bestehenden Binding-/Schemafehlern verworfen.
Es gibt weder ein Ersatzlayout noch eine automatische Korrektur.

F/B/Q/C, RunBinding, TraceEntry, FixtureRecord, API, Snapshot und Feldpfad
bleiben unveraendert. Keine Tests, Projektimporte, Projektfunktionen,
Plattformaufrufe, Matrixzellen oder Rechteerhoehung. Keine Laufnummer.

**WEITER:** Am besten geht es jetzt mit der freigegebenen engen privaten
Layout-/Decoderkorrektur und anschliessend dem statischen S2-EY-Audit weiter.
