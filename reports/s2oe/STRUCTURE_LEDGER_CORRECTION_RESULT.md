# Struktur-/Lage-Vergleich: ergänzender Ledgernachweis

## Prospektive administrative Bindung

Version `structure-location.ledger.v2-metadata98304` gilt ausschließlich für
den privaten Vergleich: Metadaten höchstens **98.304 Byte**. Historische
Defaults bleiben bei 65.536 Byte. Gesamtgrenze **4.194.304 Byte**,
Verifikation 262.144 Byte und die beiden einzelnen Ergebnis-/Teilbeleggrenzen
von jeweils 1.048.576 Byte bleiben unverändert.

`tools/_structure_comparison_ledger.py` zählt Referenzen nach tatsächlicher
Klasse. Gleicher Pfad mit gleicher Bindung wird einmal gezählt; widersprüchliche
Bindungen scheitern. Physische Kopien unter anderen Pfaden zählen vollständig.
Software ist Quellenbeleg, Pläne/Logs/Berichte sind Metadaten, native Ergebnisse
und Versiegelung sind Evidenz, Verifikationsbelege eine eigene Klasse.
Einzelreferenzen bleiben in der Vorregistrierung verfügbar; die kompakte
Bilanz bindet ihre Liste per Digest und nennt Klassensummen.

Die einzige Änderung des funktionalen Vergleichsmoduls betrifft die Weitergabe
an dieses Ledger und die getrennten Abschlussalternativen. Ein AST-Abgleich
bestätigt die unveränderten übrigen Funktionskörper. Der alte vollständige
Modulstand wurde vor der Änderung unter `previous_comparison.py` archiviert;
sein Hash entspricht der damaligen Qualifikationsbindung. Keine neuen
Rezeptor-, Form-, Distanz-, Auswahl- oder Memoryregeln.

## Einmalige ergänzende Prüfung

`structure-location-ledger-qualification-20260912-01`: **8/8 bestanden**,
genau ein neuer Testaufruf. Geprüft: vollständige Referenzzählung einschließlich
physischer Kopien, widersprüchliche Referenz, Klassenzuordnung, Gleichstand
und Überschreitung bei Klassen-/Gesamtgrenzen, getrennte Arbeitsbudgets,
Abschlussalternativen mit Berichtreserve sowie unveränderte historische Grenze.

Die vorherigen **12/12 bleiben ein separater funktionaler Teilnachweis**.
Sie wurden nicht wiederholt und nicht als neue Gesamtpasszahl ausgegeben.
Auch die sechs Quellenprüfungen wurden nicht wiederholt. Der ergänzende
Aufruf führte null Bildproduktionen, Rezeptor-/Formaufrufe, Differenzen oder
Rezeptorverifikationen aus. Bestehende Quellenversiegelung unverändert.

## Arbeit getrennt gebunden

| Bereich | Differenzen | Weitere Arbeit |
| --- | ---: | --- |
| Späterer realer Einzelvergleich einschließlich Direktrechnung | maximal 19.008 | 864 primäre Exaktgleichheiten; 24 Kriterien |
| Dessen unabhängige Offline-Verifikation | 0 neue Differenzen | höchstens 19.008 gespeicherte Terme, 88 Summen, 864 Exaktgleichheiten |
| Frühere neutrale Funktionsqualifikation | 32.256 | 15 Rezeptor-/Formaufrufe, 120 Kriterienauswertungen, 1.440 primäre Exaktgleichheiten |
| Frühere neutrale Verifikatorprüfungen | 0 neue Differenzen | 7 Versuche, 51.264 erreichte Termprüfungen, 222 Summen, 2.304 Exaktgleichheiten |
| Neue administrative Qualifikation | 0 | ausschließlich acht Ledger-/Arbeitsbindungstests |

Die Zahlen der früheren neutralen Arbeit sind **nachträglich aus dem
erreichten Aufrufpfad abgeleitet**, keine damalige Vorabbindung und keine
nachträglich eingefügte Instrumentierung. Die neue Vorregistrierung markiert
sie ausdrücklich `retrospective`. Realvergleich und Verifikation besitzen
getrennte Grenztabellen; neutrale Arbeit darf diese nicht auffüllen oder
verkleinern.

## Vollständige gemeinsame Bilanz

Vor dem neuen Test: Metadaten maximal 94.036 / 98.304 Byte; Gesamtsumme
Erfolg 1.886.664, Fehler 2.935.240 Byte. Test-, Aufruf-, Quellen-, Archiv-,
Qualifikations-, Autorisierungs- und Abschlussbindungen waren enthalten.

Nach bestandenem Test und konkreter Einmalbindung:

| Klasse | Erfolg | Fehler |
| --- | ---: | ---: |
| Software-/Quellenbelege | 345.840 | 345.840 |
| Metadaten einschließlich Reserven | 81.677 | 81.677 |
| Native Evidenz einschließlich Referenzen | 1.438.061 | 2.486.637 |
| Verifikationsbelege einschließlich Referenzen | 8.727 | 8.727 |
| Gesamt | **1.874.305** | **2.922.881** |

Erfolg enthält Auswertung, aber keinen Fehler-/Teilbeleg. Fehler enthält
konservativ vollständigen Gesamt- und Teilbeleg sowie Verifikation, aber
keine veröffentlichte Auswertung. Nach erfolgreicher Auswertung folgt im
Try-Block nur Rückgabe; Fehlerformen vor ihrer Veröffentlichung benötigen
keine zweite Auswertungsablage. Die beiden Formen werden nicht addiert.
Ein Fehler bei der abschließenden Bilanz selbst ist damit nicht als beliebig
großer Diagnosefall garantiert; die Vorbindung ist endlich.

Der unveränderte frühere Nachtrag mit **5.702 Byte** ist vollständig als
aktive Metadatenreferenz gezählt. Zusätzlich **8.192 Byte** für diesen neuen
Abschlussbericht: genügend für den alten Berichtsumfang plus 2.490 Byte
zusätzliche Bilanz-/Abschlussdarstellung. Keine Kürzung und keine Umklassifizierung.
Die noch fehlende Autorisierung ist mit 512 Byte reserviert; die Bilanzdatei
mit 2.048 Byte. Reserven sind keine gemessenen realen Ergebnisgrößen.

## Konkrete Einmalbindung, noch gesperrt

Datei:
`reports/s2oe/structure-location-ledger-qualification-20260912-01/main-binding.json`

SHA-256:
`e9267009a3211d2fc992e37d32a5edb2d89733cf357847f0ebab44befb09a393`

Neue Bindung für weiterhin unbenutzte ID
`structure-location-comparison-20260912-01`; sie löst die vorherige,
nie ausgeführte Bindung ab. Diese bleibt im Archiv erhalten, ist aber keine
aktive Laufvoraussetzung. Ausführbarer Dateieinstieg nach separater Freigabe:
`reports.qualify_structure_ledger_once`, Modus `run`, Arbeitsverzeichnis
`C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`.

`authorized=false`; noch keine `authorization.json`, kein Ergebnisverzeichnis
des Hauptlaufs. Ein späterer Aufruf verlangt eine separate, exakt an Lauf-ID
und Hauptbindungsdigest gebundene Autorisierung. Quellenhashes werden vor
jedem Rezeptoraufruf geprüft; ein Gesamtbeleg, eine read-only Verifikation,
danach getrennte Auswertung. Kein Retry.

Offene Grenzen gesammelt: reale Quellen-/Formgültigkeit und fachliche Trennung
noch ungeprüft; keine numerische Offline-Rekonstruktion aus Roh-RGB; kein
universeller Beweis beliebiger Fehlerausgabegrößen; keine Aussage über
Objektidentität, Korrespondenz oder Lernbindung. Die neue administrative
Deckung ersetzt keinen realen Funktionsbefund. Gates False, kein Hauptlauf.
