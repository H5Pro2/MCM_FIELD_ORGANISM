# Einordnung des einmaligen Kompaktierungsfehlbefunds

Status NOT_QUALIFIED, Exit 1. Genau ein Aufruf, kein Retry und keine
Code- oder Testkorrektur danach. 16 Testkoerper erreicht: 13 bestanden,
zwei mit Fehlassertions, einer mit Fehlerabschluss. Die 29 Fehlassertions
sind 28 unabhaengige Laengenunterfaelle und eine Quellenbudgetassertion;
hinzu kommt ein Ledgerfehler im vollstaendigen Huellentest.

## Tatsaechlich bestaetigt

Alle 28 ID-Bindungen sind nach administrativer Kompaktierung vollstaendig
rekonstruierbar. Die gesamten expandierten Inhalte der neutralen
Strukturfixture bleiben gleich, einschliesslich NJ-, Formations-, Scan-
und Generationsformen. Kein Replay oder neuer Funktionsnachweis dieser
gespeicherten Geschichte. Die unabhaengige ID-Verifikation, fehlende/falsche/
vertauschte/fremde Referenzabwehr und Digestkontrollen bestanden.
Die ID-Tabelle benoetigt expandiert 1041/2048 Byte und gespeichert 124 Byte.
Diese Teilersparnis ist kein Nachweis einer ausreichenden Gesamtbilanz.

## Drei offene Kontrollen

- Test 03: `s2oa-event-e01` bis `s2oa-event-e28` haben 14 Zeichen,
  `neutral-oa-01` bis `neutral-oa-28` dagegen 13. Die bisher vom Forscher
  behauptete Laengengleichheit war falsch. Die nachgelagerte Kontrolle
  im alten 13/14-Lauf hatte diesen Fehler noch nicht erreicht. Die technische
  ID-Ableitung bleibt unveraendert; eine kuenftige Groessenfixture muss
  ihre tatsaechlichen Laengen auch an Paar-/Owner-/Consume-Verwendungen
  beruecksichtigen. Keine ID-Verkuerzung oder Umdeutung erfolgt hier.
- Test 08: Der bestehende Ledger weist die vollstaendige neue Huelle mit
  METADATA_TOTAL_LIMIT ab. Eingerechnet waren 47135 Byte Basisreferenzen,
  zweimal die unveraenderten 4096 Byte Qualifikationsreserve und 512 Byte
  Laufabschlussreserve. Die Kompaktierung reicht damit nicht. Ein genauer
  Gesamtbetrag wurde wegen der fruehen Ledgerausnahme nicht gespeichert;
  er wurde nicht durch einen weiteren Aufruf nachberechnet.
- Test 05 ist ein eigener Testkoerper, verwendet aber die bereits zu grosse
  Huellenfixture. Deshalb wurde METADATA_TOTAL_LIMIT statt des erwarteten
  SOURCES_ITEM_LIMIT erreicht. Die gezielte Quellen-Einzelbudgetkontrolle
  bleibt offen. Getrennte Tests allein ersetzen keine gueltigen Vorbedingungen.

## Unverkuerzte Belegbilanz

| Datei | Byte |
| --- | ---: |
| preregistration.json | 2020 |
| result.json | 890 |
| stderr.txt | 19487 |
| stdout.txt | 0 |
| metrics.json | 169 |
| BEFUND.md | 301 |
| Summe der sechs gebundenen Dateien | 22867 |
| Unveraenderte Qualifikationsreserve | 4096 |

Damit auch 18771 Byte Ueberschreitung der Qualifikationsreserve. Das voll-
staendige Fehlerprotokoll bleibt erhalten; keine nachtraegliche Kuerzung,
keine budgetkonforme Umdeutung. Diese nachtraegliche Einordnung ist eine
zusaetzliche unqualifizierte Dokumentationsdatei und nicht Bestandteil des
bereits digestgebundenen Kurzberichts; sie kommt zu den 22867 Byte hinzu.
Die Ablage ist ein Fehlbeleg, keine freigegebene Runtime-Referenzkette.
Dokumentarische Ablage insgesamt 27084 Byte inklusive 4217 Byte Einordnung.

Quellhashinventar vor/nach unveraendert; voller Inventardigest laut
Vorregistrierung: 0f5256770b76096427b6f92a35acbfa73dc2076c917ee56b6d2600bef1c6f1d2.
Ergebnisdigest: 59b299c3d731fe03247b0b7adfb8ce27dcaf23ebf77f2b2d409519d23f307cc6.
Die zwei geaenderten OA-Anschlussdateien und vier neuen Dateien sind
explizit gegen ihre Vorgaenger gebunden. Historische Qualifikationen,
alte ID-Ableitung, Quellen, Ereignisverarbeitung und Memory bleiben unveraendert.
Der alte 13/14-Beleg bleibt NOT_QUALIFIED, der reale OA-Lauf NOT_EVALUABLE.
Keine Payloads, Rezeptor-/NJ-Analysen, Memory-/Feld- oder Hauptausfuehrung.
Gates False, ME/MI gesperrt; Prognosezweig ruht.

RUECKMELDUNG ERFORDERLICH: Vor einem weiteren freizugebenden Test muessen
die reale 14-Zeichen-ID-Laenge, isolierte Budgetfixtures und die vollstaendige
Referenz-/Fehlerabschlussbilanz zusammen behandelt werden. Keine kleinere
Reserve, Grenzerhoehung oder Quellenaenderung als Ersatz. Keine weitere
Korrektur oder Ausfuehrung aus diesem Bericht ableiten.

WEITER: Am besten geht es jetzt mit der Analystenentscheidung zu diesen
konkreten Bilanz- und Fixturegrenzen weiter.
