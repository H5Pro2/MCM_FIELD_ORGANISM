# S2-NC: Neutrale Vergleichsqualifikation

## Ergebnis und Grenze

Qualifikations-ID: `s2nc-rule-comparison-qualification-20260906-01`.
Status: `PRIVATE_RULE_COMPARISON_QUALIFICATION_VALID`.
Genau ein vorregistrierter Unittest-Aufruf bestand mit `16/16`,
Exit-Code `0`, terminal `OK`. Es gab keinen Retry.

Qualifiziert wurde die private Komposition aus zwei Anwendbarkeitsregeln,
vollstaendigem Panelvergleich, unabhaengiger A-Entscheidungstabelle,
technischer Belegpruefung und nachgelagerter Bewertung.
Die eingefrorenen Rezeptorwerte wurden nicht verglichen. Es liegt kein
Selektivitaets-, Transfer- oder Memoryfunktionsbefund vor.

## Implementierungsumfang

- `tools/_s2nc_private_rule_comparison.py`: unveraenderliche Quellen-,
  Cue-, Panel-, Beziehungs- und Ergebnistypen; zwei Regeln; vollstaendige
  Scans; bestehende A-Aufloesungssemantik; Quellenbinder, technische
  Pruefung und begrenzte kanonische Ausgabe.
- `tools/_s2nc_private_decision_baseline.py`: getrennte direkte
  Entscheidungstabelle auf bereits vorhandenen Banktreffermengen,
  ohne Distanzberechnung oder gemeinsamen Entscheidungshelfer.
- `tools/_s2nc_private_rule_evaluation.py`: nachgelagerte Sollrelationen,
  Fehler-/Verlustzaehlung und Vergleichsbewertung.
- `tests/test_s2nc_private_rule_comparison.py`: 16 neutrale Pruefgruppen.

Es gibt keine neue Laufhuelle, Recorderarchitektur oder Integration in
S2-KZ/S2-MR. Rezeptor, Memory, Kontext, Feld und Runtime wurden weder
importiert noch aufgerufen. Die Produktmodule verwenden ausschliesslich
die Standardbibliothek und die hier genannten privaten Vergleichsmodule.

## Numerische Festlegung vor dem Test

Beide Regeln verwenden dieselben Binary64-Absolutdifferenzen auf `0..23`
und inklusive `<= 0.2`. Der groesste Wert wird mit `max` bestimmt.
Der arithmetische Mittelwert wird mit `statistics.mean` bestimmt und
gegen eine unabhaengige rationale Referenz aus den Floatwerten geprueft.

Diese Festlegung vermeidet ein Ueberschreiten der Grenze durch die
Zwischenrundung einer Binary64-Summe vor Division durch 24. Insbesondere
muss eine konstante Folge von 24 Differenzen `0.2` auch den Mittelwert
`0.2` ergeben. Es gibt keinen Toleranzzuschlag, keine Dezimalrundung und
keine Aenderung der Zahl `0.2`.

Die numerische Festlegung wurde vor dem einzigen Qualifikationsaufruf
in `qualification-plan.json` gebunden. Es wird keine bitweise Identitaet
mit jeder Zwischenrechnung des historischen `sum(terms) / 24`-Pfads
behauptet. Die produktive S2-KZ-Implementierung blieb unveraendert.
Diese explizite Implementierungsbindung gehoert zur Rueckmeldung an den
Analysten vor einer etwaigen Korpusfreigabe.

## Quellen- und Entscheidungsgrenzen

Die spaetere Bindung akzeptiert den vorhandenen Materialisierungsdigest
und den versiegelten Ausfuehrungsplandigest. Quellenwerte, Elternbelege,
Zeitfenster, Profil und kanonische Wertdigests werden zusammen geprueft.
Fuer neutrale Wurzeltests wurde ausschliesslich ein selbst erzeugter
synthetischer Beleg mit einem eigenen erwarteten Wurzeldigest verwendet.

Die sechs festen Panels und ihre 48 Faelle werden aus dem unveraenderten
Ausfuehrungsplan uebernommen, einschliesslich aller leeren Positionen.
Der Test liest nur diese Planmetadaten und belegt sie mit neutralen
Werten. Kein Test liest die versiegelte Rezeptormaterialisierung.
Die historischen Dateien wurden lediglich fuer Vor-/Nachhashes gelesen.

Die Anwendbarkeit sieht nur 24 Werte. Die andere Haelfte der
Kandidatenwerte gelangt ausschliesslich in die bestehende interne
48-Werte-Gleichheitspruefung. Mehrere Treffer in einer Bank bleiben
mehrdeutig; gleiche Werte werden nicht vor dem Scan dedupliziert.
Je ein gleicher B4-/Fast-Kandidat behaelt beide Herkunftsbelege.
Unterschiedliche Kandidaten erzeugen internen A-Konflikt.

Die technische Pruefung bindet den erwarteten Ergebnisdigest aus dem
uebergeordneten Beleg, Quellen- und Zeilenbindungen, Read-only-Digests,
vollstaendige Scans, Reduktionskonsistenz und erlaubte Statusformen.
Die direkte Tabelle prueft die A-Entscheidung ohne Sollrolle. Die
Belegpruefung fuehrt keine zweite Abstandsberechnung durch; sie ist kein
weiterer unabhaengiger Messarm.

Eine technisch gueltige Enthaltung wurde bei erwarteter Hypothese
ausdruecklich akzeptiert. Ausschliesslich die nachgelagerte Bewertung
meldete dazu `FALSIFIED`.

## Neutrale Pruefungen

Die vollstaendigen 16 Test-IDs und alle Vorhashes stehen in
`qualification-plan.json`; der Aufruf und seine Ausgabe in `test-output.txt`.

```text
python -m unittest tests.test_s2nc_private_rule_comparison -v
Ran 16 tests in 0.902s
OK
```

Abgedeckt wurden:

- inklusive Grenzen, unmittelbar benachbarte Floatwerte, rationale
  Mittelwertkontrolle und Teilmengenbeziehung;
- korrekter Treffer, Verlust eines korrekten Treffers und falsche
  Eindeutigkeit nach Entfernung des richtigen Kandidaten;
- Bankmehrdeutigkeit trotz Wertgleichheit und vollstaendige Scans;
- interne Gleichheit, Herkunftsbelege, B4-/Fast-Spiegelung und Konflikt;
- getrennte Abwesenheit und Nichtanwendbarkeit;
- Unabhaengigkeit der Anwendbarkeit von verdeckten Werten;
- Quellen-, Zeit-, Profilwurzel-, Werte- und Ergebnismanipulationen;
- unveraenderliche verschachtelte Daten und Vor-/Nachdigestgleichheit;
- technisch gueltige, fachlich abweichende Enthaltung;
- feste Panelbelegung, Materialisierungswurzel und Kopie der Werte;
- gemeinsame Bewertung von Verbesserungen und verlorenen Treffern.

## Budget und Ausgabe

Die festen Panels wurden ausschliesslich mit neutralen Werten einmal je
Regel im Budgettest verglichen. Bestaetigt wurden:

- 48 Faelle und 576 Positionsbesuche je Regel;
- 528 belegte Beziehungen je Regel, zusammen 1.056 Beziehungszeilen;
- 12.672 absolute Banddifferenzen je Regel, zusammen 25.344;
- maximal 2.304 interne Gleichheitsvergleiche je Regel und nochmals
  derselbe Hoechstumfang fuer die getrennte direkte Tabellenbaseline.

Die komplette neutrale Ausgabe mit 96 Entscheidungen und ihren direkten
Baselineentscheidungen besass `497812` Byte. Die Kodierung erzwingt
`4.194.304` Byte als harte Gesamtgrenze. Ein exakt so grosser neutraler
Beleg wurde angenommen, ein um ein Byte groesserer abgewiesen.
Die gemessene Groesse ist ein neutraler Beispielwert, kein behauptetes
Worst-Case-Ergebnis des noch nicht ausgewerteten Korpus.

## Unveraenderlichkeit und Rueckmeldung

Alle privaten Produkt- und Testhashes sowie Vertrags-, Quellen-, Siegel-
und Materialisierungshashes stimmten vor und nach dem Test ueberein.
Die Nachbindung steht in `postcheck.json`. Historische Ergebnisse,
Memorykerne, Feld und produktiver Abruf wurden nicht veraendert.
Die ausgeschlossene Bootstrap-Datei blieb unberuehrt.

Der Qualifikationsbefund wird dem Analysten zur Pruefung zurueckgegeben.
Die einmalige Korpusauswertung bleibt separat freizugeben. Insbesondere
bedeutet weniger Kandidaten weiterhin keinen Fortschritt: Der neutrale
Fall mit einem falsch eindeutig verbleibenden Kandidaten wurde als
`NEGATIVE`, der gleichzeitige Gewinn und Verlust korrekter Treffer als
`TRADEOFF` bewertet.

WEITER: Am besten geht es jetzt mit der analystischen Pruefung dieser
Qualifikation einschliesslich der expliziten Mittelwertarithmetik weiter.
Erst danach ist der einmalige Zwei-Regel-Vergleich auf den eingefrorenen
Rezeptorwerten separat zu entscheiden.
