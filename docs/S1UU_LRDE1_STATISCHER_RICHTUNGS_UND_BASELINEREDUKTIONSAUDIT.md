# S1-UU: Statischer Richtungs- und Baselinereduktionsaudit fuer LRD-E1

## Auftrag und Grenze

S1-UU prueft die in S1-UT vorgeschlagene Korrektur des lokalen
Ursachenvertrags. Die diskreten Begriffe Einpendeln, Ueberschwingen und
feldnahe Ruhe werden nicht wiedereroeffnet.

Geprueft wird nur, ob eine kontinuierliche lokale Richtungsrelation aus den
bereits vorhandenen atomaren Feldendpunkten vollstaendig, schwellenfrei und
kausal verzoegert formulierbar ist und wie sie gegen die engsten Baselines
einzuordnen ist.

Es werden keine Gleichung, konkrete Distanzfunktion, Parameter,
Implementierung, Tests, Runtime, Snapshotaenderung oder Feldlaeufe
eingefuehrt oder ausgefuehrt.

## Korrigierte lokale Ursachenrolle

Fuer einen Feldort wird nur die Aenderung seiner lokalen Entfernung von der
festen Neutralreferenz zwischen abgeschlossenem `S_pre` und abgeschlossenem
`S_next` betrachtet. Die Rolle ist nur bei eindeutig fehlendem aktuellem
lokalem Rezeptorkontakt zulaessig.

Die kontinuierliche Ursachenrolle besitzt drei Vorzeichenfaelle, aber keine
drei diskreten Ereignistypen:

1. Die Entfernung wird kleiner: positiver Rueckfuehrungsbeitrag.
2. Die Entfernung wird groesser: negativer Rueckfuehrungsbeitrag.
3. Die Entfernung bleibt gleich: kein gerichteter Beitrag.

Die spaetere Beitragshoehe muss stetig mit der gemessenen
Entfernungsanderung gegen Null gehen. Eine beliebig kleine numerische
Aenderung darf deshalb keinen vollen Klassenimpuls ausloesen. Eine konkrete
Abbildung oder Skalierung bleibt ungebunden.

## Vollstaendigkeit und Eindeutigkeit

Die korrigierte Rolle besteht den statischen Berechenbarkeitsaudit:

- Sie liest nur `S_pre`, `S_next`, Neutralreferenz und Kontaktstatus.
- Kleiner, groesser und gleich sind gegenseitig ausschliessend und
  vollstaendig.
- Ein Vorzeichenwechsel von `S` benoetigt keine Sonderdeutung; massgeblich
  ist nur die Nettoaenderung der Entfernung zur Neutralreferenz.
- Eine Ruhe- oder Naeheschwelle wird nicht benoetigt.
- Nachbarfluss darf die lokale Bewegung mitverursachen, weil die Rolle nur
  die abgeschlossene lokale Feldfortsetzung und keine isolierte Eigenkraft
  behauptet.
- `H` bleibt Pflichtkontrolle des schnellen Vorzustands, ist aber keine
  Quelle der Richtungsrolle.

Damit werden die S1-UT-Luecken geschlossen, ohne K2 oder K3 umzubenennen.

## Kausale Ordnung und Dissipation

Die atomare Ordnung aus S1-US bleibt erhalten:

```text
abgeschlossener Feld- und Dispositionsvorzustand
-> normaler Feldfolgezustand unter der bisherigen Disposition
-> passiver lokaler Richtungsbeitrag aus dem abgeschlossenen Feldschritt
-> neuer privater Dispositionszustand
-> Wirkung fruehestens im folgenden Feldschritt
```

Die Disposition muss in jedem Schritt stetig zur eigenen Neutralreferenz
dissipieren. Die Dissipation ist keine dritte Ereignisklasse und benoetigt
weder Feldruhe noch eine Sonderphase. Bei aktuellem Rezeptorkontakt entsteht
kein Richtungsbeitrag; nur die allgemeine Dissipation darf fortgesetzt
werden.

## Abschwaechung, Interferenz und Wiederbeanspruchung

- **Abschwaechung:** Allgemeine Dissipation reduziert eine nicht neutrale
  Disposition ohne Loeschsignal oder Ruheklassifikation.
- **Interferenz:** Kontaktfreie Geschichten mit kleiner und groesser
  werdender Neutralentfernung wirken auf denselben skalaren Zustand in
  entgegengesetzte Richtungen.
- **Kapazitaetsfreigabe:** Dissipative Rueckkehr stellt Abstand zur endlichen
  Zustandsgrenze wieder her; ein separates Ressourcenledger existiert nicht.
- **Wiederbeanspruchung:** Nach Rueckkehr muss dieselbe lokale Rolle erneut
  auf normale kontaktfreie Feldfortsetzung reagieren koennen.

Diese Rollen bleiben auf einen skalaren Engineeringzustand begrenzt. Sie
tragen keine getrennten Inhalte, Pfade oder Episoden.

## Reduktion gegen die staerksten Baselines

Die korrigierte Form erzeugt keine neue Mechanikklasse:

| Baseline | Ergebnis |
|---|---|
| unveraendertes `S/H` | besitzt keinen zusaetzlichen langsamen Dispositionszustand |
| Fixed Adapter | kann geschichtsabhaengige A/B-Unterschiede nicht allein tragen |
| passive Leaky-Spur der Rueckfuehrungsbewegung | kann denselben langsamen Zustand tragen, wirkt allein aber nicht auf die Feldtransition zurueck |
| Leaky-Spur mit festem Zustandsleser auf Rueckfuehrungs-Gain | ist funktional eine vollstaendige Rekonstruktion |
| zustandsabhaengige Mobilitaet / adaptiver Gain | ist die bereits gebundene Mechanikklasse von LRD-E1 |
| F3 / Zweizustandsrekurrenz | ist breiter als der einzelne skalare Engineeringtraeger |

Sobald eine Leaky-Spur auf einen festen Rueckfuehrungsleser gekoppelt wird,
ist der Unterschied zu LRD-E1 nur noch Benennung und Parametrisierung. Eine
nicht baseline-reduzierbare Gegenprognose verbleibt daher nicht.

Das verbindliche wissenschaftliche Ergebnis lautet:

```text
LRD_EFFECT_EXPLAINED_BY_BASELINE
```

## Engineeringgrenze

S1-UQ und S1-UR erlauben nach offener Baselinegleichheit weiterhin die
Untersuchung einer technisch nuetzlichen, stabilen und
MCM-schnittstellenkompatiblen Rueckfuehrungsfunktion. S1-UU bestaetigt dafuer
lediglich eine statisch zulassungsfaehige Ursachenrolle.

Ein spaeteres Engineeringmodul muesste offen als leaky getriebener adaptiver
Rueckfuehrungs-Gain bezeichnet werden. Es duerfte weder als neue Feldursache
noch als eigenstaendige Mechanik der hypothetischen technischen
MCM-Memory-Entwicklungsrichtung interpretiert werden.

Ob dieser bekannte Mechanismus gegenueber vorhandenen Engineeringbausteinen
einen zusaetzlichen praktischen Nutzen besitzt, ist noch nicht entschieden.
Ohne einen vorab benannten Nutzen darf keine Mathematik oder Implementierung
folgen.

## Fail-closed-Regeln

Die korrigierte Linie wird gestoppt, wenn:

- eine konkrete Distanzrolle nicht lokal, endlich und neutralreferenziert
  ist;
- ein Richtungsbeitrag bei aktuellem lokalem Rezeptorkontakt entsteht;
- numerische Nullnaehe durch eine diskrete Vollreaktion verstaerkt wird;
- die neue Disposition im selben Feldschritt zurueckwirkt;
- Dissipation eine Ruhe-, Loesch- oder Versuchsphase benoetigt;
- ein behaupteter Nutzen bereits durch den unveraenderten Feldkern oder
  einen vorhandenen privaten Baselineadapter bereitgestellt wird;
- aus der Engineeringreduktion ein Neuheitsclaim oder eine vorhandene
  MCM-Memory-Funktion abgeleitet wird.

## Verbindliche Entscheidung

```text
S1_UU_DISCRETE_K1_K2_K3_NOT_REOPENED
S1_UU_CONTINUOUS_LOCAL_NEUTRAL_DISTANCE_CHANGE_ADMISSIBLE
S1_UU_THRESHOLD_FREE_AND_ENDPOINT_COMPUTABLE
S1_UU_UNIVERSAL_DISSIPATION_REPLACES_QUIESCENCE_CLASS
S1_UU_ONE_STEP_CAUSAL_DELAY_RETAINED
S1_UU_EXPLAINED_BY_LEAKY_DRIVEN_ADAPTIVE_GAIN_BASELINE
S1_UU_ENGINEERING_USEFULNESS_NOT_YET_ESTABLISHED
S1_UU_NO_EQUATION_NO_PARAMETERS_NO_RUNTIME_NO_EXECUTION
```

## Bester naechster Schritt

S1-UV darf ausschliesslich als statischer Engineering-Nutzenaudit genau eine
Frage entscheiden: Welche konkrete MCM-Feldkernfunktion wuerde ein privat
gekoppelter, leaky getriebener Rueckfuehrungs-Gain bereitstellen, die der
heutige Feldkern und die bereits vorhandenen privaten Baselineadapter noch
nicht bereitstellen?

Vor einer Antwort werden keine Gleichung, Parameter, Implementierung, Tests
oder Feldlaeufe zugelassen. Wenn kein eigener praktischer Nutzen mit einer
vorab beobachtbaren technischen Abnahme benannt werden kann, wird LRD-E1
vollstaendig geschlossen.

## Projektgrundlagen

- [S1-UT Berechenbarkeitsaudit](S1UT_LRDE1_STATISCHER_BERECHENBARKEITSAUDIT.md)
- [S1-US lokaler Kausal- und Lebenszyklusvertrag](S1US_LRDE1_LOKALER_KAUSAL_UND_LEBENSZYKLUSVERTRAG.md)
- [S1-UR Anatomie- und Baselinekollisionsaudit](S1UR_LRD1_ANATOMIE_BEGRENZUNGS_UND_BASELINEKOLLISIONSAUDIT.md)
- [S1-UQ Funktions- und Falsifikationsvertrag](S1UQ_FUNKTIONS_UND_FALSIFIKATIONSVERTRAG_LOKALE_RUECKFUEHRUNGSDISPOSITION.md)
