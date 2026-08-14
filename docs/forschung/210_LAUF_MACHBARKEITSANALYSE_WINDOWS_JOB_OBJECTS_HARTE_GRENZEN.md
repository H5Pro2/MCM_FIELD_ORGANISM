# Lauf 210 - Machbarkeitsanalyse Windows Job Objects und harte Grenzen

## Forschungsfrage und Auftrag

Kann der in Lauf 209 geplante Zwei-Prozess-Einmallauf unter Windows so konzipiert werden, dass Prozess-, Ressourcen-, Thread-, Handle-, Verbindungs-, Ausgabe- und Artefaktgrenzen vor der ersten Fachoperation hart oder lueckenlos erzwungen werden?

Die Analyse ist ausschliesslich dokumentarisch. Es wurden keine Projektmodule importiert, keine Tests ausgefuehrt, keine Windows-Job- oder AppContainer-Objekte angelegt und keine Laufpfade aufgerufen.

## Lokale Quellen und Bytebindung

| Quelle | SHA-256 |
|---|---|
| `docs/forschung/192_SPERR_UND_FREIGABEBEDINGUNGEN_REALE_FIXIERUNGSAUSFUEHRUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `d6b9fedd7310425bff7bbdd3b9f2a778e0ede32c6074d4b68f78c8c4cede7edb` |
| `docs/forschung/195_HUERDE_C_RESSOURCEN_UND_ZEITGRENZEN_EINMALLAUF_RUNTIME_FIXIERUNG.md` | `0154a6de7e80b5db8f373878af592855dfa6a0938bd7dedf5ebea927e5ae4ca3` |
| `docs/forschung/204_ERNEUTE_HUERDE_C_RESSOURCEN_UND_ZEITGRENZEN_PRIVATE_EINMALVERKETTUNG.md` | `ec0cead77a18d2b3ca0ba1caca43c0baf96d5af269ea8512fe72ff4823018671` |
| `docs/forschung/208_LAUF_HUERDE_G_DOKUMENTARISCHE_ENTSCHEIDUNG_EINMALLAUF_GESPERRT.md` | `13176a3c7a5725b14b8733c35cd5433b03948c2b1923c512737546ec5bc51c38` |
| `docs/forschung/209_LAUF_KORREKTURPLAN_HUERDE_G_RESSOURCENWAECHTER_PROZESSVERTRAG_ARTEFAKTKONTROLLE.md` | `b3a0123cf1169f45895095e75fe1919c81da8e28e8efed2e6f52a01c5e6e6f5c` |
| `mcm_field_organism/_runtime_fixation_single_use_path.py` | `44cc4dc42bea8b163531d5315e5bab5eda101b1a13f16323e2e34f0ba003787a` |
| `mcm_field_organism/__init__.py` | `c04e371daba2593d771e8ffa26e614746599f15541b303d5d5eaeaeaf332a9b0` |

## Tatsaechlich verwendete externe Primaerquellen

- [Microsoft: Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)
- [Microsoft: JOBOBJECT_BASIC_LIMIT_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information)
- [Microsoft: JOBOBJECT_EXTENDED_LIMIT_INFORMATION](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)
- [Microsoft: AssignProcessToJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject)
- [Microsoft: Process Creation Flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)
- [Microsoft: Creating Processes](https://learn.microsoft.com/en-us/windows/win32/procthread/creating-processes)
- [Microsoft: Kernel Objects](https://learn.microsoft.com/en-us/windows/win32/sysinfo/kernel-objects)
- [Microsoft: AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)
- [Microsoft: Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)
- [Microsoft: Windows Filtering Platform](https://learn.microsoft.com/en-us/windows/win32/fwp/about-windows-filtering-platform)

## Verwendete Dateien und Schnittstellen

Bewertet wurden der geplante private PowerShell-Supervisor, die Win32-Schnittstellen `CreateProcess`, `AssignProcessToJobObject`, `SetInformationJobObject`, `QueryInformationJobObject`, `TerminateJobObject`, `ResumeThread` sowie AppContainer- und WFP-Isolationsgrenzen.

Keine dieser Schnittstellen wurde aufgerufen. Die Supervisordatei existiert weiterhin nicht.

## Durchgefuehrte Schritte

1. Zwei-Prozess-Vertrag gegen die Windows-Job-Semantik abgegrenzt.
2. Startreihenfolge vor der ersten Fachoperation untersucht.
3. Jede geplante Ressourcenkategorie einer harten Kernelgrenze, einer reinen Messgrenze oder einer nicht vorhandenen Grenze zugeordnet.
4. Thread-, Handle- und Netzwerkkontrolle gesondert bewertet.
5. Cache-, Ausgabe- und Abbruchbedingungen gegen Prozess- und Sicherheitsgrenzen geprueft.
6. Umsetzbarkeit ohne Export, Produktions-CLI, Runner, Executor oder Weltkontakt bewertet.

## Zwei-Prozess-Vertrag und Startreihenfolge

Ein statisch sauberer Vertrag ist moeglich, wenn genau unterschieden wird:

- Supervisor: ein Kontrollprozess ausserhalb des geprueften Job Objects;
- Kindprozess: exakt ein aktiver Prozess innerhalb des Job Objects;
- Nachkommen des Kindprozesses: exakt null.

Der Kindprozess muesste mit `CREATE_SUSPENDED` erzeugt werden. Danach muesste der Supervisor alle Jobgrenzen setzen, den suspendierten Prozess dem Job zuordnen und erst nach erfolgreicher Rueckpruefung der Grenzen den Hauptthread mit `ResumeThread` freigeben.

Dies verhindert Benutzer-Code vor der Jobzuordnung. Microsoft weist darauf hin, dass Speicheroperationen vor der Jobzuordnung nicht rueckwirkend von Jobgrenzen erfasst werden. Der suspendierte Start ist daher notwendig. Huerde A und Huerde C muessten vor einer Implementierung auf genau diese Zwei-Prozess-Semantik neu gebunden werden.

## Machbarkeitsmatrix

| Grenze | Windows-Mechanismus | Bewertung |
|---|---|---|
| ein Kindprozess im Job | `JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 1` | hart erzwingbar |
| keine Kindprozesse des Kindprozesses | Vererbung in denselben Job plus Aktivprozesslimit 1 | hart erzwingbar; weiterer Prozess wird beendet |
| Prozess-Commit-Speicher | `JOB_OBJECT_LIMIT_PROCESS_MEMORY` | hart erzwingbar |
| Job-Commit-Speicher | `JOB_OBJECT_LIMIT_JOB_MEMORY` | hart erzwingbar |
| Working Set | `JOB_OBJECT_LIMIT_WORKINGSET` | Kernelgrenze vorhanden, aber nicht gleich Commit-Speicher |
| Benutzer-CPU-Zeit | `JOB_OBJECT_LIMIT_PROCESS_TIME` | Betriebssystem beendet periodisch nach Ueberschreitung; nicht zyklusgenau |
| Jobende bei Supervisorverlust | `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` | hart erzwingbar |
| Wandzeit | Supervisor-Timer plus `TerminateJobObject` | beendbar, aber keine Job-Object-Wandzeitgrenze und keine Null-Latenz-Garantie |
| Threadzahl maximal 1 | kein entsprechendes Job-Object-Limit | nicht hart erzwingbar |
| allgemeine offene Handles maximal 256 | kein numerisches Job-Object-Limit | nicht hart erzwingbar |
| USER-Handle-Isolation | `JOB_OBJECT_UILIMIT_HANDLES` | nur USER-Objekte fremder Prozesse, kein allgemeines Handlelimit |
| Netzwerkverbindungen 0 | kein Job-Object-Netzwerklimit | nicht durch Job Objects erzwingbar |
| Geraetezugriff 0 | kein Job-Object-Geraetelimit | nicht durch Job Objects erzwingbar |
| `stdout`/`stderr` 0 Bytes | anonyme Pipes, Erfolg nur bei Bytezahl 0 | lueckenlos beobachtbar, aber Schreibversuch nicht vorab verhinderbar |
| Workspace-Schreibzugriff 0 | eingeschraenkter Token/AppContainer und ACL | prinzipiell erzwingbar, Kompatibilitaet nicht nachgewiesen |

## Thread- und Handlegrenzen

Job Objects besitzen keine dokumentierte allgemeine Maximalzahl fuer Threads. Das Betriebssystem begrenzt Threaderzeugung letztlich durch verfuegbaren virtuellen Speicher, nicht durch einen Jobvertrag mit `max_threads = 1`.

Ebenso existiert kein dokumentiertes numerisches Joblimit fuer alle Kernel-Handles eines Prozesses. `JOB_OBJECT_UILIMIT_HANDLES` schraenkt die Nutzung bestimmter USER-Handles anderer Prozesse ein, begrenzt aber weder Datei-, Registry-, Prozess-, Thread- noch Sockethandles auf eine Zahl.

Eine Abfrage oder ein Polling des Prozesszustands kann eine Ueberschreitung erst nach ihrer Entstehung feststellen. Damit sind die in Lauf 209 geplanten harten Grenzen `Threads <= 1` und `Handles <= 256` mit Job Objects allein nicht lueckenlos erfuellbar.

## Verbindungs- und Geraetegrenzen

Job Objects kontrollieren keine Netzwerk- oder Geraeteverbindungen. WFP kann Verkehr pro Anwendung filtern, wuerde aber Systemfilter konfigurieren, benoetigt eigene Berechtigungen und fuegt einen getrennten Systemseiteneffektpfad hinzu.

Ein AppContainer ohne Netzwerk-, Kamera- oder Mikrofon-Capabilities bietet eine staerkere vorbeugende Isolation. Microsoft dokumentiert, dass solche Ressourcen ohne entsprechende Capability nicht zugaenglich sind. Fuer den vorliegenden Python-Prozess waeren jedoch zuvor AppContainer-Profil, Token, Dateirechte und Zugriffe auf Interpreter, Standardbibliothek und gebundene Workspace-Quellen zu konzipieren.

Damit ist AppContainer eine technische Hypothese fuer Netzwerk- und Geraeteisolation, aber im aktuellen Byteumfang nicht als kompatibel oder artefaktfrei nachgewiesen. WFP ist wegen Systemveraenderung und erforderlicher separater Ruecknahme keine geeignete Null-Seiteneffekt-Basis fuer diesen Einmallauf.

## Cache- und Artefaktkontrolle

`-B` und `PYTHONDONTWRITEBYTECODE=1` unterdruecken geplante Python-Bytecode-Caches, garantieren aber nicht, dass jede importierte native oder Drittbibliothek keinerlei Temp-, Cache- oder Diagnosedatei erzeugt.

Ein Vorher-/Nachher-Inventar erkennt neue Workspace-Artefakte, verhindert sie jedoch nicht. Harte Verhinderung erfordert einen Sicherheitskontext ohne Schreibrecht auf Workspace und gebundene Quellen. Ein AppContainer oder eingeschraenkter Token mit gezielten Nur-Lese-ACLs koennte dies prinzipiell leisten, muesste aber gesondert gegen Python- und Bibliotheksanforderungen geprueft werden.

Die AppContainer-Profilanlage kann selbst persistente Profildaten erzeugen. Eine solche Anlage waere daher kein artefaktfreier Teil desselben Einmallaufs und muesste als separate, reversible Infrastrukturhandlung vorab gebunden und freigegeben werden.

## Ausgabe- und Abbruchgrenzen

Anonyme, nicht vererbte Kontrollhandles und zwei ausschliesslich fuer das Kind vererbte Pipe-Schreibhandles koennen `stdout` und `stderr` ohne Datei kontrollieren. Ein erfolgreicher Lauf duerfte nur akzeptiert werden, wenn beide gelesenen Bytezahlen exakt null sind.

Jeder Grenzfehler, Messausfall, unerwartete Prozess- oder Pipeaktivitaet muesste `TerminateJobObject` ausloesen. `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` sichert den Abbruch auch beim Verlust des Supervisorhandles ab. Da das `_FixedDigestBundle` den Kindprozess nicht verlassen darf, entsteht bei Prozessabbruch kein verwertbares Teilresultat.

Ein Retry, zweiter Start oder Wiederaufnahme ist konzeptionell vermeidbar. Diese Aussage ist statisch; sie wurde nicht implementiert oder ausgefuehrt.

## Messergebnisse und Gegenbaselines

- hart durch Job Objects abdeckbare Kernkategorien: Prozesszahl, Prozess-/Jobspeicher, Working Set, Benutzer-CPU-Zeit und Kill-on-close;
- nur extern mit Reaktionslatenz abdeckbar: Wandzeit;
- nicht hart durch Job Objects abdeckbar: Threadzahl, allgemeine Handlezahl, Netzwerk und Geraete;
- prinzipiell durch Sicherheitskontext abdeckbar, aber nicht nachgewiesen: Netzwerk, Geraete und Schreibzugriffe;
- rein nachlaufend: Workspace-Inventarvergleich.

Gegenbaseline 1 ist ein laufend gestarteter und danach dem Job zugeordneter Prozess. Wegen nicht rueckwirkend erfasster Vorzuordnungsoperationen ist er unzulaessig.

Gegenbaseline 2 ist Polling fuer Threads, Handles oder Wandzeit. Es kann Verletzungen erkennen und abbrechen, bietet aber keine harte Vorab- oder Null-Latenz-Garantie.

Gegenbaseline 3 ist WFP-Netzwerkfilterung. Sie kann pro Anwendung blockieren, fuegt aber privilegierte Systemkonfiguration und Ruecknahme als neue Seiteneffekte hinzu.

Gegenbaseline 4 ist AppContainer ohne Capabilities. Es bietet vorbeugende Isolation, ist fuer den gebundenen Python-Korridor aber noch nicht kompatibilitaetsgeprueft.

## Grenzen und nicht gepruefte Annahmen

Nicht geprueft wurden Python unter AppContainer, konkrete ACLs, Profilfreiheit, native Bibliotheksimporte, vorhandene uebergeordnete Jobzuordnung des Supervisors, erforderliche Windows-Berechtigungen und die tatsaechliche Supervisorimplementierung.

Die Analyse beweist keine Ausfuehrungssicherheit. Insbesondere bleibt die Forderung nach harten numerischen Thread- und allgemeinen Handlegrenzen unerfuellt.

## Freigabefelder

- `real_operations_binding_release: false`
- `real_fixation_execution_release: false`
- `runtime_release: false`
- `runner_release: false`
- `integrator_release: false`
- `hook_release: false`
- `executor_release: false`
- `public_av_release: false`
- `production_switch_release: false`
- `automatic_execution_release: false`
- `orchestrator_handoff_release: false`
- `minimal_test_release: false`

`minimal_test_release_recommended: false`

## Konkrete Schlussfolgerung

Ein Zwei-Prozess-Vertrag ist statisch sauber neu bindbar. Job Objects koennen wesentliche Prozess-, Speicher- und CPU-Grenzen vor Benutzer-Code erzwingen, wenn der Kindprozess suspendiert erzeugt, vollstaendig konfiguriert und erst danach fortgesetzt wird.

Der Gesamtvertrag aus Lauf 209 ist jedoch nicht vollstaendig implementierbar, solange harte Grenzen fuer Threadzahl und allgemeine Handles unveraendert verlangt werden. Netzwerk-, Geraete- und Schreibisolation erfordern zudem einen separat geprueften Sicherheitskontext wie AppContainer; Job Objects allein reichen nicht.

Huerde G und jede reale Ausfuehrung bleiben gesperrt. Keine Supervisorimplementierung wird freigegeben.

## Naechster begrenzter Forschungs- und Entwicklungslauf

Als naechster Lauf ist ausschliesslich die unabhaengige statische Gegenpruefung von Lauf 210 zulaessig. Danach sollte ein rein dokumentarischer Entscheidungsvertrag festlegen, ob Thread- und Handlewerte zwingende harte Vorabgrenzen bleiben. Bleiben sie zwingend, ist der geplante Einmallauf technisch blockiert. Werden sie methodisch zu beobachteten Nachlaufkriterien herabgestuft, waere dies eine ausdrueckliche Aenderung von Huerde C und muesste vor jeder Implementierung neu begruendet und unabhaengig abgenommen werden.

Separat waere danach die AppContainer-Kompatibilitaet des gebundenen Python-Korridors statisch zu untersuchen. Auch daraus duerfte keine Ausfuehrungsfreigabe folgen.

## Aussagegrenze und Zielabweichung

Kein Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

Keine erkennbare Zielabweichung. Die Analyse trennt nachweisbare Kernelgrenzen von Messung und Hypothese und verhindert eine Ausfuehrung auf Basis unzutreffender Sicherheitsannahmen.
