# Lauf 209 - Korrekturplan Huerde G: Ressourcenwaechter, Prozessvertrag und Artefaktkontrolle

## Forschungsfrage und Auftrag

Wie koennen die in Lauf 208 festgestellten technischen Luecken fuer einen moeglichen spaeteren Einmallauf geschlossen werden, ohne bereits eine Implementierung oder Ausfuehrung freizugeben?

Dieser Lauf ist ausschliesslich ein dokumentarischer Korrekturplan. Es wurden keine Projektmodule importiert, keine Tests ausgefuehrt und keine Bindungs-, Handoff-, Orchestrator-, Fixierungs- oder Runtime-Funktion aufgerufen.

## Verwendete Quellen und Bytebindung

| Quelle | SHA-256 |
|---|---|
| `docs/forschung/192_SPERR_UND_FREIGABEBEDINGUNGEN_REALE_FIXIERUNGSAUSFUEHRUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md` | `d6b9fedd7310425bff7bbdd3b9f2a778e0ede32c6074d4b68f78c8c4cede7edb` |
| `docs/forschung/195_HUERDE_C_RESSOURCEN_UND_ZEITGRENZEN_EINMALLAUF_RUNTIME_FIXIERUNG.md` | `0154a6de7e80b5db8f373878af592855dfa6a0938bd7dedf5ebea927e5ae4ca3` |
| `docs/forschung/204_ERNEUTE_HUERDE_C_RESSOURCEN_UND_ZEITGRENZEN_PRIVATE_EINMALVERKETTUNG.md` | `ec0cead77a18d2b3ca0ba1caca43c0baf96d5af269ea8512fe72ff4823018671` |
| `docs/forschung/206_ERNEUTE_HUERDE_E_AUSGABE_UND_SEITENEFFEKTGRENZEN_PRIVATE_EINMALVERKETTUNG.md` | `ccca9c42afb11a03f4aa3460b275b1a8426e8a4b035a92ed146c404fbe2aced4` |
| `docs/forschung/208_LAUF_HUERDE_G_DOKUMENTARISCHE_ENTSCHEIDUNG_EINMALLAUF_GESPERRT.md` | `13176a3c7a5725b14b8733c35cd5433b03948c2b1923c512737546ec5bc51c38` |
| `mcm_field_organism/_runtime_fixation_structure.py` | `399c0c86800f353d37b77f829666f89df3d6385550caeead3893a580244c746e` |
| `mcm_field_organism/_runtime_fixation_single_use_path.py` | `44cc4dc42bea8b163531d5315e5bab5eda101b1a13f16323e2e34f0ba003787a` |
| `mcm_field_organism/__init__.py` | `c04e371daba2593d771e8ffa26e614746599f15541b303d5d5eaeaeaf332a9b0` |

## Verwendete Dateien und Schnittstellen

Statisch ausgewertet wurden die feste Kontakt- und Passstruktur, `_OPERATION_ROLES`, die private Einmalfunktion und die unveraenderte Exportflaeche. Eine spaetere technische Korrektur duerfte nur eine eng gebundene private Prozessaufsicht vorsehen.

Diese kuenftige Datei existiert noch nicht. Sie ist weder CLI noch Runner oder Executor des Produktionssystems. Bis zu einer gesonderten Umfangsbindung, Implementierungsvorabnahme und unabhaengigen Review bleibt auch sie vollstaendig gesperrt.

## Durchgefuehrte Schritte

1. Fehlende Voraussetzungen aus Lauf 208 in Prozess-, Ressourcen- und Artefaktbedingungen zerlegt.
2. Fachliche Zaehllimits aus dem gebundenen statischen Korridor abgeleitet.
3. Endliche vorlaeufige Betriebssystem-Sicherheitsobergrenzen fuer eine spaetere technische Pruefung festgelegt.
4. Einen kuenftigen Einmalbefehl und Arbeitsordnervertrag ohne Ausfuehrung formuliert.
5. Den Konflikt zwischen unabhaengiger Prozessaufsicht und bisheriger Ein-Prozess-Grenze offengelegt.
6. Abbruch-, Ausgabe- und Artefaktkontrolle als kumulative Freigabebedingungen beschrieben.

## Geplanter Arbeitsordner- und Befehlsvertrag

Gebundener Arbeitsordner fuer einen moeglichen spaeteren Einmallauf:

`C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace`

Geplanter exakter Befehl, der erst nach Existenz und Bytebindung der genannten Aufsicht ausgefuehrt werden duerfte:

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .\tools\_runtime_fixation_single_use_supervisor.ps1
```

Der geplante Supervisor duerfte aus dem gebundenen Arbeitsordner exakt einen Kindprozess mit folgendem fest eingebettetem Ziel starten:

```text
C:\Python314\python.exe -B -c "from mcm_field_organism._runtime_fixation_single_use_path import _run_private_runtime_fixation_once; _run_private_runtime_fixation_once()"
```

Der Kindprozess duerfte ausschliesslich `_run_private_runtime_fixation_once()` genau einmal aufrufen und das Ergebnis weder ausgeben noch serialisieren oder persistieren. Die geplante Supervisordatei ist derzeit nicht vorhanden; der Befehl ist nicht freigegeben und wurde nicht ausgefuehrt.

## Geplante numerische Grenzen

| Kategorie | Vorlaeufiger Grenzwert | Grundlage |
|---|---:|---|
| Wandzeit des Kindprozesses | `30000 ms` | endliche Sicherheitsobergrenze, noch dynamisch zu begruenden |
| CPU-Zeit des Kindprozesses | `20000 ms` | endliche Sicherheitsobergrenze, noch dynamisch zu begruenden |
| Peak Working Set des Kindprozesses | `1073741824 Bytes` | endliche Sicherheitsobergrenze, noch dynamisch zu begruenden |
| Kontaktableitungen | `14` | 7 Kontakte mal 2 Paesse |
| Paesse | `2` | statisch fest codiert |
| frische Kontexte | `14` | ein Kontext pro Kontakt und Pass |
| Operationsaufrufe | `127` | 1 Quellenpruefung plus 14 mal 9 Kontaktoperationen |
| `stdout` | `0 Bytes` | Huerde E |
| `stderr` | `0 Bytes` | Huerde E |
| offene Handles des Kindprozesses | maximal `256` | endliche Sicherheitsobergrenze, noch technisch zu validieren |
| Supervisorprozesse | `1` | genau eine Prozessaufsicht |
| Kindprozesse | `1` | genau ein gepruefter Einmalprozess |
| Kindprozesse des Kindprozesses | `0` | keine weitere Prozesserzeugung |
| Threads des Kindprozesses | maximal `1` | nur Hauptthread; Erzwingbarkeit noch nachzuweisen |
| externe Verbindungen | `0` | Netzwerk, IPC, Sensoren und Public-AV verboten |

Die statisch abgeleiteten Werte `14`, `2`, `14` und `127` sind Korridorgrenzen. Wandzeit, CPU-Zeit, Speicher und Handles sind konservative Planwerte, keine gemessenen Laufwerte. Sie duerfen erst nach einer gesonderten statischen Machbarkeitspruefung als technisch erzwingbar gelten.

## Ressourcenwaechter und Vertragskonflikt

Der geplante Supervisor muesste den Kindprozess vor dessen erster Fachoperation einem Windows Job Object zuordnen und mindestens Speicher- und aktive Prozessgrenzen betriebssystemseitig setzen. Wandzeit und CPU-Zeit muessten kumulativ ueberwacht werden. Jede fehlende Messquelle oder Grenzverletzung muesste den gesamten Job beenden.

Dokument 195 erlaubt bislang nur einen Hauptprozess und exakt null zusaetzliche Prozesse. Eine unabhaengige Aufsicht benoetigt jedoch einen Supervisor und einen Kindprozess. Dieser Konflikt darf nicht semantisch umgedeutet werden. Vor jeder Implementierung muessten Huerde A und Huerde C neu gebunden und der Prozessvertrag ausdruecklich auf genau zwei Gesamtprozesse geaendert werden, waehrend dem Kindprozess weiterhin null eigene Kindprozesse erlaubt sind.

Windows Job Objects erzwingen keine allgemeine harte Obergrenze fuer Threadzahl oder offene Handles. Fuer diese Kategorien ist im aktuellen Plan noch kein hinreichender Mechanismus nachgewiesen. Polling nach Entstehung waere keine vollstaendige Vorab-Erzwingung. Deshalb ist der Plan noch nicht implementierungsreif und Huerde G bleibt gesperrt.

## Grenzabbruch ohne Teilresultat

Der spaetere Supervisor muesste bei Grenzverletzung, Messausfall, unerwartetem Exit, Ausgabe auf `stdout` oder `stderr`, neuem Kindprozess oder externer Verbindung:

1. den gesamten Job beenden;
2. keinen Retry oder zweiten Prozessstart ausloesen;
3. kein `_FixedDigestBundle` oder Teilresultat uebernehmen;
4. ausschliesslich einen technischen Fehler-Exit liefern;
5. keine Projekt-, Ergebnis- oder Persistenzdatei schreiben.

Ein Erfolg duerfte nur anhand eines Exitcodes unterschieden werden. Das fluechtige `_FixedDigestBundle` duerfte den Kindprozess nicht verlassen.

## Cache- und Artefaktkontrolle

Der Kindprozess muesste mit `-B`, `PYTHONDONTWRITEBYTECODE=1` und einer vorab leeren, gesondert gebundenen Temp-Umgebung starten. Vor und nach dem Prozess waere ein byteweiser Workspace-Inventarvergleich erforderlich.

Verboten bleiben insbesondere:

- `__pycache__`, `.pyc` und `.pyo`;
- Temp-, Log-, Telemetrie- und Profildateien;
- Dumps, Checkpoints und Ergebnisdateien;
- Datenbank- oder Memory-Artefakte;
- Aenderungen an Quellen, Konfiguration oder Dokumenten.

Da auch die Inventarkontrolle keine Dateien schreiben darf, muessten Vor- und Nachinventar ausschliesslich im Speicher des Supervisors gehalten werden. Jede Abweichung waere ein Fehlerabschluss.

## Ausschluss nicht freigegebener Pfade

Weiterhin nicht vorgesehen und gesperrt bleiben:

- Export ueber `mcm_field_organism/__init__.py`;
- allgemeiner CLI-, Runner-, Integrator- oder Executorpfad;
- Hook und Produktionsschalter;
- Public-AV, Netzwerk, Geraete und Weltkontakt;
- automatische, wiederholte oder zeitgesteuerte Ausfuehrung;
- persistente Zustandsaenderung und Ausdruckskanaele.

Der geplante private Supervisor waere ein einmaliger Pruefmechanismus und duerfte nicht als allgemeiner Executor exportiert, installiert oder wiederverwendbar verdrahtet werden.

## Messergebnisse und Gegenbaselines

Beobachtet wurden vier statisch ableitbare Korridorwerte und zwei technische Blocker: der Prozessvertragskonflikt sowie fehlende harte Mechanismen fuer Thread- und Handlegrenzen.

Gegenbaseline 1 ist Dokument 195 mit exakt einem Gesamtprozess. Der geplante unabhaengige Supervisor kann diese Grenze nicht einhalten; eine ausdrueckliche Neuabnahme waere zwingend.

Gegenbaseline 2 ist ein unueberwachter direkter Python-Aufruf. Er koennte Cache-Erzeugung unterdruecken, wuerde aber Ressourcen-, Prozess- und Artefaktgrenzen nicht unabhaengig erzwingen und bleibt daher unzulaessig.

Gegenbaseline 3 ist reine Nachlaufmessung. Sie erkennt Verletzungen erst nachträglich und genuegt nicht als Grenzabbruch.

## Grenzen und nicht gepruefte Annahmen

Nicht nachgewiesen sind die praktische Job-Object-Konfiguration, harte Thread- und Handlegrenzen, die Angemessenheit der vorlaeufigen Zeit-, CPU- und Speicherwerte sowie die vollstaendige Erfassung externer Verbindungen.

Der geplante Befehl wurde nicht ausgefuehrt. Die geplante Supervisordatei existiert nicht. Es gibt keinen Befund zum Laufverhalten des privaten Pfads.

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

Der Korrekturpfad ist konzeptionell bestimmbar, aber noch nicht implementierungsreif. Vor einer Implementierung muessen der Zwei-Prozess-Vertrag und die Erzwingbarkeit aller Ressourcenkategorien unabhaengig statisch geklaert werden.

Huerde G und jede reale Ausfuehrung bleiben gesperrt. Dieser Plan gibt weder die geplante Datei noch den dokumentierten Befehl frei.

## Naechster begrenzter Forschungs- und Entwicklungslauf

Als naechster Lauf ist ausschliesslich die unabhaengige statische Gegenpruefung von Lauf 209 zulaessig. Danach sollte, falls der Plan bestaetigt wird, eine rein dokumentarische technische Machbarkeitsanalyse fuer Windows Job Objects sowie harte Thread-, Handle- und Verbindungsgrenzen folgen. Erst diese Analyse darf entscheiden, ob ein korrigierter Ressourcenwaechter ohne unkontrollierte Luecke implementierbar ist.

## Aussagegrenze und Zielabweichung

Kein Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

Keine erkennbare Zielabweichung. Der Plan begrenzt ausschliesslich einen moeglichen technischen Einmallauf und verhindert eine Freigabe trotz offener Durchsetzungsluecken.
