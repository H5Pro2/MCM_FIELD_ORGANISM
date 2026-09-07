# S2-NP: einmaliger Abdeckungsvergleich des eingefrorenen Materialisats

## Technischer Abschluss

Lauf-ID `s2np-coverage-corpus-comparison-20260907-01`, Ausgangscommit
`f324a69`. **RECORDING_COMPLETE**, **TECHNICALLY_VALID**, Exit-Code **0**.
Genau ein Hauptaufruf, je eine Primaer- und Direktberechnung, danach genau
eine read-only Belegpruefung und erst anschliessend eine getrennte Auswertung.
Kein Retry, keine erneute Qualifikation und kein Distanz-Erfolgsgate.

```powershell
C:/Python314/python.exe -m reports.s2np.compare_coverage_once
```

Verwendet wurde ausschliesslich das unveraenderte, bereits verifizierte
Rezeptor-/NJ-Materialisat. Beide Planwurzeln, Quellen-, Profil-, Interpreter-
und Codebindungen wurden vorab geprueft. Die vorhandene Verifikation der
576 Halbierungen wurde authentisiert, nicht erneut numerisch ausgefuehrt.
Payloadgeneration, Rezeptor-, NJ-, Memory-, Feld-, Kontext- und Runtime-
aufrufe jeweils **0**. Systemgates blieben `False`.

| Umfang | Primaer | Unabhaengig direkt | Gesamt |
| --- | ---: | ---: | ---: |
| Panelbefunde | 360 | 360 | 720 |
| Regelgebundene Beziehungszeilen | 360 | 360 | 720 |
| Numerische Banddifferenzen | 3840 | 3840 | 7680 |

Je Implementierung 120 vollstaendige Sicht-/Panel-/Cue-Scans mit jeweils
drei Bedingungen. Terme werden nur zwischen den drei Bedingungen derselben
Sicht geteilt. Originalindizes und numerische Differenzen stehen vollstaendig
in `recording.json`. Keine Deduplizierung, Rangfolge oder nachtraegliche
Maskenwahl. Die 24er-Vergleicher erhielten nur ihre 24 indexgebundenen Werte;
die 48er-Diagnose blieb ein separater Eingang.

Die Verifikation las die aufgezeichneten Bytes neu ein und bestaetigte die
kanonische Bitgleichheit zur unabhaengigen Direktnachrechnung, Quellbindungen,
Vollstaendigkeit, Aggregatrechnungen aus den gespeicherten Termen und
Zustandsunveraenderlichkeit. **0 neue Quelldifferenzen** bei dieser Pruefung.
Technisch gueltige leere und mehrdeutige Treffermengen blieben auswertbar.

Die fuenf technischen JSON-Belege einschliesslich eingebettetem Materialisat,
beider Termbelege, Verifikation, Auswertung und Vorregistrierung umfassen
**1195570 Byte**, unter der unveraenderten Gesamtgrenze **2097152 Byte**.
Jede Datei wurde nach Groessenpruefung atomar unter neuem Namen publiziert.
Keine neue Recorderplattform; qualifizierte Vergleichsmodule unveraendert.

## Hauptbefund: Distributed 24 gegen Contiguous 24

Die verteilte Sicht zeigt **einen begrenzten Vorteil bei zwei Bedingungen**,
keinen allgemeinen Abdeckungssieg:

| Bedingung | Beziehung N/D/R/L | Richtig eindeutig N/D/R/L | Neue richtige Eindeutigkeiten | Neue falsche Anwendbarkeit | Vorab definierter Befund |
| --- | --- | --- | ---: | ---: | --- |
| A_HISTORICAL_SUM | 16/16/16/0 | 16/8/8/0 | 0 | 0 | NO_ADVANTAGE |
| A_ALL_BANDS | 16/16/16/0 | 16/16/16/0 | 0 | 0 | LIMITED_ADVANTAGE |
| SLOW_HISTORICAL_SUM | 16/16/16/0 | 16/16/16/0 | 0 | 0 | LIMITED_ADVANTAGE |

N zaehlt bekannte Hinweis-/Panel-Faelle mit vorhandenem Ziel. D bezeichnet
die zuvor anwendbaren Zielbeziehungen beziehungsweise zuvor richtig
eindeutigen Panelbefunde, R deren Erhaltung, L deren Verlust. Fuer beide
Leistungen gilt getrennt D=R+L. **Kein Beziehungs- oder Eindeutigkeitsverlust**,
keine neue falsche Anwendbarkeit und kein Gewinn einer neuen Zielbeziehung.
Der Nutzen entsteht hier ausschliesslich durch verhinderte falsche
Anwendbarkeit, nicht durch neue bekannte Treffer.

## Treffer, Fehlanwendbarkeit und Enthaltung

Je Sicht und Bedingung 40 Panelbefunde, davon 16 mit vorhandenem bekannten
Ziel. Die 24 Nichtziel-Beziehungen bilden den Nenner falscher Anwendbarkeit.
Falsch eindeutig und mehrdeutig sind unterschiedliche Panelbefunde.

| Bedingung | Sicht | Richtig eindeutig /40 | Falsche Beziehung /24 | Falsch eindeutig /40 | Mehrdeutig /40 | Leer /40 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A_HISTORICAL_SUM | Contiguous 24 | 8 | 24 | 12 | 10 | 10 |
| A_HISTORICAL_SUM | Distributed 24 | 8 | 24 | 12 | 10 | 10 |
| A_HISTORICAL_SUM | Full 48, Diagnose | 8 | 24 | 12 | 10 | 10 |
| A_ALL_BANDS | Contiguous 24 | 16 | 2 | 2 | 0 | 22 |
| A_ALL_BANDS | Distributed 24 | 16 | 0 | 0 | 0 | 24 |
| A_ALL_BANDS | Full 48, Diagnose | 16 | 0 | 0 | 0 | 24 |
| SLOW_HISTORICAL_SUM | Contiguous 24 | 16 | 2 | 2 | 0 | 22 |
| SLOW_HISTORICAL_SUM | Distributed 24 | 16 | 0 | 0 | 0 | 24 |
| SLOW_HISTORICAL_SUM | Full 48, Diagnose | 16 | 2 | 2 | 0 | 22 |

Die vier Befundspalten richtig eindeutig, falsch eindeutig, mehrdeutig und
leer summieren sich je Zeile zu 40. Die Beziehungsspalte hat einen eigenen
Nenner und darf nicht dazuaddiert werden. Leeres Panel p04 liefert in allen
Sichten/Bedingungen 10/10 leere Befunde; dies ist keine sensorische
Unbekanntheitserkennung.

## Exaktkontrollen und Varianten getrennt

Jeder Subtyp besitzt zwei Hinweise und je zwei Panels mit vorhandenem Ziel:
N=4. Die drei Variationsgruppen sind sowohl in beiden 24er-Sichten als auch
in der Vollsicht tatsaechlich nicht bitidentisch zur zugeordneten Referenz.
Exaktkontrollen bleiben bitidentisch und zaehlen nicht als Variantenbeleg.

| Bedingung | Subtyp | Beziehung N/D/R/L | Richtig eindeutig N/D/R/L | Beziehungsgewinne / -verluste | Eindeutigkeitsgewinne / -verluste |
| --- | --- | --- | --- | --- | --- |
| A_HISTORICAL_SUM | EXACT | 4/4/4/0 | 4/2/2/0 | 0/0 | 0/0 |
| A_HISTORICAL_SUM | LEVEL | 4/4/4/0 | 4/2/2/0 | 0/0 | 0/0 |
| A_HISTORICAL_SUM | FREQUENCY | 4/4/4/0 | 4/2/2/0 | 0/0 | 0/0 |
| A_HISTORICAL_SUM | SPECTRAL | 4/4/4/0 | 4/2/2/0 | 0/0 | 0/0 |
| A_ALL_BANDS | EXACT | 4/4/4/0 | 4/4/4/0 | 0/0 | 0/0 |
| A_ALL_BANDS | LEVEL | 4/4/4/0 | 4/4/4/0 | 0/0 | 0/0 |
| A_ALL_BANDS | FREQUENCY | 4/4/4/0 | 4/4/4/0 | 0/0 | 0/0 |
| A_ALL_BANDS | SPECTRAL | 4/4/4/0 | 4/4/4/0 | 0/0 | 0/0 |
| SLOW_HISTORICAL_SUM | EXACT | 4/4/4/0 | 4/4/4/0 | 0/0 | 0/0 |
| SLOW_HISTORICAL_SUM | LEVEL | 4/4/4/0 | 4/4/4/0 | 0/0 | 0/0 |
| SLOW_HISTORICAL_SUM | FREQUENCY | 4/4/4/0 | 4/4/4/0 | 0/0 | 0/0 |
| SLOW_HISTORICAL_SUM | SPECTRAL | 4/4/4/0 | 4/4/4/0 | 0/0 | 0/0 |

Damit bleiben 12/12 bereits anwendbare variierte Zielbeziehungen erhalten:
**sechs verschiedene Varianten in je zwei Panels**, nicht zwoelf unabhaengige
Quellen. Bei richtiger Eindeutigkeit sind es unter A_HISTORICAL_SUM 6/6,
unter den beiden anderen Bedingungen jeweils 12/12.

Fuer jeden der vier bekannten Subtypen gilt bei A_HISTORICAL_SUM separat:
4/4 falsche Nichtziel-Beziehungen, 2/8 mehrdeutige Panelbefunde und 2/8 falsch
eindeutige Panelbefunde, jeweils unveraendert zwischen beiden 24er-Sichten.
Unter A_ALL_BANDS und SLOW_HISTORICAL_SUM liegen diese Zahlen je bekanntem
Subtyp in beiden Sichten bei 0/4, 0/8 und 0/8. Neue falsche Beziehungen
entstehen in keiner Gruppe. Der Kontrollquelleneffekt ist getrennt unten
ausgewiesen und wird nicht mit Verlusten oder Varianten verrechnet.

## Konkurrenz, Zielentfernung und leere Nenner

| Bedingung | Belegung | Beziehung N/D/R/L | Richtig eindeutig N/D/R/L |
| --- | --- | --- | --- |
| A_HISTORICAL_SUM | Ziel allein | 8/8/8/0 | 8/8/8/0 |
| A_HISTORICAL_SUM | Ziel plus Konkurrent | 8/8/8/0 | 8/0/0/0 |
| A_ALL_BANDS | Ziel allein | 8/8/8/0 | 8/8/8/0 |
| A_ALL_BANDS | Ziel plus Konkurrent | 8/8/8/0 | 8/8/8/0 |
| SLOW_HISTORICAL_SUM | Ziel allein | 8/8/8/0 | 8/8/8/0 |
| SLOW_HISTORICAL_SUM | Ziel plus Konkurrent | 8/8/8/0 | 8/8/8/0 |

**D=0 unter Konkurrenz bei A_HISTORICAL_SUM bedeutet weiterhin
ERHALTUNG_NICHT_GEPRUEFT fuer richtige Eindeutigkeit.** Die erhaltenen
Zielbeziehungen loesen dort keine der acht bekannten Mehrdeutigkeiten auf.
Pro bekanntem Subtyp betrifft dies zwei Konkurrenzfaelle. Beide Familien
zeigen dieselben hier tabellierten Zaehler; die getrennten Familien- und
Variationsstrata stehen vollstaendig in `evaluation.json`.

Nach Zielentfernung bei verbleibender anderer Referenz ergeben sich unter
A_HISTORICAL_SUM 8/8 falsch eindeutige Befunde in beiden 24er-Sichten.
Unter ALL-BANDS und der Slow-Bedingung bleiben diese acht Faelle in beiden
Sichten leer. Zielentfernung in das leere Panel liefert ebenfalls nur leere
Befunde. Fehlende Ziele und unabhaengige Kontrollen haben N=D=0 fuer
Erhaltung; dies ist keine erfolgreiche Erhaltungspruefung.

## Die konkret verhinderten falschen Beziehungen

Nur die unabhaengige Kontrollquelle **np-a12 gegen np-a02** aendert ihre
Anwendbarkeit, wiederholt in **p01** und **p03**:

- A_ALL_BANDS: zwei falsch eindeutige Befunde werden leer.
- SLOW_HISTORICAL_SUM: dieselben zwei falsch eindeutigen Befunde werden leer.
- A_HISTORICAL_SUM: keine Aenderung; die Kontrolle bleibt anwendbar.

Dies sind zwei Panelbeziehungen **derselben Quelle**, keine zwei unabhaengigen
Negativquellen. Innerhalb der Kontrollgruppe sinkt die falsche Anwendbarkeit
bei den beiden engeren Bedingungen von 2/8 Nichtziel-Beziehungen auf 0/8;
falsch eindeutige Panels sinken von 2/8 auf 0/8, Mehrdeutigkeiten bleiben 0/8.
Bei A_HISTORICAL_SUM bleiben die Kontrollwerte 8/8 falsche Beziehungen,
4/8 falsch eindeutige Panels und 2/8 Mehrdeutigkeiten. np-a11 bringt keinen
weiteren Abdeckungsgewinn. Aus beiden Quellen folgt keine allgemeine
Erkennung von Unbekanntheit.

Gespeicherte Statistikwerte fuer np-a12/np-a02 aus p03, nur gelesen:

| Sicht | Historischer Mittelwert | Maximum |
| --- | ---: | ---: |
| Contiguous 24 | 1.4792857742595469e-09 | 6.756967058597124e-09 |
| Distributed 24 | 0.016784432675437295 | 0.18058917088271517 |
| Full 48, Diagnose | 0.00916086964704567 | 0.18058917088271517 |

Die Vollsicht-Mittelwertdiagnose bleibt hier unter 0.01, die verteilte
24er-Sicht liegt darueber. Die Vollsicht ist damit beobachtbar **keine
garantierte Leistungsobergrenze**. Sie verhindert die falsche Beziehung nur
beim Maximumtest. Kein Vollsichtwert floss in einen 24er-Vergleich ein.

## Einordnung und Grenzen

Beobachtet ist eine begrenzte, regelabhaengige Verbesserung verfuegbarer
Rezeptorevidenz ohne Verlust der geprueften bekannten Beziehungen. Die
unabhaengige Direktnachrechnung erklaert alle Befunde vollstaendig.
Keine neue Regel, Schwelle oder Maskenoptimierung. Kein globales Erfolgssiegel,
das die unveraendert breite A-Mittelwertbedingung verdeckt.

Nicht nachgewiesen: funktionaler Memoryabruf mit dieser Maske, allgemeine
Verlustfreiheit, Robustheit gegen weitere Quellen oder semantische
Klangidentitaet. Die Panelquellen sind keine real erzeugten Memoryslots.
Es folgt keine automatische Produktions-/Runtimeumstellung und keine
Wiederoeffnung von NO/NH. Historische Belege bleiben unveraendert.

## Belegidentitaeten

| Beleg | Bytes | SHA-256 |
| --- | ---: | --- |
| preregistration.json | 9406 | `69d298c95007acf40d4adad5e77f091043e93ef5438a12eea304cde574c6d8b0` |
| recording.json | 767662 | `07e8544f184177e7b221b5e2a9b3d4460a7cfec7c93a7e41aea69723a1d65707` |
| verification.json | 9093 | `b6e18ed4bf3284bf387bc4cbe99a676aa73987eb7c81b4cef2f5394e3f09eb2d` |
| evaluation.json | 401061 | `cf4edd7afe8225427ff1d03691f247b65b74b71d0af792f96d605f187ce82839` |
| result.json | 8348 | `fdb00582fc667a3c94fe450199efd28f047910245b6cb78833a3938b0d2be1dc` |

Kanonischer Ergebnisdigest:
`84f23b4159a1b52d96602356981441c17219b2e8288fab2a53375a45585dd566`.

Auswertungsdigest:
`43103f39c17ece53299f9e423ae2572f33ec401205ecbc7148f98a4d406d0bdb`.

Unveraenderte Materialisatdatei SHA-256:
`59796211f0203216a9c71c5b1e93a0326ebcc6d947e7c7ad7d4910d97307f430`.

Vollstaendige Plan-, Profil-, Quellen- und Codebindungen stehen in den
Belegen. Alle gebundenen Quelldateien vor/nach identisch. Auswertungstabellen
und Termbelege wurden fuer diesen Bericht nur gelesen, nicht erneut berechnet
oder verifiziert. Fremde Aenderungen und Bootstrap bleiben ausgeschlossen.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieses begrenzten
Abdeckungsvorteils weiter. Eine moegliche private Transferpruefung an realen
Memoryzustaenden waere gesondert zu planen und freizugeben; keine Integration
oder weitere Quellen-/Maskensuche wurde begonnen.
