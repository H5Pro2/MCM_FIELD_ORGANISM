# S1-FB: Statische Diskretisierungs- und Schrittskalierung

## Forschungsfrage

Entsteht der Rueckgang des aktiven E1-Reihenfolgekontrasts ueber r2/r4/r8
durch eine fehlende Zeitskalierung, durch veraenderte Weltkontakte oder durch
eine tatsaechlich diskretisierungsabhaengige Integrationsstufe?

## Statischer Befund

Die Verfeinerungen halten den physischen Horizont, alle Rezeptorsupports und
ihre Abschlusszeitpunkte konstant. Nur die Zahl der Teilintervalle steigt:

| Stufe | Faktor | Bildungsschritte je Arm | Probeschritte je Rolle |
|---|---:|---:|---:|
| r2 | 2 | 402 | 200 |
| r4 | 4 | 804 | 400 |
| r8 | 8 | 1608 | 800 |

Feld-, Nachhall- und E1-Raten sind pro Sekunde definiert. Die kuerzeren
Teilintervalle werden ueber `elapsed_seconds` in Exponential- und
Freigabe-/Bindungsterme eingesetzt. Ein fester Zusatz pro Schritt wurde nicht
gefunden.

Die neutrale S/H-Felddynamik und die spaetere eingefrorene E1-Probe werden
zwischen festen Ereignissen spektral exakt fortgeschrieben. Die erste
strukturell nicht exakte Stufe ist die E1-Bildung: Der nichtlineare lokale
E1-Zustand wird pro Teilintervall mit einer Halbentwicklung am Startfeld und
einer Halbentwicklung am Endfeld gekoppelt. Dadurch darf das gebildete E1-
Substrat von der Verfeinerung abhaengen.

## Beobachtete Skalierung

Die Abnahme von r4 nach r8 betraegt gegenueber der Abnahme von r2 nach r4:

- Aktivierung: etwa `0.461881`;
- Nachhall: etwa `0.464260`.

Die beinahe Halbierung ist mit einem erstordnungsartigen asymptotischen Trend
vereinbar. Drei Skalarstufen beweisen jedoch weder eine Konvergenzordnung noch
Instabilitaet, insbesondere weil die zugrunde liegenden Vektoren fehlen.

Entscheidung:
`TIME_SCALING_SOUND_E1_FORMATION_IS_FIRST_NONEXACT_STAGE`.

Es wurde kein fehlender `dt`-Faktor gefunden, kein Feld ausgefuehrt und EC46
nicht nachtraeglich geaendert. Kein Memory- oder KI-Claim.

## Verifikation

Sechs fokussierte S1-FB-Tests und 179 relevante Verbundtests mit 29 Subtests
bestehen. Dreizehn historische S1-EB-Planer-/Formationstests sind nach dem
abgeschlossenen Einmallauf nicht erneut gueltig ausfuehrbar, weil sie freie
Report-, Attempt- und Lock-Zielpfade als Vorlaufbedingung verlangen. Alle
dreizehn brechen an genau dieser belegten Einmallaufgrenze ab; es liegt kein
S1-FB- oder Operatorfehler vor.

## Bester naechster Schritt

Am besten geht es mit S1-FC weiter: statisch einen getrennten
Bildungszustands-Konvergenzvertrag entwerfen. Dieser muss E1-Endzustandsvektoren
vor der Probe vergleichen und darf die bestehende EC46-Probeentscheidung weder
ersetzen noch nachtraeglich lockern. Noch keine Ausfuehrung.
