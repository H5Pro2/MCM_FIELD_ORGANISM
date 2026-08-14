# Teilpaket 213D: Read-only ACL- und Mandatory-Label-Istaufnahme

## Einordnung, Forschungsfrage und Auftrag

Dies ist eine statische Read-only-Istaufnahme und **kein Forschungslauf**. Deshalb
wird keine Laufnummer vergeben. Der freigegebene Auftrag lautet, vorhandene DACL- und
Mandatory-Label-Strukturen auf den bereits gebundenen Pfadklassen des Python-Korridors
zu erfassen.

Es wurden ausschliesslich Dateiattribute und Sicherheitsdeskriptoren gelesen. Es gab
keine SID-Ableitung, Profilanlage, ACL-/Systemaenderung, Projektimporte, Tests,
Prozessstarts oder Implementierung. Huerde G bleibt gesperrt.

## Tatsaechlich verwendete Quellen

Lokale Quellen:

- aktueller Uebergabe-Eingang mit der Freigabe von 213D;
- `docs/forschung/213A_STATISCHE_LOKALE_PYTHON_KORRIDOR_DATEI_UND_IMPORTKARTE.md`;
- `docs/forschung/213B_STATISCHE_APPCONTAINER_ACL_PROFIL_TEMP_CACHE_DIAGNOSEKARTE.md`;
- `docs/forschung/213C_STATISCHE_PACKAGE_CAPABILITY_SID_ACE_SOLLMATRIX.md`;
- `.venv/pyvenv.cfg`;
- read-only Ausgaben von `Get-Item`, `Get-Acl`, `Resolve-Path` und statischer
  Markdown-Auswertung mit `Select-String`.

Externe Primaerquelle:

- [Microsoft: Mandatory Integrity Control](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control).

Andere projektweite MCM-Quellen wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Untersucht wurden vier Pfadgruppen:

1. Workspace-Elternkette von `C:\` bis `workspace/mcm_field_organism`;
2. virtuelle Umgebung bis `.venv/Scripts/python.exe` und NumPy unter
   `.venv/Lib/site-packages`;
3. Basisinterpreter `C:/Python314` mit `python.exe`, `python3.dll`, `python314.dll`,
   `DLLs` und `Lib`;
4. die 20 in 213A gebundenen lokalen Module plus `mcm_field_organism/__init__.py`.

`Get-Acl` wurde fuer Owner, DACL-Schutzstatus, Access-ACEs und SDDL-DACL verwendet.
`Get-Acl -Audit` wurde read-only fuer die SACL-/Mandatory-Label-Klasse versucht. Der
Versuch scheiterte bei allen sechs repraesentativ abgefragten Objekten an fehlendem
`SeSecurityPrivilege`. Es wurde keine Berechtigung angefordert oder aktiviert.

## Durchgefuehrte Schritte

1. Existenz, Objekttyp und Reparse-Point-Status der gebundenen Pfadklassen gelesen.
2. Owner, DACL-Schutzstatus, Regelanzahl, Trustee, Allow/Deny, Rechte und Vererbung
   erfasst.
3. Die 21 lokalen Paketdateien nach identischer DACL und Owner gruppiert.
4. Lesbare DACLs auf AppContainer-Praefix `S-1-15-` geprueft.
5. Repraesentative SACL-Leseversuche fuer Workspace, Paket, venv-Interpreter und
   Python-Basis vorgenommen.
6. Beobachtete Iststruktur gegen die symbolische Sollmatrix aus 213C abgegrenzt.

## Beobachtete DACL-Iststruktur

### Eltern- und Laufzeitpfade

| Pfadklasse | DACL lesbar | Owner | DACL geschuetzt | Regeln | `S-1-15-`-ACE | Reparse Point |
| --- | --- | --- | --- | ---: | --- | --- |
| `C:\` | ja | Administratoren | nein | 8 | nein | nein |
| `C:\Users` | ja | SYSTEM | ja | 6 | nein | nein |
| `C:\Users\TV` | **nein** | nicht beobachtbar | nicht beobachtbar | - | nicht beobachtbar | nicht beobachtbar |
| `C:\Users\TV\Documents` | ja | Benutzer `TV` | nein | 4 | nein | nein |
| `...\MCM_FIELD_ORGANISM` | ja | Benutzer `TV` | nein | 7 | nein | nein |
| Workspace | ja | Benutzer `TV` | nein | 9 | nein | nein |
| `workspace\mcm_field_organism` | ja | Benutzer `TV` | nein | 8 | nein | nein |
| `.venv` | ja | `CodexSandboxOnline` | nein | 8 | nein | nein |
| `.venv\Lib\site-packages` | ja | `CodexSandboxOnline` | nein | 8 | nein | nein |
| `.venv\Lib\site-packages\numpy` | ja | `CodexSandboxOnline` | nein | 8 | nein | nein |
| `C:\Python314` | ja | Administratoren | **ja** | 3 | nein | nein |
| `C:\Python314\DLLs` | ja | SYSTEM | nein | 3 | nein | nein |
| `C:\Python314\Lib` | ja | SYSTEM | nein | 3 | nein | nein |

Von 13 ausgewaehlten Eltern-/Laufzeitpfaden waren 12 DACLs lesbar. Die DACL von
`C:\Users\TV` verweigerte die read-only Abfrage. Damit ist die fuer Pfadauflosung
relevante Elternkette nicht vollstaendig beobachtet.

### Aufgeloeste Rechtefamilien

Workspace und Paketverzeichnis enthalten ausschliesslich Allow-Regeln. Beobachtet
wurden:

- mehrere Sandbox-Trustees mit `Modify, Synchronize`;
- `SYSTEM`, Administratoren und Benutzer `TV` mit `FullControl`;
- im Workspace drei explizite und sechs geerbte Allow-Regeln;
- im Paketverzeichnis acht geerbte Allow-Regeln.

Fuenf Sandbox-Trustees erscheinen teilweise nur als nicht lokal aufloesbare
Konten-SIDs. Ihre fachliche Herkunft und Lebensdauer wurde nicht abgeleitet.

Die `.venv/Scripts/python.exe` besitzt acht geerbte Allow-Regeln: Sandbox-Trustees
mit `Modify, Synchronize` sowie `SYSTEM`, Administratoren und Benutzer `TV` mit
`FullControl`.

`C:\Python314` besitzt drei explizite, auf Kinder vererbbare Allow-Regeln:

- `SYSTEM`: `FullControl`;
- Administratoren: `FullControl`;
- eingebaute Benutzergruppe: `ReadAndExecute, Synchronize`.

`python.exe`, `python3.dll`, `python314.dll`, `DLLs` und `Lib` uebernehmen diese
Familie geerbt. Die Basisinterpreter-DACL ist damit gegen Veraenderung durch normale
Benutzer restriktiver als die Workspace-DACL, enthaelt aber ebenfalls keine
beobachtete Package-SID-ACE.

### Lokale Python-Dateien

Die 20 in 213A kartierten Module plus `__init__.py` ergeben 21 Dateien. Ihre
Access-DACL ist in allen 21 Faellen strukturell gleich: acht geerbte Allow-Regeln aus
dem Paketverzeichnis. Es wurden zwei Ownergruppen beobachtet:

| Ownergruppe | Dateien | DACL-Regeln | DACL geschuetzt |
| --- | ---: | ---: | --- |
| `CodexSandboxOffline` | 6 | 8 geerbte Allow-Regeln | nein |
| Benutzer `TV` | 15 | 8 geerbte Allow-Regeln | nein |

Der abweichende Owner aendert in dieser Istaufnahme nicht die beobachtete Access-DACL.
Er waere bei einer spaeteren Aenderungs- oder Ruecknahmeplanung dennoch eine eigene
persistente Sicherheitsdimension. Eine solche Planung ist nicht freigegeben.

## Package- und Capability-SID-Befund

Keine der 12 lesbaren Eltern-/Laufzeit-DACLs und keine der 21 lokalen Datei-DACLs
enthielt im gelesenen Access-SDDL einen Trustee mit dem AppContainer-Praefix
`S-1-15-`.

**Beobachtetes Ergebnis:** Es gibt auf den lesbaren, ausgewaehlten Objekten keine
bereits vorhandene Package- oder Capability-SID-ACE.

**Grenze:** Daraus folgt keine systemweite Abwesenheit solcher ACEs. Die DACL von
`C:\Users\TV`, nicht ausgewaehlte System-/Bibliotheksdateien und nicht lesbare
Deskriptoren sind nicht abgedeckt.

## Mandatory-Label-Istaufnahme

Microsoft dokumentiert, dass ein Mandatory Integrity Label als
`SYSTEM_MANDATORY_LABEL_ACE` in der SACL liegt und vor der DACL-Zugriffspruefung wirkt.
Ein Objekt ohne Integrity SID wird von Windows wie Medium Integrity behandelt.

Repraesentativ wurden folgende sechs Objekte mit `Get-Acl -Audit` abgefragt:

- Workspace;
- `mcm_field_organism`;
- `.venv/Scripts/python.exe`;
- `C:\Python314`;
- `C:\Python314\python.exe`;
- `C:\Python314\Lib`.

Alle sechs Abfragen scheiterten mit dem Befund, dass dem Prozess
`SeSecurityPrivilege` fehlt.

Damit gilt:

- lesbare Mandatory Labels: `0/6`;
- nachgewiesene Low-/Medium-/High-/System-Labels: `0`;
- nachgewiesene Abwesenheit eines Labels: `0`;
- zulaessige Aussage zur effektiven MIC-Pruefung: offen.

Die normale DACL-SDDL-Ausgabe enthaelt keine gelesene SACL. Das Fehlen eines Labels in
dieser Ausgabe darf daher nicht als unlabeled/Medium-Befund interpretiert werden.

## Soll-Ist-Abgleich zu 213C

| 213C-Sollpunkt | Istbefund | Bewertung |
| --- | --- | --- |
| konkrete Package-SID-ACE | auf lesbaren Objekten nicht vorhanden | Sollmatrix nicht angewandt |
| 0 Capability-SIDs | keine `S-1-15-`-ACE beobachtet | konsistent mit Nichtanwendung, kein Tokenbefund |
| keine Deny-ACEs in neuer Matrix | untersuchte DACLs zeigen nur Allow-Regeln | bestehender Zustand, keine Matrixvalidierung |
| keine pauschale Vererbung fuer neue SID | keine Package-SID vorhanden | nicht pruefbar |
| Elternpfade muessen traverse-faehig sein | eine Eltern-DACL unlesbar | Abschluss blockiert |
| Benutzerrechte muessen Sollrechte tragen | Workspace breit, Python-Basis `ReadAndExecute` fuer Benutzer | nur Teilvoraussetzung, Token-Schnittmenge offen |
| Mandatory Label muss kompatibel sein | SACL unlesbar | blockiert |
| keine Schreibrechte fuer Package-SID | keine Package-SID vorhanden | weder bestaetigt noch widerlegt fuer spaetere Matrix |

Die vorhandenen breiten Benutzer-/Sandbox-Rechte ersetzen keine AppContainer-ACE.
Nach dem dualen Zugriffsmodell bleibt die Package-SID-Seite der Schnittmenge leer.

## Messergebnisse und Gegenbaselines

Statische Read-only-Ergebnisse:

- ausgewaehlte Eltern-/Laufzeitpfade: `13`;
- lesbare DACLs: `12/13`;
- unlesbare DACLs: `1/13` (`C:\Users\TV`);
- lokale Python-Dateien: `21`;
- gemeinsame lokale Datei-DACL-Familien: `1`;
- lokale Datei-Ownergruppen: `2` (`6 + 15` Dateien);
- lesbare DACLs mit `S-1-15-`-Trustee: `0`;
- repraesentative SACL-Abfragen: `6`;
- lesbare SACLs/Mandatory Labels: `0/6`;
- Reparse Points unter den erfolgreich gelesenen ausgewaehlten Pfaden: `0`;
- ACL-/Systemaenderungen, SID-Ableitungen, Profile, Imports, Tests und Prozessstarts:
  jeweils `0`.

Gegenbaselines:

| Gegenbaseline | Ergebnis |
| --- | --- |
| Workspace-DACL | breite Modify-/FullControl-Struktur, aber keine Package-SID |
| Python-Basis-DACL | drei Trustees; Benutzer nur ReadAndExecute, aber keine Package-SID |
| 213C-Sollmatrix | engere Einzelobjekt-ACEs; aktuell nirgends angewandt |
| lesbare DACL ohne SACL | erlaubt keine Mandatory-Label-Aussage |
| Microsoft-Fallback fuer unlabeled Objekte | konzeptionell Medium, aber Unlabeled-Status lokal nicht beobachtet |

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

- **Beobachtet:** Zwei zentrale DACL-Familien, keine `S-1-15-`-ACE auf lesbaren
  Objekten, eine unlesbare Eltern-DACL und sechs wegen fehlendem Privileg unlesbare
  SACLs.
- **Technische Interpretation:** Die bestehende Benutzer-DACL kann den
  AppContainer-Anteil der dualen Zugriffsschnittmenge nicht ersetzen.
- **Hypothese:** Die Benutzerseite koennte fuer Python-Basisdateien mindestens
  read/execute tragen; der reale AppContainer-Zugriff bleibt ohne Package-SID und MIC-
  Befund unmoeglich zu bewerten.
- **Offene Frage:** Welche Mandatory Labels und Policies liegen tatsaechlich vor?
- **Nicht gepruefte Annahme:** Nicht aufloesbare Sandbox-SIDs bleiben stabil oder sind
  fuer einen spaeteren AppContainer-Aufbau relevant.
- Die Istaufnahme ist eine Auswahl gebundener Pfadklassen, kein vollstaendiger
  Standardbibliotheks-, NumPy-, Loader- oder System-DLL-Abschluss.
- Es wurde keine effektive Zugriffssimulation gegen einen AppContainer-Token
  ausgefuehrt.
- Harter Thread-/Handlevertrag, Lauffaehigkeit und Artefaktfreiheit bleiben offen.
- Es gibt keinen Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation,
  Topologie, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## Konkrete Schlussfolgerung

Die vorhandenen ACLs enthalten auf den lesbaren ausgewaehlten Pfaden keine
AppContainer-Package- oder Capability-SID-ACE. Workspace und venv besitzen breite
geerbte Benutzer-/Sandbox-Rechte; die Python-Basis ist mit einer geschuetzten
Root-DACL und vererbtem ReadAndExecute fuer die Benutzergruppe restriktiver. Eine
Eltern-DACL und saemtliche repraesentativen SACL-/Mandatory-Label-Abfragen bleiben
unlesbar.

Damit ist die Sollmatrix aus 213C weder anwendbar noch validiert. Es gibt weiterhin
keinen Nachweis fuer Python-AppContainer-Lauffaehigkeit oder Artefaktfreiheit. Huerde
G, SID-Ableitung, Profilanlage, ACL-/Systemaenderungen, Projektimporte, Tests,
Prozessstarts und Implementierung bleiben gesperrt.

## Naechster begrenzter Schritt

Als naechster Schritt ist ausschliesslich eine unabhaengige statische Gegenpruefung
von 213D vorgesehen. Sie soll insbesondere die `12/13` lesbaren DACLs, die eine
unlesbare Eltern-DACL, die zwei lokalen Ownergruppen, die fehlenden `S-1-15-`-ACEs,
die `0/6` lesbaren SACLs und die daraus folgende Mandatory-Label-Grenze reproduzieren.

Aus dem aktuellen Stand folgt kein automatisch zulaessiges Anschlussvorhaben. Eine
privilegierte SACL-Abfrage oder Erweiterung auf einen vollstaendigen Loaderbaum
benoetigt wegen des Sicherheits- beziehungsweise Umfangswechsels einen neuen, eng
begrenzten Pruefauftrag. Sie darf nicht aus 213D abgeleitet ausgefuehrt werden.

## Zielabweichung

Keine erkennbare Zielabweichung. Die Istaufnahme betrifft nur den gesperrten Windows-
Isolationspfad und behauptet keine MCM-, Memory-, Organismus- oder KI-Funktion.
