# S1-L: Implementierung In-Memory-F3-Feldverlaufspruefadapter

Stand: 2026-08-09

Technische Entscheidung: `IN_MEMORY_FUNCTION_ADAPTER_BOUND_NO_RESEARCH_DECISION`

Implementierung: abgeschlossen

Forschungslauf: nein

## Ziel

S1-L implementiert ausschliesslich die in S1-K vorregistrierten Quellen,
Armpfade und Kontrollinterventionen im Speicher. Der Adapter berechnet noch
keine vorregistrierte Hauptentscheidung und erzeugt weder Runner noch Report
oder Laufnummer.

## Aenderungen

Die S1-J-Sequenzkomposition akzeptiert nun explizit die bereits von der
F3-Runtime unterstuetzten Verfeinerungen. Gleichung, Parameter, Integrator und
Feldgeometrie bleiben unveraendert.

Der neue Adapter
[`s1l_f3_history_function_adapter.py`](../mcm_field_organism/s1l_f3_history_function_adapter.py)
bindet:

- Verlauf A mit `auditory[0]=0.8` und `visual[5]=0.6`;
- Verlauf B mit `auditory[7]=0.8` und `visual[12]=0.6`;
- vier Verlaufssupports und zwei Nullsupports;
- exakte externe S/H-Angleichung;
- die identische Probe P;
- F3, lineare gekoppelte Baseline, `eta=0` und P0;
- eine getrennte uniform M-neutralisierte F3-Kontrollkopie;
- den extern neutralisierten B-Wiederbindungspfad;
- Verfeinerungen 1, 2 und 4;
- fluechtige S/H/M-Zustandsvektoren und Digests.

Alle Ergebnisvertraege sperren Forschungsentscheidung, Lernclaim und
Memoryclaim. Es wird kein Rohbild-, Audio- oder Medienpayload gehalten.

## Technische Vertragspruefungen

Die neuen Tests pruefen:

1. gleiche Supportzahl, Ereigniszahl, Wertemultimenge, L1- und L2-Amplitude
   von A und B;
2. verschiedene technische Quelldigests;
3. exakt angeglichene S/H-Zustaende vor P;
4. nichtnegative M-Werte und Gesamtmasse 1.0;
5. verschiedene M-Zustaende nach A/B in F3, linearer Baseline und `eta=0`;
6. uniforme M-Gleichheit in P0 und M-neutralisierter Kontrolle;
7. exakte S/H-Wirkungsnullen in `eta=0`, P0 und M-neutralisierter Kontrolle;
8. zugaengliche Verfeinerungen 1, 2 und 4;
9. exakte Wiederholung der Verfeinerung 4;
10. exakte Zustandsuebereinstimmung des extern neutralisierten
    Wiederbindungspfads mit der frischen B-Referenz.

## Testergebnis

Der fokussierte angrenzende Verbund besteht mit:

```text
65 passed
24 subtests passed
```

Die bekannte Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen
Cachepfad.

## Unverarbeitete technische Skalarwerte

Die folgenden Werte sind reine Adapterausgaben. S1-L berechnet daraus noch
keinen Nachweisboden, relativen Baselinefehler oder Forschungsentscheid.

| Arm | Verfeinerung | maximaler S/H-A/B-Unterschied waehrend P |
|---|---:|---:|
| F3 | 1 | 0.0006346286978317526 |
| F3 | 2 | 0.0006343987978132987 |
| F3 | 4 | 0.0006343726494123916 |
| lineare gekoppelte Baseline | 4 | 0.0006226954320371393 |
| `eta=0` | 4 | 0.0 |
| P0 | 4 | 0.0 |
| F3 M-neutral | 4 | 0.0 |

Der maximale S/H/M-Unterschied zwischen extern neutralisiertem
Wiederbindungspfad und frischer B-Referenz ist `0.0`.

Diese Werte zeigen nur, dass der Adapter den vorregistrierten Effekt- und
Nullraum technisch aufloesen kann. Insbesondere wird der skalare Unterschied
zwischen F3 und linearer Baseline nicht als Mechanikrest interpretiert. Der
S1-K-Vertrag verlangt dafuer den Vergleich vollstaendiger Effektvektoren und
den vorregistrierten Konvergenzboden.

## Aussagegrenze

S1-L ist technische Implementierung und Testausfuehrung, kein
Forschungsdurchlauf. Der Stand belegt nicht:

- Lernen, Praegung, Vergessen oder Rekonstruktion;
- MCM-Memory oder organisches Memory;
- relative Feldzeit oder Feldzeitverdichtung;
- inneren Kontext, Bedeutung oder Semantik;
- Organisation, Topologie oder Selbstregulation;
- feldbasierte KI oder neue Feldphysik.

Es gab keinen Browserstart, keine Kamera, kein Mikrofon, keine reale
Sensorik, keinen Ergebnisreport und keine neue Laufnummer. Lauf 194 wird
nicht wiederholt; Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

S1-M implementiert einen reinen passiven In-Memory-Evaluator ueber den
unveraenderten S1-L-Messungen. Er berechnet Effektvektoren,
2/4-Verfeinerungsboden, relativen linearen Baselinefehler sowie die bereits
in S1-K festgelegten Kontrollflags. S1-M darf die vorregistrierten Schwellen
nicht aendern und erzeugt weiterhin keinen Runner, Report oder Laufnummer.

## Spaeterer Auswertungsstand S1-M

S1-M ist inzwischen in der
[`passiven Auswertung der minimalen F3-Feldverlaufsfunktion`](S1M_PASSIVE_AUSWERTUNG_MINIMALE_F3_FELDVERLAUFSFUNKTION.md)
umgesetzt. Alle Pflichtkontrollen bestehen. Der F3-Effekt liegt ueber dem
Nachweisboden, wird aber mit 1.842 Prozent Rest innerhalb der festen
5-Prozent-Grenze durch die lineare gekoppelte Baseline erklaert. Naechster
Schritt ist die statische S1-N-Vorregistrierung einer Expositions- und
Erhaltungskurve.
