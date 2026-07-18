# Befund 031: Lokale Feldfolgen-Inertheit

## Ergebnis

Methodik 027 wurde über eine kontrollierte Parameterfamilie ausgeführt:

```text
3 Kontaktamplituden
x 3 feste Nachhallzeitkonstanten
x 3 Pausenlängen
= 27 gespiegelte Parameterpaare
= 54 Zweigbeobachtungen
```

Für jedes Paar trugen Vorwärts- und Rückwärtszweig:

- exakt denselben vorherigen Zentrumzustand,
- exakt denselben aktuellen Rezeptorkontakt,
- verschiedene vollständige lokale Wahrnehmungen,
- entgegengesetzte räumliche Orientierung,
- dieselbe technische Zeitlage.

## Übergangsergebnis

Die beiden vorhandenen Übergänge erzeugten in allen 27 Paaren identische
Aktivierungs- und Nachhallausgaben:

```text
Hold:
maximale Aktivierungsdifferenz = 0.0
maximale Nachhalldifferenz     = 0.0

Rezeptorprojektion:
maximale Aktivierungsdifferenz = 0.0
maximale Nachhalldifferenz     = 0.0
```

Reihenfolge, Wiederholung und passiver Observer veränderten das Ergebnis nicht.
Der exakte Reset entfernte Orientierung und Ausgangszustand vollständig.

Der kanonische Gesamtdigest lautet:

```text
aa59b055f15f05fcb624e8048e181077df502d65e7759d3578b468f62459b8eb
```

## Provenienzkorrektur

Die vollständigen Digests der nächsten `MCMNeuron`-Zustände blieben zwischen
den Spiegelzweigen verschieden. Das ist kein Widerspruch zum Nullbefund.

Das Neuron bewahrt seine aktuelle `perception` als technische Herkunft:

```text
verschiedene lokale Feldproben
→ verschiedene Wahrnehmungsprovenienz
→ verschiedene vollständige Neuron-Digests
```

Die eigentlichen Übergangsausgaben blieben dennoch gleich:

```text
gleiche nächste Aktivierung
+ gleicher nächster Nachhall
```

Damit wurde Provenienz nicht fälschlich als Feldwirkung ausgegeben.

## Interpretation

Die Architektur führt lokale Feldinformation kausal und zeitlich korrekt bis
an jedes MCM-Neuron. Der passive Observer kann die räumliche Asymmetrie lesen.

Keiner der vorhandenen Übergänge verwendet diese Information jedoch für die
nächste Aktivierung oder den nächsten Nachhall.

Der bestätigte Funktionsmangel lautet:

> Lokale Feldgeschichte erreicht das Neuron und bleibt als Wahrnehmungsquelle
> unterscheidbar, ist für die Bildung des nächsten schnellen Feldzustands aber
> kausal inert.

## Stärkstes Gegenargument

Das Ergebnis folgt unmittelbar aus den Definitionen:

- `hold_state_baseline` liest nur den vorherigen Eigenzustand.
- `receptor_projection_baseline` liest nur den aktuellen Rezeptorkontakt.

Der Versuch entdeckt keine unerwartete Dynamik. Er lokalisiert die offene
Kausalgrenze exakt zwischen `MCMNeuronDrive` und `MCMNeuronOutput`.

## Nicht gezeigt

Nicht gezeigt ist:

- dass eine Feldreaktion benötigt wird,
- in welche Richtung eine Feldlage wirken sollte,
- dass vergangene Bewegung fortgesetzt werden sollte,
- dass Diffusion oder Rekurrenz unzureichend wären,
- dass eine neue Feldvariable benötigt wird,
- dass räumliche Orientierung Bedeutung besitzt,
- dass Organisation, Lernen oder Feldintelligenz vorliegt.

## Evidenz

```text
räumliche Feldinformation erreicht das Neuron: E2
passive lokale Lesbarkeit:                       E2
kausale Inertheit unter vorhandenen Übergängen:  E1
eigenständige lokale Feldfolge:                  E0
organische Feldorganisation:                     E0
Feldintelligenz:                                 E0
```

## Stopplinie

Der Befund gibt nicht frei:

- Orientierung als Aktivierungsbefehl,
- Bewegungsfortsetzung,
- Diffusion oder Nachbarmittelung,
- feste Rekurrenz,
- Impuls- oder Spannungsvariable,
- adaptive Kopplung,
- Rezeptorselbstregulation,
- Handlung oder Semantik.

## Bester nächster Schritt

Vor einer Übergangsregel muss eine konkrete Weltfunktion benannt werden:

```text
Welche beobachtbare Leistung fehlt,
obwohl lokale Feldgeschichte bereits lesbar ist?
```

Diese Leistung muss gegen Projektion, unabhängigen Nachhall, festen Puffer,
Rekurrenz, Diffusion und eine direkte feste Abbildung der räumlichen
Asymmetrie bestehen. Erst danach darf ein Feldmechanikkandidat formuliert
werden.
