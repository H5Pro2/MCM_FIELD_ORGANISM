# Teilpaket 213E: Statischer Loader-, Standardbibliotheks-, NumPy- und System-DLL-Pfadbaum

## Einordnung, Forschungsfrage und Auftrag

Dies ist eine statische Read-only-Istaufnahme und kein Forschungslauf. Deshalb wird
keine Laufnummer vergeben. Der freigegebene Auftrag war, die Istaufnahme aus 213D
auf den installierten Loader-, Standardbibliotheks-, NumPy- und System-DLL-Pfadbaum
zu erweitern.

Untersucht wurde, welche lokalen Pfadklassen fuer den in 213A beschriebenen
Python-Korridor vorhanden sind, welche nativen PE-Dateien darin liegen und welche
Importnamen deren PE-Importtabellen statisch nennen. Python oder Projektcode wurde
nicht importiert oder gestartet.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabe-Eingang mit der korrigierten Freigabe;
- `docs/forschung/213A_STATISCHE_LOKALE_PYTHON_KORRIDOR_DATEI_UND_IMPORTKARTE.md`;
- `docs/forschung/213D_READ_ONLY_ACL_MANDATORY_LABEL_ISTAUFNAHME.md`;
- `.venv/pyvenv.cfg`;
- installierte Dateibaeume unter `C:\Python314`, `.venv/Lib/site-packages/numpy`,
  `.venv/Lib/site-packages/numpy.libs` und `%WINDIR%/System32`;
- read-only PowerShell-Ausgaben von `Get-ChildItem`, `Get-Item`, `Get-FileHash`,
  `Get-Acl` sowie ein nur im Arbeitsspeicher ausgefuehrter PE-Headerleser.

Externe MCM- oder Webquellen wurden nicht verwendet.

## Verwendete Dateien und Schnittstellen

`.venv/pyvenv.cfg` bindet die Umgebung an Python `3.14.4`, Basisinterpreter
`C:\Python314\python.exe` und `include-system-site-packages = false`.

Erfasst wurden:

- Loaderkerne `python.exe`, `.venv/Scripts/python.exe`, `python3.dll` und
  `python314.dll`;
- der vollstaendige installierte Baum `C:\Python314\Lib`;
- der vollstaendige installierte Baum `C:\Python314\DLLs`;
- die vollstaendigen installierten Baeume `numpy` und `numpy.libs`;
- statisch referenzierte System-DLL-Namen mit Aufloesung gegen `%WINDIR%/System32`;
- Access-DACL und Owner aller Dateien in den vier installierten Bibliotheksbaeumen.

Der PE-Leser las DOS-/PE-Header, Section-Tabelle und regulaeres Import Directory
direkt als Bytes. Er lud keine DLL und wertete keinen ausfuehrbaren Code aus.

## Durchgefuehrte Schritte

1. Interpreterbindung aus `pyvenv.cfg` gelesen.
2. Dateien, Verzeichnisse, Bytes und Dateiendungen der vier Bibliotheksbaeume
   vollstaendig gezaehlt.
3. Die zwoelf Standardbibliotheksnamen aus 213A gegen den installierten Baum
   abgeglichen; `numpy` bildet die dreizehnte externe Importwurzel.
4. Loaderkerne, Python-DLL/PYD-Dateien sowie NumPy-PYD-Dateien und die zwei
   `numpy.libs`-DLLs von Beginn an als 25 native Seeds bestimmt.
5. Regulaere PE-Importtabellen rekursiv gegen Python-, NumPy- und System32-Dateien
   aufgeloest; API-Set-Namen separat als virtuelle Loadervertraege behandelt.
6. Die zwei gebuendelten `numpy.libs`-DLLs innerhalb desselben PE-Abschlusses
   gelesen und zusaetzlich gehasht.
7. Access-DACL und Owner aller 4.831 Dateien der vier Bibliotheksbaeume gelesen.

## Beobachteter installierter Pfadbaum

| Wurzel | Dateien | Verzeichnisse | Bytes | wichtige Typen |
| --- | ---: | ---: | ---: | --- |
| `C:\Python314\Lib` | 3.454 | 479 | 64.868.625 | 2.250 `.py`, 571 `.pyc`, weitere Daten |
| `C:\Python314\DLLs` | 45 | 0 | 15.929.219 | 34 `.pyd`, 7 `.dll`, 4 sonstige |
| `.../site-packages/numpy` | 1.330 | 129 | 32.662.329 | 407 `.py`, 407 `.pyc`, 275 `.pyi`, 19 `.pyd` |
| `.../site-packages/numpy.libs` | 2 | 0 | 20.980.816 | 2 `.dll` |
| **Summe** | **4.831** | **608** | **134.440.989** | getrennte installierte Baeume |

Die Summenzeile ist die arithmetische Summe der vier installierten Baeume. Wegen der
unterschiedlichen Pfadklassen wird sie nicht als einzelnes Laufzeitabbild
interpretiert.

Die in 213A genannten Standardbibliothekswurzeln wurden lokal gefunden als einzelne
Module (`__future__`, `dataclasses`, `enum`, `hashlib`, `hmac`, `queue`, `typing`),
Pakete (`json`, `pathlib`, `re`) oder in den Interpreter eingebundene Module
(`math`, `time`; keine gleichnamige Datei unter `Lib`/`DLLs`). Die breite Suche fand
bei `queue` zusaetzlich eine fremde vendored Datei; sie ist kein Beleg fuer eine
Importkante des privaten Korridors.

## Nativer Loader- und DLL-Befund

Der korrigierte einheitliche rekursive PE-Abschluss umfasste 25 Seeds einschliesslich
der zwei `numpy.libs`-Dateien. Beobachtet wurden:

- 37 aufgeloeste PE-Dateien;
- 465 regulaere Importkanten;
- 157 eindeutige Importnamen;
- 142 API-Set-/Extension-Set-Vertragsnamen;
- 0 gegen den verwendeten Suchindex unaufgeloeste regulaere Namen.

Die 465 Importkanten zerfallen in 104 gegen konkrete PE-Dateien aufgeloeste Kanten
und 361 API-Set-/Extension-Set-Vertragskanten. Die 37 eindeutigen PE-Knoten
gruppierten sich in 19 NumPy-PYDs, 2 `numpy.libs`-DLLs, 5 Dateien am Python-Root,
10 System32-Dateien und 1 venv-Loaderdatei. Diese Zahlen beschreiben den verwendeten
statischen Resolver, nicht den echten Windows-Loaderlauf.

Die zwei im einheitlichen Abschluss enthaltenen `numpy.libs`-Dateien sind:

| Datei | Bytes | SHA-256 |
| --- | ---: | --- |
| `libscipy_openblas64_-b788215d9d47792bcba3a2e2a7114320.dll` | 20.405.760 | `b788215d9d47792bcba3a2e2a71143205a57282828a483f1fb071ca2c159f616` |
| `msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll` | 575.056 | `a4c2229bdc2a2a630acdc095b4d86008e5c3e3bc7773174354f3da4f5beb9cde` |

Ihre regulaeren Importtabellen enthalten zusammen 28 der oben bereits enthaltenen
Kanten. Genannt werden API-MS-Win-CRT-Vertraege und `kernel32.dll`; die MSVC-Datei
nennt zusaetzlich `vcruntime140.dll` und `vcruntime140_1.dll`. `kernel32.dll` wurde
auf genau einen System32-Knoten aufgeloest. Fuer beide `vcruntime`-Namen existiert
je eine gleichnamige Datei am Python-Root und in System32; entsprechend der
dokumentierten Indexprioritaet wurde jeweils genau der Python-Root-Knoten verwendet.
Die System32-Dubletten wurden nicht als weitere Knoten gezaehlt. Damit sind die
beiden gebuendelten DLLs, ihre Kanten und ihre Folgeknoten einheitlich in allen
Abschluss- und Unique-Zaehlern enthalten.

## ACL-Erweiterung gegen 213D

Alle 4.831 Bibliotheksdateien waren fuer die Access-DACL-Abfrage lesbar. Auf keiner
wurde eine Access-ACE mit Praefix `S-1-15-` beobachtet.

| Baum | Dateien | DACL-Lesefehler | Dateien mit `S-1-15-`-ACE | Ownergruppen |
| --- | ---: | ---: | ---: | --- |
| Standardbibliothek | 3.454 | 0 | 0 | SYSTEM 2.409; Administratoren 1.045 |
| Python `DLLs` | 45 | 0 | 0 | SYSTEM 45 |
| NumPy | 1.330 | 0 | 0 | `CodexSandboxOnline` 1.330 |
| `numpy.libs` | 2 | 0 | 0 | `CodexSandboxOnline` 2 |

Es wurden keine SACLs oder Mandatory Labels abgefragt. Die Mandatory-Label-Grenze
aus 213D bleibt unveraendert.

## Messergebnisse und Gegenbaselines

- vollstaendig enumerierte Bibliotheksdateien: `4.831`;
- vollstaendig enumerierte Bibliotheksverzeichnisse: `608`;
- native PE-Seeds im einheitlichen Abschluss: `25`;
- aufgeloeste PE-Dateien im einheitlichen Abschluss: `37`;
- regulaere Importkanten im einheitlichen Abschluss: `465` (`104` aufgeloest,
  `361` API-Set-/Extension-Set-Vertragskanten);
- eindeutige Importnamen: `157`;
- API-Set-Vertraege: `142`;
- unaufgeloeste regulaere Importnamen im verwendeten Index: `0`;
- im Abschluss enthaltene `numpy.libs`-DLLs: `2` mit `28` bereits eingerechneten
  regulaeren Importkanten;
- Python-Root/System32-Namenskollisionen: `2`; beide `vcruntime`-Namen wurden
  jeweils auf genau einen Python-Root-Knoten dedupliziert;
- Access-DACL-Lesefehler: `0/4.831`;
- Dateien mit beobachteter `S-1-15-`-Access-ACE: `0/4.831`;
- Projektimporte, Tests, Zielprozesse, ACL-/Systemaenderungen und SACL-Abfragen: `0`.

Gegenbaselines:

| Gegenbaseline | Befund |
| --- | --- |
| nur 20 private Projektmodule aus 213A | blendet 4.831 installierte Bibliotheksdateien aus |
| nur Python-Root und `DLLs` | blendet NumPy und 20,98 MB gebuendelte Laufzeit-DLLs aus |
| API-Set-Namen als fehlende Dateien zaehlen | methodisch falsch; es sind virtuelle Loadervertraege |
| statischer PE-Abschluss als realer Loaderlauf | unzulaessig; keine Suchreihenfolge oder Laufzeitentscheidung beobachtet |

## Grenzen und nicht gepruefte Annahmen

- Der vollstaendige **installierte Pfadbaum** ist enumeriert; daraus folgt nicht,
  dass ein konkreter Prozess jede Datei liest.
- Der PE-Resolver deckt das regulaere Import Directory ab, nicht Delay-Load,
  `LoadLibrary`, `.pth`, Registry, Side-by-Side, KnownDLLs oder Paketinitialisierung.
- Der System32-Index loest gleiche Dateinamen nach dem ersten Treffer auf und
  simuliert keine reale Windows-DLL-Suchreihenfolge.
- API-Set-Vertraege wurden nicht auf ihre Host-DLL-Schemata abgebildet.
- `math` und `time` wurden statisch als nicht dateifoermige Importwurzeln
  klassifiziert; ein Interpreterlauf zur Bestaetigung war gesperrt.
- Es wurde keine effektive AppContainer-Token-Schnittmenge geprueft.
- Keine Aussage betrifft Lauffaehigkeit, Artefaktfreiheit, Feldwirkung, Memory,
  Organisation, Topologie, Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## Konkrete Schlussfolgerung

Die 213D-Auswahl war fuer den real vorhandenen Python-Korridor deutlich zu schmal.
Der installierte Bibliotheksraum umfasst mindestens 4.831 Dateien in vier relevanten
Baeumen, darunter 55 native Python-/NumPy-PYD/DLL-Dateien und zwei grosse gebuendelte
NumPy-Laufzeit-DLLs. Der statische PE-Abschluss fuehrt zudem in System32 und ueber
zahlreiche API-Set-Vertraege.

Auf allen 4.831 Bibliotheksdateien fehlen weiterhin beobachtbare `S-1-15-`-Access-
ACEs. Das ist ein breiterer Istbefund, aber kein AppContainer-Lauffaehigkeitsnachweis.
Huerde G und alle in der Freigabe genannten Eingriffe bleiben gesperrt.

## Naechster begrenzter Schritt

Teilpaket 213E ist in seiner korrigierten Fassung unabhaengig statisch zu pruefen.
Zu reproduzieren sind die vier Baumzaehler, die einheitlichen
`25/37/465/157/142/0`-Werte, die Kantenzerlegung `104/361/0`, die Gruppierung
`19/2/5/10/1`, die zwei `numpy.libs`-Hashes und deren 28 bereits eingerechnete
Importkanten sowie die Deduplikation der zwei `vcruntime`-Namenskollisionen auf den
Python-Root. Der unveraenderte ACL-Befund lautet `0/4.831` Lesefehler und `0/4.831`
beobachtete `S-1-15-`-ACEs.

Aus 213E folgt keine Ausfuehrungs- oder Aenderungsfreigabe.

## Zielabweichung

Keine erkennbare Zielabweichung. Das Teilpaket bleibt statische technische Vorarbeit
am gesperrten Windows-Isolationspfad und behauptet keine MCM-Funktion.
