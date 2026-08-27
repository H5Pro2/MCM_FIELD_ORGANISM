# S2-EJ: Einmalige Ausfuehrung der 51 synthetischen Vertragstests

## Ergebnis

**51 von 51 Tests bestanden.** `PASS_51_OF_51`.

Ausfuehrungskennung: `s2ej.001`. Genau ein Testprozess, kein Retry und keine
Wiederholung. Exit-Code des Testprozesses und des Protokollierers jeweils
`0`; terminales `OK`. Die von unittest gemeldete Testdauer ist `104.764 s`.

Gepruefter Quellcommit:
`e42ec19dea213c8b3b73b8f70c1e33e504414793`.
Grundlage ist die bestandene statische S2-EG-Wiederholung nach S2-EI mit
Digest `b9dfcafb00b3b28aa3821a52e576ef20d568cd208f3ee0ff72017cd8c719179e`.
Die anschliessende ausdrueckliche Benutzerfreigabe erlaubt genau diesen
einmaligen Lauf und dessen atomare Ergebnisaufzeichnung.

## Ausfuehrung

```text
python -B -u tools/run_s2ej_contract_tests_once.py
```

Der Protokollierer startet genau einen Kindprozess:

```text
C:\Python314\python.exe -B -u -m unittest tests.test_tspm1_s2dr_private_comparison_contract -v -f
```

`-f` bindet den sofortigen Stopp bei einem Test- oder Untertestfehler.
Kein solcher Fehler ist aufgetreten. Die Ausfuehrung begann am
27.08.2026 um 07:33:06 UTC; der Ergebnisbeleg wurde nach dem Testende um
07:34:52 UTC erstellt. Es wurden keine weiteren Testmodule gesammelt.

Vor dem Start wurden Auditdigest, Quellcommit, Quell-/Blobbindungen,
Schutzdateien, T01-T51 und das weiterhin geschlossene Matrixgate statisch
geprueft. Die exklusive Reservierung wird bei Fehlern nicht entfernt.
Vorhandene Belege derselben Kennung verhindern einen zweiten Start.

## Ergebnisbelege

- `reports/s2ej_tspm1_51_contract_tests_attempt_v1.json`: verbrauchte
  Einmalfreigabe, Quellstand, 51 Testnamen, Befehl und Protokolliererhash.
- `reports/s2ej_tspm1_51_contract_tests_output_v1.txt`: direkt vom
  Testprozess geschriebene vollstaendige Standard-/Fehlerausgabe.
- `reports/s2ej_tspm1_51_contract_tests_v1.json`: vollstaendig eingebettetes
  Rohprotokoll, Einzeltestlisten, Exit-Code sowie Vorher-/Nachher-Quellhashes.
- `reports/s2ej_tspm1_51_contract_tests_publication_v1.json`: gesonderte
  Bestaetigung der veroeffentlichten Ergebnisbytes und ihres Artefaktdigests.

Die Ergebnisdatei wurde exklusiv als Stagingdatei geschrieben, per `fsync`
gesichert, vollstaendig zurueckgelesen und unter Windows ohne Ueberschreiben
an den finalen Ort umbenannt. Danach wurden die finalen Bytes erneut
geprueft und die separate Veroeffentlichungsbestaetigung atomar gespeichert.
Dies ist die Aufzeichnung eines Testlaufs, kein Beleg fuer die produktive
Matrix-Veroeffentlichung oder eine unabhaengig gepruefte Stromausfallsicherheit.

Ergebnisdigest:
`77b9cefa1e60714143f7f7ca029d5fc4f446a48e5a9d501cf56f087fed5b2b70`.
Veroeffentlichungsdigest:
`c070f07647d4417dd07722249f4d90170851623bb835b9e01cf0afe008e09696`.

Eine nachgelagerte rein lesende Pruefung bestaetigt alle drei JSON-Digests,
die Protokollbytes, exakt T01-T51 jeweils einmal mit `ok`, das terminale
`OK`, Exit-Code 0 und die identischen Vorher-/Nachher-Hashes aller 21
gebundenen Dateien. Es gab weder eine Aufzeichnungskorrektur noch einen
zweiten Testlauf. Das eingebettete UTF-8-Protokoll im JSON ist der
Bytebeleg; die separate Textansicht kann bei einem Git-Checkout andere
Zeilenenden erhalten.

## Gepruefter Umfang und Grenze

Auch die neun angepassten Definitionen T01, T34-T39, T46 und T51 sind
bestanden. Damit sind die gebundenen Generator-Unterfaelle G1-G5,
Veroeffentlichungs-Unterfaelle P1-P9 und die angepasste Comparatorgrenze
innerhalb der synthetischen Vertragstests geprueft. Die Test-Doubles
belegen keine reale Produktions- oder Dateisystemintegration.

Die 56-Zellen-Matrix wurde nicht ausgefuehrt. Die bestehenden gebundenen
Mikro-/Einzelzellfixtures innerhalb der 51 Tests sind kein Matrixlauf.
Es gab keine Zustandsaufrufe ausserhalb dieses Testumfangs. TSPM-1, PPB-1,
Vergleichsmodul, Testdatei, oeffentliche API, Snapshot und Feldpfad wurden
nicht veraendert. Neu ist nur der gesonderte Einmal-Protokollierer samt
Ergebnis- und Abschlussdokumentation.

Der Befund betrifft ausschliesslich die Vergleichsinfrastruktur. Er sagt
nichts ueber einen funktionalen Vorteil von TSPM-1, die strukturelle Qualitaet
der Wahrnehmungsrepraesentationen oder einen eigenen MCM-Memory-Mechanismus aus.

WEITER: Am besten geht es jetzt mit S2-EK als rein statischem Abschlussaudit
von Einmaligkeit, Quellbindung, Testabdeckung und Ergebnisveroeffentlichung
weiter. Keine erneute Testausfuehrung; die Matrix bleibt gesperrt.
