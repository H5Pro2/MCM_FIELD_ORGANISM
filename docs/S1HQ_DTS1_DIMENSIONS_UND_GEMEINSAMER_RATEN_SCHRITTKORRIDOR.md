# S1-HQ: DTS-1 Dimensions- und Rate-Schritt-Korridor

## Status

S1-HQ auditiert die Dimensionen der drei DTS-1-Raten und bindet einen
gemeinsamen technischen Rate-Schritt-Korridor. Es werden keine absoluten
Ratenwerte, keine Ratenordnung und kein positiver Unter- oder absoluter
Obergrenzwert fuer eine Materialrate gewaehlt. Keine Parameterschaetzung,
keine Feldrueckwirkung, keine Runtime und kein Lauf.

Entscheidung:

```text
DTS1_DIMENSIONS_AND_JOINT_RATE_STEP_CORRIDOR_BOUND_VALUES_OPEN
```

## Dimensionsbilanz

```text
q_i, f_i, b_e, u_e                 Ressource
x_e, y_e, z_e                      Ressource
p_e, alpha_bind, alpha_turn,
alpha_rec                          dimensionslos
k_bind, k_turn, k_rec              1 / Zeit
Delta_t, T                         Zeit
```

Die diskrete S1-HN-Abbildung haengt von den dimensionslosen Produkten ab:

```text
theta_bind = k_bind * Delta_t
theta_turn = k_turn * Delta_t
theta_rec  = k_rec  * Delta_t

alpha_x = 1 - exp(-theta_x)
```

Eine gemeinsame Skalierung aller Raten und inverse Skalierung der Zeit laesst
diese Produkte unveraendert. Ein Einzelschritt identifiziert daher keine
absolute Materialzeitskala. Physikalische Kontaktdauern und ihre Zeiteinheit
muessen vor jeder spaeteren Parameterschaetzung feststehen.

## Technischer und funktionaler Ratendomänenrand

Der technische Definitionsbereich umfasst alle endlichen nichtnegativen
Raten. Seine Nullraender sind verbindliche Kontrollen:

| Rand | Technische Bedeutung |
|---|---|
| `k_bind=0` | keine neue Bindung |
| `k_turn=0` | kein Umsatz von leitend zu refraktaer |
| `k_rec=0` | keine Freigabe aus refraktaer |
| alle Raten null | exakt statischer Ressourcenarm |
| `Delta_t=0` | exakte Identitaetsabbildung |

Ein spaeterer Test der vollstaendigen Dreirollenfunktion liegt dagegen nur im
offenen Inneren `k_bind>0`, `k_turn>0`, `k_rec>0`. S1-HQ setzt weder einen
positiven Mindestwert noch eine Ordnung wie `k_turn>k_rec` voraus.

## Gemeinsamer Aufloesungskorridor

Die S1-HN-Abbildung bleibt fuer jeden nichtnegativen dimensionslosen
Ratenanteil positiv und bilanziert. Sie benoetigt daher keine endliche
Stabilitaetsgrenze. Sehr grosse Anteile treiben `alpha_x` jedoch gegen eins
und machen zeitliche Rollenwechsel und groessere Raten unaufloesbar.

Fuer eine spaetere technische Intervallzerlegung wird deshalb global und
inhaltsfrei gebunden:

```text
alpha_step_max = 0.5

k_bind * Delta_t <= ln(2)
k_turn * Delta_t <= ln(2)
k_rec  * Delta_t <= ln(2)
```

Damit wechselt pro Subschritt hoechstens die Haelfte einer jeweiligen
Quellrolle. `0.5` ist ein fester technischer Aufloesungsdeckel, kein
Materialparameter und kein behauptetes Naturgesetz.

Fuer ein spaeteres abgeschlossenes physisches Intervall `T>0` lautet die
rein statische Zerlegungsregel:

```text
k_max = max(k_bind, k_turn, k_rec)
n = max(1, ceil(T * k_max / ln(2)))
Delta_t = T / n
```

Der letzte gleichfoermige Subschritt endet damit exakt an der geschlossenen
Intervallgrenze. Verfeinerung verwendet `n`, `2n` und `4n` bei identischem
physischen Eingang. Fuer `T=0` gilt direkt der Identitaetsarm ohne Subschritt.
S1-HQ implementiert weder Zerleger noch Runtime.

## Identifizierbarkeitsgrenze

Im positiven Inneren sind die Verhaeltnisse

```text
k_turn / k_bind
k_rec  / k_bind
```

dimensionslose Formgroessen. Die gemeinsame absolute Skala bestimmt nur die
Zeitlage relativ zu den fest vorgegebenen Kontaktdauern. Ein spaeterer
Parametersatz muss deshalb als ein globales Tripel ueber Abschwaechungs-,
Interferenz- und Erholungsarme gemeinsam gelten. Armweise passende Raten
sind unzulaessig.

Verboten bleiben insbesondere:

- Auswahl aus einem gewuenschten Feldprofil;
- modalitaets-, welt-, ziel-, label- oder verlaufsabhaengige Raten;
- Wechsel des Tripels zwischen Funktionsarmen;
- Verwendung der Schrittweite als angepasster Materialparameter;
- Erweiterung des Suchbereichs nach Kenntnis desselben Testergebnisses.

## Aussagegrenze

S1-HQ bindet nur Dimensionskonsistenz und numerische Aufloesung. Es zeigt
keinen geeigneten Materialparametersatz, keine Feldwirkung und keine
funktionale Trennung von Fixed Adapter, Leaky/Integrator, F3/CONST-V oder
schnellem Nachhall.

## Bester naechster Schritt

S1-HR darf nach dem naechsten `ok weiter` genau eine minimale ablatierbare
Rueckwirkungsfamilie von leitend gebundener Ressource auf bestehende
MCM-Kanten statisch auditieren. Ergebnis nur `ZULASSEN` oder `STOPP`; noch
keine Parameterwerte, Implementierung, Runtime oder Feldlauf.
