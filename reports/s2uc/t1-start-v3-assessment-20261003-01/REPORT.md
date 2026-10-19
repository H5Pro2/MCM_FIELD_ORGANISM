# Administrative T1-Startkorrektur V3

Die administrative Startkorrektur ist implementiert und neutral qualifiziert:
12/12 Tests A01–A12 bestanden, keine Fehler oder ausgelassenen Prüfungen.
Fachliche Abnahme dieser Startkorrektur und neue Einmallauffreigabe sind offen.
Keine T1-Quelle materialisiert, keine Policy-Replays und keine neue operative
Autorisierungsdatei erstellt. Die fachliche T1-V2-Qualifikation wird wiederverwendet.
Der frühere Fehlversuch bleibt geschlossen und unverändert NOT_EVALUABLE.

## Geänderte beziehungsweise neue Dateien

Neuer einziger CLI-Einstieg tools/s2uc_t1_start_v3.py und zugehörige Tests
 tests/test_s2uc_t1_start_v3.py. Separater PLAN, BINDUNG, AUFRUF und ausstehhende
AUTORISIERUNG_VORLAGE unter docs/S2UC_T1_START_V3_*_20261003.*.
Neutrale Belege unter reports/s2uc/t1-start-v3-qualification-20261003-01;
dieses Abschlussdossier unter reports/s2uc/t1-start-v3-assessment-20261003-01.
README und Forschungsweg werden auf diesen Stand synchronisiert.
Kein nachträglicher launch_once-Wrapper; der dokumentierte CLI-run ruft direkt
den qualifizierten launch-Pfad auf. Fachliche Quelle, Replays, Policy und
Auswertung V2 bleiben unverändert; nur Start und Supervisor sind separat V3.

Bindung SHA256: a1bbd35b1f0e6f618a95e3bd544cd95bc143a6498d686bdf746e54afe04945fe
Qualifikationsabschluss SHA256: 38bdfff8339e0290125d9b992be81673ca2eb8de28a4b7860f7151d0db0ac5c6
Die neue Bindung enthält Einstieg, Tests, Plan, Aufrufleitfaden, V2-Bindung,
V2-Qualifikationsabschluss sowie beide vorherigen Übergabedossiers.
Die transitive V2-Bindungsprüfung prüft weiterhin deren gesamte Code-/Referenzmenge.
Runtime und Python-Executable sind ebenfalls gebunden. Sämtliche Bindungen
wurden nach der neutralen Qualifikation unverändert abgeglichen.

## Startformat und Fehlerabschluss

Der konkrete serialisierte Claim umfasst **155 Byte /1.024**.
Er enthält ausschließlich status=CLAIMED_ONCE, accounting_file=start-accounting.json
und dessen SHA256. Die separat gespeicherte Bilanz enthält die Autorisierung,
Budgetvorbelastung, Gesamtgrenze und Abschlussreserve. Beide Bytefolgen werden
vollständig vor Verzeichnisreservierung und Workerstart erzeugt und geprüft.
Die Bilanz mit der realen PENDING-Vorlage umfasst976 Byte.
Der autorisierte Status ist kürzer; der Claim behält wegen der festen Hashlänge
exakt155 Byte. Es wurde dafür keine operative Autorisierungsdatei angelegt.

Erst nach bestandenen Vorbedingungen reserviert mkdir(exist_ok=False) das Ziel.
Ab erfolgreicher eigener Reservierung liegen Bilanz-, Claim- und Zeitbelegschreiben
sowie Prozessstart innerhalb des Fehlerabschlusses. Ein partiell geschriebener
Claim bleibt als Fehlerbeleg erhalten. Ein unabhängiger terminaler Schreibpfad
legt closure.json an, begrenzt auf524.288 Byte innerhalb des gemeinsamen Budgets.
Bestehende fremde oder historische Ziele werden weder übernommen noch verändert.

A03: Bilanzschreiben scheitert, FAILED, worker_started=false, keine Quelldatei.
A04: Claimschreiben scheitert nach7 Byte; partieller Claim und Bilanz bleiben,
FAILED, worker_started=false. A09: Prozessstart scheitert, ebenfalls terminaler
Abschluss ohne gestarteten Worker. Die konkreten Abschlussdateien bleiben im
Qualifikationsordner erhalten und sind gehasht. A08 bestätigt den Timeoutpfad
mit beendetem neutralem Worker und Abschluss innerhalb der neutralen Gesamtfrist.

Ein dauerhafter Dateisystemausfall kann auch den terminalen Schreibvorgang
verhindern; dann wird der Schreibfehler weitergegeben. Es wird keine physikalische
Garantie bei unbeschreibbarem Datenträger behauptet. Abschlusszeitstempel schließen
ihren eigenen Schreibvorgang aus; nach dem Schreiben wird die Gesamtfrist erneut
geprüft. Die fachlichen Workerchecks und Systemlimits bleiben bestehen.

## Neutrale Prüfungen

| ID | Ergebnis und Gegenstand |
| --- | --- |
| A01 | PASS: derselbe Startpfad, echter neutraler Kindprozess, gültiger Claim/Bilanzhash, COMPLETE |
| A02 | PASS: übergroßer Claim vor Reservierung abgewiesen |
| A03 | PASS: Bilanz-Schreibfehler mit frühem terminalem Abschluss |
| A04 | PASS: partieller Claim-Schreibfehler mit frühem terminalem Abschluss |
| A05 | PASS: PENDING-Autorisierung vor Reservierung abgewiesen |
| A06 | PASS: belegtes Ziel bleibt bytegleich und ohne neue Dateien |
| A07 | PASS: überhöhte Budgetvorbelastung vor Reservierung abgewiesen |
| A08 | PASS: echter neutraler Timeoutprozess beendet, Fristabschluss vorhanden |
| A09 | PASS: Prozessstartfehler ohne Worker mit terminalem Abschluss |
| A10 | PASS: CLI-run-Funktionspfad weist PENDING vor launch zurück |
| A11 | PASS: konkretes Claim-/Bilanzformat mit T1-Vorlagenstruktur im Speicher geprüft |
| A12 | PASS: übergroße separate Bilanz vor Reservierung abgewiesen |

Die administrativen Fehlersimulationen ersetzen gezielt Schreib-/Startoperationen;
es gibt keinen Test-/Mock-Dispatch im Produktionscode. Die zwei tatsächlichen
Kindprozesse A01/A08 führen ausschließlich einen neutralen Abschluss beziehungsweise
Warten aus. Quellengenerator und fachlicher Execute-Aufruf sind während der Tests
mit Verbotssentinels geschützt; kein T1-Generator- oder Policyaufruf erfolgte.
A10 verwendet isolierte Vorbedingungsfixtures; A01–A09/A12 prüfen den echten
launch-Pfad direkt. Keine Wiederholung der fachlichen Qualifikation.

## Budget und Ausführungsgrenzen

Aktuell eindeutige Vorbereitungs-/Referenzdateien einschließlich bisheriger
Dossiers und neuer Startqualifikation: **6665342 /8.388.608 Byte**.
Eine spätere separate Autorisierungsdatei wird beim Start zusätzlich in tatsächlicher
Größe mitgerechnet. Für dieses neue Dossier und den späteren externen Abschluss
werden zusammen524.288 Byte vorab reserviert. Vorbelastung ohne die noch nicht
vorhandene operative Autorisierungsdatei: **7189630 Byte**.
Die vollständige Pfad-/Bytebilanz steht in facts.json. Claim, Bilanz und alle
Laufausgaben zählen zusätzlich im selben64MiB-Exportbudget.1MiB bleibt für den
Laufabschluss reserviert. Der neue Qualifikationsordner umfasst10855 Byte.

3.600s Gesamtgrenze,3.540s Workergrenze,60s Abschluss bleiben unverändert.
Ebenso16 Fälle,1.280 Quellpositionen,80 Arme,6.400 Aufnahmen und6.400 getrennte
Referenzfortschreibungen. Alle52 Übergänge einschließlich20 I/H-Kontrollen;
G_w bleibt festes Zeitfenster. Keine neue T1-Laufzeit- oder Nutzenmessung.

## Exakt vorbereiteter Aufruf

Arbeitsverzeichnis C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace.
Erst nach fachlicher Abnahme und separater neuer Einmallauffreigabe:

```powershell
C:/Python314/python.exe -m tools.s2uc_t1_start_v3 run --authorization <separate-Datei>
```

Die separate Datei wäre aus docs/S2UC_T1_START_V3_AUTORISIERUNG_VORLAGE_20261003.json
mit ausschließlich status=AUTHORIZED_ONCE zu erstellen. Der aktuelle Status ist
PENDING_SEPARATE_AUTHORIZATION. Neues exklusives Ziel:
reports/s2uc/t1-transfer-20261003-02, derzeit nicht vorhanden.
Prepare und qualify sind abgeschlossen und werden für diesen Stand nicht wiederholt.

Empfehlung an den Projektleiter: diese administrative Korrektur anhand der
155-Byte-Claimprüfung und erhaltenen frühen Fehlerabschlüsse abnehmen; danach
über eine neue ausdrückliche Einmallauffreigabe für das neue Ziel entscheiden.
Keine fachliche Kriterienänderung und keine Policyoptimierung aus dem Startfehler.
Synthetischer Transfer ab48-Vektor-Grenze, kein Audio-/Video-Kettentransfer.
Defaults bleiben deaktiviert; alter Raster32-Lauf separat NOT_EVALUABLE.
