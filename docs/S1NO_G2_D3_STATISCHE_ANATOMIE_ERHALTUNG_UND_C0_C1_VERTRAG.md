# S1-NO G2/D3 statische Anatomie, Erhaltung und C0/C1-Vertrag

## Status

S1-NO bindet ausschliesslich die statische Einkantenanatomie der in S1-NN
ausgewaehlten Darstellung
`G2_CONSERVATIVE_BOUND_SUBPARTITION`. Der Schritt enthaelt keine Transfer-,
Bildungs-, Abschwaechungs- oder Admissibilitaetsgleichung, keine Parameter,
Runtime, Feldrueckwirkung oder Ausfuehrung.

Entscheidung:

```text
G2_D3_SINGLE_EDGE_ANATOMY_CONSERVATION_AND_C0_C1_BOUND
```

## Anatomieeinheit

S1-NO gilt fuer genau eine kanonische lokale Kante:

```text
edge_id
first_carrier_id
second_carrier_id
capacity
free
bound_unconfigured
bound_configured
blocked
```

`edge_id` und beide Traegerkennungen muessen nichtleer und vorregistriert
sein. Die Endpunkte sind kanonisch geordnet und verschieden. Mehrkanten-,
Nachbarschafts- und globale Zustandsrollen bleiben fuer diesen Schritt
gesperrt.

## Gespeicherte Ressourcenrollen

Die D3-Anatomie speichert genau vier disjunkte nichtnegative Betraege:

| Rolle | Technische Bedeutung |
|---|---|
| `free` | aktuell nicht gebundene lokale Ressource |
| `bound_unconfigured` | gebundener Anteil ohne G2-Konfigurationsbelegung |
| `bound_configured` | gebundener Anteil mit G2-Konfigurationsbelegung |
| `blocked` | aktuell nicht direkt bindbare lokale Ressource |

`bound_configured` speichert keine Eingabe, Reihenfolge oder Bedeutung. Die
Rolle bezeichnet nur einen technisch getrennten Teil derselben gebundenen
Ressource.

Nicht gespeichert werden:

- ein zusaetzlicher Gesamtbetrag `bound`;
- freie Reserve ausserhalb von `capacity`;
- S/H, Adapter, Gain, Leaky- oder Integratorzustand;
- Rohdaten, Ereignisse, Sequenzen, Labels, Reward oder Readoutwerte.

## Abgeleitete Aggregation

Die bisherige Dreirollenoberflaeche wird ausschliesslich abgeleitet:

```text
bound = bound_unconfigured + bound_configured

aggregate_ledger = (free, bound, blocked)
```

Ein zusaetzlich gespeicherter `bound`-Wert waere eine zweite
widerspruechliche Bilanzquelle und ist unzulaessig.

## Lokale Erhaltungsidentitaet

Fuer jeden gueltigen D3-Zustand gilt exakt:

```text
capacity
= free
+ bound_unconfigured
+ bound_configured
+ blocked
```

Durch Aggregation folgt exakt die bestehende KFS-1-Identitaet:

```text
capacity = free + bound + blocked
```

Alle Betraege und `capacity` sind endlich. `capacity` ist positiv, alle vier
Ressourcenrollen sind nichtnegativ. Es gibt kein Clipping, keine
Nachnormalisierung und keine Reparatur.

## Gebundener F1-Vorzustand

Beide S1-NM-Arme verwenden dieselbe Kapazitaet und dasselbe aggregierte
Ledger:

```text
capacity = 1.0
free = 0.5
bound = 0.5
blocked = 0.0
```

Die G2-Unterteilung ist der einzige Unterschied.

### C0

```text
arm_id = F1_G2_C0
free = 0.5
bound_unconfigured = 0.5
bound_configured = 0.0
blocked = 0.0
```

### C1

```text
arm_id = F1_G2_C1
free = 0.5
bound_unconfigured = 0.0
bound_configured = 0.5
blocked = 0.0
```

Die beiden Extremunterteilungen sind dyadische technische Fixturewerte. Sie
sind keine Materialparameter und behaupten keine spaetere natuerliche
Bildung. Zwischenzustaende mit beiden positiven Unterrollen bleiben
anatomisch zulaessig, werden in S1-NO aber nicht als Fixture ausgewaehlt.

## Projektionsidentitaet zu Gegenbaselines

C0 und C1 muessen unter der reinen Aggregation bitgleich projizieren:

```text
project(C0) = project(C1) = (free=0.5, bound=0.5, blocked=0.0)
```

DTS-1 und T1 erhalten ausschliesslich diese aggregierte Projektion. Die
G2-Unterrollen duerfen weder in ihre Zustandsobjekte noch in ihre Adapter
gelangen.

Damit bleibt ihre S1-NM-Gegenprognose fuer beide Arme identisch. Diese
Projektionsidentitaet ist eine Anatomieeigenschaft und noch keine
Ausfuehrung.

## Statische G2-Ablation

Die reine D3-Ablation ist als anatomische Projektion gebunden:

```text
ablate(free, bound_unconfigured, bound_configured, blocked)
= (
    free,
    bound_unconfigured + bound_configured,
    0.0,
    blocked,
  )
```

Sie erhaelt Kapazitaet und aggregiertes Dreirollenledger exakt. Fuer den
F1-C1-Fixturezustand gilt:

```text
ablate(C1) = C0
```

Die Ablation ist keine Dynamik und kein Loesungsprozess. Sie dient nur dem
spaeteren kausalen Vergleich, indem sie ausschliesslich die zusaetzliche
Unterteilung entfernt.

## Anatomische Nullfaelle

Verbindlich gelten:

- Bei `bound=0` sind `bound_unconfigured=0` und `bound_configured=0`.
- Bei `bound_configured=0` bleibt die Anatomie gueltig, sofern die
  Gesamtidentitaet gilt.
- Bei `bound_unconfigured=0` bleibt die Anatomie gueltig, sofern die
  Gesamtidentitaet gilt.
- Bei `free=0` oder `blocked=0` bleibt die Anatomie gueltig, sofern alle
  uebrigen Rollen endlich, nichtnegativ und erhalten sind.
- `capacity=0` ist ungueltig.

## Verbotene Zustaende

Fail-closed ungueltig sind:

- leere, gleiche oder nichtkanonische Traegerkennungen;
- eine Kantenkennung, die nicht eindeutig zu den gebundenen Endpunkten
  gehoert;
- boolesche, negative oder nicht endliche Kapazitaets- oder Rollenwerte;
- nichtpositive Kapazitaet;
- jede Verletzung der Vierrollen-Erhaltungsidentitaet;
- redundant gespeichertes aggregiertes `bound`;
- jede externe Projektion, deren angegebener `bound`-Wert von
  `bound_unconfigured + bound_configured` abweicht;
- positive Unterrollen bei aggregiertem `bound=0`;
- versteckte Reserve, zweite Kapazitaet oder globale Ausgleichsrolle;
- S/H-, Adapter-, Baseline-, Rohdaten-, Sequenz- oder Readoutinhalt;
- stille Reparatur, Clipping oder Nachnormalisierung;
- Mehrkanten- oder Nachbarschaftszustand im F1-Einkantenrecord.

## Erlaubte Anatomietests

S1-NO erlaubt spaeter ausschliesslich Tests fuer:

- eindeutige Einkantenidentitaet;
- positive endliche Kapazitaet und vier nichtnegative Unterrollen;
- exakte Vierrollen- und aggregierte Dreirollenerhaltung;
- bitgleiche C0/C1-Aggregation;
- exakte Ablation `C1 -> C0`;
- gueltige reine C0-, reine C1- und gemischte Unterteilungen;
- gebundenen Nullfall bei `bound=0`;
- Fail-Closed-Verhalten fuer alle verbotenen Zustaende;
- Abwesenheit von Feld-, Runtime-, I/O- und Baselinezustand.

Nicht erlaubt sind Admissibilitaets-, Transfer-, Bildungs-, Abschwaechungs-,
Interferenz- oder Feldwirkungstests.

## Aussagegrenze

S1-NO bindet nur Anatomie, Projektion, Ablation und Erhaltung. Die Existenz
zweier gueltiger Unterteilungen zeigt keine kausale Wirkung. Es gibt keine
G2-Dynamik, keine Feldwirkung, keine Lernfunktion und keinen Befund zur
hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-NP darf ausschliesslich einen statischen Schema-, Digest- und
Fail-Closed-Validatorvertrag fuer genau diese Einkantenanatomie binden. Er
darf die erlaubten Anatomietests maschinenlesbar festlegen, aber noch keinen
Validator implementieren oder ausfuehren.

Transfer-, Admissibilitaets-, Bildungs- und Feldgleichungen bleiben gesperrt.
