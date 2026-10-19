# URA1: Laufzeitmachbarkeit der 32-Fall-Serie

Stand 2026-10-15. Ausschliesslich vorhandene Messungen, Codelektüre und
Dokumentation. Keine Implementierung, Benchmarks, Policy-Läufe, Quellen- oder
Bootstrapmatrix-Erzeugung. Der bestandene Einzelgrössenlauf und sein verbrauchter
Marker bleiben unverändert. Keine neue Ausführungsfreigabe.

## Entscheidung

Die 32-Fall-Serie ist unter dem bisherigen Gesamtzeitvertrag von 3600 Sekunden
**nicht als machbar nachgewiesen**; die vorhandene Messung spricht gegen eine
unveränderte Übernahme der aktuellen Hülle. Genau eine Empfehlung: ein separat
zu beauftragendes, begrenztes Optimierungspaket für die wiederholte kanonische
Recordverarbeitung. Keine Änderung des Zeitbudgets in diesem Auftrag.

## Noch offene Forschungsvoraussetzungen

- Quellenprüfung: unabhängige Prüfung des festgelegten Rezepts, der 32 neuen
  D-Geschichten, Ziehungsgrenzen, Kontingenzen, Orientierungen und Kausalität;
  vollständige Versiegelung vor dem ersten Forschungsarm, keine Ergebniswahl.
- Statistik-/Bootstrapprüfung: ein Primärkontrast U−R über alle 256 Q-Ziele je
  Geschichte; unabhängige Prüfung der exakten Aggregation, 10000 geschichteten
  Paarziehungen, 320000 Matrixbytes, Quantile und vollständigen Nebenbilanzen.
- Serienressourcen: Gesamtlaufzeit einschliesslich Quellenvalidierung, 64 Armen,
  aller Ereignis-/Referenzprüfungen, Archivierung, unabhängiger Archivprüfung,
  Statistik und Abschluss; ferner gemeinsamer Speicher, temporäre Daten,
  Gesamtexport und Abbruch/Cleanup über alle 32 Fälle. Ein Fallpeak wird weder
  blind mit 32 multipliziert noch als Serienbeleg ausgegeben.
- Vorstartbindung: erst nach diesen Nachweisen endgültigen Seriencode, Quellen,
  Matrix, Runtime, Aufruf, globale Grenzen und exklusiven Startmarker binden;
  anschliessend gesonderte Einmalfreigabe auf diesen SHA.

Die bereits abgenommenen U/R-, Referenz-, Codec-, Integritäts- und
Einzelfallnachweise werden hierfür nicht unverändert wiederholt.
Grundlage: [Konzeptvertrag, Abschnitte 5–7](S2UC_URA1_AUSWAHLABLATION_KONZEPT_20261014.md).

## Gemessene Phasen und konkrete Mehrfacharbeit

Quelle: [result.json](../reports/s2uc/ura1-delta-size-neutral-20261015-01/result.json).

| Phase | Gemessen | Inhalt und vermeidbare Mehrfacharbeit |
|---|---:|---|
| Erfassung/Referenzen/Anker | 640,984 s | Beide Arme, Snapshots, unabhängige Referenzen, Deltaerfassung sowie anschliessende Paarvergleiche. Kein reiner Policyzeitwert. |
| Envelope-Prüfsumme/Kodierung | 220,550 s | Vollständige Rekonstruktion aller Collections durch full_record_digest, erneute Normalisierung/Serialisierung und Hashbildung; danach erst JSON/gzip-Ausgabe. Keine isolierte gzip-Messung. |
| Unabhängige Dekodierung | 329,786 s | Tabellenvalidierung, vollständige unabhängige Rekonstruktion, Anker-/Struktur-/Envelopeprüfung; zusätzlich komplette Recordserialisierung nach jeder Deltaoperation. |
| Cleanup | 0,314 s | Freigabe und Abschluss. |
| Supervisor gesamt | 1193,505 s | Enthält Start-/Bindungs- und Supervisorüberhang; Worker insgesamt 1191,638 s. |

Codebelege (Zeilen des unveränderten gebundenen Stands):

1. [size_once.py:136](../tools/s2uc_ura1_delta_size_once.py#L136) ruft vor write_archive
   full_record_digest auf. [capture_integrity.py:50](../tools/_s2uc_ura1_capture_integrity.py#L50)
   durchläuft sämtliche Folgen erneut; canonical (:7) führt dumps→loads→dumps
   aus. [delta_encode.py:105](../tools/_s2uc_ura1_delta_encode.py#L105) rekonstruiert
   dabei jeden Record und erzeugt jeweils deepcopy. Das sind zusätzliche
   Verarbeitungsschritte, kein zweiter wissenschaftlicher Referenznachweis.
   Die Kleinfallkodierung von 0,092 s ist nicht direkt vergleichbar: dort
   verwendet [delta_qualify.py:82](../tools/s2uc_ura1_delta_qualify.py#L82) bereits
   vorhandene Originalprüfsummen; der neue vollständige Envelope-Durchlauf fehlt.
2. [delta_size_engine.py:126](../tools/_s2uc_ura1_delta_size_engine.py#L126) liest
   Ereignisse für Paarvergleiche, Feedback und Prognosen für Metadatenvergleiche
   und Prognosen erneut für differences. Danach liest die Einstiegshülle
   Feedback/Prognosen erneut für Vollständigkeitslisten (:122–127), gefolgt vom
   vollständigen Envelope-Durchlauf. Gleiche Inhalte werden mehrfach dekodiert,
   kopiert und serialisiert. Die Prüfungen müssen bleiben; ihre getrennten
   Durchläufe sind keine fachliche Voraussetzung.
3. [delta_decode.py:85](../tools/_s2uc_ura1_delta_decode.py#L85) serialisiert nach
   **jeder Operation** den gesamten state zur Recordgrenzenprüfung (:115) und
   nochmals beim Yield (:116). Die Grenze muss nach jeder Operation gelten;
   eine exakt fortgeschriebene kanonische Bytezahl könnte dieselbe Prüfung ohne
   wiederholte Vollserialisierung erfüllen. Das ist eine Optimierungshypothese,
   noch kein implementierter oder gemessener Ersatz.
4. [delta_encode.py:70](../tools/_s2uc_ura1_delta_encode.py#L70) normalisiert vor
   dem Codec für den unabhängigen Anker; danach nochmals json.loads für den
   Delta-Vorzustand. same (:59) serialisiert gleiche Container erneut. Hier ist
   weiteres Mehrfachverarbeiten erkennbar, aber kein separater Zeitanteil belegt.

Der letzte Fortschrittsbeleg meldet beide Arme bei Frame 1024 nach 547,595 s.
Bis zum Phasenende verbleiben ungefähr 93,389 s für abschliessende Operationen,
Paarvergleiche, Vollständigkeit und Ankerablage. Diese Differenz ist nur eine
zeitliche Eingrenzung aus bestehenden Zeitmarken: weder isolierte Paarprüfzeit
noch vollständig vermeidbarer Aufwand.

## Messinstrumentierung und unverzichtbare Prüfungen

tracemalloc läuft über alle Workerphasen ([size_once.py:96](../tools/s2uc_ura1_delta_size_once.py#L96)).
Der Supervisor prüft ungefähr alle 20 ms Verzeichnisgrössen, Phase und zwei
Prozessspeicherwerte (:187–204); supervisor.json dokumentiert 45774 Samples.
Die Warteintervalle überlappen die Workerarbeit und dürfen nicht als addierbare
Einsparung gezählt werden. sys.setprofile erfasst interne Aufruf-/Rückkehrereignisse
([delta_size_engine.py:60](../tools/_s2uc_ura1_delta_size_engine.py#L60)); sein Filter
wird auch für nicht ausgewählte Funktionsereignisse aufgerufen.

**Kein belastbarer Sekunden- oder Prozentanteil** für tracemalloc, Profiling,
Sampling, Delta-Differenzbildung oder reine Policyarbeit ist vorhanden.
Es fehlen vergleichbare Messungen mit isolierten Schaltern. Python-Peakwerte
sind Speicherwerte, keine Zeitanteile; frühere Codecvarianten sind keine
kontrollierte Messung des Instrumentierungsaufwands. trace=True umgeht ausserdem
ResourceMeter.measure_full; dessen deep-Messung pro Operation ist deshalb
keine Erklärung dieser Laufzeit.

Unverzichtbar bleiben alle internen/äusseren Ereignisse, getrennte unabhängige
Referenzen, vollständige Bestands-/Zell-/Ticket-/Hypothesenprüfungen,
Erfassungsanker vor Encoderverarbeitung, vollständige Zielmengen sowie die
unabhängige Archivprüfung. sys.setprofile einfach abzuschalten würde Ereignisse
entfernen und ist keine zulässige Optimierung. Harte Job-, Zeit-, Export- und
Recordgrenzen samt Cleanup bleiben erhalten. Zusätzliche Python-Allokationstraces
sind Messinstrumentierung; ihr möglicher Aufwand wird hier weder entfernt noch
als gesicherter Gewinn eingeplant.

## Abschätzung und verbleibende Unsicherheit

Lineare Abschätzung unter der ausdrücklich unbewiesenen Annahme gleicher Kosten
wie beim periodischen Handfall: 32 × 1193,505 s ≈ 38192 s = **10,61 Stunden**,
beide Arme bereits enthalten. Dazu fehlen noch serielle Quellen-/Statistik- und
Abschlussarbeiten. Ein Stundenbudget erlaubt höchstens 112,5 s je Fall im Mittel
**vor** diesen Zusatzkosten: erforderlich wäre mehr als Faktor 10,61 gegenüber
diesem Beleg. Keine Prognose für tatsächlich andere Geschichten.

Selbst hypothetischer Wegfall der gesamten 220,550-s-Kodierungsphase ergäbe
noch rund 8,65 Stunden für 32 gleich teure Fälle. Allein die unverändert gemessene
Decoderphase entspräche rund 2,93 Stunden. Daraus folgt: ausschliessliche
Beseitigung des Envelope-Durchlaufs kann die Stundenmachbarkeit nicht begründen.
Nichtrepetitive Folgen, andere Deltazahlen, Rechnerlast, Statistik und Serienexport
sind ungeprüft. Ein Erfolg der vorgeschlagenen Optimierung ist nicht zugesichert.

Die 3600 s gelten weiterhin für die **gesamte geplante Serie**, nicht je Fall.
Keine Umgehung durch Teilstarts, Fallgruppen oder ausgelagerte ungezählte
Archivprüfung. Eine spätere Budgetänderung wäre eine ausdrücklich neue
Entscheidung vor Forschung und würde keinen alten Versuch nachträglich lockern.

## Genau ein nächstes Umsetzungspaket – separat zu beauftragen

**Begrenzte Reduktion wiederholter kanonischer Recordverarbeitung.** Neue,
separat gebundene Variante; historische Dateien, Archive und Marker unverändert.
Paar-/Vollständigkeits-/Diagnoseprüfungen pro Folge bündeln und den weiterhin
geprüften Envelopehash in einen ohnehin erforderlichen vollständigen Durchlauf
integrieren; keine Ableitung des Gesamthashes aus Teilhashes. Im unabhängigen
Decoder die Recordbytezahl exakt nach jeder Operation fortschreiben und jeden
fertigen Record nur einmal kanonisch für Anker und Envelope serialisieren.
Keine Änderungen an U/R, Ereignisschema, Deltaformat oder Prüfumfang.

Abnahme des Pakets: bitgleiche kanonische Inhalte und Erfassungsanker an den
vorhandenen Belegen; gezielte Grenz-/Mutationsfälle für UTF-8/JSON-Escapes,
Zahltypen/negatives Null, Set/Delete/Textspans und Überschreitung auch in einem
Zwischenzustand; gleiche terminale Fehler und bounded Speicher. Erst im separat
beauftragten Paket fokussierte Codec-/Kleinfallzeitmessungen mit getrennten
Zeiten für Paarprüfung, Envelope, Ausgabe und Decoder sowie kenntlicher
Instrumentierung. Bestehende grosse Archive dürfen dabei nur im ausdrücklich
beauftragten Rahmen gelesen werden; kein neuer 1024-Frame-Policy-Lauf aus
historischer Einmalfreigabe.

Danach genau eine erneute Serienmachbarkeitsbewertung mit allen Prüfkosten und
Unsicherheitsreserve. Keine offene Optimierungsschleife und keine versprochene
Forschung innerhalb einer Stunde. Bleibt die Zeitlücke, geht dieser konkrete
Befund zur Entscheidung zurück; hier wird kein zweiter Alternativauftrag erteilt.
