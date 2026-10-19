# T1-Einmallauf: technischer Abbruch vor Workerstart

Die fachlich abgenommene Vorbereitung wurde nicht erneut qualifiziert. Die separate
operative Autorisierungsdatei wurde ausschließlich durch Änderung von status auf
AUTHORIZED_ONCE aus der T1-V2-Vorlage erstellt. Alle282 gebundenen Dateien und
Qualifikationsbelege wurden vor Start geprüft. Die Policy wurde nicht verändert.

Der einmalige Startversuch scheiterte mit RuntimeError:FILE_CAP:claim.json.
Der zusätzliche Bilanzblock im administrativen launch_once.py vergrößerte den
Startbeleg auf **1264 Byte bei1.024 Byte Grenze**. Das war ein Fehler des hier
hinzugefügten administrativen Aufrufs. Die bestehende Ledger-Grenze wies die Datei
korrekt vor dem Schreiben zurück. Keine Aussage über eine fehlerhafte Policy.

Die Verzeichnisreservierung und deadline_established wurden bereits ausgeführt.
Der Fehler liegt vor dem try/finally des Supervisors und vor dem Workerstart.
Daher gibt es im unverändert erhaltenen Laufverzeichnis nur lifecycle.jsonl
(291 Byte), keinen claim, keinen Worker und keinen regulären Abschlussbeleg.
Dieses externe Dossier dokumentiert den tatsächlichen Teilabschluss; es ergänzt
oder repariert das ursprüngliche Laufverzeichnis nicht. Der Shellprozess endete
mit Exit1. Keine Wiederholung, Fortsetzung oder Reparatur wurde durchgeführt.

## Vollständigkeit und Einzelurteile

| Größe | Tatsächlich | Geplant |
| --- | ---: | ---: |
| Quellenfälle | 0 | 16 |
| Quellpositionen | 0 | 1.280 |
| Gestartete / abgeschlossene Arme | 0 / 0 | 80 |
| Arm-Aufnahmen | 0 | 6.400 |
| Separate Referenzfortschreibungen | 0 | 6.400 |
| Beobachtete Übergänge | 0 | Nenner52 |
| Beobachtete negative Kontrollen | 0 | 20: I12/H8 |

Wiedererkennung, Verfügbarkeit, erfahrungsabhängige Anpassung, Gesamtnutzen und
Stabilität/Schäden sind sämtlich **NOT_EVALUABLE**. Dies ist kein negativer
Transferbefund, weil keine Policyprüfung begonnen hat. Herkunftsüberschneidungen
sind mangels erzeugter Quellen ebenfalls nicht auswertbar. Keine Quellen ersetzt.
Die52 Übergänge und20 Kontrollen bleiben im unveränderten Plan; es wird keine
Erfolgsquote0/52 aus nicht beobachteten Übergängen behauptet. G_w bleibt das feste
Zeitfenster. Modale Fortsetzung und realisierte Fehler wurden nicht beobachtet.
Es gibt weder nachgewiesene Schäden noch einen Nachweis der Schadensfreiheit.

## Ressourcen, Zeit und Integrität

Vorbereitungsbilanz einschließlich neuer Autorisierung:6.540.018 Byte.
Zusätzliches Übergabedossier59.677 Byte. Für dieses externe Start-/Abschlussdossier
wurden vorab524.288 Byte reserviert. Vorbelastung des Laufledgers:7.123.983 Byte.
Die tatsächliche Gesamtbilanz und verbleibende Reserve stehen in closure.json.
Die8MiB-Vorbereitungsgrenze wurde eingehalten. Auch mit der vollständigen externen
Dossierreserve bleibt die Bilanz unter64MiB einschließlich1MiB Abschlussreserve.
Die Startdateigrenze wurde nicht überschrieben: sie verhinderte den Start.
Keine Heap-, Frame-, Slot- oder Policy-Laufzeitmessung aus diesem Versuch vorhanden.

Gesetzter Beginn:2026-10-03T20:26:48.878528 UTC; geplante Workerfrist
21:25:48.878528 UTC, Gesamtfrist21:26:48.878528 UTC. Die Shell meldete Prozessende
nach ungefähr1,05s einschließlich Vorstartprüfung. Eine präzise abgeschlossene
Supervisor-Laufzeit fehlt, weil kein terminaler Zeitstempel geschrieben wurde.
Der extern dokumentierte Abschlusszeitpunkt wird getrennt ausgewiesen und liegt
innerhalb der3.600s-Grenze. Es gab keinen laufenden Worker zu terminieren.

Die Bindung bleibt78525e2ff688151cc0dfbb9400a40a4a5732df426d52b89e4d6b5067ddc016f3.
Die operative Autorisierung bleibt als Beleg erhalten; die Einmalfreigabe ist
für diesen Fehlversuch verbraucht. Die PENDING-Vorlage bleibt unverändert.
Gebundene Implementierung, V1/V2-Qualifikationsarchive und Vorbereitungsbericht
wurden nicht verändert. result.json enthält die vollständige Dateiprüfbilanz.

## Nächste Forschungsentscheidung

Aus diesem Versuch lässt sich keine Entscheidung über Transferfähigkeit ableiten.
Empfehlung an den Projektleiter: den technischen Teilversuch als geschlossen
NOT_EVALUABLE abnehmen. Als separates, begrenztes Folgepaket den administrativen
Start prüfen lassen: Zusatzbilanz außerhalb des auf1.024 Byte begrenzten claim
belassen, identische Budgetvorbelastung erhalten und den Fehlerabschluss vor dem
Workerstart ausdrücklich absichern. Vor einer neuen Ausführung muss der konkrete
Startbeleg gegen die Dateigrenze geprüft und die Startkorrektur separat abgenommen
werden. Dies ist ein Vorschlag, keine bereits ausgeführte Reparatur oder Freigabe.
Eine neue T1-Ausführung benötigt eine neue ausdrückliche Einmallauffreigabe und
neues exklusives Ziel; der fehlgeschlagene Ordner bleibt unverändert.

Der wissenschaftliche Vertrag und die Policy benötigen aufgrund dieses rein
administrativen Fehlers keine Anpassung. Aussagegrenze bleibt synthetischer
Transfer ab der48-Vektor-Grenze, kein Audio-/Video-Kettentransfer. Defaults bleiben
deaktiviert. Der alte Raster32-Lauf bleibt separat NOT_EVALUABLE.
