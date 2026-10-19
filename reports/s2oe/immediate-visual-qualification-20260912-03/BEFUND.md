# 17/18 bestanden: native Cuezeit nach Formation noch unzulässig

Genau ein Aufruf unter `immediate-visual-qualification-20260912-03`.
**NOT_QUALIFIED**: alle 18 Testkörper erreicht, 17 bestanden, ein Fehler in
Prüfgruppe 14. Keine Wiederholung, keine Korrektur nach dem Aufruf.
Die historischen 18 Setupfehler und der spätere Vorabstopp bleiben unverändert.

## Erreicht und offen

Die unabhängigen administrativen Herkunfts-, Extraktions-, Manipulations-,
Lesezähler-, Scope- und Budgetprüfungen wurden erreicht und bestanden.
Die korrigierte native Fixture wurde aufgebaut. Der native Kontrollpfad
durchlief den Leerabruf einschließlich Direktbaseline und die reguläre
Formation; anschließend wurde der primäre Wiederabruf abgewiesen.
Die nachgelagerten Ergebnis- und Größenassertions des nativen Tests wurden
deshalb nicht erreicht. Kein vollständiger nativer Kontrollnachweis.

`_s2oe_immediate_visual_control.py:run` übergibt nach der Formation erneut
die unveränderte native Cuezeit [14,15). Die neue gemeinsame Sitzungszeit
ist bereits später, ersetzt aber nicht die native Zeitprüfung.
`_s2kq_private_partial_cue_retrieval_336.py:_state_and_cue` (Zeilen 463–472)
verlangt bei `generation > 0` insbesondere
`cue.visual_window_start_tick >= fast.visual_last_end_tick` und ein späteres
Ende. Nach Formation endet die native Visualzeit bei 15; Start 14 erfüllt
diese Bedingung nicht. Geworfener Code: **S2KQ_SOURCE_INVALID**.

Dies ist ein belegter Anschlusskonflikt zwischen eingefrorener Herkunftszeit
und neuer Abrufzeit, kein fachlich negativer Wiederabruf. Kein Validator wurde
gelockert. Kleinste zu prüfende Korrekturrichtung: ursprüngliche Medien- und
Rezeptorzeit unverändert als Herkunft erhalten, eine explizite neue native
Präsentationszeit für den Wiederhinweis binden. Keine verdeckte Umetikettierung
des historischen Rohzustands; noch keine solche Änderung ausgeführt.

Aus dem erreichten Aufrufpfad: eine synthetische NJ-Fixtureprojektion, eine
reguläre Formation, zwei vollständige Leerzustandsscans, dritter Scanaufruf
an der Eingangsvalidierung abgewiesen; kein vierter Scan. Null Medien- oder
Rezeptoranalysen, null Feldaufrufe, kein realer e03-Kontrolllauf.

## Unveränderte Quellen und Bilanz

Inventar vor/nach identisch:
`15697766ebdafb2ca685ec1029229d7a32f8032785b1f2d65aeb918f1e1ca61e`.
Präregistrierung:
`26ac7a896ac053b465fd9d334582f66536d0ab3281566dc0b9c0c30aed14da75`.
Elternrecord: 1.359.778 Byte, einmal in der historischen Eingangsbelegklasse.
Ein administrativer Vorbereitungszugriff; null Elternzugriffe im Test.

Qualifikationsbudget separat versioniert:
`s2oe.immediate-qualification-metadata.v2`. Nur Qualifikationsmetadaten
bis 131.072 Byte; Logreserve 65.536. Reale Sitzungen weiterhin 65.536,
Gesamt unverändert 4.194.304 Byte. Keine Produktlimitänderung.
Vorbilanz 2.127.564 Byte; Metadatenreserve 98.304 / 131.072.
Vollständiges Istlog 4.346 / 65.536 Byte. Keine Kürzung oder Verpackung.
Istbilanz einschließlich dieses Berichts und Bilanzdatei: `final-balance.json`.

Gates False. Reale Kontrolle und weitere Qualifikation bleiben gesperrt.
