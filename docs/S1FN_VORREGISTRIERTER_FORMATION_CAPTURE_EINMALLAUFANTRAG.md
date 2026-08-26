# S1-FN: Vorregistrierter Formation-Capture-Einmallaufantrag

## Forschungsfrage

Erzeugen dieselben kontrollierten AV-Bestandteile bei angeglichenen Supports,
Abschlusszeiten und Kontaktintegralen allein durch die Reihenfolge AB gegen BA
eine reproduzierbar unterscheidbare und ueber r2/r4/r8 numerisch konvergierende
E1-Bildungszustandsdifferenz?

## Gebundene Messung

Der Lauf umfasst genau 15 Formation-Arme:

```text
r2, r4, r8
x
active-ab, active-ba, identity-ab,
formation-ablated-ab, formation-ablated-ba
```

Nach vollstaendiger Formation werden die 15 lebenden E1-Endzustaende genau
einmal durch S1-FF erfasst und durch S1-FD ausgewertet. Es folgt keine Probe.

## Vorregistrierte Entscheidungen

- `INVALID_FORMATION_STATE_CONTROLS`: Identity-, Ablations- oder
  Ressourcenbaseline ist ungueltig.
- `NO_DISTINGUISHABLE_FORMATION_ORDER_STATE`: AB und BA besitzen keinen ueber
  die absolute Kontrolle hinaus unterscheidbaren Zustandsrest.
- `FORMATION_STATE_NOT_CONVERGED`: Ein Rest ist vorhanden, aber nicht ueber
  r2/r4/r8 numerisch belastbar.
- `FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY`: Der AB/BA-Zustandsrest besteht
  Kontrollen und Aufloesungspruefung.

Keine dieser Entscheidungen ist allein ein Nachweis von Memory, Feldzeit,
Verdichtung, innerem Kontext, Organisation oder KI. Ein positiver Ausgang
wuerde nur zeigen, dass Reihenfolge unter den gebundenen Kontrollen einen
robusten E1-Bildungszustand mitbestimmt.

## Gegenbaselines und Grenzen

- `identity-ab` begrenzt den aktiven Bildungsbeitrag;
- beide Formationsablationsarme muessen neutral bleiben;
- Ressourcenfehler muessen innerhalb `1e-12` bleiben;
- r2/r4/r8 trennen einen numerischen Rest von Aufloesungsstabilitaet;
- maximal 14.000 Feldschritte;
- keine Probe, Persistenz, Wiederholung oder Nachparametrierung;
- keine Ergebnisentscheidung waehrend des Laufs;
- unmittelbarer S1-FI-RAM-Preflight vor dem ersten Arm, sonst kein Teilstart.

## Erforderliche Besitzerentscheidung

Der technische Pfad ist antragsreif, aber nicht autorisiert. Eine Freigabe
muss exakt lauten:

```text
Ich gebe genau einen nicht persistenten S1-FK Formation-Capture-Lauf mit maximal 14.000 Feldschritten frei. Kein Retry, keine Nachparametrierung und keine Probe. Die Ausfuehrung darf nur starten, wenn der S1-FI-Preflight unmittelbar vor dem ersten Formation-Arm erneut vollstaendig besteht.
```

Ein allgemeines `ok weiter`, `weiter` oder eine sinngemaesse Kurzfassung ist
keine Freigabe.

## Bester naechster Schritt

Besitzerentscheidung zum exakt vorgelegten Einmallauftext abwarten. Bis dahin
keine echte Formation. Nach einer Freigabe genau einen Lauf ausfuehren und
Messwerte, technische Interpretation, Nichtnachweise und offene Annahmen
getrennt berichten.
