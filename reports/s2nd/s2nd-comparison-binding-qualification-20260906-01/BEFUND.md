# S2-ND: Private Vergleichsanbindung, neutrale Einmalqualifikation

## Ergebnis und Ausfuehrungsgrenze

Qualifikations-ID: `s2nd-comparison-binding-qualification-20260906-01`.
Status: `NEUTRAL_QUALIFICATION_PASSED`.
Genau ein vorregistrierter Aufruf: **15/15 Tests, Exit-Code 0, OK**.
Unittest-Laufzeit 3.447 s. Kein Retry und keine Aenderung nach Testbeginn.

```text
C:/Python314/python.exe -m unittest tests.test_s2nd_private_comparison_binding -v
```

Ausgefuehrt aus dem workspace-Root. Vollstaendige Ausgabe und Exit-Code
stehen in `call-result.json`; Testliste, Imports, Grenzen und Vorhashes in
`qualification-plan.json`. `postcheck.json` dokumentiert ausschliesslich
die nachfolgende lesende Dateihashpruefung, ohne erneute Tests oder Importe
der Projektmodule. Alle vorgebundenen Hashes sind unveraendert.

Die Qualifikation verwendet ausschliesslich handgebundene neutrale Werte
und die versiegelten Planmetadaten. Die reale Materialisierungsdatei wurde
nur als Bytefolge zur Unveraendertheitspruefung gehasht, nicht geparst oder
verglichen. Keine PCM-Erzeugung, Rezeptoranalyse, Memory-, Kontext-, Feld-
oder Runtimefunktion. Kein Erhaltungs- oder Verlustbefund zum echten Korpus.

## Kleine private Anbindung

- `tools/_s2nd_private_comparison_binding.py`: feste neue S2-ND-Wurzeln;
  Bindung von Quellen, Reihenfolge, Zeiten, Rezepten, Profil, Materialisat,
  Werte- und Byte-Digests sowie vorhandenem Verifikationsbeleg. Daraus
  unveraenderliche `Source48`-, `Cue24`- und `Case`-Objekte.
- Historische S2-NC-Digests und Korpushelfer bleiben unveraendert. Die
  Anbindung ruft keinen alten 23-Quellen-/528-Beziehungs-Korpushelfer auf.
- Die existierenden `compare_case`, A-Aufloesung, direkte `decide`-Baseline
  und `verify_case` bleiben bytegleich. Keine weitere Regel oder Schwelle.
- `tools/_s2nd_private_retention_evaluation.py` ergaenzt ausschliesslich
  nachgelagerte N/D/R/L-Gruppen. Die bestehende gemeinsame Fallbewertung
  wird unveraendert wiederverwendet.
- Kein Dateilader, Hauptaufruf, Recorder, neues Gate oder allgemeiner Runner
  im Produktmodul. Die expliziten alternativen Wurzeln im neutralen Test
  kennzeichnen synthetische Materialisate; der Default bindet das reale,
  noch nicht ausgewertete S2-ND-Materialisat.

## Statischer Codepreflight und neutrale Pruefung

Vor dem einzigen Aufruf wurden die drei neuen Dateien per AST gelesen,
15 eindeutige Testmethoden materialisiert und die erlaubten Importe sowie
die drei Metadaten-Dateihashes geprueft. Keine Testentdeckung oder
Produktausfuehrung im statischen Preflight. Die Tests schreiben keine
Dateien und benoetigen keine konkurrierenden Ergebnisverzeichnisse.

| Pruefgruppe | Ergebnis |
| --- | --- |
| Neue Plan-/Quellenbindung, 18 synthetische Quellen / 864 Werte | bestanden |
| Quellen-ID, Typ, Dimension, Zeit, Profil, Rezept und Werte-/Bytedigests | fail-closed bestaetigt |
| Materialisierungs- und Verifikationswurzeln, unvollstaendige Analysen | fail-closed bestaetigt |
| Leere Panels, vollstaendige Scans, keine Deduplication | bestanden |
| Unveraenderliche Eingaben, getrennte Kopien und Pre-/Postgleichheit | bestanden |
| Fehlende Zeilen/Positionen, manipulierte Treffer und Postdigests | abgewiesen |
| Ausgabe bei 4.194.304 Bytes / plus einem Byte | akzeptiert / abgewiesen |
| Erhaltung nach Subtyp, Konkurrenz und echter Rezeptorbitvariation | bestanden |
| Gueltige Enthaltung trotz erwarteter Hypothese | technisch gueltig, funktionaler Verlust |
| Leerer Varianten-Ausgangsnenner trotz erfolgreicher Exaktkontrollen | ERHALTUNG_NICHT_GEPRUEFT |
| Gleichzeitiger Gewinn und Verlust | Verlust bleibt separat falsifiziert |
| Nur verdeckte Cuewerte geaendert | Anwendbarkeit unveraendert |
| Zielentfernung und manipulierte Evaluationsbindung | bestanden / abgewiesen |
| Falsch eindeutig verbleibender Konkurrent | Fehlzulassung, kein Gewinn |
| Fremder oder widerspruechlicher Verifikationsbeleg | abgewiesen |

Die Testkoerper pruefen zwoelf vollstaendige synthetische Vergleichsbatches
innerhalb dieses einen unittest-Aufrufs. Das ist keine Korpusauswertung.
Bei den Herkunftsfehlern werden gezielt auch innere Belege neu gehasht, damit
nicht nur ein oberflaechlicher Gesamtdigestfehler geprueft wird.

## Gebundene Kosten und N/D/R/L

Je spaeterem Vergleich beziehungsweise synthetischem Batch: 48 Faelle je
Regel, 96 Entscheidungen plus 96 direkte Baselineentscheidungen, insgesamt
144 Beziehungszeilen, 3.456 Banddifferenzen und 1.152 Positionsbesuche.
Auch leere Panels absolvieren alle zwoelf Positionen. Maximal 2.304 interne
Gleichheitsvergleiche pro Ausfuehrungsstufe, einschliesslich direkter
Baseline und Verifikation 6.912; die bisherige Obergrenze 9.216 bleibt
unveraendert. Ergebnisbytes maximal 4.194.304, einschliesslich einer
gegebenenfalls beigefuegten getrennten Auswertung.

N bezeichnet nur vorgebundene Faelle mit vorhandener Referenz; D die darunter
korrekt eindeutigen Mittelwerttreffer, R deren Erhalt und L deren Verlust.
`D = R + L` sowie die Aufteilung von L in Enthaltung und falsche Zulassung
werden explizit geprueft. D=0 ergibt immer `ERHALTUNG_NICHT_GEPRUEFT`.

Die Gruppen trennen Exakt, Pegel, Frequenz, Spektralumgewichtung und alle
Varianten, jeweils nach Konkurrenz und Bitgleichheit der vollstaendigen
48 Werte. Diese Wertebindung wird nur im Auswerter fuer die Variation
verwendet, nicht als zusaetzliche Anwendbarkeitsregel. Bei ausschliesslich
verdeckter Variation bleiben alle Treffermengen unveraendert.

Synthetisch bestaetigt: Varianten-N/D/R/L von 18/18/18/0, ein gezielt
verlorener Pegelhinweis in zwei referenzhaltigen Panels mit D/R/L=6/4/2,
sowie N/D=18/0 trotz sechs erfolgreicher Exaktkontrollen. Diese Zahlen
belegen nur den Auswerter, nicht Erhaltung im versiegelten Audiokorpus.
Eine erfolgreiche gemeinsame Vergleichsbewertung kann L nicht verrechnen.

## Aussagegrenze und Uebergabe

Die S2-ND-Anbindung ist neutral qualifiziert. Die vorhandenen 18 realen
Quellen mit 864 Rezeptorwerten wurden noch nicht durch diese Regeln
verglichen. Historische Versiegelung, Arithmetiknachtrag, Materialisierung
und ihre Belege bleiben unveraendert. Bootstrap bleibt ausgeschlossen.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses
Qualifikationsbefunds und danach gegebenenfalls der separaten Freigabe
des einmaligen S2-ND-Erhaltungs- und Verlustvergleichs weiter.
