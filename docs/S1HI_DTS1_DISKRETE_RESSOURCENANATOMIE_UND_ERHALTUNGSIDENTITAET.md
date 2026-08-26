# S1-HI: DTS-1 diskrete Ressourcenanatomie und Erhaltungsidentitaet

## Status

Anatomie- und Bilanzvertrag fuer den in S1-HH gebundenen Kandidaten. Die in
der Freigabe verwendete Kurzform D1 bezeichnet hier ausschliesslich den
aktuellen Kandidaten `DTS-1`; `D1` bleibt im Projekt eine historische
W7-Kennung.

Keine Dynamikgleichung, keine Rate, kein Parameterkorridor, keine Runtime,
keine Feldkopplung, kein Lauf und kein Funktions- oder Faehigkeitsbefund.

Entscheidung:

```text
DTS1_DISCRETE_RESOURCE_ANATOMY_AND_LOCAL_IDENTITY_BOUND
```

## Vorhandene Geometrie

DTS-1 verwendet nur das vollstaendige vorhandene ungerichtete
MCM-Kanteninventar. Jede Kante erscheint genau einmal in kanonischer Ordnung.
Selbstkanten, doppelte Kanten, unbekannte Endpunkte und unvollstaendige
Inventare sind ungueltig. DTS-1 erzeugt keine Kante und speichert keine
Eingangsinhalte.

## Gespeicherte Anatomie

Jeder vorhandene Feldknoten `i` besitzt eine feste positive Kapazitaet `q_i`.
Sie ist Anatomie und kein veraenderlicher Laufparameter.

Jede vorhandene ungerichtete Kante `e = {i,j}` besitzt genau zwei
nichtnegative gespeicherte Ressourcenwerte:

```text
b_e = leitend gebundener Anteil
u_e = refraktaerer Anteil
```

Damit sind die beiden kantenbezogenen Rollen eindeutig. Die dritte Rolle
`frei` wird nicht pro Kante gespeichert, weil benachbarte Kanten die lokale
Kapazitaet ihres gemeinsamen Endpunkts beanspruchen. Eine zusaetzlich
gespeicherte freie Ressource wuerde eine zweite widerspruechliche Bilanzquelle
erzeugen und ist deshalb verboten.

## Abgeleitete freie Ressource

Jede Kantenressource wird an ihren beiden Endpunkten mit je einem halben Anteil
bilanziert. Fuer jeden Knoten wird freie Ressource nur als Rest abgeleitet:

```text
f_i = q_i - 0.5 * Summe(b_e + u_e fuer alle an i inzidenten Kanten e)
```

Ein gueltiger Zustand verlangt `f_i >= 0` an jedem Knoten. Es gibt kein
Clipping, keine Nachnormierung und keine Reparatur eines ueberbelegten
Zustands.

## Lokale und globale Erhaltungsidentitaet

Fuer jeden Knoten gilt konstruktiv:

```text
q_i = f_i + 0.5 * Summe(b_e + u_e fuer alle an i inzidenten Kanten e)
```

Durch Summation ueber alle Knoten folgt, weil jede ungerichtete Kante genau
zwei Endpunkte besitzt:

```text
Q = Summe(q_i)
  = Summe(f_i) + Summe(b_e) + Summe(u_e)
```

Dies sind Zustandsidentitaeten und keine Bewegungs- oder Wirkungsgleichungen.
S1-HI legt nicht fest, ob, wann oder wie Ressource spaeter ihre Rolle wechselt.

## Ungueltige Zustaende

Fail-closed verworfen werden:

- leere oder doppelte Knotenkennungen;
- nichtpositive oder nichtendliche Knotenkapazitaet;
- leere, doppelte, nichtkanonische oder selbstbezogene Kanten;
- Kantenendpunkte ausserhalb des Knotenbestands;
- negative oder nichtendliche Werte fuer `b_e` oder `u_e`;
- jede lokale Belegung oberhalb von `q_i`;
- redundant gespeicherte freie Ressource;
- S, H, Adapter, Gain, Integratorzustand oder Replayinhalt im DTS-1-Container;
- Clipping, Nachnormierung oder stille Reparatur einer Verletzung.

## Strukturelle Abgrenzung

| Vergleich | Reine Anatomiedifferenz |
| --- | --- |
| Fixed Adapter | feste Kantenkoeffizienten ohne endliches Dreirollenledger |
| Gain | Antwortskalierung ohne erhaltene Aufteilung frei/gebunden/refraktaer |
| schneller Nachhall H | Teil des schnellen S/H-Feldzustands, kein Kantenressourcenkompartiment |
| Integrator | Signalakkumulation ohne aus einer Kantenbilanz abgeleitete freie Kapazitaet |
| Replay | gespeicherter Eingangsinhalt statt inhaltsfreier lokaler Ressourcenbetraege |

Diese Unterschiede beweisen keine Funktion. Insbesondere zeigt S1-HI weder
Abschwaechung noch Interferenz, Freigabe, Wiederbeanspruchung oder
Feldrueckwirkung.

## Technische Abnahmegrenze

Die Tests duerfen nur pruefen:

- eindeutige Knoten- und Kantenanatomie;
- drei Rollen bei nur zwei gespeicherten Kantenwerten und abgeleitetem `f_i`;
- lokale und globale Bilanzidentitaet;
- Ablehnung negativer, nichtendlicher, ueberbelegter oder strukturell
  unvollstaendiger Zustaende;
- strukturelle Trennung von Baselineklassen;
- geschlossene Gleichungs-, Runtime-, Feld- und Claimgrenzen.

## Bester naechster Schritt

S1-HJ darf erst nach einem weiteren `ok weiter` genau die zulaessigen lokalen
Rollenwechsel und ihre Kausalquellen auf Vertragsniveau binden. Noch keine
Raten, keine diskrete oder kontinuierliche Dynamikgleichung, keine
Feldrueckwirkung und kein Lauf.
