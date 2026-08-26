# S1-M: Passive Auswertung minimale F3-Feldverlaufsfunktion

Stand: 2026-08-09

Technische Klassifikation: `TRANSPARENT_HISTORY_EFFECT_LINEARLY_EXPLAINED`

Implementierung: abgeschlossen

Formaler Forschungslauf: nein

## Ziel

S1-M wertet die in S1-L erzeugten In-Memory-Messungen ausschliesslich nach
den in S1-K vorregistrierten Formeln und Schwellen aus. Der Evaluator besitzt
keine Runtimeautoritaet, veraendert keine Quelle und schreibt kein Ergebnis
zurueck.

## Implementierung

Der neue passive Evaluator
[`s1m_f3_history_function_evaluator.py`](../mcm_field_organism/s1m_f3_history_function_evaluator.py)
berechnet:

- den vollstaendigen S/H-Effektvektor ueber beide Probegrenzen;
- den F3- und linearen Linf-Effekt;
- die Verfeinerungsabweichungen 1/2 und 2/4;
- den vorregistrierten Konvergenz- und Nachweisboden;
- den relativen Rest gegen die lineare gekoppelte Baseline;
- Quellen-, Angleichungs-, Null-, Massen-, Wiederholungs- und
  Wiederbindungskontrollen;
- genau eine der vier in S1-K festgelegten Klassifikationen.

Schwellen, Quellen, Gleichungen, Parameter und Messwerte werden nicht
veraendert.

## Kontrollstatus

| Kontrolle | Ergebnis |
|---|---|
| Quellenmarginalien | bestanden |
| exakte S/H-Angleichung | bestanden |
| P0-, `eta=0`- und M-neutralisierte Nullwirkung | bestanden |
| Gesamtmasse und Nichtnegativitaet | bestanden |
| exakte Wiederholung | bestanden |
| externe Wiederbindung | bestanden |
| endliche numerische Metriken | bestanden |

Damit ist die technische Klassifikation gueltig. Keine Kontrolle wurde nach
Kenntnis des Effekts gelockert.

## Numerisches Ergebnis

```text
F3 effect Linf:                    0.0006343726494123916
linear effect Linf:                0.0006226954320371393
refinement 1/2 Linf:               2.5888146229871047e-07
refinement 2/4 Linf:               2.9426476406296288e-08
convergence floor:                 2.354118112503703e-07
detection floor:                   2.354118112503703e-07
linear relative residual:          0.018416817611312034
linear equivalence limit:          0.05
```

Der F3-Effekt liegt ueber dem vorregistrierten Nachweisboden. Der relative
Rest des vollstaendigen Effektvektors gegen die lineare gekoppelte Baseline
betraegt rund 1.842 Prozent und liegt damit unter der festen 5-Prozent-Grenze.

Die vorregistrierte technische Klassifikation lautet deshalb:

```text
TRANSPARENT_HISTORY_EFFECT_LINEARLY_EXPLAINED
```

## Bedeutung fuer die Entwicklung

Die aktuelle 26-Neuronen-AV-Architektur besitzt mit F3 eine reproduzierbare
geschichtsabhaengige spaetere Feldwirkung. Diese Wirkung:

- bleibt nach exakter S/H-Angleichung messbar;
- verschwindet exakt ohne M-Rueckwirkung;
- verschwindet exakt nach uniformer M-Neutralisierung;
- kann nach externer Neutralisierung technisch erneut gebunden werden;
- wird im geprueften Korridor durch die enge lineare gekoppelte Feldbaseline
  innerhalb der vorregistrierten Grenze erklaert.

Damit ist eine transparente technische Feldverlaufsfunktion vorhanden. Das
Projekt muss fuer die weitere Engineeringentwicklung keine unbekannte neue
Physik behaupten. Gleichzeitig darf die Funktion nicht als organisches
Memory oder emergente Organisation ausgegeben werden.

## Testergebnis

Der fokussierte angrenzende Verbund besteht mit:

```text
69 passed
24 subtests passed
```

Die bekannte Pytest-Cachewarnung `WinError 183` betrifft nur den lokalen
Cachepfad.

## Aussagegrenze

S1-M ist eine passive technische In-Memory-Auswertung, kein formaler
Forschungslauf. Die Klassifikation belegt nicht:

- Lernen, Praegung, Vergessen oder Rekonstruktion;
- MCM-Memory oder organisches Memory;
- relative Feldzeit oder Feldzeitverdichtung;
- inneren Kontext, Bedeutung oder Semantik;
- Organisation, Topologie oder Selbstregulation;
- feldbasierte KI oder neue Feldphysik.

Es gab keinen Browserstart, keine reale Sensorik, keinen Forschungsrunner,
keinen Report und keine neue Laufnummer. Lauf 194 wird nicht wiederholt; Lauf
197 bleibt unberuehrt.

## Bester naechster Schritt

S1-N registriert als naechste Engineeringfrage eine Expositions- und
Erhaltungskurve auf der aktuellen Geometrie vor. Sie soll pruefen, ob ein,
zwei, vier und acht gleiche kontrollierte Kontakte die spaetere technische
Feldwirkung abgestuft veraendern und wie diese Wirkung unter festen
Nullkontaktdauern abnimmt.

F3 und die lineare gekoppelte Baseline bleiben gleichwertige Hauptarme; P0
und `eta=0` bleiben Nullkontrollen. Die Begriffe Praegung,
Feldzeitverdichtung und Vergessen bleiben bis zu weitergehender funktionaler
Evidenz gesperrt.

## Spaeterer Vertragsstand S1-N

S1-N ist inzwischen in der
[`Vorregistrierung der Expositions- und Erhaltungskurve`](S1N_VORREGISTRIERUNG_EXPOSITIONS_UND_ERHALTUNGSKURVE.md)
gebunden. Der Vertrag trennt Expositionsdosis, Ereignissegmentierung,
Nullkontaktdauer und lineare Mechanikerlaerung. Naechster Schritt ist der
reine S1-O-In-Memory-Quellen- und Matrixadapter ohne Klassifikation.
