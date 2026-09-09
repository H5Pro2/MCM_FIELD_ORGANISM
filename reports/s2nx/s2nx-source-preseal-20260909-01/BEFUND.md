# S2-NX: einmalige rezeptorfreie Vorversiegelung

Lauf-ID: `s2nx-source-preseal-20260909-01`.
Status: `S2NX_SOURCES_PRESEALED`; unabhaengige Bindungspruefung:
`S2NX_PRESEAL_VERIFIED`. Exit-Code `0`, kein Retry.

Nach [24/24 neutralen Quellenpruefungen](../s2nx-source-binding-qualification-20260909-01/BEFUND.md)
wurden genau **32 PCM-Fenster** in versiegelter Reihenfolge erzeugt:
153.600 Samples, 614.400 Byte insgesamt, hoechstens ein vollstaendiger
Payload mit 19.200 Byte gleichzeitig. Keine Rohpayloadablage oder
Deduplizierung. Der Nenner 1024 ist im privaten NX-Anschluss explizit;
historische NW-Validatoren, Quellen und Belege blieben unveraendert.

## Gebundener Umfang

[execution-plan.json](execution-plan.json) bindet sechs Folgen: zwei
Sechser-Lernhistorien und vier Fuenfer-Prueffolgen. Acht Updatepositionen,
zwei getrennte Nullzustaende und beide Einfriergrenzen vor der ersten
Pruefquelle sind festgeschrieben. Zwoelf Pruefstellen erhalten spaeter beide
eingefrorenen Zustaende sowie PERSIST, LINEAR und die konstante 0.5
(`0x1.0000000000000p-1`). Beide erwarteten Lernkoeffizienten bleiben `null`.

[evaluation-plan.json](evaluation-plan.json) bindet getrennt 28 Kriterien:
sechs Kreuzhistorien-, sechs Festfaktor-, zwoelf Baseline- und vier
Wechselverlustbedingungen. Unterschiedliche Koeffizienten sind kein
technisches Startgate. Kategorien und erwartete Historien bleiben im
Auswerter; keine nachtraegliche Auswahl des besseren Zustands.

## Saemtliche Bytegleichheiten

Alle Quellenkennungen tragen das Praefix `nx-`. Die vollstaendigen
Payloadhashes und getrennten Quellen-/Zeitbindungen stehen im
[Siegel](seal.json). Folgende sieben Gruppen sind bytegleich:

| Gruppe | Quellen ohne gemeinsames Praefix |
| --- | --- |
| 1 | l01-w00, l02-w00 |
| 2 | l01-w01, l02-w01 |
| 3 | s01-w00, s02-w00, s03-w00, s04-w00 |
| 4 | s01-w01, s02-w01, s03-w01, s03-w03, s04-w01 |
| 5 | s01-w02, s03-w02 |
| 6 | s02-w02, s04-w02 |
| 7 | s04-w03, s04-w04 |

Neben den vorgesehenen Praefixentsprechungen sind auch s03-w03 in Gruppe 4
und die beiden letzten s04-Fenster dokumentiert. Keine Kollision wurde
beseitigt oder als unabhaengige Replikation gewertet.

## Einmalige Bindungspruefung

[verification.json](verification.json) prueft einmal read-only kanonische
Wurzeln, Quellen-/Rezept-/Zeitformen, alle Metadatenpositionen, Profil,
Interpreter-/Generatoridentitaet, Codehashes, Qualifikation, Zaehler und
vollstaendige Kollisionsgruppen. Vorher-/Nachher-Dateihashes sind gleich;
Payloadregenerationen `0`. Dies ist keine zweite Berechnung der PCM-Bytes
und kein Nachweis der spaeteren kausalen Prognose-vor-Ziel-Reihenfolge.

| Bindung | Digest |
| --- | --- |
| Ausfuehrungswurzel | `f52992815d49889334b11f64a13e00879984ce4cabecd3670a0fcf2d7441b80c` |
| Evaluationswurzel | `c755699e69fa38dff0426080ac7d37500e6ba044afd9c53abff4ffe97613847e` |
| Siegel | `2c6d26ccacfb55341b513d9f240973335d076e69c5a4bd134092c06471953f42` |
| Verifikation | `3ce0b1d01818e228ca18b6e1786aaa9e6062ed3442d262e0366e296056a8a93e` |

## Aussagegrenze und Stopp

Rezeptor-, NJ-, Lern-, Prognose-, Fehler-, Memory-, Feld-, Kontext- und
Runtimeaufrufe jeweils **0**. Keine Koeffizienten oder fachlichen Kriterien
berechnet. Gates bleiben `False`, ME/MI gesperrt. Keine separate
Rezeptormaterialisierung und kein Hauptlauf freigegeben.

Die Quellenbindung ist abgeschlossen. Die kausale Zwei-Lerner-Anbindung
benoetigt eine separate Freigabe und Qualifikation. Selbst ein spaeterer
vollstaendiger Erfolg belegt keine selbststaendige Auswahl der passenden
Historie bei identischem Praefix und keine Quellen-/Objektidentitaet.
Historische Belege, fremde Aenderungen und Bootstrap bleiben unveraendert.

WEITER: Am besten geht es jetzt mit der Analystenpruefung dieser Bindungsbelege
und der separaten Entscheidung zur kausalen Zwei-Lerner-Anbindung weiter.
