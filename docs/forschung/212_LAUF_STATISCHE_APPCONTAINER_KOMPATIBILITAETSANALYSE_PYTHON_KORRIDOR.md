# Lauf 212: Statische AppContainer-Kompatibilitaetsanalyse des Python-Korridors

## Forschungsfrage und Auftrag

Rein statisch ist zu pruefen, ob der gebundene private Python-Korridor prinzipiell in
einem Windows AppContainer lauffaehig sein koennte, welche ACL- und Capability-Grenzen
dafuer erforderlich waeren, welche Artefakte eine Profilanlage erzeugen wuerde und ob
AppContainer die harten Thread- oder Handlegrenzen aus Huerde C erfuellen kann.

Dieser Lauf legt kein AppContainer-Profil an, aendert keine ACL, startet keinen Prozess,
importiert keine Projektmodule und ruft keine Lauf-, Prozesswaechter-, Bindungs-, Handoff-,
Fixierungs- oder Runtimefunktion auf.

## Lokale Bytebasis

| Quelle | SHA-256 |
| --- | --- |
| `docs/forschung/210_LAUF_MACHBARKEITSANALYSE_WINDOWS_JOB_OBJECTS_HARTE_GRENZEN.md` | `e861ab6412df014c9775d0badb9981d4fed17135c44a50bb573ab3ab9a7b6456` |
| `docs/forschung/211_LAUF_ENTSCHEIDUNGSVERTRAG_HUERDE_C_G_HARTE_THREAD_HANDLE_GRENZEN.md` | `1a1f4f16d778b06b51ce0e56807c024a4a2585665f13c96b878669dcf0923b90` |
| `mcm_field_organism/_runtime_fixation_single_use_path.py` | `44cc4dc42bea8b163531d5315e5bab5eda101b1a13f16323e2e34f0ba003787a` |
| `mcm_field_organism/_runtime_fixation_handoff.py` | `73e3fd5559dbc9eced92e2b7e31adea247c9fe8be73f79b59fc359ca2bbab068` |
| `mcm_field_organism/_runtime_fixation_binding.py` | `2fa92c99b9386c1d407128b22980d211a8f2ffbad574866524010fb5c0cc7444` |
| `mcm_field_organism/_runtime_fixation_structure.py` | `399c0c86800f353d37b77f829666f89df3d6385550caeead3893a580244c746e` |
| `mcm_field_organism/_previous_state_minimal_runner.py` | `f25aa5e4f5affe9755ae5f011b029a2ad46aa5a6560532706b7db7a40d12ae72` |
| `mcm_field_organism/__init__.py` | `c04e371daba2593d771e8ffa26e614746599f15541b303d5d5eaeaeaf332a9b0` |

Diese Bytebasis beschreibt nicht die vollstaendige Importabhaengigkeit des Korridors.
Insbesondere sind Interpreter, Python-DLLs, Standardbibliothek, native Bibliotheken und
weitere relativ importierte Projektmodule nicht vollstaendig gebunden. Daher kann sie
keine konkrete Lauffaehigkeit beweisen.

## Verwendete externe Primaerquellen

- [Microsoft: AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)
- [Microsoft: Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)
- [Microsoft: CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)
- [Microsoft: App capability declarations](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/app-capability-declarations)

## Verwendete Dateien und Schnittstellen

Die lokalen Dateien wurden ausschliesslich als Text und Bytefolgen gelesen. Statisch
bewertet wurden `CreateAppContainerProfile`, AppContainer-Package-SID,
Capability-SIDs, DACLs, Low Integrity Level und der AppContainer-Prozessstart ueber
Prozess- und Threadattribute. Keine dieser Schnittstellen wurde aufgerufen.

## Durchgefuehrte Schritte

1. Die lokalen Python-Importkanten des privaten Einmalpfads wurden statisch gelesen.
2. Die benoetigten Zugriffsarten fuer Interpreter, Laufzeit und gebundene Quellen
   wurden aus dem AppContainer-SID-/DACL-Modell abgeleitet.
3. Netzwerk-, Geraete- und Schreibisolation wurden gegen fehlende Capabilities und
   eingeschraenkte DACLs abgegrenzt.
4. Die Profilanlage wurde auf persistente Infrastrukturartefakte geprueft.
5. Der moegliche Beitrag zu Thread- und Handlegrenzen wurde gegen Lauf 210 und 211
   bewertet.

## Prinzipielle Python-Kompatibilitaet

Microsoft dokumentiert, dass ein AppContainer-Prozess eine Package-SID und
gegebenenfalls Capability-SIDs im Zugriffstoken traegt. Der wirksame Zugriff auf ein
geschuetztes Objekt ist durch die Rechte des Benutzers und die fuer AppContainer-SIDs
erteilten DACL-Rechte begrenzt. Damit ist ein nativer Python-Prozess prinzipiell in
einem AppContainer startbar, sofern der komplette benoetigte Dateizugriff und alle
Laufzeitvoraussetzungen explizit zugelassen sind.

Fuer den vorliegenden Korridor waeren vor dem Start mindestens statisch zu binden:

| Ressource | Minimal benoetigte Zugriffsart | Aktueller Nachweis |
| --- | --- | --- |
| konkrete Python-Executable | Lesen und Ausfuehren | nicht gebunden |
| Python-Laufzeit-DLLs und transitive System-DLLs | Lesen und Ausfuehren | nicht gebunden |
| verwendete Standardbibliothek, insbesondere `dataclasses`, `typing`, `hashlib` und `json` | Lesen; bei dynamischen Modulen gegebenenfalls Ausfuehren | nur Importnamen statisch sichtbar |
| gebundene Projektquellen und transitive Projektimporte | Lesen | Abhaengigkeitsabschluss nicht vollstaendig gebunden |
| Arbeitsverzeichnis | Verzeichnis durchqueren und Quellen lesen | kein konkreter AppContainer-SID/ACL-Vertrag |
| Temp-, Cache-, Profil- und Diagnoseschreiborte | kein Schreibrecht fuer Null-Artefakt-Vertrag | nicht nachgewiesen |

Die Aussage `prinzipiell startbar` ist deshalb eine Plattformmoeglichkeit, kein
Kompatibilitaetsnachweis fuer diesen Korridor. Ohne vollstaendigen transitiven
Abhaengigkeitsabschluss und konkrete ACL-Matrix bleibt die Lauffaehigkeit offen.

## Netzwerk-, Geraete- und Schreibgrenzen

| Grenze | Statische Bewertung |
| --- | --- |
| Internet und privates Netzwerk | Ohne Netzwerk-Capability vorbeugend blockierbar. Es darf keine entsprechende Capability-SID erteilt werden. |
| Kamera und Mikrofon | Standardmaessig blockiert; Webcam- und Mikrofon-Capabilities duerfen nicht erteilt werden. |
| weitere Geraete | Capability-geschuetzte Geraete bleiben ohne passende Device-Capability gesperrt; eine pauschale Aussage fuer jedes denkbare Geraeteinterface ist nicht nachgewiesen. |
| Workspace-Schreiben | Durch ausschliessliche Lese-/Ausfuehrungs-ACLs fuer die AppContainer-SID prinzipiell blockierbar. Konkrete ACL-Vererbung ist nicht gebunden. |
| andere Benutzerdateien und Registry | Durch AppContainer/Low-Integrity-Kontext stark eingeschraenkt; regulaere AppContainer besitzen jedoch Zugriff auf bestimmte gemeinsame Systemressourcen. Vollstaendige Nullzugriffsbehauptung waere unzulaessig. |

Ein AppContainer ohne Netzwerk-, Webcam-, Mikrofon- oder sonstige nicht benoetigte
Capabilities ist damit ein plausibler vorbeugender Isolationsbaustein. Er beweist aber
weder einen allgemeinen Null-Verbindungs- noch einen allgemeinen Null-Geraetevertrag
fuer alle Windows-Schnittstellen ohne zusaetzliche statische Abgrenzung.

## Profil- und Artefaktgrenze

`CreateAppContainerProfile` erzeugt ein benutzer- und anwendungsspezifisches Profil mit
Ordnern und Registryspeicher. Die Profilanlage ist daher selbst eine persistente
Infrastrukturhandlung und kein artefaktfreier Bestandteil des Einmallaufs.

Eine spaetere Profilanlage muesste separat vorregistriert, bytegebunden, freigegeben
und mit einer ebenfalls separaten Ruecknahme- und Restartefaktpruefung versehen werden.
Auch `DeleteAppContainerProfile` waere eine eigene Systemhandlung; seine Existenz
beweist keine rueckstandsfreie Ruecknahme. Im aktuellen Lauf wird weder Anlage noch
Loeschung freigegeben.

## Thread- und Handlegrenzen

AppContainer schraenkt Zugriffsrechte auf Ressourcen und fremde Prozesse ein. Die
Microsoft-Quellen dokumentieren jedoch keine numerische Obergrenze fuer die Anzahl der
Threads oder aller offenen Handles des enthaltenen Prozesses. Ein Prozess kann
innerhalb seines erlaubten Sicherheitskontexts weiterhin eigene Threads und erlaubte
Handles erzeugen.

Damit gilt:

- Beitrag zur harten Threadgrenze: `false`
- Beitrag zur harten allgemeinen Handlegrenze: `false`
- Aufhebung der Sperrentscheidung aus Lauf 211: `false`

AppContainer loest die blockierende Huerde-C/G-Bedingung nicht.

## Messergebnisse und Gegenbaselines

Dieser Lauf erzeugt keine dynamischen Messwerte. Statisch ergeben sich:

- Plattformmechanismus fuer AppContainer-Start eines nativen Prozesses: vorhanden;
- konkreter Kompatibilitaetsnachweis fuer den gebundenen Python-Korridor: nicht
  vorhanden;
- vorbeugende Netzwerkisolation ohne Netzwerk-Capability: prinzipiell vorhanden;
- vorbeugende Kamera-/Mikrofonisolation ohne entsprechende Capabilities: prinzipiell
  vorhanden;
- vorbeugende Workspace-Schreibsperre mit geeigneten ACLs: prinzipiell vorhanden,
  konkret nicht gebunden;
- persistente Profilartefakte bei Profilanlage: vorhanden;
- harte Thread- und allgemeine Handleobergrenzen: nicht vorhanden.

Gegenbaselines:

| Gegenbaseline | Ergebnis |
| --- | --- |
| normaler Benutzerprozess | besitzt keine AppContainer-SID-Grenze; fuer vorbeugende Isolation unzureichend |
| eingeschraenkter Token ohne AppContainer | kann Rechte reduzieren, liefert aber nicht automatisch das Capability- und Package-SID-Modell |
| AppContainer mit breiten Capabilities | verbessert Kompatibilitaet, verletzt aber den vorgesehenen Null-Netzwerk-/Null-Geraetekorridor |
| AppContainer ohne gezielte Quellen-ACLs | Prozessstart oder Importe koennen scheitern; kein Kompatibilitaetsnachweis |
| AppContainer plus Job Object | kombiniert Sicherheits- und Ressourcengrenzen, loest aber weiterhin keine harte Thread- oder allgemeine Handlezahl |

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

## Grenzen und nicht gepruefte Annahmen

- Weder der konkrete Python-Interpreter noch seine Laufzeitabhaengigkeiten wurden
  bytegebunden oder unter AppContainer ausgefuehrt.
- Es wurde keine transitive Import-, DLL- oder ACL-Vollstaendigkeitsanalyse erstellt.
- Keine Aussage belegt, dass Dritt- oder native Bibliotheken artefaktfrei arbeiten.
- Keine Profilanlage, ACL-Aenderung, Capability-Erteilung oder Ruecknahme wurde
  vorgenommen.
- Keine allgemeine Sperre jedes Windows-Geraete- oder IPC-Pfads ist nachgewiesen.
- Es gibt keinen Befund zu Feldwirkung, Kontaktgeschichte, Memory, Organisation,
  Bedeutung, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## Konkrete Schlussfolgerung

AppContainer ist prinzipiell als vorbeugender Isolationsbaustein fuer Netzwerk,
Capability-geschuetzte Geraete und Workspace-Schreibzugriffe geeignet. Die konkrete
Lauffaehigkeit des privaten Python-Korridors ist statisch nicht nachgewiesen, weil sein
vollstaendiger Interpreter-, DLL-, Standardbibliotheks-, Import- und ACL-Abschluss
fehlt. Die Profilanlage erzeugt persistente Infrastrukturartefakte und muesste separat
behandelt werden.

AppContainer liefert keine harte numerische Thread- oder allgemeine Handlegrenze.
Huerde G und jede reale Ausfuehrung bleiben deshalb gesperrt.

## Naechster begrenzter Forschungslauf

Als naechster Schritt ist ausschliesslich eine unabhaengige statische Gegenpruefung
dieses Dokuments zulaessig. Sie muss die acht lokalen Bytebindungen, die vier
Microsoft-Primaerquellen, die offene Python-Kompatibilitaet, die persistente
Profilwirkung, den fehlenden Thread-/Handlebeitrag, alle zwoelf falschen
Freigabefelder und die fortbestehende Huerde-G-Sperre reproduzieren.

Erst nach positiver Gegenpruefung kann entschieden werden, ob eine weitere rein
statische transitive Abhaengigkeits- und ACL-Karte sinnvoll ist. Eine Implementierung,
Profilanlage oder Ausfuehrung folgt daraus nicht.

## Zielabweichung

Keine erkennbare Zielabweichung. Die Analyse bewertet ausschliesslich einen gesperrten
technischen Isolationspfad und behauptet keine Organismus- oder KI-Funktion.
