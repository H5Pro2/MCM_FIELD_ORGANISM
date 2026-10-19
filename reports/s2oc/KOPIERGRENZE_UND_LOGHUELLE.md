# OC: Kopiergrenze und vollständige Loghülle

Freigegeben ist nur die administrative Korrektur und eine bedingte neutrale
Qualifikation. `s2oc-shared-administration.v2` ersetzt keine historischen
Befunde. Der alte 24/26-Beleg bleibt `NOT_QUALIFIED`.

`transform()` kopiert nur die beiden administrativen Wurzeln und gegebenenfalls
den Ausführungscontainer. Native Unterstrukturen werden dabei nur gelesen.
Die nach außen gegebenen Pack-/Unpack-Ergebnisse sind über die vorhandene
kanonische JSON-Darstellung vollständig abgetrennt. Der Zustandspool wird
nicht rekonstruiert; sein Codec und seine Validatoren bleiben unverändert.

Die gesamte betroffene Suite wird unter
`s2oc-shared-closure-qualification-20260910-02` einmal ausgeführt: 30 Gruppen,
keine Übernahme historischer Passzahlen. Vier zusätzliche Gruppen prüfen
den echten Nullzustandspool ohne Schreibzugriff, getrennte Pack-/Unpack-Ausgaben
und die vollständige Logwiederherstellung. Zwei kurze neutrale Sitzungen
bleiben bei drei Audio-/NJ- und zwei visuellen Analysen; kein realer Hauptlauf.
Ein Nullzustand für die Codecprüfung ist keine zusätzliche Formation.

Die vorhandene unveränderte Verpackung `s2oc.evidence-zip.v3` übernimmt alle
sechs Qualifikationsdateien bytegetreu. Der unabhängige Verifikator prüft
Index, Klassifikation, rekonstruierte Bytes und Hashes. Keine neue Kompression,
keine gekürzten Logs. Das bestehende Format begrenzt Einzelinhalt auf
4.194.304 Byte, Entpackarbeit auf 16.777.216 Byte, Index auf 65.536 Byte
und ausgewiesenen Entpackspeicher auf 10.485.760 Byte.

Unverändert: Qualifikation 4.096 Byte einschließlich äußerem Prüfbeleg;
Bericht 512, Metadaten 65.536, Quellen 174.080, Zusatzhülle 262.144,
Gesamt 4.194.304. Die alte 256-Byte-Logannahme entfällt. Die vorhandene
Paketklassifikation bleibt erhalten: komprimierte Qualifikationsobjekte mit
ihrem ZIP-Overhead plus höchstens 768 Byte Prüfbeleg nutzen die 4.096 Byte.
Der Index samt ZIP-Abschluss nutzt höchstens 2.048 Byte der Metadatenklasse.
Damit werden höchstens 5.376 Byte Archiv und 768 Byte Prüfbeleg referenziert.
Physisch vorhandene Originale sind zusätzlich zu zählen. Sie werden erst
nach erfolgreicher byteweiser Paketprüfung ausschließlich in der neuen
Qualifikationsablage entfernt; bei Verpackungsfehler bleiben sie vollständig.

Vor dem Test werden Code, Materialisierer, Tests, Aufrufdatei, Quelleninventar
und diese Dokumentation gebunden. Die 22 Fortschrittspositionen und beide
Abschlussalternativen werden vollständig bilanziert. Zusätzlich wird eine
synthetische vollständige Fehlerhülle mit einem Traceback je Prüfgruppe,
allen Aufrufrahmen und Budgetdiagnostik verpackt. Sie ist keine ausgeführte
Qualifikation und kein universeller Komprimierbarkeitsbeweis beliebiger Logs.
Unvorhergesehene größere Ausgaben dürfen niemals gekürzt werden; ihre
Überschreitung beendet die Qualifikation als nicht bestanden.

Die Vorregistrierung legt Fehlerhülle, beide Größenbilanzen und Codehashes
vor dem einzigen Testaufruf fest. Passt schon diese Fehlerhülle nicht,
endet der Einstieg mit null Testaufrufen. Keine zusätzliche Reserve,
keine Auswahl eines günstigeren Fehlerbeispiels und kein Retry.
