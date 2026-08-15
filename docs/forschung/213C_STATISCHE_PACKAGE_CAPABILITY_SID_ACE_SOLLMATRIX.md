# Teilpaket 213C: Statische Package-SID-/Capability-SID-/ACE-Sollmatrix

## Einordnung, Forschungsfrage und Auftrag

Dies ist statische Dokumentation und **kein Forschungslauf**. Deshalb wird keine
Laufnummer vergeben. Der freigegebene Auftrag lautet, fuer den in 213A und 213B
abgegrenzten Python-Korridor eine konkrete, aber noch nicht angewandte
Package-SID-/Capability-SID-/ACE-Sollmatrix zu erstellen.

Die Matrix ist ein Pruefmodell. Sie erzeugt keine SID, legt kein Profil an, liest oder
aendert keine ACL und startet weder Interpreter noch Projektcode. Sie gibt Huerde G,
Implementierung, Tests oder reale Ausfuehrung nicht frei.

## Tatsaechlich verwendete Quellen

Lokale Quellen:

- aktueller Uebergabe-Eingang mit der Freigabe dieses statischen Teilpakets;
- `docs/forschung/213A_STATISCHE_LOKALE_PYTHON_KORRIDOR_DATEI_UND_IMPORTKARTE.md`;
- `docs/forschung/213B_STATISCHE_APPCONTAINER_ACL_PROFIL_TEMP_CACHE_DIAGNOSEKARTE.md`;
- `.venv/pyvenv.cfg`.

Externe Microsoft-Primaerquellen:

- [Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer);
- [AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation);
- [`DeriveAppContainerSidFromAppContainerName`](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-deriveappcontainersidfromappcontainername);
- [File security and access rights](https://learn.microsoft.com/en-us/windows/win32/fileio/file-security-and-access-rights);
- [`AddAccessAllowedObjectAce`](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-addaccessallowedobjectace);
- [Access control entries](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-control-entries).

Andere projektweite MCM-Quellen wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

Die Sollmatrix bezieht sich auf diese bereits statisch erfassten Klassen:

- `.venv/Scripts/python.exe`;
- `C:/Python314/python.exe` und die Python-/VC-Runtime-DLLs;
- `C:/Python314/DLLs` und `C:/Python314/Lib`;
- die in 213A gebundenen 20 lokalen Python-Dateien;
- die in 213A genannten nativen NumPy-PYD-/DLL-Klassen;
- die Elternverzeichnisse dieser Dateien;
- vorab gebundene Standardhandles als noch offene Schnittstellenklasse.

Statisch betrachtet wurden `DeriveAppContainerSidFromAppContainerName`,
`SECURITY_CAPABILITIES`, `PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES`, Windows-DACLs,
Access-Allowed-ACEs und ACE-Vererbungsflags. Keine Schnittstelle wurde aufgerufen.

## Durchgefuehrte Schritte

1. Den Package-SID-Trustee symbolisch festgelegt, ohne SID-Ableitung.
2. Die Capability-Liste nach dem Least-Privilege-Ziel auf leer gesetzt.
3. Verzeichnis- und Dateirechte nach Windows-Zugriffsmasken getrennt.
4. Fuer jede bekannte Ressourcengruppe Trustee, ACE-Typ, Maske und Vererbung als
   Sollwert angegeben.
5. Nichtgewollte Rechte und zu breite Trustees explizit ausgeschlossen.
6. Offene Loader-, Standardbibliotheks-, System- und Handleklassen als Blocker
   markiert.
7. Gegenbaselines und alle Freigabefelder kontrolliert.

## Symbolische Identitaetsbindung

| Feld | Sollwert | Bindungsstand |
| --- | --- | --- |
| Profilname/Moniker | `<UNBOUND_APPCONTAINER_NAME>` | nicht festgelegt |
| Package-SID | `<PACKAGE_SID_DERIVED_FROM_BOUND_NAME>` | nicht abgeleitet |
| Ableitungsbeziehung | deterministisch aus dem gebundenen Namen ueber dokumentierte Windows-Schnittstelle | nur konzeptionell |
| AppContainer-Typ | regulaerer AppContainer als primaere Sollbaseline | nicht gestartet |
| LPAC | getrennte strengere Gegenbaseline | nicht ausgewaehlt oder gestartet |
| Capability-SID-Liste | leer (`CapabilityCount = 0`) | Sollwert, nicht angewandt |
| `ALL APPLICATION PACKAGES` als eigener Trustee | nicht hinzufuegen | Sollwert |
| Benutzer-/Gruppenanteil der Zugriffsschnittmenge | vorhandene Rechte muessen mindestens den Package-SID-Rechten entsprechen | nicht geprueft |
| Mandatory Integrity Label der Ressourcen | muss mit dem Low-IL-Zugriffsmodell vereinbar sein | nicht geprueft |

Ohne gebundenen Moniker gibt es keinen pruefbaren konkreten SID-String. Ein erfundener
SID-Wert waere kein valider Sicherheitsprincipal. Die Microsoft-Funktion zur
SID-Ableitung wird daher nur als spaetere, weiterhin gesperrte Schnittstelle genannt.

## Capability-SID-Sollmatrix

| Capability-Klasse | Sollwert | Begruendung | Restgrenze |
| --- | --- | --- | --- |
| Internet Client | nicht vorhanden | kein Netzwerkbedarf im statischen Korridor | kein allgemeiner Null-IPC-Nachweis |
| Internet Client/Server | nicht vorhanden | kein Listener- oder Netzwerkbedarf | keine Laufzeitpruefung |
| Private Network Client/Server | nicht vorhanden | kein LAN-Bedarf | keine Laufzeitpruefung |
| Webcam | nicht vorhanden | Kamera bleibt gesperrt | Geraetepfade nicht ausgefuehrt |
| Mikrofon | nicht vorhanden | Live-Mikrofon bleibt gesperrt | Geraetepfade nicht ausgefuehrt |
| Pictures/Videos/Music/Documents Library | nicht vorhanden | keine Bibliotheksfreigabe benoetigt | lokale Projektdateien brauchen separate Package-SID-ACEs |
| Removable Storage | nicht vorhanden | kein Wechseldatentraegerbedarf | keine Geraetevollstaendigkeitsbehauptung |
| Shared User Certificates | nicht vorhanden | kein Zertifikatbedarf | keine Krypto-Laufzeitpruefung |
| Enterprise Authentication | nicht vorhanden | kein Anmeldeinformationsbedarf | keine Credential-Laufzeitpruefung |
| LPAC Registry/COM-Zusatzcapabilities | nicht vorhanden | Registry/COM nicht als Korridorbedarf gebunden | LPAC-Kompatibilitaet offen |

Die leere Liste ist ein Minimierungs-Sollwert, kein Beweis, dass der Interpreter damit
startet oder dass keinerlei Windows-Ressource erreichbar ist.

## Rechtelegende

Die Matrix verwendet symbolische Rechteklassen statt SDDL oder `icacls`-Befehlen:

| Symbol | Windows-nahe Bedeutung | Ausdruecklich nicht enthalten |
| --- | --- | --- |
| `T` | Verzeichnis durchqueren (`FILE_TRAVERSE`) und fuer Pfadauflosung erforderliche Attribute lesen | Verzeichnisinhalt auflisten, Dateien anlegen, schreiben, loeschen |
| `R` | Datei lesen einschliesslich Daten, Attribute und erforderlicher Standardrechte | schreiben, anhaengen, loeschen, Berechtigungen aendern |
| `RX` | Datei lesen und ausfuehren | schreiben, anhaengen, loeschen, Berechtigungen aendern |
| `NONE` | keine zusaetzliche Access-Allowed-ACE fuer `<PACKAGE_SID>` | keine Aussage ueber bereits vorhandene System-/Benutzer-ACEs |

`FILE_GENERIC_READ` und `FILE_GENERIC_EXECUTE` werden erst in einer spaeteren
Implementierungspruefung auf konkrete Objektmasken abgebildet. Verzeichnisrechte sind
nicht pauschal mit Dateirechten gleichzusetzen.

## ACE-Sollmatrix fuer Verzeichnisse

| Objektklasse | Trustee | ACE-Typ | Sollmaske | Vererbung | Status/Grund |
| --- | --- | --- | --- | --- | --- |
| Laufwerks-/Elternpfade bis `.venv` | `<PACKAGE_SID>` | Access Allowed | `T` | keine | nur bekannte Pfadauflosung, konkrete Elternliste offen |
| `.venv` und `.venv/Scripts` | `<PACKAGE_SID>` | Access Allowed | `T` | keine | keine pauschale rekursive Freigabe |
| Elternpfade bis `C:/Python314` | `<PACKAGE_SID>` | Access Allowed | `T` | keine | System-/Laufwerksanteil konkret zu binden |
| `C:/Python314` | `<PACKAGE_SID>` | Access Allowed | `T` | keine | Wurzel darf nicht automatisch alles freigeben |
| `C:/Python314/DLLs` | `<PACKAGE_SID>` | Access Allowed | `T` | keine | native Dateien erhalten separate `RX`-ACEs |
| `C:/Python314/Lib` und benoetigte Unterverzeichnisse | `<PACKAGE_SID>` | Access Allowed | `T` | keine | konkreter Standardbibliotheksabschluss fehlt |
| Workspace-Elternpfade | `<PACKAGE_SID>` | Access Allowed | `T` | keine | nur Pfadauflosung |
| Workspace | `<PACKAGE_SID>` | Access Allowed | `T` | keine | kein Schreiben und keine pauschale Rekursion |
| `mcm_field_organism` | `<PACKAGE_SID>` | Access Allowed | `T` | keine | nur die gebundenen Dateien erhalten `R` |
| NumPy-/Site-Packages-Eltern und benoetigte Unterverzeichnisse | `<PACKAGE_SID>` | Access Allowed | `T` | keine | konkrete Pfade/transitive Auswahl offen |
| Profil-, Temp-, Cache- und Diagnoseverzeichnisse | `<PACKAGE_SID>` | keine neue ACE | `NONE` | keine | Null-Artefakt-Sollbaseline; Kompatibilitaet offen |

Die primaere Matrix setzt keine Vererbungsflags. Damit wird verhindert, dass eine ACE
unbeabsichtigt auf nicht gebundene Geschwister oder spaeter hinzukommende Dateien
wirkt. Eine spaetere Alternative mit `OBJECT_INHERIT_ACE` oder
`CONTAINER_INHERIT_ACE` waere ein eigenes, breiteres Modell und muesste gesondert
gegen den aktuellen Dateibaum geprueft werden.

## ACE-Sollmatrix fuer Dateien

| Objektklasse | Trustee | ACE-Typ | Sollmaske | Vererbung | Nachweisstand |
| --- | --- | --- | --- | --- | --- |
| `.venv/Scripts/python.exe` | `<PACKAGE_SID>` | Access Allowed | `RX` | keine | konkrete Datei aus 213B |
| `C:/Python314/python.exe` | `<PACKAGE_SID>` | Access Allowed | `RX` | keine | konkrete Datei aus `pyvenv.cfg` |
| Python-/VC-Runtime-DLLs | `<PACKAGE_SID>` | Access Allowed | `RX` | keine | Bestand erfasst, transitive Auswahl offen |
| benoetigte Dateien unter `C:/Python314/DLLs` | `<PACKAGE_SID>` | Access Allowed | `RX` | keine | konkrete Loaderauswahl offen |
| benoetigte `.py`-/Daten-Dateien der Standardbibliothek | `<PACKAGE_SID>` | Access Allowed | `R` | keine | konkrete Importauswahl offen |
| native Standardbibliotheks-PYD/DLLs | `<PACKAGE_SID>` | Access Allowed | `RX` | keine | konkrete Importauswahl offen |
| 20 lokale Python-Dateien aus 213A | `<PACKAGE_SID>` | Access Allowed | `R` | keine | statisch gebunden |
| Paketdatei `mcm_field_organism/__init__.py` | `<PACKAGE_SID>` | Access Allowed | `R` | keine | normale Importbaseline aus 213A |
| native NumPy-PYD-/DLL-Auswahl | `<PACKAGE_SID>` | Access Allowed | `RX` | keine | Bestand erfasst, transitive Auswahl offen |
| benoetigte NumPy-Python-/Daten-Dateien | `<PACKAGE_SID>` | Access Allowed | `R` | keine | konkrete Importauswahl offen |
| alle anderen Workspace-Dateien | `<PACKAGE_SID>` | keine neue ACE | `NONE` | keine | ausdruecklich ausserhalb der Sollfreigabe |
| Test-, Report-, Medien- und Forschungsdateien | `<PACKAGE_SID>` | keine neue ACE | `NONE` | keine | kein Runtimebedarf gebunden |

Die Matrix enthaelt keine Write-, Append-, Delete-, Delete-Child-, Write-Attributes-,
Write-EA-, Change-Permissions-, Take-Ownership- oder Full-Control-Freigabe.

## ACE- und DACL-Regeln

1. Primaer sind nur Access-Allowed-ACEs fuer die konkrete `<PACKAGE_SID>` vorgesehen.
2. Fehlende Rechte werden durch Abwesenheit einer Allow-ACE modelliert. Neue
   Access-Denied-ACEs sind nicht Teil der Sollmatrix, weil sie bestehende Benutzer-,
   System- oder Loaderrechte unerwartet uebersteuern koennen.
3. `ALL APPLICATION PACKAGES` wird nicht als Ersatz fuer die konkrete Package-SID
   verwendet, weil dies alle AppContainer statt nur diesen Korridor adressieren wuerde.
4. Capability-SIDs werden nicht als Dateitrustees verwendet, weil keine Capability
   fuer die privaten Korridordateien vorgesehen ist.
5. Vor einer spaeteren Anwendung muessten bestehende explizite und geerbte ACEs,
   kanonische Reihenfolge, Eigentum und Mandatory Label read-only gebunden werden.
6. Die effektive Berechtigung bleibt die Schnittmenge mit Benutzer-/Gruppenrechten.
   Die Sollmatrix allein kann daher keinen Zugriff garantieren.
7. Eine DACL-Aenderung waere persistent, sicherheitsrelevant und weiterhin verboten.

## Prozess- und Handlegrenze

Ein spaeterer AppContainer-Token muesste die symbolisch gebundene Package-SID in
`SECURITY_CAPABILITIES.AppContainerSid` und eine leere Capability-Liste tragen. Diese
Struktur ist hier weder erzeugt noch an einen Prozessstart uebergeben worden.

Standardinput, Standardoutput, Standardfehler, Job-, Prozess-, Thread- und sonstige
Handles werden durch Datei-ACEs nicht vollstaendig geregelt. Ein separater
Handle-Vererbungs- und Startvertrag fehlt. AppContainer stellt weiterhin keine harte
numerische Thread- oder allgemeine Handleobergrenze bereit.

## Messergebnisse und Gegenbaselines

Dieses Teilpaket erzeugte keine dynamischen Messwerte. Statisch wurden erstellt:

- 1 symbolischer Package-SID-Trustee;
- 0 freigegebene Capability-SIDs;
- 11 Verzeichnisobjektklassen;
- 12 Dateiobjektklassen;
- 3 positive Rechteklassen (`T`, `R`, `RX`) plus `NONE`;
- 0 Deny-ACEs;
- 0 Vererbungsflags in der primaeren Sollmatrix;
- 0 erzeugte SIDs, Profile oder ACL-Aenderungen;
- 0 Projektimporte, Tests oder Prozessstarts.

| Gegenbaseline | Statische Bewertung |
| --- | --- |
| konkrete Package-SID mit Einzeldatei-ACEs | engste hier formulierte Sollbaseline, aber hoher Bindungsaufwand |
| `ALL APPLICATION PACKAGES` | zu breit, da alle AppContainer adressiert werden |
| Capability-SID fuer private Dateien | semantisch unnoetig und breiter als projektspezifische Package-SID |
| rekursive `RX`-ACE auf Python-/Workspace-Wurzeln | einfacher, aber gibt nicht gebundene Dateien und zukuenftige Kinder frei |
| explizite Deny-ACEs | koennen Zugriffspruefung und Loader unerwartet blockieren; nicht Teil der Baseline |
| regulaerer AppContainer mit Systemstandardzugriff | besitzt weiterhin gemeinsamen Systemzugriff; kein Nullzugriffsbeweis |
| LPAC | strengere Isolation, aber konkrete Python-Kompatibilitaet noch weniger belegt |
| normaler Benutzerprozess | keine AppContainer-SID-Schnittmenge und fuer die Isolationsfrage unzureichend |

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
| `coordinator_handoff_release` | `false` |
| `minimal_test_release` | `false` |

`minimal_test_release_recommended: false`

## Grenzen, offene Fragen und nicht gepruefte Annahmen

- **Beobachtet:** 213A bindet den lokalen Projektgraphen; 213B kartiert die
  Zugriffsklassen. Eine Package-SID oder ACL wurde nicht erzeugt oder gelesen.
- **Technische Interpretation:** Einzelobjekt-Allow-ACEs fuer eine konkrete
  Package-SID begrenzen die Projektfreigabe staerker als globale oder rekursive ACEs.
- **Hypothese:** Die Sollmatrix koennte nach vollstaendigem Loader- und
  Standardbibliotheksabschluss eine minimale Dateizugriffsgrundlage bilden.
- **Offene Frage:** Welche exakten System-DLL-, Standardbibliotheks-, NumPy-Daten- und
  Verzeichnisauflistingsrechte benoetigt der Interpreterstart wirklich?
- **Nicht gepruefte Annahme:** `T`, `R` und `RX` reichen fuer jede beteiligte
  Dateisystemoperation aus. Reparse Points, Junctions und Loader-Sonderpfade sind
  nicht gebunden.
- Moniker, SID-String, Benutzerrechte, bestehende ACLs, Mandatory Labels und
  kanonische ACE-Reihenfolge sind offen.
- Der leere Capability-Satz ist ein Sollwert, kein Kompatibilitaetsnachweis.
- Null-Artefakt-Verhalten, AppContainer-Lauffaehigkeit und Rueckstandsfreiheit sind
  nicht nachgewiesen.
- Harte Thread- und allgemeine Handlegrenzen bleiben ungeloest.
- Es gibt keinen Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation,
  Topologie, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## Konkrete Schlussfolgerung

Die engste statische Sollmatrix verwendet genau eine noch ungebundene Package-SID,
keine Capability-SIDs, keine pauschale `ALL APPLICATION PACKAGES`-Freigabe, keine
Deny-ACEs und keine Vererbung. Elternverzeichnisse erhalten symbolisch nur
Traverserechte; Python- und Projektdaten nur Leserechte; Executables und native
Bibliotheken Lese-/Ausfuehrungsrechte.

Diese Matrix ist noch nicht anwendbar. Moniker/SID, vorhandene ACLs und Labels sowie
der transitive Loader-, Standardbibliotheks-, NumPy- und Handleabschluss fehlen. Sie
beweist weder Lauffaehigkeit noch Artefaktfreiheit. Huerde G, Profilanlage,
ACL-/Systemaenderungen, Projektimporte, Tests und reale Ausfuehrung bleiben gesperrt.

## Naechster begrenzter Schritt

Als naechster Schritt ist ausschliesslich eine unabhaengige statische Gegenpruefung
dieser Sollmatrix vorgesehen. Zu pruefen sind insbesondere das duale
Benutzer-/AppContainer-Zugriffsmodell, der symbolische SID-Status, die leere
Capability-Liste, die Nichtverwendung von `ALL APPLICATION PACKAGES`, die getrennten
`T`-/`R`-/`RX`-Klassen, fehlende Vererbung und Deny-ACEs sowie alle Sperrfelder.

Erst nach positiver Pruefung waere als weiteres getrenntes statisches Teilpaket eine
read-only Istaufnahme der bereits vorhandenen ACL-/Mandatory-Label-Struktur auf den
gebundenen Pfadklassen fachlich diskutierbar. Sie duerfte weiterhin keine SID-
Ableitung, Profilanlage, ACL-Aenderung, Implementierung oder Ausfuehrung enthalten.

## Zielabweichung

Keine erkennbare Zielabweichung. Die Sollmatrix dokumentiert ausschliesslich einen
gesperrten Windows-Isolationspfad und behauptet keine MCM-, Memory-, Organismus- oder
KI-Funktion.
