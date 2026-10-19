# Separate technische Ausführungsvorbereitung V2 – Abschluss

Technische Integration bestanden; ausreichende Zeitreserve für einen vollständigen Lauf innerhalb3600 Sekunden NICHT NACHGEWIESEN. Keine Rasterquelle materialisiert und kein Rasterarm ausgeführt.

## Stand und Änderungen

Neue Hülle tools/s2uc_repeat_prepare_v2.py samt tests/test_s2uc_repeat_prepare_v2.py. Ausführungskern verwendet unveränderten eingefrorenen execute-Bytecode; Baseline-Aufruf aktiviert ausschließlich den qualifizierten Frame-Blattfall, danach Wiederherstellung. Policy, Quellenverfahren, Belegprüfung, Kriterien und Ressourcenlimits unverändert. Zusätzliche Metadaten kennzeichnen bekannte Daten und verbieten Ergebniszusammensetzung. 78 Codebindungen, davon71 historische unverändert.
V1 wurde wegen einer tatsächlich0,7951 ms zu frühen Abbruchanforderung nicht abgenommen. Prozess-join kann vor der Deadline zurückkehren. V2 prüft deshalb erneut die monotone Restzeit und wartet weiter, solange sie positiv ist. V1-Dateien, Bindung und fehlgeschlagene Qualifikation bleiben unverändert erhalten. Keine zusätzliche Visitoroptimierung.

## Prüfungen

V2 I01–I07:7/7 bestanden,keine Fehler/Skips. I01 eingefrorene Parameter/Bindung; I02 Autorisierung vor Start; I03 Normalende,erzwungener Abbruch,Workerfehler und exklusives Verzeichnis; I04 wiederverwendete vollständige neutrale Integration mit AST-/Hashgleichheit der unveränderten Integrationsfunktionen; I05 sieben Ressourcenverletzungen; I06 bekannte Daten/fehlende Zeitreserve; I07 simulierte vorzeitige join-Rückkehr ohne vorzeitigen Abbruch.
In V1 bestanden zehn neutrale80er-Replays N1/N2 × U/M/E/K/P,800 Aufnahmen und800 Referenzfortschreibungen. Acht Baseline-Fachvergleiche und sämtliche Meterfelder stimmen mit gespeicherter NEW-Visitorqualifikation überein. U bleibt unverändert; der originale Belegprüfer bestätigt gemeinsame Speicherzustände. Beide Fallprüfungen ohne technische Fehler. Alle Zustände/Ausgabeplätze freigegeben. V2 verwendet diese Belege unverändert erneut; keine zehn zusätzlichen Replays für günstigere Zeiten. Frühere Einzelqualifikationen V01–V08/R01–R25 gezielt wiederverwendet.
Integrierte neutrale Gesamtzeit einschließlich bestätigtem Prozessende und echter Abschlussverwaltung: 143.230698 s. Zusatzheappeak maximal 5184 Byte bei16384 Byte Grenze. Vollständige Ressourcenwerte pro Arm in Qualifikation02/facts.json/I04; sie trennen U-Obergrenzen und Baseline-Messfelder.

## Vollständiger Zeitwächter

Deadlinefestlegung mit UTC/monotoner Worker- und Gesamtdeadline,Abbruchanforderung,Workerbestätigung und Anfang/Ende der echten Abschlussverwaltung sind im Journal getrennt. Abschluss umfasst Prozesshandle-Schließung,Dateiinventar,Hashes,Schreiben der closure.json und deren Hashprüfung. Nur die letzte Journalzeile liegt als Selbstmessungs-Endmarker nach ihrem eigenen Zeitstempel. Die Bestätigung nach join ist kein exakter Todeszeitpunkt. Historischer Workerstop bleibt unbekannt.
V2-Abbruchprobe: Abbruch3,7026 ms nach Worker-Deadline;Bestätigung6,9464 ms danach. Tatsächliche Abschlussverwaltung: normal24,6119 ms,Abbruch12,4191 ms,Workerfehler11,8991 ms. Alle Gesamtdeadlines eingehalten. Exklusiver Neustart jeweils abgelehnt.
Für spätere Ausführung: Gesamtdeadline3600 s ab exklusivem Start,Workerdeadline3540 s,60 s für Abschluss. Kein Anheben der60-Minuten-Grenze. Eine Überschreitung bei blockierenden Betriebssystem-/Dateioperationen kann nicht als unmöglich garantiert werden; sie wird anhand des Abschlusszeitstempels als Fehler gemeldet.

## Laufzeitplan: Messung und Hochrechnung getrennt

Neutral gemessene Teilzeiten für zwei80er-Fälle,insgesamtzehn Arme:

| Teil | Sekunden |
|---|---:|
| U_replay | 0.221049 |
| aggregation | 0.000027 |
| baseline_replay | 141.320184 |
| case_assessment | 0.688451 |
| export | 0.071298 |
| manifest | 0.006293 |
| materialization | 0.000175 |
| resource_check | 0.000050 |
| source_validation | 0.019296 |

Engine insgesamt 142.368065 s; die nicht separat erfasste Restverwaltung ist darin enthalten. Die neutrale Aggregation prüft nur die zwei neutralen Fälle; daraus wird keine Laufzeitgarantie für die32-Fall-Aggregation abgeleitet.

Konservative Planung: langsamster historischer Baseline-Startabstand48,458863 s (einschließlich damaliger Export-/Verwaltungsanteile),schwächste gemessene NEW/OLD-Quote0,781602,alle128 Baseline-Arme wie den langsamsten Arm behandeln und25 Prozent Hostreserve. Hinzu kommen180 s Materialisierung/Validierung/Belegprüfung/Export/Startverwaltung,30 s U und60 s Abschluss. Die Verwaltungspauschale liegt über der aus neutralen Teilzeiten skalierten Größe; historisch enthaltene Verwaltung wird bewusst nicht abgezogen.

| Planbestandteil | Hochrechnung s |
|---|---:|
| baseline_seconds | 6060.088 |
| administration_seconds | 180.000 |
| U_seconds | 30.000 |
| closure_seconds | 60.000 |
| total_seconds | 6330.088 |
| limit | 3600.000 |
| reserve_seconds | -2730.088 |

Ergebnis: rund105,5 Minuten konservativer Plan gegenüber60 Minuten Grenze. Dies ist eine vorsichtige Planung,kein gemessener Rasterlauf und kein mathematischer Worst-Case-Beweis. Auch ohne25 Prozent Hostreserve überschreitet dieser Ansatz die Grenze. Keine ausreichende belegbare Reserve; vollständige Ausführung jetzt nicht empfohlen. Neutrale schnellere Zeiten allein ersetzen diesen Nachweis nicht.

## Bindung, Budget und ausstehende Autorisierung

Bindung SHA256: d752fc323cae2c440c5de7ce7ef540d4245a605e4583ff84dc5f04306d1ce254. Aktuelles operatives Vorbereitungspaket: 2636403 Byte gegenüber8.388.608 Byte Vorbereitung-/Referenzdeckel. Gesamtlimit64 MiB,1 MiB Abschlussreserve und alle Dateicaps unverändert. Gezählt werden neuer Code,gebundene operative Referenzen sowie beide Integrationsvorbereitungen. Alte Raster-/Auditarchive bleiben separat erhalten und werden nicht als neue Ergebnisarme eingerechnet.
Die Vorlage docs/S2UC_TECHNISCHE_WIEDERHOLUNG_V2_AUTORISIERUNG_VORLAGE_20261003.json steht auf PENDING_SEPARATE_AUTHORIZATION. Der reale run-Einstiegspunkt hat diese Vorlage mit EXPLICIT_SEPARATE_AUTHORIZATION_REQUIRED zurückgewiesen,ohne ein Ausgabeverzeichnis anzulegen. Keine operative Autorisierungsdatei erzeugt.

Vorbereiteter Aufruf,nicht als Evaluationslauf ausgeführt:

```powershell
C:/Python314/python.exe -m tools.s2uc_repeat_prepare_v2 run --authorization docs/S2UC_TECHNISCHE_WIEDERHOLUNG_V2_AUTORISIERUNG_20261003.json
```

## Evidenzstatus und nächste Entscheidung

Alle32 historischen Quellenprofile werden in der Provenienz als bekannt geführt. Ein späterer vollständiger Lauf wäre eine gesondert autorisierte technische Wiederholungsprüfung der eingefrorenen Policy. Er wäre keine unberührte Evaluation. Historische und neue Arme dürfen nicht zu einem vermeintlich ursprünglichen vollständigen Lauf zusammengesetzt werden. Raster32 bleibt geschlossen und global NOT_EVALUABLE.
Nächste Entscheidung beim Projektleiter: technische Integration abnehmen,Ausführung wegen fehlender Zeitreserve zurückstellen und gegebenenfalls einen gesonderten Auftrag zur Absicherung der60-Minuten-Grenze formulieren. Keine zusätzliche Optimierungsvariante oder Ausführung aus diesem Abschluss ableiten.

Belege: Qualifikation02/tests.json,facts.json,time-plan.json,closure.json; wiederverwendete Integration unter Qualifikation01/integration; vorbereiteter Aufruf und Budgetdefinition im V2-AUFRUF-Dokument. Alle Dateien bleiben separat versioniert.
