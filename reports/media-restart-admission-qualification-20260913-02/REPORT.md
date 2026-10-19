# Reale Checkpoint-Zulassung: Anschluss qualifiziert

**12/12, QUALIFIED**, genau ein neutraler Aufruf, 0,360 s Testzeit.
Kein Zugriff auf die ausgewählte MP4, keine reale Medienausführung. Gates
anschließend False. Der Vorabstopp -01 bleibt unverändert erhalten.

## Quellen- und Artefaktklassen

Das gemeinsame Inventar steht einmal in `preregistration.json`: 118 Dateien
mit Pfad, Größe und SHA-256. `charged_sources` ordnet jede Datei eindeutig zu:

- **32 vollständig mitgezählte Quellenbelege: 290.408 Byte.** Sämtliche
  bisherigen `external`-Quellen der -05-Bindung sowie die neuen Anschluss-,
  Test- und Aufrufdateien. Keine zusätzliche Quellkopie erzeugt.
- **86 nur gebundene Basisdateien:** unverändert installierte Abhängigkeiten,
  keine Kopien. Alle Hashes vor und nach dem Test geprüft. Ihre Inventareinträge
  zählen als Metadaten; ihre Quellbytes werden nicht neu als Ablage ausgegeben.
- **Sechs historische Referenzdateien: 42.680 Byte**, vollständig mitgezählt:
  Vorregistrierung, Ergebnis und vollständiges stderr von Restart -01 und -05.
- Alle erzeugten Fixtures, Claims, Objektdateien, vollständigen Logs und
  Abschlussdateien zählen physisch. Auch die zwei außerhalb des Testordners
  notwendigen Dateieinstiegs-Fixturedateien zählen vollständig: 228 Byte.

Die Zuordnung übernimmt die bisherige -05-`external`-Pflicht und ergänzt alle
neuen Pflichtdateien. Kein Weglassen historischer Referenzen und keine
Grenzerhöhung. Die vollständige Liste ist aus Inventar und `charged_sources`
ohne zusätzliche Datenquelle auflösbar. Ergebnis und späterer Einstieg
referenzieren das Inventar digestgebunden, statt es erneut einzubetten.

## Vorbilanz und Istbilanz

Vorregistrierung: 20.644 Byte; SHA-256
`a25b2b745106126dc142073e35a15a1addd005b4fff8221a2dec7e9b6891869b`.
Vorregistrierungspublikation: 108.544 Byte Metadaten einschließlich temporärer
Kopie und Reserven. Getrennte Testphase einschließlich 32.768 Byte
Fixturehülle: **120.668 / 131.072 Byte Metadaten**, 290.408 / 327.680 Byte
Quellen, 290.408 / 393.216 Byte Zusatzhülle, 411.076 / 4.194.304 Byte gesamt.
Diese Phasen werden nicht gleichzeitig addiert.

Gebunden: vollständige Logs 8.192 Byte, Ergebnis/Bericht/Bilanz gemeinsam
8.192 Byte, primärer Fehlerabschluss einschließlich temporärer Kopie 8.192
Byte. Tatsächliches vollständiges Log: 2.036 Byte, Ergebnis: 1.156 Byte.
Die abschließende `balance.json` zählt sich selbst und diesen Bericht mit;
sie weist tatsächliche Belegung und verbleibende Reserven getrennt aus.

## Tatsächlich erreichte Prüfdeckung

Alle zwölf Gruppen stehen mit Einzelstatus in `stderr.log`. Geprüft wurden
unveränderliche Realzulassung, Quellenfelder, Profil/Lauf/Manifest/Code,
fehlende Freigabe, unveränderte Neutralbedingungen, beide echten Prüforte,
Dateibindung, Startabweisung, Rollenfolge und einmalige Verifikation,
Hashlesen einschließlich Fehlerfall sowie Primärfehler ohne Verifikation.

Beide produktiven Zulassungsstellen wurden durchlaufen; erst **danach** wurde
der native Runtimeaufbau im neutralen Test gezielt gestoppt. Die
Prozessausführung und numerische Gesamtprüfung wurden im Dateieinstiegstest
durch neutrale Kontrollfunktionen ersetzt. Kein neuer nativer Fortsetzungs-
oder Decoderbefund wird behauptet. Ein kleiner 16-Byte-Eingang prüfte separat
die unveränderte, tatsächlich zählende Hashlesefunktion.

Die acht -05-Fortsetzungsprüfungen wurden nicht wiederholt. Work-/Decoder-,
Zustandscodec-, Serialisierungs- und Ledgerdateien blieben unverändert;
ihre historische Prüfdeckung wird nicht als neuer Testlauf ausgegeben.

## Grenze und Folge

Quellen vor/nach dem Aufruf unverändert. Inventardigest:
`3c57126512189c2fdf262e82c62add8014e4463d85bafecc09871735cbeea46b`.
HEAD `537109994cf777f8d36cda617aafe12226806c25`, vorhandener schmutziger
Arbeitsbaum. Historische Belege und fremde Änderungen bleiben unberührt.

Der reale Dateivergleich benötigt weiterhin eine neue ausdrückliche
Ausführungsfreigabe. Die reale Datei wurde weder gelesen noch decodiert.
Erfolg bleibt von der tatsächlichen Beleggröße abhängig; keine universelle
Erfolgsgarantie und keine Aussage über allgemeine Crash-Recovery.
