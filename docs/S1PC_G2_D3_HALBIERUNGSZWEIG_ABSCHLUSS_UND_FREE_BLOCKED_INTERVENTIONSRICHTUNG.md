# S1-PC G2/D3 Halbierungszweig-Abschluss und Free/Blocked-Interventionsrichtung

## Status und Umfang

S1-PC ist ausschliesslich ein statischer Abschluss- und Richtungsvertrag.
Dieser Schritt fuehrt keine neue Gleichung, keinen Zahlenwert, keinen
Parameter, kein Schema, keine Implementierung, keinen Test und keinen Lauf
ein. Der primaere technische Kern bleibt das MCM-Wahrnehmungsfeld.

## Verbindliche Entscheidung

Die atomare Entscheidung lautet:

```text
G2_D3_HALVING_BRANCH_CLOSED_EQUAL_BOUND_FREE_BLOCKED_NEXT_BINDING_SELECTED
```

Der in S1-PB geschlossene Halbierungsvektor wird nicht weiter als eigene
Kandidatenfunktion verfolgt. Er darf als Regression und technische Kontrolle
erhalten bleiben. Weitere Anpassungen oder Wiederholungen desselben
Baselinevergleichs sind keine neue Evidenz.

Als einzige naechste Untersuchungsrichtung wird eine lokale Zweiarm-
Intervention ausgewaehlt. Beide Arme besitzen dieselbe Gesamtressource und
dieselbe leitende Bindung. Sie unterscheiden sich ausschliesslich in der
Aufteilung der verbleibenden Ressource auf `free` und `blocked`. Anschliessend
erhalten beide Arme dasselbe frische Bindungsereignis.

## Rollenbezug

Die aktuelle G2/D3-Anatomie speichert pro Kante exakt:

- `free`;
- `bound_unconfigured`;
- `bound_configured`;
- `blocked`.

`blocked` bezeichnet dabei die aktuell nicht direkt bindbare lokale
Ressource. Diese vorhandene Rolle uebernimmt in dieser Untersuchungsrichtung
die technische Funktion der zuvor allgemein als refraktaer beschriebenen
Ressource. Der Schemawortschatz wird nicht umbenannt oder erweitert.

Die leitende Gesamtbindung ist:

```text
bound = bound_unconfigured + bound_configured
```

## Gebundene Zweiarm-Anatomie

Die spaeteren Arme `FREE_AVAILABLE` und `BLOCKED_HELD` muessen vor jeder
Ausfuehrung folgende Identitaeten erfuellen:

```text
capacity_FREE_AVAILABLE = capacity_BLOCKED_HELD
bound_unconfigured_FREE_AVAILABLE = bound_unconfigured_BLOCKED_HELD
bound_configured_FREE_AVAILABLE = bound_configured_BLOCKED_HELD
bound_FREE_AVAILABLE = bound_BLOCKED_HELD
free_FREE_AVAILABLE + blocked_FREE_AVAILABLE
  = free_BLOCKED_HELD + blocked_BLOCKED_HELD
capacity = free + bound_unconfigured + bound_configured + blocked
```

Diese Zeilen wiederholen ausschliesslich die bereits gebundene Anatomie und
Erhaltung. Sie sind keine neue Wirkungs- oder Entwicklungsgleichung.

Kante, Traeger, Geometrie, Feldreferenz und kausaler Vorzustand muessen
ebenfalls identisch sein. Nur die lokale `free`/`blocked`-Aufteilung darf
zwischen den Armen variieren. Konkrete Werte sind in S1-PC gesperrt.

## Kausale Reihenfolge

Eine spaetere Pruefung muss diese Reihenfolge einhalten:

1. Ein gemeinsamer gueltiger Vorzustand wird gebunden.
2. Eine atomare externe Ressourcenintervention erzeugt die beiden Arme.
3. Beide Armzustaende werden vollstaendig und fail-closed validiert.
4. Ein unmittelbarer O3-Readout darf nur als Manipulationskontrolle dienen.
5. Beide Arme erhalten dasselbe frische lokale Bindungsereignis.
6. Erst die tatsaechlich gebundene Menge und das gueltige Nachereignis-Ledger
   bilden den primaeren Vergleich.

Der vorhandene D3-Fortsetzungsoperator verschiebt nur
`bound_unconfigured` nach `bound_configured` und laesst `free` sowie
`blocked` unveraendert. Er darf deshalb weder die Intervention erzeugen noch
als vorweggenommene Loesung dieser neuen Frage ausgelegt werden.

## Funktionsprognose

Die zu pruefende Kandidatenprognose lautet:

> Bei gleicher Gesamtressource, gleicher leitender Bindung und demselben
> frischen Bindungsereignis fuehrt eine hoehere frei verfuegbare lokale
> Ressource zu einer anderen tatsaechlichen naechsten Bindung als eine
> entsprechend hoehere blockierte Ressource.

Diese Prognose bezieht sich auf eine spaetere reale Ledger-Aenderung. Eine
blosse Differenz des unmittelbaren O3-Readouts reicht nicht aus, weil O3
`free` bereits direkt ausliest und diese Differenz daher konstruktiv waere.

## Gegenprognosen und faire Exposition

Eine Fixed-, Gain- oder skalare Retentionsbaseline, die aus demselben
Vorzustand dasselbe frische Ereignis erhaelt, aber keine lokale
Ressourcenaufteilung besitzt, prognostiziert keine armabhaengige naechste
Bindung. Sie darf weder Armname noch Kandidatenledger als versteckten Eingang
erhalten.

Eine Baseline, die den unmittelbaren O3-Wert oder die `free`/`blocked`-
Aufteilung als Eingang erhaelt, kann die Armtrennung direkt uebernehmen. Ein
solcher Vergleich waere fuer die hier gebundene Funktionsfrage nicht
unterscheidend und darf nicht als Gegenbaseline verwendet werden.

## Falsifikation und Abbruch

Die Richtung ist fuer den gebundenen Zweck zu verwerfen oder vor Ausfuehrung
abzubrechen, wenn mindestens eine Bedingung eintritt:

- Gesamtressource oder leitende Bindung unterscheiden sich zwischen den
  Armen;
- ausser `free` und `blocked` wird eine weitere Kandidatenvariable veraendert;
- die Intervention wird durch den vorhandenen Fortsetzungsoperator erzeugt;
- nur der unmittelbare O3-Readout unterscheidet sich;
- nach dem identischen frischen Ereignis unterscheidet sich keine
  tatsaechliche Bindung;
- eine Gegenbaseline erhaelt Armname, Kandidatenledger oder postinterventionellen
  Kandidatenreadout;
- ein ungueltiger Zustand wird geklemmt, repariert, normalisiert oder
  fortgesetzt;
- Vor- oder Nachzustand verletzt die lokale Erhaltungsidentitaet.

## Gesperrte Aussagen

S1-PC ist kein Nachweis von Speicherung, Lernen, Anpassung, autonomer
Organisation oder einer hypothetischen MCM-Memory-Funktion. Er begruendet
keine Systemfaehigkeit und keine Aussage ueber biologische Eigenschaften.
Er waehlt nur eine kausal unterscheidbare technische Pruefrichtung aus.

## Naechster erlaubter Schritt

S1-PD darf ausschliesslich die atomare `free`/`blocked`-
Umbuchungsanatomie binden: zulaessige Kausalquelle, Vor- und
Nachinterventionsidentitaeten, verbotene Zustaende und Fail-Closed-Codes.
Konkrete Ressourcenwerte, Wirkungsgleichung, Bindungsdynamik,
Implementierung, Test und Lauf bleiben auch dort gesperrt.
