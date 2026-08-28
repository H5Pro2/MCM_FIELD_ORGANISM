# S2-FE: Private Implementierung der Startinfrastruktur

## Status

**IMPLEMENTED_STATIC_CHECKS_ONLY_SEPARATE_CODE_AUDIT_PENDING**

Die vier in S2-FD vorgesehenen privaten Dateien sind implementiert.
S2-FC bleibt blockiert. Dieser Schritt ist keine Codeabnahme und kein
Plattformlauf. Es wurden keine Projektmodule importiert, keine Tests oder
Projektfunktionen ausgefuehrt und keine nativen Metadaten erneut erhoben.
Ledger, Zielverzeichnis, Recorder und Vergleichsmatrix wurden nicht gestartet
oder beschrieben. Der bestehende Feldkern bleibt unveraendert.

Der maschinenlesbare Quell- und Pruefbeleg steht in
[S2FE_PRIVATE_STARTINFRASTRUKTUR_IMPLEMENTIERUNGSBELEG_V1.json](S2FE_PRIVATE_STARTINFRASTRUKTUR_IMPLEMENTIERUNGSBELEG_V1.json).

## Implementierter Umfang

- `_s2fd_start_contract.py`: geschlossene Datenformen, unveraenderliche
  Paketbytes, Originalquellen, Digestbeziehungen und statische Budgetableitung.
- `_s2fd_start_owner.py`: getrennte Dispatch-/Seal-Pfadrollen,
  Einmalverbrauch, gehaltene Quellen und unabhaengiger Starter.
- `_s2fd_completion_observer.py`: begrenzte Pipe-Kommunikation,
  observer-eigene Prozesshandles, Prozessidentitaeten und Abschlussvalidierung.
- `tools/run_s2fd_isolated_platform_once.py`: getrennte private
  Starter-, Supervisor- und Worker-Einstiege, kein oeffentlicher Observerstart.

Die acht bestehenden Recorder-/Publikationsmodule wurden nicht geaendert.
TSPM-1, PPB-1, API, Snapshot und Feldpfad bleiben unangetastet. Zusaetzlich
sind genau vier LF-Regeln in `.gitattributes` fuer die neuen Python-Dateien
gebunden; bestehende Dateiregeln wurden nicht erweitert oder normalisiert.

## Budget- und Quellgrenze

Die Budgetfunktion liest uebergebene Originalbytes mit dem AST-Parser. Sie
importiert die analysierten Module nicht. Kostenzeilen muessen an konkrete
Quellorte und Rohbyte-Digests gebunden sein. Fehlende Quellabdeckung, falsche
Integerableitungen, unbekannte Groessen oder eine zyklische Groessenfolge
werden verworfen. Native Aufrufe, Recorder-Aufrufpaare, Bytes, Validierungs-
arbeit und Speichergrenzen haben getrennte Zaehleinheiten.

Die Wahrheit einer angegebenen Schleifen- oder Schemaobergrenze folgt nicht
allein aus ihrer korrekten Rechnung. Diese Annahmen muessen im separaten
statischen Audit anhand der festgeschriebenen Quellen geprueft werden.

Ein numerisch vollstaendiger Budgetbeleg wurde nicht erfunden. Es fehlen
weiterhin die vollstaendig abgenommene Runtime-/Importabschlussmenge,
Elternverzeichnisbelege und die konkreten inneren Freigabebytes. Die im
JSON genannten Quellbytes und AST-Aufrufknoten sind lediglich ein
statisches Inventar, keine ausgefuehrten Operationen und kein Laufbudget.

## Start- und Abschlussgrenze

Der aeussere Vertrauenskontext ist standardmaessig leer. JSON, Kommandozeile
oder Umgebungsvariable koennen ihn nicht als Ausfuehrungsfreigabe setzen.
Der spaetere Aufrufer muss unabhaengig zugelassen sein und den tatsaechlichen
terminalen Abschluss des Beobachters selbst feststellen.

Die Implementierung sieht feste, plandigestunabhaengige Dispatchnamen vor.
Bestehende oder unvollstaendige Eintraege erlauben keinen Wiederanlauf. Der
Starter erstellt keine Verzeichnisse. Der Worker darf erst nach der
Supervisorreservierung und der unabhaengigen Handle-Uebernahme eintreten.

Ein spaeteres Ergebnis muss zu den Originalbytes von Manifest, Marker,
Kontrolltrace, Report, Transkript und allen 13 Falltraces passen. Exit-Codes
werden ueber eigene Prozesshandles abgefragt. Reine Lesbarkeit oder ein
vom Kind gelieferter Erfolgswert reicht fuer den Abschluss nicht aus.

Die privaten konkreten IPC-Formen und inneren Freigabeschemata sind im JSON
aufgefuehrt. Sie erweitern weder die 133 Recorderpfadrollen noch die Matrix.
Die Prozesseinstiege und ihre Fehlerpfade sind noch nicht ausgefuehrt worden.

## Statische Pruefung

Vier Dateien wurden mit `ast.parse` und `symtable` als Text geprueft:
keine Syntaxfehler und keine unaufgeloesten globalen Namen. Alle 15
geerbten Quell-/Belegbindungen stimmen weiterhin bytegenau. Das ist kein
Funktions-, Plattform- oder Importtest. Die Windows-Pipe- und Prozess-
schnittstellen wurden nur mit primaerer Dokumentation abgeglichen; deren
konkrete Eignung auf der vorgesehenen Runtime bleibt ungeprueft.

Dokumentationsgrundlagen: [Python-Pipe-Modus](https://docs.python.org/3.14/library/os.html#os.set_blocking),
[Handle-Duplikation](https://learn.microsoft.com/en-us/windows/win32/api/handleapi/nf-handleapi-duplicatehandle),
[Prozesszeiten](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes),
[Pipe-Herkunft](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getnamedpipeserverprocessid)
und [anonyme Pipes](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-createpipe).

## Naechster Schritt

S2-FF ist separat als rein statischer Codeaudit gegen S2-FD vorzusehen.
Besonders zu pruefen sind Quellabschluss, Budgetannahmen, Bootstrap-Herkunft,
Pipe-/Prozesssignaturen, Abbruchzustaendigkeiten und Schliessreihenfolge.
Es wird keine bestandene Abnahme vorweggenommen.

Ledger-Einrichtung, weitere native Herkunftserhebung, Tests und eine
Plattformausfuehrung bleiben gesondert freizugebende Schritte. Auch eine
spaetere Codeabnahme ersetzt diese fehlenden Voraussetzungen nicht.
