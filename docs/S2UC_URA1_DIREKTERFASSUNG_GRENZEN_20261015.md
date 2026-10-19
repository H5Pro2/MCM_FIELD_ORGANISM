# URA1: Grenzen der direkt referenzierenden Erfassung

Diese Ergänzung beschreibt ausschließlich den neutralen Erfassungs-/Exportpfad.
Archivschema und unabhängiger Decoder bleiben URA1_JSON_DAG_V1. U/R, Referenzen
und Ereignisprüfungen bleiben unverändert.

Beim append wird der vollständige Record auf seine serialisierte Größe geprüft
und unmittelbar in einen gemeinsamen Teilbaum-Dictionary überführt. Jede
Collection speichert nur die geordneten Knotennummern. Beim Prüfen wird ein
Record rekonstruiert; beim paarweisen Vergleich sind die aktuellen Records
beider Arme vorhanden. Es gibt keine expandierte Historienliste und keine
JSONL-Datei. Gleiche Teilbäume dürfen dieselben Knoten verwenden; Originalindex,
Metadaten, Tickets, Zellen und Arrayreihenfolge sind weiterhin Teil der Daten.

| Größe | Feste Grenze je Fall |
| --- | ---: |
| Knoten | 65.536 |
| Referenzkanten in Knoten | 262.144 |
| Geordnete Recordindizes über alle Collections | 65.536 |
| Collections | 16 |
| Kanonischer Einzelrecord einschließlich Zeilenumbruch | 262.144 Byte |
| Summe serialisierter Dictionaryknoten | 4.194.304 Byte |
| Vollständiges dekomprimiertes Archivformat | 4.194.304 Byte |
| gzip-Archiv | 524.288 Byte |
| Temporäre Dateien zusammen | 67.108.864 Byte |
| Gemeinsamer harter Windows-Job | 536.870.912 Byte |

Dictionarybytes sind nicht Python-Heapbytes. Die Python-Tabelle, Schlüssel,
Referenzen, Listenüberallokation, Konvertierungsbuffer und Rekonstruktionsobjekte
liegen vollständig im Prozessbudget. Die Anzahl und serialisierte Datenmenge
aller persistenten Erfassungsobjekte sind separat beschränkt. Es gibt keinen
unbeschränkten Rekonstruktionscache. Material und Prüfhülle bleiben auf die
vorhandenen kleinen Fälle beschränkt; für größere Eingänge ist das keine
allgemeine Implementierungsfreigabe.

Finalisierung referenziert die bereits erfassten Knoten. Das kompakte Dokument
wird als begrenzter JSON-Buffer kodiert und einmal gzip-komprimiert. Ein
String-/Bytes-Zwischenbuffer im RAM bleibt möglich und wird prozessweit gezählt.
Auf Platte entsteht ausschließlich eine gzip-Partialdatei im Zielverzeichnis.
Nach vollständigem Schreiben wird sie im selben Verzeichnis umbenannt;
dadurch entsteht keine zweite Dateikopie. Es werden keine Dictionarydateien,
Journale oder rekonstruierten Historien auf Platte angelegt. Die temporäre
Dateigröße wird nach beiden Schreibabschnitten erfasst, einschließlich vor
Fehlerinjektion. Ihre logische Bytezahl ist von Dateisystemblockbelegung zu
unterscheiden. Erfolgreich veröffentlichte Archive werden separat bilanziert.

Die kanonische Originalbytezahl und der externe Originalhash stammen in dieser
Qualifikation aus dem unveränderten gebundenen Kleinfallbeleg. Der Encoder
darf sie nicht als selbst bestätigtes Ergebnis ausgeben: Erst der unabhängige
Decoder rekonstruiert sämtliche Bytes und bestätigt beide gegen diesen Bezug.
Der volle Vergleich umfasst damit auch die Ereignisreihenfolge und jedes
Original-, Hypothesen-, Ticket- und Zellfeld. Dies ist eine Vergleichshülle
für vorhandene Belege, kein fertiger Erzeugungs-/Abnahmevertrag für bisher
unbekannte große Forschungsrecords.

Grenzüberschreitung oder Schreib-/Encoderfehler beendet die jeweilige Arbeit.
Partielle Dateien werden entfernt; beim Verlassen des Stores werden sämtliche
Knoten-, Schlüssel- und Indextabellen freigegeben. Der Armfehlerpfad wird durch
eine während der Erfassung injizierte Indexgrenze gesondert geprüft.
