# S2-NR: fokussierte Testbindung qualifiziert

## Ergebnis

`S2NR_FOCUSED_BINDING_QUALIFIED`, **3/3**, Exit-Code **0**.
Genau ein neuer Qualifikationsaufruf, kein Retry:

```powershell
& C:/Python314/python.exe -m reports.s2nr.qualify_failure_binding_once
```

Der einzige unittest-Unteraufruf selektierte ausschliesslich
`tests.test_s2nr_private_run.NRFailureBindingTests`. Das bisherige
`NRRunTests.setUpClass` und die elf bestandenen Tests wurden nicht ausgefuehrt.
Die historische 16/16-Qualifikation wurde ebenfalls nicht wiederholt.

ID: `s2nr-main-binding-focused-qualification-20260908-01`.
Ergebnisdigest:
`aa50dab768a841ff282854532cd5089a76cfa231e7888ac7619f17807c896502`.
Inventar, Kommando, Umgebung, Quellhashes und Obergrenzen stehen in
`preregistration.json`; Ergebnis, Vor-/Nachhashes und Kontrollbeleg-Hashes
stehen in `result.json`. Das Protokoll bestaetigt `Ran 3 tests` und `OK`.

## Drei unabhaengig erreichte Kontrollen

| Test | Eingriff in frische neutrale Kopie | Exakte Fehlerklasse / Code | Erreichbarkeit |
| --- | --- | --- | --- |
| 12a | Richtiger Fehlerplan, Ordinal 2 bei null abgeschlossenen Ereignissen | `S2NRRunError` / `FAILURE_PHASE_PROGRESS_INVALID` | Fehlerfortschrittsvalidator genau einmal erreicht |
| 12b | Verifikationsbeleg nennt einen anderen Recorddigest | `S2NRRunError` / `EVALUATION_REQUIRES_VERIFICATION` | Eigener Auswerteraufruf erreicht die Verifikationsgrenze |
| 12c | Fehlerbeleg gegen urspruenglichen, unpassenden Plan | `S2NRRunError` / `TOTAL_BINDING_INVALID` | Tiefere Fehlerpruefung nicht erreicht, wie erwartet |

Jeder Test laedt frische Kopien; keine Abhaengigkeit von einem vorherigen
Testresultat. Konkrete Klasse, konkreter Code und Unveraendertheit der
Eingabekopie sind geprueft. Keine allgemeine Exceptionakzeptanz.

Der zum Fehlerbeleg passende Plandigest ist weiterhin
`f89d09e54af774bd4e3bba82c88614b38eb6ca41abc0dda6f9b46d1c4a33ba00`.
Er wurde allein aus der belegten Metadatenaenderung des alten Test 05
hergestellt, ohne dessen Quellen- oder Runtimeausfuehrung zu wiederholen.
Der urspruengliche Plan bleibt getrennt mit
`fb4a93ad0e9dc1c458316ae9a9175b25903ff76d6235a19c58445837c9796bb8`.

## Quellen- und Ausfuehrungsgrenze

Produktmodule, Ressourcenlimits und Versiegelung sind bytegleich zum
vorherigen Stand. Geaendert wurde nur die Testdatei, ergaenzt wurden der
fokussierte Aufrufer und seine Dokumentation. Die elf alten Testkoerper
einschliesslich ihres Klassen-Setups wurden gegen Commit `161c058a` statisch
auf Unveraendertheit geprueft, nicht erneut ausgefuehrt.

In den ausdruecklich synthetischen Fehlerbelegkopien wurde ausschliesslich
die administrative Testdatei-Hashbindung aktualisiert. Die Differenzmenge
zur historischen Codebindung musste exakt diese eine Testdatei sein.
Diese Kopien sind keine nachtraeglich korrigierten historischen Laufbelege.
Die gespeicherten historischen Dateien und alle vor/nach gebundenen
Quellen- und Artefakthashes blieben unveraendert.

Beobachteter Umfang: zwei Gesamtverifikator-Eintritte in Fehlerpfade und ein
Auswertereintritt bis zur Ablehnung. **Null** PCM-/RGB-Erzeugungen,
Rezeptoranalysen, Audiohops, NJ-Projektionen, Formationen, Runtimeereignisse,
Feldkontakte, Abrufbelege oder Distanzberechnungen. Aufrufsperren sichern
Generator, Materialisierer, Runtimekonstruktion und vollstaendige
Kompositionsverifikation ab. Keine NR-Payloads und keine Hauptgeschichte.

## Gemeinsame Qualifikationsdeckung

Die Deckung beruht auf getrennten, unveraendert nachvollziehbaren Befunden:

1. [Historische 16/16-Typ-/Maskenanbindung](../s2nr-runtime-binding-qualification-20260908-01/BEFUND.md):
   geschlossene Hypothesentypen, Masken-/Komplementbindung, Instanzisolation,
   Fehlerisolation, Read-only-Abruf und Lifecycle.
2. [Elf bestandene Laufanbindungsgruppen im historischen 11/12-Lauf](../s2nr-main-binding-qualification-20260908-01/BEFUND.md):
   neutrale Materialisierung mit fortlaufender Zeit, gemeinsamer Elternbeleg,
   fortgesetzte Geschichte, gueltige Enthaltung, Payloadfehler, Herkunft und
   Variation, getrennte Nenner, Hauptgates und vollstaendige Beleggrenzen.
3. Die drei neuen Kontrollen schliessen die beiden fehlenden Unterkontrollen
   von Test 12 und erhalten die vorgelagerte Ablehnung der falschen Planwurzel.

Damit ist die benannte Testbindungsluecke geschlossen. Dies ist **kein neuer
12/12- oder 16/16-Komplettlauf**. Der alte Lauf bleibt dauerhaft
`NOT_QUALIFIED` mit 11/12; sein Fehlbefund wird nicht umgeschrieben.
Es liegt weiterhin kein realer NR-Funktionsbefund vor.

## Noch geschlossener Haupteinstieg

Alle Gates bleiben False. Der unveraenderte Produktcode verweist administrativ
weiterhin auf den alten `QUAL_ID`-Beleg des 11/12-Laufs; er wurde in diesem
reinen Testkorrekturauftrag nicht auf eine zusammengefuehrte Qualifikationsbindung
umgestellt. Die neue Testdeckung ist daher keine automatische Freischaltung.
Eine spaetere Hauptlaufentscheidung muss diese eng begrenzte Beleganbindung
ausdruecklich einbeziehen. Keine weitere Quellen-/Rezeptorpruefung folgt daraus.

WEITER: Am besten geht es jetzt mit der Analystenentscheidung ueber die
zusammengefuehrte Qualifikationsdeckung und ihre administrative Hauptlaufbindung
weiter. Kein Hauptlauf ohne separate Freigabe.
