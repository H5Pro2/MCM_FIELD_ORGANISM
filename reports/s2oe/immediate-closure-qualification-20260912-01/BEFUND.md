# Abschlussanschlüsse: vier neue Prüfungen bestanden

`immediate-closure-qualification-20260912-01`: genau ein fokussierter Aufruf,
**4/4 bestanden**. Die historischen 22/22 und 7/7 wurden nicht wiederholt.
Keine reale e03-Verarbeitung. Alle Gates nach dem Aufruf False.

## Geprüfte Ergänzungen

Der bestehende Kontrollaufruf meldet nach Initialisierung, Leerhinweis,
Formation und Wiederhinweis unveränderliche kanonische Fortschrittsbelege.
Der Dateieinstieg übernimmt jeweils den neuesten Beleg vor weiteren
Prüfungen. Ein Fehler vor Formation erhält den Leerzustand und einen
abgeschlossenen Hinweis; nach Formation bleiben zwei Zustände, die reguläre
Transaktion und zwei abgeschlossene Ereignisse verfügbar. Kein Rollback.
Es gibt weiterhin keinen Feldzweig in dieser Kontrolle; Feldaufrufe sind null.

Der unveränderte Grundledger prüft die eigenen historischen Eingangsbytes,
Metadaten, Quellen, Verifikation und Gesamtsumme. Der Anschluss ergänzt
physische Referenz- und Ausgabedateigrößen, zählt dieselbe Referenzdatei
nicht mehrfach und prüft feste Einzelgrößen vor Veröffentlichung.
Erfolg, Fehler vor Recordpublikation und Fehler nach Recordpublikation sind
getrennte Vorab-Alternativen. Teilbeleg und Gesamtbeleg werden nicht pauschal
als gleichzeitige Pflichtablagen addiert; tatsächlich vorhandene Dateien
bleiben immer mitgezählt. Die Abschlussbilanz zählt ihre eigene exakte Größe.

Die vier nativen neutralen Tests prüfen:
1. Regulären vollständigen Abschluss mit einmaliger Verifikation und
   Istsumme gleich allen tatsächlich vorhandenen Dateien, Bindung und Eltern.
2. Primärfehler vor Formation, erhaltenen Leerabruf, keine Verifikation
   oder Auswertung und zuverlässig geschlossenes Gate.
3. Primärfehler nach Formation, erhaltene Generation 1 samt Transaktionsbeleg,
   keine Auswertung und vollständige Fehlerbilanz.
4. Metadatenüberschreitung vor Start mit vollständiger Budgetdiagnose und
   ohne angelegte Ergebnisablage.

Auch beim Fehlerabschluss wird nicht gekürzt: vollständiger ursprünglicher
Fehler und vorhandene Teilbelege bleiben erhalten. Falls der Fehlerbeleg
selbst die Grenze überschreitet, weist die Istbilanz dies aus; ein Fehler
beim Sichern ersetzt die ursprüngliche Ausnahme nicht. Die künstlich
injizierten Fehler erreichten keine solche zusätzliche Speicherstörung.

## Bindungen und Aussagegrenze

Vorbilanz: **2.130.361 / 4.194.304 Byte**; Metadatenreserve 98.304 / 131.072
ausschließlich für die Qualifikation. Reale Sitzung weiterhin 65.536 Byte.
Vollständiges Log 525 / 65.536 Byte.
Inventar vor/nach identisch:
`744561ab75adb3cad260c0a154810c508aeaa2423465b42c2051dd1ab727a301`.
Präregistrierung:
`1a21fc60d17775a4fd2d8becbe9e27db8d45a8973fc8172f3ff9d31828bd0f8f`.

Vier synthetische Eingangsfixtures; davon drei Kontrollaufrufe. Zwei reguläre
Formationen, acht öffentliche Scans und ein unabhängiger Verifikationsaufruf.
Keine neue Rezeptoranalyse oder reale Quelle. Die Testdaten lagen temporär;
die Prüfungen erfassen deren vollständige Abschlussdateien vor Bereinigung.
Es wird keine zusätzliche dauerhafte Ablage dieser neutralen Zustände behauptet.

Die Freigabe des echten Kontrolllaufs ist separat. Die neue Quelleinventarisierung
bindet die Änderungen am Fortschritts- und Abschlussanschluss ausdrücklich;
alte Quellhashes werden nicht als aktuelle Zulassung ausgegeben. Die alte
Präsentations- und Verifikationsdeckung bleibt für die unveränderten Bereiche
referenziert, nicht als neu ausgeführte Gesamtqualifikation dargestellt.
