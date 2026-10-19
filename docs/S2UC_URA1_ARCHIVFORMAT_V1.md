# URA1: referenziertes neutrales Archivformat V1

Dieses Format betrifft ausschließlich den Transport vorhandener neutraler
URA1-Belege. Es ändert keine Policy und ist keine Forschungsfreigabe.

Nach genau einer gzip-Dekompression liegt lesbares UTF-8-JSON vor:
`format`, `nodes`, `root`, `original_bytes`, `original_sha256`.
`format` lautet `URA1_JSON_DAG_V1`. Es gibt weder Base64-Nutzlast noch innere
Kompression. Die Grenze von 4 MiB gilt für dieses vollständige JSON-Dokument;
512 KiB gelten für seine gzip-Datei.

Jeder Knoten hat genau zwei Elemente: Typ und Inhalt. `scalar` enthält einen
JSON-Skalar, `array` eine geordnete Liste von Knotennummern, `object` eine nach
Schlüsseln sortierte Liste aus Schlüssel und Knotennummer. Referenzen zeigen
streng auf frühere Knoten; Wurzel ist der letzte Knoten. Dadurch sind Zyklen
ausgeschlossen. Strukturell identische Teilbäume werden einmal gespeichert.
Das ist Wörterbuchkodierung mit expliziten Referenzen, keine numerische
Differenzkodierung. Es existieren folglich keine Delta-Operationscodes.

Identische Werte dürfen dieselbe Kodierung benutzen. Unterschiedliche
Originalidentitäten bleiben durch ihre vollständigen Metadaten unterscheidbar.
Arraypositionen, wiederholte Ereignisse und deren Reihenfolge bleiben erhalten.
Erhalten werden die JSON-Werte und die ursprünglichen kanonischen Bytes;
Python-Objektadressen waren kein Bestandteil der Originalarchive.

Der unabhängig implementierte Decoder importiert weder Encoder noch Policy.
Er validiert Schema, Schlüsselordnung und Referenzen, rekonstruiert sortiertes
kanonisches JSON mit kompakten Trennzeichen und abschließendem Zeilenumbruch
und prüft Länge sowie SHA-256 gegen einen extern übergebenen Originalbezug.
Die Hashangabe aus dem Archiv allein ist kein Vertrauensanker. Eine gemeinsam
mit ihrem externen Vertrauensanker ersetzte Datei kann so nicht authentifiziert
werden; die Bindung des ursprünglichen Belegpakets muss erhalten bleiben.

Die Ausgabe kann Stück für Stück verarbeitet werden. Ein optionaler Sink
erhält vorläufige Bytes; erst ein erfolgreicher Decoderabschluss bestätigt die
gesamte Ausgabe. Verbraucher dürfen Teilresultate vorher nicht als geprüft
publizieren. Der Decoder hält das kodierte JSON und seinen Knotengraphen,
aber keine vollständig expandierte Historie. Eine gezielte Manipulation kann
erst am abschließenden Originalhash auffallen. Die erwartete Ausgabelänge
begrenzt Expansion; die maximale Knotentiefe ist 128.

Ressourcenmessungen müssen getrennt benennen: gzip-Datei, dekomprimiertes
kodiertes JSON, vollständig rekonstruierte kanonische Bytes und Python-Peak
bei fortlaufender Prüfung beziehungsweise vollständiger Materialisierung.
Die größeren Originalhistorien verschwinden durch Referenzierung nicht.
Kleine neutrale Fälle belegen keine Skalierung auf Forschungsumfang.
