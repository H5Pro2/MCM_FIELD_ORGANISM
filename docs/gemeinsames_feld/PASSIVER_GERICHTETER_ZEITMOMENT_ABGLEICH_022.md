# Passiver gerichteter Zeitmoment-Abgleich 022

## Status

Diese Untersuchung ist ein passiver Observerlauf vor `GF_001`. Sie führt
weder eine Feldwirkung noch einen zeitlichen Runtime-Zustand ein.

Die [Passive Kompaktzusammenfassungs-Kollision 021](PASSIVE_KOMPAKTZUSAMMENFASSUNGS_KOLLISION_021.md)
hat fehlende Zeitrichtung als konkrete Grenze eines festen Bündels aus 13
üblichen Kennwerten isoliert.

## Frage

Kann eine feste, stützbasierte und gerichtete Zeitbeobachtung:

1. dieselbe Kontaktstütze trotz anderer Segmentdichte gleich abbilden,
2. eine Bahn von ihrer Zeitumkehr unterscheiden,
3. und dennoch an anderen geordneten Bahnen kollidieren?

Der dritte Punkt ist zwingend, damit ein positiver Richtungsbefund nicht als
vollständige Zeitrepräsentation fehlgedeutet wird.

## Nullobserver

Geprüft wird das normierte erste zentrierte Zeitmoment:

```text
M1[x] = (1 / T²) ∫(t - T/2) x(t) dt
```

Die Integration erfolgt ausschließlich über die vollständig bekannte
synthetische Stützbahn. Das Moment ist eine feste skalare Nullbaseline, keine
MCM-Feldgleichung.

## Kontrolle 1: Darstellungsdichte

Die dichte und grobe konstante Bahn aus Vertrag 019 ergeben beide:

```text
M1 = 0
```

Das Aufteilen derselben konstanten Stütze verändert den Observer nicht.

## Kontrolle 2: Zeitumkehr

Für die Wege aus Untersuchung 021 gilt:

```text
A: 0,5 -> 0,2 -> 0,8 -> 0,3 -> 0,7 -> 0,5
B: 0,5 -> 0,7 -> 0,3 -> 0,8 -> 0,2 -> 0,5

M1[A] =  0,013888...
M1[B] = -0,013888...
```

Der gerichtete Observer unterscheidet diese Zeitumkehr und reagiert
antisymmetrisch.

## Kontrolle 3: andere Ordnungskollision

Zwei weitere vollständig gestützte Wege lauten:

```text
C: 0,5 -> 0,2 -> 0,3 -> 0,8 -> 0,7 -> 0,5
D: 0,5 -> 0,3 -> 0,2 -> 0,7 -> 0,8 -> 0,5
```

Sie sind als geordnete Bahnen verschieden, besitzen aber denselben Mittelwert
und dasselbe erste Zeitmoment:

```text
M1[C] = M1[D] = 0,027777...
```

## Tragfähiger Befund

Ein gerichtetes erstes Zeitmoment kann eine bestimmte Ordnungsdifferenz mit
fester Breite und ohne Segmentdichtefehler bewahren. Es kodiert die zeitliche
Ordnung jedoch nicht eindeutig.

Korrekte Aussage:

> Gerichtete Zeitinformation kann kompakt beobachtet werden, aber ein einzelnes
> Moment ist nur eine Projektion der gestützten Geschichte.

Nicht gezeigt ist:

- dass dieses Moment für eine Feldwirkung relevant ist,
- dass Zeitumkehr im Organismus immer verschieden wirken muss,
- dass weitere Momente eine vollständige Darstellung ergeben,
- dass ein Moment gespeichert oder rekurrent fortgeschrieben werden soll,
- dass ein fester Zeitoperator organischer als die vollständige Bahn ist.

## Stopplinie

`GF_001` bleibt geschlossen. Nicht freigegeben sind:

- das Zeitmoment als Dock- oder Neuronennutzlast,
- eine Momentenbank,
- ein Integrator oder lokaler Zeitwirkzustand,
- Schwellen, Gewichtungen oder Zeitkonstanten,
- Feldkopplung, Memory, Topologie oder Lernen.

## Nächster Prüfpunkt

Die nächste Untersuchung sollte nicht einfach weitere Momente anhäufen. Vor
einer Mechanik ist formal zu prüfen, ob jede feste endliche Bank linearer
Zeitprojektionen bei ausreichend reichen Kontaktbahnen einen Kollisionsraum
besitzt.

Damit lässt sich entscheiden, ob die Forschung weiter nach vollständiger
kompakter Geschichtsbewahrung suchen darf oder stattdessen die funktional
relevante, im lebenden Feld entstehende Wirkung begrenzen muss.

Der [Exakte lineare Zeitprojektions-Nullraum 023](EXAKTER_LINEARER_ZEITPROJEKTIONS_NULLRAUM_023.md)
beantwortet diese Frage für feste lineare Banken: Sobald der Verlaufsraum mehr
Dimensionen als die Bank besitzt, entsteht zwingend ein nichttrivialer
Kollisionsraum. Weitere feste lineare Momente lösen diese Grenze nicht.
