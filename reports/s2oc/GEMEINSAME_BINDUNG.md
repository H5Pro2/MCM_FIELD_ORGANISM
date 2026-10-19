# Gemeinsame administrative OC-Bindung

Version: `s2oc.shared-administration.v1`. Privater, begrenzter Anschluss;
keine reale Laufgenehmigung. Historische Zulassungen und Befunde bleiben
unverändert. Die Qualifikation gilt nur für die neu gebundenen Quelldateien.

## Inhalt und Auflösung

`common.json` enthält das vollständige unveränderliche Aufrufermanifest,
Referenzen mit Pfad, Größe und SHA-256, die feste Profil-/Regelbindung,
Runtimekonfiguration sowie den aktuellen Qualifikationsverweis.
`record.json` und `session.json` referenzieren diese konkreten Felder über
eine geschlossene, versionierte Referenzform und den Hash der gesamten
gemeinsamen Datei. Der Auflöser erzeugt daraus die ursprünglichen nativen
Belegformen und prüft ihre ursprünglichen Digests. Wahrnehmungswerte,
Zustandsdarstellung, Generationen, Reihenfolge und Hinweise werden nicht
transformiert. Ein fehlender Inhalt oder widersprüchlicher Verweis wird
abgewiesen; keine Ersatzwerte oder Rekonstruktion aus Digests.

Die feste NG-Komponentenliste wird über die ausdrücklich versionierte Gruppe
`ng-source-paths-v1` aus dem vollständig verfügbaren Codeinventar aufgelöst.
Ihre Reihenfolge stammt aus den gebundenen `SOURCE_PATHS`; jeder Codehash muss
als Inhalt im Inventar vorhanden sein. Der rekonstruierte native Bindungsdigest
wird geprüft. Die Codehashlisten werden nicht nochmals in jedem Regelbeleg
abgelegt. Keine Wahrnehmungswerte sind Teil dieses administrativen Verweises.

Die gemeinsame Datei zählt vollständig zur Metadatenklasse. Die vorhandene
native Klassifikation des OC-Ledgers bleibt bestehen; Präfixschritte zählen
als Schritte. Alle tatsächlich erforderlichen Referenzdateien zählen einmal
als physische Abhängigkeit. Wiederholte administrative Verweistokens bleiben
gezählte Bytes. Erfolg und Fehler sind alternative vollständige Abschlüsse,
keine Summe zweier sich ausschließender Kernbelege.

Die Aufruferdatei wird beim Dateieinstieg nicht nochmals kopiert: Ein maximal
512 Byte großer `common-reference.json` verweist auf ihren verfügbaren Inhalt.
Verweis und Inhalt zählen beide. Direkt eröffnete neutrale Sitzungen legen
die gemeinsame Datei genau einmal lokal ab.

## Aktive Software und Abschluss

- `tools/_s2oc_shared_binding.py`: geschlossene Auflösung, aktuelles transitives
  Codeinventar und physische Bilanz am bestehenden Ledger.
- `tools/_s2oc_bound_session.py`: dieselbe OC-Sitzungsmechanik, ein Materialisierer
  und eine Runtime; Budgetfehler gelangen mit Primärdiagnose in `_fail()`.
- `tools/_s2oc_shared_verification.py`: Referenzprüfung und unveränderte direkte
  Zustands-/Scanprüfung; keine alte pauschale OB-Qualifikationsreserve darüberlegen.
- `reports/s2oc/run_bound_session_once.py`: dateigebundener Einmaleinstieg,
  Fehlerabschluss, eine unabhängige Verifikation und gezählte Abschlussdateien.
  Keine CLI-Option öffnet das Hauptgate. Funktionsauswertung bleibt getrennt.
- Materialisierer: optionale Zählung der vom Leseaufruf zurückgegebenen Bytes
  vor Hashprüfung und Analyse; alter Standardaufruf und seine Zähler bleiben
  erhalten. Betriebssysteminterne Leseversuche ohne zurückgegebene Bytes werden
  damit nicht als gemessene Bytes behauptet.

Die Quellenidentität umfasst sämtliche transitiven lokalen Module sowie
Test-, Aufruf- und Dokumentdateien. Software bleibt installierte Voraussetzung;
das vollständige Pfad-/Hash-/Byteinventar ist ein gezählter Quellenanhang.
Die neuen eigenen Anschluss-, Test-, Aufruf- und Dokumentdateien werden zudem
als konkrete Referenzdateien in der Qualifikationsbilanz mitgezählt. Es gibt
keine Übernahme historischer Passzahlen. Für einen späteren Lauf werden eine
neue Manifestbindung und das neue bestandene Qualifikationsergebnis benötigt.

## Unveränderte Grenzen und Vorbedingung

Metadaten 65.536 Byte; Quellenklasse 174.080; gemeinsame Zusatzhülle 262.144;
Gesamt 4.194.304; Verifikation 262.144. Native Einzelgrenzen bleiben insbesondere
98.304 Byte pro Zustand und 16.384 Byte pro Schritt/Eingang.
Die bestehende Abschlussreserve bleibt: Auswertung 3.000, Dispatch 768,
Bilanz 1.536 und Bericht 512 Byte. Diagnose: höchstens 4.096 Byte innerhalb
derselben Fehler-Metadatenhülle, nicht zusätzlich zur Grenze. Feste Tiefe mit
Teilbeträgen, Summen, Grenzen, Phase und Fortschritt; keine Selbstverschachtelung.

Vorstart und Qualifikation konstruieren für jede Position 0 bis 21 beide
Hüllen aus der konkreten gemeinsamen Bindung und den nativen Größenmaxima.
Administrative Zähler verwenden maximale Ziffernbreiten, Digests ihre festen
Längen, Fehlerschlüssel und Klassen jeweils 128 Zeichen. Dies sind Größenformen,
keine behaupteten Memoryzustände. Die zulässige Metadatengrammatik ist geschlossen;
unerwartete zusätzliche Felder sind kein Teil dieser oberen Zusage.
Tatsächliche Ergebnisse werden weiterhin bei Fortschritt und Abschluss geprüft.
Unvorhergesehene größere Fehlerbelege werden nicht gekürzt oder nachträglich
umklassifiziert; eine Überschreitung wäre offen ein technischer Fehler.

## Neue neutrale Qualifikation

Eigene ID: `s2oc-shared-closure-qualification-20260910-01`, ein Testaufruf,
26 neue Prüfgruppen. Keine historischen Testserien oder realen Aufruferdateien.
Die Gruppen stehen in `tests/test_s2oc_shared_closure.py`; Quelldigests und
Inventardigest werden vor dem Aufruf gebunden.

Synthetisch: 22 Fortschrittspositionen und beide Alternativen, maximale native
Belegkörper, verlustfreier Binary64-Rückweg, fehlende/manipulierte/widersprüchliche
Referenzen, Grenzgleichheit und Überschreitung, Klassifikation und Diagnosetiefe.
Die globale Summenprobe ist ausdrücklich kein behaupteter vollständiger
Memoryzustand an sämtlichen lokalen Maxima.

Zwei frische kurze neutrale Sitzungen: insgesamt zwei Formationen und ein
auditiver Hinweis; drei Audioanalysen/NJ-Projektionen, zwei visuelle Analysen.
Ein zusätzlicher Analyseaufruf wird vor der eigentlichen Analyse gezielt
abgewiesen. Eine native unabhängige Gesamtprüfung und eine unabhängige
Fehlerabschlussprüfung; die bestehenden direkten Vergleichs- und
Zustandsprüfgrenzen bleiben erhalten. Keine Memorygeschichte mit 21 Ereignissen.
Standalone Leseprüfungen verwenden ausschließlich neutrale temporäre Dateien.

Qualifikationsablage: 4.096 Byte für Vorregistrierung, vollständige Logs,
Metriken, Ergebnis und Istbilanz; Berichtreserve 512.
Bindung der Teilreserven: 1.280 Byte Vorregistrierung, 0 Standardausgabe,
256 Fehlerausgabe, 256 Metriken, 1.024 Ergebnis, 1.280 Istbilanz. Zusammen
weiterhin 4.096 Byte. Die neue aktive Bindung referenziert alle sechs Dateien,
nicht allein den Ergebnisstatus. Unerwartet größere Logs bleiben vollständig
erhalten und führen zum offen ausgewiesenen Nichtbestehen.
Größen- und gemeinsame
Bindungsbelege werden zusätzlich vollständig als Metadaten gezählt, nicht
in die Quellenklasse verschoben. Der Quellenanhang, konkrete eigenen
Quelldateien und sämtliche neutralen Abschlussbelege sind gemeinsam bilanziert.
Maximal zwei Prüfbelege zu je 16.384 Byte innerhalb der unveränderten globalen
Prüfgrenze. Keine vollständigen synthetischen 21er-Hüllen werden archiviert;
ihre vollständige Serialisierung wird geprüft und ihre Positionsbilanz gespeichert.
Temporäre neutrale PCM-/RGB-Dateien sind getrennte Testeingaben, keine Systemausgabe.

Bei scheiternder vollständiger Vorbilanz kein Teststart. Bei Testfehler kein
Retry und keine Logkürzung. Ein positives Ergebnis wäre nur Anschlussqualifikation,
kein neuer 21-Ereignis-Funktionsbefund. Hauptgate außerhalb neutraler Tests False.
