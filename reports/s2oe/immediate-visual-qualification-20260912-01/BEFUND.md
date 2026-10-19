# Unmittelbarer visueller Abruf: Qualifikation nicht bestanden

Genau ein Testaufruf unter `immediate-visual-qualification-20260912-01`.
Status **NOT_QUALIFIED**: 18 Testinstanzen aufgerufen, 18 Setupfehler,
kein Testkörper erreicht, keine bestandene Prüfgruppe. Kein Retry.

## Implementiert, noch nicht qualifiziert

Neue private Herkunftsklasse `s2oe.immediate-historical-input.v1` für den
einzigen benannten Elternrecord, maximal 2.097.152 Byte. Vollständige
Byte-/SHA-Prüfung vor e03-Auswahl, Extraktionsbeziehung und separate
Lesezähler; bestehende lokale und globale Grenzen bleiben unverändert.
Die schmale Rekonstruktions-/Formationskomposition ist ebenfalls angelegt,
aber der native Pfad wurde nicht erreicht. Kein Nachweis seiner Funktion.

## Konkreter Fehler

`tests/test_s2oe_immediate_visual_input.py:fixture` übergibt das spätere
Visualfenster [466666666,500000000) und das frühere gemeinsame Audiofenster
[400000000,500000000) an `NN.bind_event`. Dessen unveränderter Validator
verlangt in dieser Sonderform `visual_start <= common_start` und weist mit
`S2NNError: VISUAL_TIME_BINDING_INVALID` ab (NN, Zeilen 86–91).
Die Fixture verwendet somit den falschen bestehenden Zeitanschluss für
diese Fensterkombination. Das ist kein Memory- oder Rezeptorbefund.

Die Ablehnung erfolgt vor NJ. Tatsächlich: null NJ-Projektionen,
null Rezeptoranalysen, null Formationen, null Scans, null Feldaufrufe.
Alle 18 Tests hängen derzeit an derselben fehlerhaften Setupform; auch
administrative Negativprüfungen wurden deshalb nicht erreicht.

Korrekturrichtung, nicht ausgeführt: Fixture über den bereits vorhandenen
AV-Paaranschluss für die unterschiedlichen Modalitätsfenster binden, ohne
NN-Zeitvalidierung zu lockern oder Fenster zu verschieben. Administrative
Prüfgruppen von der nativen Gesamtfixture entkoppeln.

## Bindung und Budget

Vorbilanz: 2.094.796 / 4.194.304 Byte, keine übergeordnete Verletzung.
Elternrecord 1.359.778 Byte, SHA-256:
`4da6485b12ce98dca625fe5998130d1f2c0f9225d78a0fefb9c4bcf18298f3e7`.
Dieser Dateihash ist nicht der historische interne Recorddigest.
Ein administrativer Elternlesezugriff bei Vorbereitung, 1.359.778 Byte;
null Elternzugriffe im Test. Kein realer e03-Memoryaufruf.

Inventar vor/nach identisch:
`fcf996ff23eeeb2d66eb5cc1e2332f784411fc0b2fee321dfeaf1162307ca57b`.
Präregistrierung:
`138576ba94d9a39dbf40f345f94434fc469af27b6965fac31f37f231451db2be`.
Vollständiges Log: **36.578 / 32.768 Byte**, lokale Überschreitung **3.810**.
Keine Kürzung, Verpackung, Umklassifizierung oder Reserveänderung.
Die kleinere tatsächliche Belegung anderer Metadaten heilt diese lokale
Verletzung nicht. Vollständige Istbilanz in `final-balance.json`.

Keine weitere Qualifikation freigegeben oder ausgeführt. Keine konkrete
ausführbare Hauptlaufbindung: dieser Schritt bleibt von einer bestandenen
Qualifikation abhängig. Historische Belege unverändert, Gates False.
