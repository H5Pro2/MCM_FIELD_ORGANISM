# Teilpaket 213B: Statische AppContainer-, ACL-, Profil-, Temp-, Cache- und Diagnosekarte

## Einordnung, Forschungsfrage und Auftrag

Dies ist statische Dokumentation und **kein Forschungslauf**. Deshalb wird keine
Laufnummer vergeben. Der freigegebene Auftrag 213B lautet, fuer den in 213A
kartierten Python-Korridor die benoetigten AppContainer-/ACL-Klassen sowie Profil-,
Temp-, Cache- und Diagnosepfade mit ihren Artefaktrisiken zu dokumentieren.

Es wurden keine Projektmodule importiert, keine Tests oder Runtimepfade gestartet,
kein AppContainer-Profil angelegt und keine ACL oder Systemeinstellung geaendert.
Dieses Dokument gibt weder eine Implementierung noch Huerde G frei.

## Tatsaechlich verwendete Quellen

Lokale Quellen:

- aktueller Uebergabe-Eingang mit der Freigabe von 213B;
- `docs/forschung/212_LAUF_STATISCHE_APPCONTAINER_KOMPATIBILITAETSANALYSE_PYTHON_KORRIDOR.md`;
- `docs/forschung/213A_STATISCHE_LOKALE_PYTHON_KORRIDOR_DATEI_UND_IMPORTKARTE.md`;
- `.venv/pyvenv.cfg`;
- read-only Ausgaben der Prozessumgebung und statische Dateibestandsdaten aus 212/213A.

Externe Primaerquellen:

- [Microsoft: AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation);
- [Microsoft: Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer);
- [Microsoft: CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile);
- [Python 3.14: Command line and environment](https://docs.python.org/3.14/using/cmdline.html);
- [Python 3.14: `tempfile`](https://docs.python.org/3.14/library/tempfile.html).

Andere projektweite MCM-Quellen wurden fuer diese Windows-Isolationskarte nicht
verwendet.

## Verwendete Dateien und Schnittstellen

213A bindet statisch 20 lokale Python-Dateien mit 44 relativen Importkanten und 13
externen Importwurzeln. Fuer die Windows-Karte wurden ferner folgende lokale
Interpreter- und Laufzeitklassen aus dem dokumentierten Bestand uebernommen:

- `.venv/Scripts/python.exe`;
- `C:/Python314/python.exe`, `python3.dll`, `python314.dll` und Visual-C-Runtime-DLLs;
- `C:/Python314/DLLs` und `C:/Python314/Lib`;
- native NumPy-PYD- und DLL-Bestaende;
- der Workspace und die in 213A erfassten Projektquellen.

`CreateAppContainerProfile`, Package-SID, Capability-SIDs, DACL-Pruefung und der
AppContainer-Prozessstart wurden nur als dokumentierte Windows-Schnittstellen
bewertet. Keine davon wurde aufgerufen. Es wurde keine vorhandene ACL ausgelesen
oder veraendert und keine SID erzeugt oder abgeleitet.

## Durchgefuehrte Schritte

1. Den statischen Datei- und Importabschluss aus 213A als Korridorgrenze uebernommen.
2. Fuer jede Dateiklasse die mindestens plausible Zugriffsart kartiert.
3. Das Package-SID-/Capability-SID-/DACL-Modell gegen die lokale Dateiverteilung
   abgegrenzt.
4. Profil-, Temp-, Bytecode-Cache- und Diagnosepfade auf moegliche persistente
   Artefakte eingeordnet.
5. Normale Benutzerumgebung, regulaeren AppContainer, LPAC und schreibfreien
   Korridor als statische Gegenbaselines verglichen.
6. Die Freigabefelder und die fortbestehenden Thread-/Handlegrenzen kontrolliert.

## Beobachtete lokale Basis

| Beobachtung | Statischer Wert |
| --- | --- |
| venv-Basisinterpreter | `C:\Python314\python.exe` |
| venv-Version | `3.14.4` |
| `include-system-site-packages` | `false` |
| normale `TEMP`-/`TMP`-Baseline | `C:\Users\TV\AppData\Local\Temp` |
| normale `LOCALAPPDATA`-Baseline | `C:\Users\TV\AppData\Local` |
| normale `APPDATA`-Baseline | `C:\Users\TV\AppData\Roaming` |
| `PYTHONDONTWRITEBYTECODE` | nicht gesetzt |
| `PYTHONPYCACHEPREFIX` | nicht gesetzt |
| `PYTHONHOME`, `PYTHONUSERBASE`, `PYTHONSTARTUP` | nicht gesetzt |
| `PYTHONFAULTHANDLER` | nicht gesetzt |

Diese Werte stammen aus dem normalen Agentprozess. Sie sind **keine** Messung einer
AppContainer-Umgebung. Microsoft dokumentiert fuer ein angelegtes AppContainer-Profil
eine Umleitung von `LOCALAPPDATA` in den Paketprofilbereich und von `TEMP`/`TMP` in
dessen `AC\Temp`-Unterverzeichnis. Die konkrete Zielzeichenfolge kann erst nach einer
Profilbindung feststehen; eine solche Bindung existiert hier nicht.

## AppContainer- und ACL-Modell

Nach Microsoft traegt der AppContainer-Token eine Package-SID und gegebenenfalls
Capability-SIDs. Bei geschuetzten Ressourcen muss der Zugriff sowohl fuer den
Benutzerkontext als auch fuer den AppContainer-Kontext zulaessig sein. Daraus folgt
technisch: Benutzerrechte allein beweisen keinen Zugriff des AppContainers, und eine
Package-SID-DACL allein ersetzt nicht die uebrigen Windows-Zugriffspruefungen.

Die folgende Matrix nennt erforderliche Zugriffsklassen, aber keine fertigen DACLs:

| Ressourcenklasse | Mindestens plausible Rechte | Schreibrecht | Nachweisstand |
| --- | --- | --- | --- |
| `.venv/Scripts/python.exe` | Eltern durchqueren, Datei lesen/ausfuehren | nein | Datei gebunden, SID/DACL offen |
| Basisinterpreter und Python-/VC-Runtime-DLLs | Eltern durchqueren, lesen/ausfuehren | nein | Bestand statisch erfasst, transitive Loaderkette offen |
| `C:/Python314/DLLs` und native PYD/DLLs | Eltern durchqueren, lesen/ausfuehren | nein | Klassen erfasst, Loader-/System-DLL-Abschluss offen |
| Python-Standardbibliothek | Eltern durchqueren, Quelldateien lesen | nein | Bestand erfasst, verwendete Dateien nicht transitiv gebunden |
| 20 lokale Projektdateien aus 213A | Workspace/Paket durchqueren, Dateien lesen | nein | Dateien gebunden, konkrete SID/DACL offen |
| Arbeitsverzeichnis | durchqueren und benoetigte Quellen lesen | nein | Arbeitsverzeichnis fuer Start nicht festgelegt |
| Eingabe-/Ausgabe-Handles | nur vorab gebundene Standardhandles oder eng definierte IPC | nein | Handlevertrag nicht vorhanden |
| AppContainer-Profil | Windows-seitig profilbezogener Zugriff | grundsaetzlich ja | Profilanlage verboten und nicht erfolgt |
| Temp-Bereich | nur falls Laufzeitoperation ihn tatsaechlich benoetigt | moeglicherweise | Bedarf und Ziel nicht dynamisch geprueft |

Die konkreten ACEs, Vererbungsflags, Integritaetslabels, Eigentumsverhaeltnisse und
Package-SID sind nicht festgelegt. Eine ACL-Aenderung waere eine separate persistente
Systemhandlung und ist nicht Bestandteil von 213B.

## Capability- und Isolationsannahmen

| Klasse | Statische Anforderung | Grenze |
| --- | --- | --- |
| Netzwerk | keine Netzwerk-Capability erteilen | keine allgemeine Null-IPC-Aussage |
| Kamera/Mikrofon | keine Webcam-/Mikrofon-Capability erteilen | keine Geraeteausfuehrung geprueft |
| weitere Geraete | keine unnoetige Device-Capability erteilen | Microsoft nennt Ausnahmen bzw. allgemein zugaengliche Ressourcen |
| fremde Dateien/Registry | keine zusaetzlichen persistenten Pfade freigeben | regulaere AppContainer haben begrenzten gemeinsamen Systemzugriff |
| LPAC | als strengere Gegenbaseline betrachten | Kompatibilitaet des Python-Korridors nicht nachgewiesen |

Ein regulaerer AppContainer ist daher keine belegte absolute Nullzugriffsumgebung.
LPAC kann den Zugriff weiter reduzieren, ist aber ebenfalls kein statischer
Kompatibilitaetsnachweis.

## Profil-, Temp-, Cache- und Diagnosekarte

| Klasse | Kandidatenpfad oder Mechanismus | Artefaktrisiko | Einordnung |
| --- | --- | --- | --- |
| Profilanlage | per-user/per-app Paketordner und Registryspeicher | persistent | `CreateAppContainerProfile` erzeugt beides; aktuell verboten |
| AppContainer LocalAppData | `...\Packages\<Profil>\AC` | persistent | Profilname/SID nicht gebunden |
| AppContainer Temp | `...\Packages\<Profil>\AC\Temp` | Dateien koennen Laufende ueberdauern | Schreibbedarf ungeprueft |
| normale Temp-Baseline | `C:\Users\TV\AppData\Local\Temp` | persistent bis Loeschung | kein AppContainer-Nachweis |
| Python-Temp-Auswahl | `TMPDIR`, `TEMP`, `TMP`, Windows-Fallbacks, danach Arbeitsverzeichnis | Ausweichschreiben moeglich | `tempfile`-Verhalten; kein Projektbedarf nachgewiesen |
| Bytecode-Cache | `__pycache__` oder `PYTHONPYCACHEPREFIX` | `.pyc`-Artefakte | `-B`/`PYTHONDONTWRITEBYTECODE` unterdrueckt `.pyc`, nicht alle Caches |
| Benutzer-/Bibliothekscache | bibliotheksspezifisch, oft unter Profil/LocalAppData | unbekannt bis persistent | statisch nicht vollstaendig kartiert |
| Standardausgabe/-fehler | geerbte oder explizit gebundene Handles | kein Dateiartefakt bei nichtdateibasiertem Sink | konkrete Handles offen |
| Python-Diagnose | `PYTHONFAULTHANDLER`, Tracebacks, Warnungen | je nach Sink | Variable aktuell nicht gesetzt; Verhalten ungeprueft |
| Windows-Fehlerdiagnose | WER/CrashDump-Systempfade und Richtlinien | moegliche Dump-/Berichtsartefakte | lokale Richtlinie und AppContainer-Verhalten ungeprueft |

Die Python-Optionen `-B`, `-E` und `-I` sind nur begrenzte technische Kontrollen:
`-B` verhindert Python-Bytecode-Schreiben, `-E` ignoriert `PYTHON*`-Variablen und
`-I` aktiviert isolierten Modus. Keine dieser Optionen verhindert allgemein Temp-,
Drittbibliotheks-, WER-, Dump- oder andere Windows-Artefakte.

## Technische Interpretation

Eine minimale statische ACL-Konzeption waere read/execute fuer Interpreter und native
Bibliotheken, read fuer Python- und Projektquellen, traverse fuer alle Elternpfade und
kein Workspace-Schreibrecht. Diese Konzeption ist noch nicht implementierbar, weil
Package-SID, vollstaendiger Loaderabschluss, konkrete Standardbibliotheksdateien,
Startarbeitsverzeichnis und Handlevertrag fehlen.

Das AppContainer-Profil stellt einen systemseitigen Schreibbereich bereit. Das kann
Python-Kompatibilitaet erleichtern, kollidiert aber mit einem strikten
Null-Artefakt-Vertrag. Ein vollstaendig schreibfreier Korridor vermeidet diese Klasse,
kann jedoch bereits beim Interpreter- oder Bibliotheksstart inkompatibel sein. Welche
Seite zutrifft, ist ohne einen spaeter separat freigegebenen Versuch nicht entschieden.

## Messergebnisse und Gegenbaselines

213B erzeugte keine dynamischen Messwerte. Statisch wurden kartiert:

- 7 zentrale lokale Zugriffsklassen plus Profil- und Tempklasse;
- 10 Profil-/Temp-/Cache-/Diagnoseklassen;
- 5 Capability-/Isolationsklassen;
- 0 konkrete Package-SIDs;
- 0 gelesene oder geaenderte ACLs;
- 0 angelegte Profile;
- 0 gestartete Prozesse, Imports oder Tests.

| Gegenbaseline | Statische Aussage |
| --- | --- |
| normaler Benutzerprozess | lokale Umgebungswerte sind sichtbar, aber keine Package-SID-Isolation vorhanden |
| regulaerer AppContainer mit Profil | bietet Paketprofil und Temp-Umleitung, erzeugt jedoch persistente Infrastruktur |
| LPAC | reduziert gemeinsamen Zugriff weiter; Python-Kompatibilitaet bleibt offen |
| AppContainer mit breiten Capabilities/ACLs | hoeherer Kompatibilitaetskandidat, verletzt das Minimierungsziel |
| AppContainer ohne Quellen-ACLs | erwartbarer Zugriffsfehler; kein sinnvoller Kompatibilitaetsnachweis |
| schreibfreier Korridor mit `-B -E -I` | reduziert Python-seitige Schreib-/Umgebungspfade, beweist aber keine Artefaktfreiheit oder Lauffaehigkeit |
| normaler Paketimport | umfasst laut 213A mehr als den privaten Einstieg allein und bleibt die weitere Abhaengigkeits-Gegenbaseline |

AppContainer dokumentiert weiterhin keine harte numerische Grenze fuer eigene Threads
oder alle offenen Handles. Der Beitrag zur harten Threadgrenze und zur allgemeinen
Handlegrenze bleibt jeweils `false`.

## Freigabefelder

| Freigabefeld | Wert |
| --- | --- |
| `real_operations_binding_release` | `false` |
| `real_fixation_execution_release` | `false` |
| `runtime_release` | `false` |
| `runner_release` | `false` |
| `integrator_release` | `false` |
| `hook_release` | `false` |
| `executor_release` | `false` |
| `public_av_release` | `false` |
| `production_switch_release` | `false` |
| `automatic_execution_release` | `false` |
| `orchestrator_handoff_release` | `false` |
| `minimal_test_release` | `false` |

`minimal_test_release_recommended: false`

## Grenzen, offene Fragen und nicht gepruefte Annahmen

- **Beobachtet:** Interpreterpfad, normale Benutzer-Umgebungswerte und statische
  Dateiklassen sind vorhanden; ein AppContainer-Profil wurde nicht angelegt.
- **Technische Interpretation:** Die kartierten read/execute/read/traverse-Rechte
  sind plausible Mindestklassen, keine validierte DACL.
- **Hypothese:** Ein read-only Korridor mit eng gebundenen Handles koennte einen Teil
  der Artefaktflaeche reduzieren. Seine Lauffaehigkeit ist nicht nachgewiesen.
- **Offene Frage:** Welche Standardbibliotheks-, System-DLL-, Temp-, Cache- und
  Diagnosepfade werden bei genau diesem Start tatsaechlich beruehrt?
- **Nicht gepruefte Annahme:** `-B -E -I` genuegt nicht als Null-Artefakt-Beweis und
  wird hier nicht als solcher behandelt.
- Konkrete Package-SID, ACE-Reihenfolge, Vererbung, Integritaetslabel und vorhandene
  Systemrichtlinien wurden nicht gebunden.
- WER-, CrashDump- und Drittbibliotheksverhalten im AppContainer wurde nicht geprueft.
- Thread- und allgemeine Handleobergrenzen bleiben ungeloest.
- Es gibt keinen Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation,
  Topologie, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## Konkrete Schlussfolgerung

213B liefert eine pruefbare statische Klassenkarte, aber keine konkrete ACL- oder
AppContainer-Konfiguration. Fuer den Python-Korridor waeren mindestens traverse,
read und read/execute auf mehreren getrennten Verzeichnis- und Dateiklassen noetig.
Profilanlage und profilbezogene Temp-Nutzung sind persistente Infrastruktur- bzw.
Artefaktrisiken. Python-Schalter koennen einzelne Cache- und Umgebungseffekte
reduzieren, ersetzen aber weder Windows-Isolation noch einen Null-Artefakt-Nachweis.

Die konkrete Python-AppContainer-Lauffaehigkeit ist nicht nachgewiesen. Huerde G,
Implementierung, Profilanlage, ACL-/Systemaenderungen, Projektimporte, Tests und reale
Ausfuehrung bleiben gesperrt.

## Naechster begrenzter Schritt

Als naechster Schritt ist ausschliesslich die unabhaengige statische Gegenpruefung von
213B vorgesehen. Sie soll Quellenbezug, lokale Pfadwerte, Zugriffsklassen,
Profilpersistenz, Temp-/Cache-/Diagnoserisiken, Gegenbaselines, die zwoelf falschen
Freigabefelder und die fortbestehende Huerde-G-Sperre reproduzieren.

Eine positive Pruefung waere keine Freigabe fuer Implementierung oder Ausfuehrung.
Danach waere als weiteres getrenntes statisches Teilpaket hoechstens die Bindung einer
konkreten Package-SID-/ACE-Sollmatrix zu pruefen, weiterhin ohne Profilanlage oder
ACL-Aenderung.

## Zielabweichung

Keine erkennbare Zielabweichung. 213B dokumentiert nur den gesperrten technischen
Isolationskorridor und behauptet keine MCM-, Memory-, Organismus- oder KI-Funktion.
