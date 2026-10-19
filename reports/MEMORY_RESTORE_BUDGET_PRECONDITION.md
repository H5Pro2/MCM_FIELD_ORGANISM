# Checkpoint-/Restore-Anschluss: Budgetvorbedingung

Auftrag: `MEMORY-SPEICHERN-WIEDERLADEN`. Stand 12.09.2026,
Bezugscommit `537109994cf777f8d36cda617aafe12226806c25` mit unverändert
vorhandenen fremden Änderungen im Arbeitsbaum. Kein Qualifikationslauf:
keine Test-ID verbraucht, keine Projektimporte, Payloads oder Zustandsbildung.
Nur Code gelesen und eine JSON-Grammatik-Untergrenze arithmetisch bestimmt.

## Konkreter Budgetkonflikt

Der Plan hatte die vollständige Feldgröße offen gelassen. Das heutige
[OB-Ledger](../tools/_s2ob_private_caller_binding.py), `core_sizes()` und
`balance()` ab Zeile 393, kennt Memoryzustände, Eingänge, Scans, Schritte,
NJ-, Formations- und Generationsbelege. Die Memoryzustände haben den eigenen
98.304-Byte-Codec. Ein vollständiger Feldsnapshot ist keine dieser bisherigen
Darstellungen. Unzugeordnete zusätzliche Inhalte verbleiben in der
Metadatenrechnung; deren Grenze beträgt 65.536 Byte.

Die native Feldserialisierung enthält pro Neuron dessen vollständige
Wahrnehmung und lokale Samples. Sie darf nicht durch das kurze `field_record`
mit bloßen Digests ersetzt werden. Nach einem vollständigen Feldschritt gilt
für die gebundene Geometrie folgende quellenunabhängige Untergrenze:

| Beitrag | Herleitung | Mindestens Byte |
| --- | --- | ---: |
| 336 Neuronen | 336 × 175 | 58.800 |
| 1.230 lokale Samples | 1.230 × 109 | 134.070 |
| Summe ohne äußere Hülle | | **192.870** |

Die Längen 175 und 109 stammen aus den vollständigen Schlüsseln der beiden
nativen JSON-Objekte, aber absichtlich verkürzten Werten: leere Identitäten,
Zahl `0`, Position `[0,0]`. Das ist **kein gültiger synthetischer Zustand**,
sondern eine untere Längenschranke. Listenkommas, echte Identitäten,
Binary64-Zahltexte, äußere Layer-/Dock-/Zeitdaten und Integrität fehlen darin.
Die tatsächliche vollständige Datei ist größer. Kein historischer Messwert
und keine passende Obergrenze werden daraus abgeleitet.

Codeherkunft:

- [AV-Geometrie](../mcm_field_organism/audio_video_field_geometry.py):
  Audiozeile mit 48 Positionen, Visualfeld mit acht Zeilen zu je 36 Positionen.
  Die 12×8×3-Bindung steht in
  [S2JO](../tools/_s2jo_private_canonical_av_boundary.py), Zeile 44.
- Horizontale gerichtete Nachbarschaften: `2*(47 + 8*35) = 654`.
  Vertikal einschließlich Audio-/Visualgrenze: `2*(36 + 7*36) = 576`.
  Zusammen 1.230; vier orthogonale Offsets, kein Quellen- oder Messergebnisbezug.
- [Layer](../mcm_field_organism/mcm_neuron_layer.py), `_perception_for()`
  ab Zeile 318: je vorhandener Nachbar ein Sample; keine Entfernung nach
  Nullaktivierung. [Neuron](../mcm_field_organism/mcm_neuron.py),
  `canonical_payload()` Zeilen 88, 150 und 198: vollständige Schlüsselformen.
- [Feldsnapshot](../mcm_field_organism/shared_mcm_field.py), Zeile 340:
  serialisiert alle Neuronen; der native transiente Fortschreibungspfad
  [neutral_local_field_substrate](../mcm_field_organism/neutral_local_field_substrate.py)
  endet in `field.advance()` und erhält diese Wahrnehmungsdarstellung.

## Was daraus folgt und was nicht

Eine Ablage als zusätzliche Metadaten überschreitet deren Grenze schon allein
um mindestens **127.334 Byte**. Die Memory-Einzelgrenze würde um mindestens
**94.566 Byte** überschritten; sie wird nicht pauschal auf Feldzustände
übertragen oder erhöht. Eine Ablage als Quellenbeleg wäre sachlich falsch.

Damit ist die unveränderte Ledgerübernahme nicht tragfähig. **Eine Verletzung
der übergeordneten 4.194.304-Byte-Grenze ist damit nicht bewiesen.** Ebenso
wenig liegt bereits eine vollständige Vorbilanz beider Arme vor. Die neue
native Belegklasse muss vor einer solchen Rechnung ausdrücklich feststehen.
Es wird keine komprimierte Größe als garantiert unterstellt und keine neue
Verpackung oder vereinfachte Fixture eingeführt.

## Gesammelte Restblocker und kleinster Vorschlag

1. Eine explizite versionierte **Feldcheckpoint-Klasse** im privaten Ledger
   vorsehen, getrennt von Memorycodec und Metadaten, vollständig im Gesamtbudget.
   Ihre endliche Einzelobergrenze und Zuordnung sind noch nicht gebunden.
   Keine stillschweigende Umklassifizierung bestehender Belege; historische
   Ledger und Zulassungen bleiben unverändert. Erst nach dieser Entscheidung
   lässt sich eine vollständige Formatobergrenze statt einer Beispielgröße binden.
2. Dann alle neuen Quellen-, Test-, Aufruf- und Abschlussbindungen zusammen mit
   Memory-/Feldcheckpoint, zugänglichem Präfix, beiden Vergleichsarmen und
   temporären Dateien bilanzieren. Schreib-/Fehlerabschluss und Erfolg als
   Alternativen erfassen; tatsächlich gleichzeitig bestehende Dateien zählen.
   Die aktuelle Untergrenze rechtfertigt keine fehlenden Reserven.
3. Die im Anschlussplan benannten versionierten MR-/Caller-/Sitzungseinstiege
   sind noch nicht implementiert. Bestehende Frischevalidatoren, Quellenzulassungen
   und Memorymechanik wurden nicht geändert. Kein unqualifizierter Restore
   wird als nutzbarer Anschluss ausgegeben.
4. Die spätere einmalige neutrale Qualifikation muss ein beendetes
   Präfixprogramm und einen frischen Restore-Prozess tatsächlich erreichen.
   Reine Codec-Rundläufe reichen nicht. Logische IDs, Zeiten, Zähler, native
   Werte und Generationsbindungen bleiben Vergleichsgegenstand; physische
   Prozess-IDs und neue lokale Lockobjekte nicht. Historische Consume-Belege
   bleiben erhalten, verbrauchte Owner werden nicht wiederbelebt.

**Vorabstopp, kein Fehllauf.** Noch keine vollständige Anschlussqualifikation
und keine konkrete Hauptlaufbindung. Keine historische Datei geändert,
keine Gates geöffnet, keine Prozessfortsetzung oder reale Vergleichsfolge
ausgeführt. Benötigt wird die konkrete Budgetzuordnung des neuen Feldbelegs,
nicht eine Wiederholung geschlossener Versuche oder ein weiterer Auditvertrag.
