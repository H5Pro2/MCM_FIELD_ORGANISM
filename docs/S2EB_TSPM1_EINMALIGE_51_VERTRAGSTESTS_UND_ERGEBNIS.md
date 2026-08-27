# S2-EB: Einmalige Ausfuehrung der 51 Vertragstests

## Auftrag und Ergebnis

Die ausdruecklich freigegebene Ausfuehrung `s2eb.001` ist abgeschlossen:
**51 von 51 Tests bestanden**, keine Fehler, Fehlschlaege oder
uebersprungenen Tests. Exit-Code `0`, terminales `OK`.
Die von unittest gemeldete Testdauer betraegt `1.351 s`.

Quellcommit: `f4b16f33483d5751901da6f628467b59e8e4a385`.
S2-DX-Freigabegrundlage: Artefaktdigest
`42d5f8219e7808b8df28093554fdf7f53c68fbabbe5bd3fc6e7d7ac910432ffc`.

Es gab genau einen Testprozess mit diesem Befehl:

```text
C:\Python314\python.exe -B -u -m unittest tests.test_tspm1_s2dr_private_comparison_contract -v
```

Vor dem Start wurden die gebundenen Quellenhashes und das Inventar
T01-T51 statisch geprueft. Ein exklusiv angelegter Versuchsbeleg verhindert
eine unbemerkte erneute Verwendung derselben Ausfuehrungskennung.
Es wurde keine Test-, Produktiv- oder Hilfsfunktion neu implementiert.
Die Prozesssteuerung und Protokollaufzeichnung erfolgten ausserhalb des
Projektcodes mit der Standardbibliothek.

## Protokoll und Auswertung

Die folgenden Artefakte bleiben getrennt erhalten:

- `reports/s2eb_tspm1_51_contract_tests_attempt_v1.json`: Einmalreservierung,
  Befehl, Quellcommit und Quellenhashes vor Ausfuehrung.
- `reports/s2eb_tspm1_51_contract_tests_output_v1.txt`: vollstaendiges
  menschenlesbares Rohprotokoll.
- `reports/s2eb_tspm1_51_contract_tests_v1.json`: urspruenglicher
  Prozessbeleg mit Exit-Code, vollstaendig eingebettetem Rohprotokoll und
  Quellenhashes vor/nach Ausfuehrung.
- `reports/s2eb_tspm1_51_contract_tests_transcript_verification_v1.json`:
  abschliessende Auswertung ausschliesslich des gespeicherten Protokolls.

Der erste automatische Einzeltestzaehler erkannte die CRLF-Zeilenenden
nicht. Deshalb enthaelt der urspruengliche Prozessbeleg trotz Exit-Code 0,
`Ran 51 tests` und `OK` eine unvollstaendige maschinelle Einzelzaehlung
und den Status `FAIL_CLOSED_TEST_FAILURE_OR_INCOMPLETE`.
Dieser Beleg wurde nicht ueberschrieben.

Die separate Auswertung zerlegt das vorhandene Protokoll mit `splitlines`
und bestaetigt genau T01-T51 in Reihenfolge, jeweils einmal mit `ok`.
Quellbelegdigest, Protokollhash, eingebettetes Rohprotokoll und
Einmalreservierung stimmen ueberein. Die Rohbytes enthalten 56
CRLF-Zeilenenden. Es gab **keine erneute Testausfuehrung**, keine
Codekorrektur und keine Aenderung der Testresultate.

Fuer eine plattformunabhaengige Bytepruefung ist die UTF-8-Kodierung des
Feldes `raw_output` im Prozess-JSON massgeblich. Die separate Textdatei
dient als lesbare Ansicht und kann durch Git-Zeilenendennormalisierung
eine andere Dateibyteform erhalten. Die bestehenden Git-Regeln fuer
JSON-Reports sichern deren LF-Dateiform; es wurden keine Attribute geaendert.

Beide Ergebnis-JSONs wurden zunaechst vollstaendig in temporaere Dateien
geschrieben und danach ohne Ueberschreiben an ihren endgueltigen Ort
umbenannt. Der abschliessende Auswertungsdigest lautet:
`e200fba9dc16650dd4a856cf02c7cbb368f4935e70989e84584107c0bfd2d7a6`.

## Technisch gepruefter Umfang

- T01-T34: gebundene Quellen, Registry, Initialzustaende, Mikrotransitionen,
  Budgets sowie Datentraeger-/Receipt-Digests.
- T35-T39 und T51: tatsaechlicher Comparator mit synthetischen
  Ergebnisbelegen, inklusive R0-Abweichung und Entscheidungsreihenfolge.
- T40-T50: die gebundenen Negativfaelle. T44 erreicht den erwarteten
  Autorisierungsfehler. T48 prueft die fremde Budgetquelle; T49 und T50
  pruefen die vorgesehenen relationalen Budgetueberschreitungen.
- T50: die korrigierten technischen Quellen-IDs erlauben die Vorbereitung
  aus H1/TSPM1 bis zur Mutation von `formation_write_counts`, Index 1,
  Grenze 293, Verbrauch 294.

Die vollstaendige R0-Projektion gehoert zum unveraendert gebundenen
Quellstand. Die vorhandenen Comparatortests pruefen synthetische
Projektionsgleichheit bzw. -abweichung. Sie sind kein erschoepfender
Mutationstest jedes einzelnen Projektionsfeldes und noch kein Vergleich
real fortgeschriebener TSPM1- und R0-Geschichten. Zusatztests wurden nicht
angelegt, weil nur die bestehenden 51 Definitionen freigegeben waren.

Die Testhelfer verwenden ihre gebundenen Einzelzellen-/Mikrofixtures.
Die synthetischen Comparatorbelege stellen keine Ausfuehrung der
registrierten 56-Zellen-Vergleichsmatrix dar. Ausserhalb des freigegebenen
Testumfangs wurden keine Zustandsfunktionen aufgerufen.

## Grenzen und naechster Schritt

`PASS_51_OF_51_CONFIRMED_FROM_COMPLETE_SAVED_TRANSCRIPT`.

TSPM-1, PPB-1, Vergleichsmodul, Tests, API, Snapshot und Feldpfad sind
unveraendert. Die geprueften Vorher-/Nachher-Quellenhashes stimmen ueberein;
Git zeigt keine Aenderung an bestehenden versionierten Dateien.

Dies ist ein technischer Vertragstestbefund. Er belegt weder einen
Memory-Befund noch einen Vorteil gegenueber einer Baseline oder die
strukturelle Qualitaet auditiver/visueller Wahrnehmungsrepraesentationen.
Diese konzeptionelle Frage bleibt ausdruecklich fuer die spaeter separat
freizugebende Vergleichsmatrix und die weitere Entwicklung erhalten.

Naechster Schritt: S2-EC als rein statischer Abschlussaudit von
Einmaligkeit, Quellenbindung, Protokollvollstaendigkeit, nachtraeglicher
Protokollauswertung und Testabdeckung. Keine Wiederholung. Die
56-Zellen-Matrix, Produktionsanbindung und Feldintegration bleiben gesperrt.
