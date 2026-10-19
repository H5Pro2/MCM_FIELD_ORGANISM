# URA1_STATE_DELTA_V1: genau eine gezielte Formatänderung

Nur neutrale Codec-/Kleinfallentwicklung. Keine neue Größenfreigabe.

Die vollständigen bisherigen Kleinfallarchive zeigen, dass vollständig
gespeicherte Zustandsobjekte, Ereignishüllen und Bankstrings die wesentlichen
Dictionaryanteile bilden. Die einzige neue Darstellung ersetzt aufeinander-
folgende vollständige Records durch einen vollständigen Anfangsrecord und
geordnete strukturelle Änderungen. Geänderte Zeichenbereiche langer Strings
sind ein expliziter Operationstyp innerhalb dieses einen Formats.

Nach genau einer gzip-Dekompression liegt lesbares JSON vor. Es gibt keine
innere Kompression, Base64-Nutzlast oder ausgelassene Ereignisse. Top-Level:
`format`, `values`, `paths`, `deltas`, `sequences`, `root`, `original_bytes`,
`original_sha256`.

## Vollständig definierte Werte und Reihenfolge

`values` enthält skalare, Array- und Objektknoten wie im bisherigen DAG-Format.
Referenzen zeigen ausschließlich auf frühere Wertknoten. Objektschlüssel sind
sortierte eindeutige Strings. Zahlen bleiben JSON-Zahlen mit ihrer kanonischen
Python-JSON-Repräsentation; Integer, Float, boolesche Werte und negatives Null
werden nicht durch bloße numerische Gleichheit zusammengelegt.

`paths` ist eine Tabelle von Pfaden aus Objekt-Schlüsseln oder ganzzahligen
Arrayindizes. Keine Schlüsselinterpretation als Organismuswissen. `deltas`
enthält geordnete Operationslisten. `sequences` enthält je Recordfolge
`[initial_value_reference, delta_references]`. Der erste Record ist vollständig
definiert. Jede folgende Deltareferenz erzeugt genau den nächsten Record;
auch eine leere Operationsliste zählt als weiterer Record. Leere Folgen
verwenden `[-1, []]`. Es gibt keinen impliziten fremden Ausgangszustand und
keinen Zugriff auf frühere Fälle.

Der Wert bei `root` ist die übrige ursprüngliche Recordstruktur. An den
gebundenen Collectionpositionen steht genau `{"$sequence": index}`. Jede
Sequence muss dort genau einmal verwendet werden. Die unabhängigen
Erfassungsanker bestimmen diese Positionen; sonstige Objekte werden nicht
als solche Platzhalter interpretiert.

## Operationen

- `[path_id, 0, value_ref]`: Wert am Pfad setzen. Der leere Pfad ersetzt den
  ganzen Record. Bestehende Arrayindizes dürfen ersetzt, nicht implizit
  angelegt werden; neue Objektschlüssel sind erlaubt.
- `[path_id, 1]`: vorhandenen Objektschlüssel entfernen. Keine implizite
  Arraylöschung mit Verschiebung und keine Löschung der Recordwurzel.
- `[path_id, 2, [[start, text_ref], ...]]`: nichtleere, geordnete,
  nichtüberlappende Zeichenbereiche eines vorhandenen Strings ersetzen.
  Die Ersetzung behält dessen Länge; `start` zählt Stringzeichen, nicht
  UTF-8-Bytes. Jeder Textwert ist ein referenzierter String. Bereiche müssen
  vollständig im vorherigen String liegen.

Encoderregel: Objekte rekursiv vergleichen; entfernte Schlüssel zuerst,
danach neue/geänderte Schlüssel sortiert. Gleich lange Arrays bis acht
Elemente rekursiv vergleichen; größere oder anders lange Arrays vollständig
ersetzen. Für gleich lange Strings ab 128 Zeichen werden die zusammenhängenden
geänderten Zeichenbereiche explizit kodiert. Andere Änderungen ersetzen den
Wert. Keine Runden-/Fehler-/Policyanpassung und keine verlustbehaftete Numerik.

## Unabhängigkeit und Grenzen

Vor jeder Differenzbildung wird der ursprüngliche Record mit der bereits
gebundenen unabhängigen kanonischen Normalisierung gehasht. Die bisherigen
Erfassungsanker (Anzahl, Bytezahl, SHA-256 je Folge plus übrige Struktur)
bleiben erhalten. Der Decoder importiert weder Encoder noch Policy und
implementiert Referenzauflösung und Zustandsänderungen selbst. Vollständige
kanonische Rekonstruktion wird außerdem gegen die ursprünglichen, extern
gebundenen Kleinfallhashes geprüft. Ein Envelopehash allein genügt nicht.

Unverändert: höchstens 512 KiB gzip und 4 MiB dekomprimiertes Format;
Dictionarywerte, Pfade und Deltas zählen zusammen gegen 4 MiB. Zusammen
höchstens 65.536 Tabelleneinträge, 262.144 Referenzkanten, 65.536 Recordindizes
und 16 Collections. Anfangszustands-, Pfad-, Wert-, Delta- und Wurzelreferenzen
werden gezählt. Einzelrecords einschließlich Zeilenumbruch bleiben unter
262.144 Byte. Werteexpansion und Tiefe werden vor Rekonstruktion begrenzt;
nach jeder angewandten Operation wird die Recordgrenze geprüft.

Der Encoder hält höchstens einen vorherigen Record je Collection, insgesamt
höchstens 16 × 262.144 kanonische Byte, sowie begrenzte Tabellen. Deren
Pythonobjektbelegung ist größer und wird vollständig im gemeinsamen harten
512-MiB-Windows-Job erfasst. Iteratoren/Decoder halten jeweils ihren aktuellen
Record; es gibt keinen Cache einer vollständigen rekonstruierten Historie.
Einzelne Kopien und Serialisierungsbuffer sind ebenfalls prozessweit gezählt.

Temporär entsteht nur eine gzip-Partialdatei; nach Erfolg Umbenennung im
gleichen Verzeichnis, keine zusätzliche Dateikopie. Höchstens 64 MiB temporäre
Daten; kein zusätzlicher Rohspool. Schreibfehler entfernen die Partialdatei.
Der Cleanup gibt Tabellen, Indizes und vorherige Records frei.

Die kleinen Archive und eine gezielte Integration mit ihren bestehenden
Handfolgen sind der gesamte Prüfbereich. Der frühere abgebrochene Größenlauf
bleibt verbraucht; seine fehlenden Daten werden nicht aus Hashankern erzeugt.
