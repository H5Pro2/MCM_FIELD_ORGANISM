# S1-X: Gezielte Komponentenrest-Replikation

Stand: 2026-08-09

Entscheidung: `COMPONENT_REST_REPLICATED_AT_4_8`

Formaler Forschungslauf: nein

## Ausgangspunkt und Auswahl

S1-X waehlt deterministisch alle direkten S1-W-Komponenten mit einem
linearen R4-Rest oberhalb 5 Prozent. Es wurden weder Treffer entfernt noch
Zellen unterhalb der Grenze hinzugefuegt.

Die Auswahl ergibt exakt drei Treffer:

1. Dosis 8, wiederholte Supports, kumulativ 0.000 bis 0.200 Sekunden,
   Aktivierungsantrieb;
2. Dosis 8, wiederholte Supports, Intervall 0.200 bis 0.400 Sekunden,
   Aktivierungsantrieb;
3. Dosis 8, wiederholte Supports, Intervall 0.400 bis 0.800 Sekunden,
   Aktivierungsantrieb.

Es gibt keinen Treffer im massenausgleichenden Transport, bei Dosis 1, bei
kontinuierlichen Supports oder im Intervall 0.800 bis 1.600 Sekunden.

## Replikationsergebnis

| Ziel | Rest R4 | Rest R8 | F3-Diff. 2/4 | F3-Diff. 4/8 | linear Diff. 2/4 | linear Diff. 4/8 |
|---|---:|---:|---:|---:|---:|---:|
| D8 wiederholt kumulativ 0.2 | 0.05226694967860188 | 0.05226696101801521 | 1.4688710361964244e-09 | 1.7650619990117536e-10 | 1.3888521624536194e-09 | 1.6677092953137906e-10 |
| D8 wiederholt 0.2->0.4 | 0.05752400477029081 | 0.05752400507649125 | 7.391330758056182e-09 | 8.919349886492636e-10 | 7.336960703048512e-09 | 8.856799391110393e-10 |
| D8 wiederholt 0.4->0.8 | 0.054060801713728616 | 0.054060797552333985 | 4.6844942649341276e-09 | 5.682153662520117e-10 | 4.646431691116525e-09 | 5.636891708613034e-10 |

Alle drei R8-Reste bleiben oberhalb 5 Prozent. Bei F3 und linearer Baseline
ist die 4/8-Differenz jeweils deutlich kleiner als die 2/4-Differenz. Alle
drei Treffer erfuellen damit die vorregistrierte Replikationsregel.

Der maximale R8-Rest betraegt `0.05752400507649125` beziehungsweise rund
5.7524 Prozent.

## Gegenwirkungsbilanz

| Ziel | Komponentenunterschied R8 | Gesamt-M-Unterschied R8 | Gesamt/Komponente |
|---|---:|---:|---:|
| D8 wiederholt kumulativ 0.2 | 0.0001487106318426067 | 0.000056171462104105674 | 0.3777232428381905 |
| D8 wiederholt 0.2->0.4 | 0.00008468419440028538 | 0.0000419599291516734 | 0.49548713840669184 |
| D8 wiederholt 0.4->0.8 | 0.0000689159634235765 | 0.00006642906807717563 | 0.9639140886543844 |

Der direkte Komponentenunterschied wird in den ersten beiden Treffern durch
andere Beitragsanteile deutlich reduziert. Im dritten Treffer uebertraegt er
sich fast vollstaendig auf das M-Inkrement. Eine einheitliche
Gegenwirkungsstaerke darf daraus nicht abgeleitet werden.

## Mechanische Einordnung

Alle Treffer liegen im F3-Aktivierungsantrieb:

```text
A_i = -lambda * kappa
      * sum_j ((M_i + M_j) * (S_j - S_i))
```

Die lineare Baseline ersetzt die lokale Massensumme durch `2*M_0`. Bei der
staerksten wiederholten Exposition weicht die lokale M-Lage ausreichend von
der uniformen Referenz ab, um diese feste nichtlineare Massengewichtung
reproduzierbar sichtbar zu machen.

S1-X entdeckt damit keine unbekannte Gleichungsrolle. Es bestaetigt einen
engen, numerisch stabilen Unterschied zwischen der vorhandenen nichtlinearen
F3-Gleichung und ihrer bekannten Linearisierung.

## Kontrollen und Test

Deterministische Auswahl, exakte R4-Neuberechnung, Bilanzschluss,
Observertransparenz, endliche Metriken und Wiederholung bestehen.

Der fokussierte, in einem frischen Prozess reproduzierte Verbund besteht mit:

```text
4 passed
3 subtests passed
151.34 s
```

Die bekannte Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen
Cachepfad.

## Aussagegrenze

Der replizierte Rest ist kein Nachweis neuer Physik, von Memory, Lernen,
Praegung, Vergessen, Feldzeit oder innerem Kontext. Er zeigt keine Semantik,
Organisation, Topologie, Selbstregulation oder KI.

S1-S hatte die zusammengesetzte M-/Probeantwort weiterhin innerhalb der
linearen Grenze eingeordnet. Ein Komponentenunterschied allein belegt daher
keinen funktionalen Vorteil des F3-Pfads.

Es gab keinen Browserstart, keine reale Sensorik, keinen externen Runner,
keinen Report und keine neue Laufnummer. Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

S1-Y schliesst die Komponentenverfeinerung zunaechst statisch ab und trifft
eine Architekturentscheidung. Es ordnet den replizierten Rest der bekannten
nichtlinearen Massengewichtung zu und prueft, ob daraus gegenueber der
linearen Baseline bereits irgendein separates funktionales Kriterium folgt.

Wenn kein solches Kriterium vorliegt, wird diese Mikrolinie nicht weiter
verfeinert. Dann wird als naechste Entwicklungsfrage der noch fehlende lokale
Substratfreiheitsgrad formuliert, der wiederholungsabhaengige Bildung,
Erhaltung und Loesbarkeit ueber die feste F3-Relaxation hinaus ueberhaupt
tragen koennte, ohne Memoryfunktion vorzuprogrammieren.
