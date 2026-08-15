# S1-HM: DTS-1 statischer Transfergesetzfamilien-Audit

## Status

Genau eine symbolische Transfergesetzfamilie wurde gegen S1-HH bis S1-HL und
die historischen Baseline-Stopplinien geprueft. Keine Parameterwerte, kein
diskreter Integrator, keine Konfliktloesung, keine Feldrueckwirkung, keine
Runtime und kein Lauf.

Entscheidung:

```text
ZULASSEN_DTS1_THREE_COMPARTMENT_ENGINEERING_FAMILY
```

`ZULASSEN` bedeutet nur: Die Familie darf als offen konstruierte technische
Materialhypothese isoliert weiter spezifiziert und falsifiziert werden. Sie ist
keine neue MCM-Natur und kein Funktionsbefund.

## Eine gepruefte Familie

```text
LOCAL_BOUNDED_THREE_COMPARTMENT_TURNOVER
```

Fuer jede vorhandene Kante werden drei nichtnegative, global homogene und
inhaltsfreie Ratensymbole mit Einheit `1/Zeit` verwendet. Ihre Werte bleiben
offen:

```text
k_bind, k_turn, k_rec >= 0
```

Die einzige auditierte Flussfamilie lautet symbolisch:

```text
J_bind = k_bind * p_e * 2 * min(f_i, f_j)
J_turn = k_turn * b_e
J_rec  = k_rec  * u_e
```

und die einzige Zustandsbilanz:

```text
d b_e / dt = J_bind - J_turn
d u_e / dt = J_turn - J_rec
d f_i / dt = -0.5 * Summe(J_bind - J_rec fuer inzidente Kanten)
```

Diese Gleichungen werden in S1-HM nicht integriert oder ausgefuehrt.

## Abgleich S1-HH bis S1-HL

- `J_bind` verwendet nur S1-HK-Observable und freie Endpunktressource.
- `J_turn` realisiert nur `gebunden -> refraktaer` auf derselben Kante.
- `J_rec` realisiert nur `refraktaer -> frei` auf derselben Kante.
- alle Fluesse besitzen Einheit Ressource/Zeit;
- alle in S1-HL geforderten Quellnullen bestehen;
- bei `f_i=0`, `b_e=0` oder `u_e=0` zeigen die jeweiligen kontinuierlichen
  Randfluesse nicht aus dem zulaessigen Bereich;
- Umsatz hebt sich zwischen `b_e` und `u_e` aus der Gesamtbilanz heraus;
- Bindung und Erholung aendern freie Endpunktanteile mit der S1-HI-Halbbilanz.

Ein spaeterer diskreter Integrator muss diese Eigenschaften konstruktiv
erhalten. Clipping oder Nachnormierung bleiben unzulaessig.

## Eigene technische Gegenprognose

Zwei Zustaende koennen identisches S, H, `b_e` und dieselbe Gesamtressource,
aber unterschiedliche Aufteilung von `f_i,f_j` gegen `u_e` besitzen. Dann ist
`J_bind` verschieden, obwohl ein aus `b_e` gebildeter Fixed Adapter identisch
waere.

Das ist eine strukturelle Gegenprognose fuer einen spaeteren isolierten Test.
Sie ist noch nicht numerisch oder funktional bestaetigt. Ein zweistufiges E1
besitzt bei festem `b_e` keine unabhaengige refraktaere Aufteilung.

## Historische Stopplinie

Die fruehere Refraktaer-/Erschoepfungsrolle wurde zu Recht verworfen, weil ihr
eine Stoff-, Energie- oder Kapazitaetsbilanz fehlte und sie nur als
Integrator/Leaky-Spur mit festem Leser erschien. S1-HI liefert nun ein
explizites endliches Ressourcenledger. Die Benutzerfreigabe setzt DTS-1 offen
als technische Materialhypothese.

Damit ist nur die damalige Bilanz- und Freigabeluecke fuer einen
Engineeringtest geschlossen. Eine intrinsische Herleitung aus dem bisherigen
MCM-Feld liegt weiterhin nicht vor. Die Familie bleibt bekannte
Drei-Kompartiment-Kinetik und besitzt keinen Neuheitsclaim.

## Weiter aktive Baselines und STOPP-Bedingungen

Verbindlich bleiben Fixed Adapter, zweistufiges E1, Leaky/Integrator,
F3/CONST-V und schneller Nachhall. DTS-1 wird spaeter gestoppt, wenn unter
anderem:

- eine registrierte Leaky-/Integratorbaseline alle Pflichtprofile erklaert;
- frei gegen refraktaer die spaetere Bindung nicht unterscheidet;
- ein Fixed Adapter die vollstaendige dynamische Probe reproduziert;
- Bilanz oder Nichtnegativitaet Clipping oder Nachnormierung benoetigt;
- die Feldrueckwirkung fuer das gewuenschte Ergebnis zugeschnitten werden
  muesste;
- Labels, Zaehler, Phasen oder inhaltsspezifische Regeln erforderlich werden.

## Aussagegrenze

S1-HM laesst eine bekannte technische Familie fuer isolierte weitere Pruefung
zu. Nicht gezeigt sind numerische Stabilitaet, Ressourcenwechsel,
Abschwaechung, Interferenz, Freigabe, Wiederbeanspruchung oder Wirkung auf das
MCM-Wahrnehmungsfeld.

## Bester naechster Schritt

S1-HN darf nach dem naechsten `ok weiter` einen positivity- und
bilanzwahrenden diskreten Integrationsvertrag fuer diese eine Familie
auswaehlen. Noch keine Parameterwerte, keine Implementierung, keine
Feldrueckwirkung und kein Lauf.
