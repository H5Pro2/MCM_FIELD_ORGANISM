# ER1: Ausführungsstruktur und Ressourcenplan

Workflow 17468e31-58e4-46da-9b73-b3fff84058de, 2026-10-17.
Dies ist Planung aus kurzen neutralen Messungen, keine Vollgrößenqualifikation.

## Durchgänge

| Arbeit | Anzahl | Produktionspolicy? |
|---|---:|---|
| Geschichten | 32 × 1024 Frames | jeweils zwei frische Arme |
| E/F-Policy einschließlich Messung und Capture | 64 | ja, genau einmal je Arm |
| Begleitende unabhängige Referenz | 64 | nein |
| Unabhängige Archivrekonstruktion | 64 | nein |
| Quellenrezept und unabhängige Rekonstruktion | je 32 | nein |
| Primärstatistik und unabhängige Referenz | je 1 Serie | nein |
| Zusätzliche Mess- oder Capture-Policywiederholungen | 0 | keine |

Der Einstieg überwacht insgesamt höchstens 64 Arme, die Fallfunktion höchstens zwei.
Die Einzeloperationsmessung läuft im einzigen Policydurchgang. Vor-/Nachzustände,
Feedback, Auswahl und Herkunft werden dabei erfasst. Keine zusätzliche Ausführung
für die Messung und kein Forschungs-Policy-Replay. Die innere Methodenprofilierung
aus der alten neutralen Entwicklung ist nicht Teil dieses Einstiegspfads; die
vertraglich benötigten vollständigen Block-, Feedback- und Zielbelege bleiben erhalten.
Damit besteht kein Konflikt mit der vertraglichen Zahl von 64 Vergleichsarmen.

## Gemessen und hochgerechnet

Endgültige kurze Integrationsfälle: 44 und 32 Frames je Arm.
Details: integration-complete/case-01-summary.json und case-02-summary.json.
Die folgende lineare Hochrechnung verwendet jeweils den ungünstigeren Quotienten
beider kurzen Fälle und rundet Byte-/Tabellenzahlen auf. Sie ist keine Garantie;
Quellenkonkurrenz, längere Feedbackhistorie und Kompressibilität können anders wachsen.

| Größe je 1024-Frame-Geschichte mit E und F | Linear geplant | Harte Grenze |
|---|---:|---:|
| gzip | 298624 Bytes | 524288 |
| encoded | 1375424 Bytes | 4194304 |
| Dictionary | 1307456 Bytes | 4194304 |
| Knoten | 31680 | 65536 |
| Kanten | 120856 | 262144 |
| Indizes | 10217 | 65536 |
| Beobachterheap | 4322002 Bytes | im gemeinsamen 512-MiB-Job |
| Mechanismenbelege im Heap | 165344 Bytes | im gemeinsamen 512-MiB-Job |

14 Collections sind fest: acht Armsequenzen, fünf Beobachtersequenzen, eine
Mechanismensequenz; Grenze 16. Größter gemessener Record
14123 Bytes, Grenze 262144. Die maximale
Recordgröße wird weiterhin bei jeder Einfügung geprüft, nicht linear freigegeben.
Archive zusammen linear 9555968 Bytes, Grenze 33554432. Selbst
32 Archive an ihrer individuellen 512-KiB-Grenze ergeben nur 16 MiB; die
individuelle Grenze bleibt dennoch strikt und wird nicht gegen freie Gesamtkapazität getauscht.

Die größte kompakte neutrale Quelle des unveränderten Rezeptformats hat
7439 Bytes. Geplant sind höchstens 32 × 32768 = 1048576 Bytes;
Gesamtquellengrenze 2097152. Forschungsquellen wurden nicht erzeugt.
Pro Fall werden Capture-Anker, Zusammenfassung und Archiv geführt. Vollständige
Beobachter-/Mechanismenbelege bleiben in begrenzten Archivsequenzen. Kein großer
redundanter JSON-Export sämtlicher Zustandsdaten. Für Administration sind bis
2 MiB, für Closure bis 1 MiB reserviert; eine Überschreitung bricht technisch ab.
Vorbereitung (einschließlich Testbelegen und Bindung) höchstens 8 MiB; Export
inklusive Vorbereitung und temporärer Dateien höchstens 64 MiB. Es bleibt nur
ein aktiver Codecstore je Geschichte. Fallquittung erst nach Archivprüfung und Cleanup.

## Zeit und Speicher

Lineare Hochrechnung für die gesamte Serie einschließlich beider Arme:

- Policy, Einzeloperationsmessung, Capture und begleitende Referenzen zusammen:
  1052.9 Sekunden.
- Zusätzliche Archivprüfung einschließlich 64 Referenzrekonstruktionen:
  318.5 Sekunden.
- Gesamte Fallarbeit einschließlich Kodierung, Herkunftsbelegen und Dateiprüfungen:
  1670.6 Sekunden. Diese Gesamtzeit enthält die beiden vorigen
  Posten; sie werden nicht nochmals addiert.

Arbeitsplanung mit explizitem Unsicherheitsfaktor 8 auf die gesamte Fallarbeit plus
600 Sekunden für Quellenerzeugung/-referenz, Statistik/-referenz und Dateiverwaltung:
13966 Sekunden. Hinzu kommt die unveränderte
Abschlussreserve 3600 Sekunden innerhalb der Gesamtfrist. Dies ist eine
Planungsannahme, keine aus einem Vollgrößenlauf gemessene Laufzeit.
Harte Workerfrist 54000 Sekunden, Gesamtfrist 57600 Sekunden. Der Supervisor
überwacht die gemeinsame Zeit und Dateiinventur während des Workers.

Windows-Jobpeak im positiven Integrationstest:
54013952 Bytes.
Er darf nicht einfach mit 1024/32 multipliziert werden: Laufzeitinterpreter ist
konstant, Wörterbuch, Fehlerhistorie und Beobachter sind variabel. Gleichzeitig
werden nur eine Geschichte, zwei abgeschlossene Armcaptures und die zugehörigen
Referenzdaten gehalten. Größere Peak-Allokationen beim Codec und Rekonstruktion
bleiben eine ungeprüfte Vollgrößenunsicherheit. Harte gemeinsame Grenze 512 MiB,
höchstens zwei Prozesse. Die gespeicherten Fallzusammenfassungen/Statistikzeilen
aller 32 Geschichten zählen zusätzlich zum Jobpeak.

## Beendigung und Evidenzgrenzen

Erschöpftes Administrations- und Exportbudget wurden am tatsächlichen Einstieg
nach quittiertem Fall 1 in Fall 2 injiziert. Erwarteter TECHNICAL_ABORT,
Worker beendet, Arm-/Dateicleanup bestätigt, keine Quittung für Fall 2 und kein
Teilserien-Nutzenurteil. Der reservierte Terminalslot funktioniert auch dann,
wenn worker.json oder der reguläre Abschlussbericht nicht mehr geschrieben werden kann.

Kein vollständiger 1024-Frame-Policyfall wurde ausgeführt. Größere Archive,
längere Wiederverwendungsketten und veränderte Kompression können die Planung
überschreiten. Jede harte Grenzverletzung beendet den Versuch technisch; kein
Retry, Resume, Ersatzfall, zusätzlicher Messdurchgang oder Nutzenurteil aus Teilserien.
