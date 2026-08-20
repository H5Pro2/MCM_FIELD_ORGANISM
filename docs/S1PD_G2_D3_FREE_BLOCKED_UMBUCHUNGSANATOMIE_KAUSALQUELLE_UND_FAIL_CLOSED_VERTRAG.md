# S1-PD G2/D3 Free/Blocked-Umbuchungsanatomie, Kausalquelle und Fail-Closed-Vertrag

## Status und Umfang

S1-PD bindet ausschliesslich die Anatomie der in S1-PC ausgewaehlten
Zweiarm-Intervention. Der Schritt legt Kausalquelle, Rollen, atomare
Paargrenze, Erhaltungsbedingungen, ungueltige Zustaende und Fehlerrollen fest.

Nicht gebunden werden konkrete Ressourcenwerte, Wirkungsgleichung,
Bindungsdynamik, Schemaimplementierung, Digestwerte, Test oder Ausfuehrung.
Der technische Kern bleibt das MCM-Wahrnehmungsfeld.

Entscheidung:

```text
G2_D3_FREE_BLOCKED_PAIRED_INTERVENTION_ANATOMY_BOUND
```

## Zulaessige Kausalquelle

Die Umbuchung darf ausschliesslich durch eine vorregistrierte externe
Testintervention ausgeloest werden. Sie liegt zwischen einem vollstaendig
validierten gemeinsamen D3-Vorzustand und dem spaeteren identischen frischen
Bindungsereignis.

Die Intervention ist eine kontrollierte unabhaengige Variable. Sie ist keine
Feldwirkung, keine D3-Eigenaenderung und keine Ausgabe des vorhandenen
Fortsetzungsoperators. Ihre Richtung und Paarzuordnung muessen vor O3-Readout
und vor jedem Nachereignis feststehen.

Als Kausalquelle sind verboten:

- der unmittelbare oder spaetere O3-Readout;
- eine Feldantwort oder ein Baselineergebnis;
- Armresultate, Nachzustandswerte oder Fehlerausgaenge;
- Zufall ohne vorregistrierte und reproduzierbare Zuordnung;
- der bestehende D3-Fortsetzungsoperator;
- nachtraegliche Reparatur oder Ergebnisanpassung.

## Gemeinsamer Vorzustand

Beide Arme muessen vom selben unveraenderten, bereits gueltigen
D3-Vorzustand derselben Kante abgeleitet werden. Identisch bleiben:

- Kanten-ID, Traeger und Geometrie;
- Feldreferenz und kausale Vorzustandsreferenz;
- `capacity`;
- `bound_unconfigured`;
- `bound_configured`;
- `free` und `blocked` vor der Intervention.

Der Vorzustand muss ausreichende positive Ressource in `free` und `blocked`
besitzen, damit beide entgegengesetzten Umbuchungen ohne Klemmen oder
Ergaenzung moeglich sind. Ein konkreter Betrag wird in S1-PD nicht gewaehlt.

## Exakt zwei Interventionsrollen

Das Paar besitzt genau zwei Rollen:

```text
FREE_AVAILABLE
BLOCKED_HELD
```

`FREE_AVAILABLE` bucht einen spaeter exakt zu bindenden endlichen Betrag
atomar von `blocked` nach `free` um.

`BLOCKED_HELD` bucht denselben Betrag atomar von `free` nach `blocked` um.

Der Betrag muss in einem spaeteren Vertrag positiv, endlich und fuer beide
Richtungen exakt gleich sein. S1-PD bindet weder seinen Zahlenwert noch seine
Darstellung.

Es gibt keinen Kontrollarm, keine dritte Richtung und keine Teilintervention.
Beide Rollen muessen aus demselben Vorzustand erzeugt werden.

## Unveraenderte und veraenderbare Rollen

Pro Arm duerfen sich ausschliesslich `free` und `blocked` aendern. Folgende
Bestandteile bleiben byteidentisch zum gemeinsamen Vorzustand:

- `capacity`;
- `bound_unconfigured`;
- `bound_configured`;
- alle Kanten-, Traeger-, Geometrie- und Feldreferenzen.

Anatomisch gilt fuer jeden Arm:

```text
post.free + post.blocked = pre.free + pre.blocked
post.bound_unconfigured = pre.bound_unconfigured
post.bound_configured = pre.bound_configured
post.capacity = pre.capacity
post.capacity
  = post.free
  + post.bound_unconfigured
  + post.bound_configured
  + post.blocked
```

Paarweise muessen die absoluten Umbuchungsbetraege identisch sein. Diese
Identitaeten wiederholen nur die vorhandene D3-Erhaltung und die statische
Interventionsanatomie. Sie sind keine Wirkungs- oder Bindungsgleichung.

## Atomare Paargrenze

Die einzig zulaessige spaetere Commitordnung lautet:

1. gemeinsamen D3-Vorzustand vollstaendig validieren;
2. vorregistrierte Paarintervention vollstaendig entgegennehmen;
3. Kausalquelle, zwei Rollen und gleiche Umbuchungsbetraege pruefen;
4. beide Nachzustandsentwuerfe ohne Mutation des Vorzustands bilden;
5. beide Entwuerfe einzeln gegen D3-Anatomie und Erhaltung validieren;
6. paarweise Gleichheit aller Kontrollgroessen pruefen;
7. beide Armzustaende gemeinsam atomar freigeben oder keinen Arm freigeben;
8. erst danach einen optionalen Manipulationsreadout zulassen.

Ein einzelner Arm darf niemals vor dem anderen publiziert oder weitergegeben
werden. Bei jedem Fehler bleibt der gemeinsame Vorzustand unveraendert und es
entsteht kein gueltiges Interventionspaar.

## Persistenz- und Expositionsgrenze

In den beiden D3-Nachzustaenden darf nur die gueltige Ressourcenaufteilung
fortbestehen. Interventionsrichtung, Armname, Umbuchungsbetrag,
Paarzuordnung, Testentscheidung und Beobachterbeleg duerfen nicht als
Kandidatenzustand an O3, Feld oder das spaetere Bindungsereignis uebergeben
werden.

Ein externer unveraenderlicher Beobachterbeleg darf die technische Abnahme
dokumentieren. Er ist nie Kandidateneingang. Eine Gegenbaseline darf nur
ihren bereits gebundenen aequivalenten Vorzustand und das spaetere
modellneutrale frische Ereignis sehen; sie erhaelt keine Ressourcenrollen,
Armkennung oder Kandidatenzustandsbytes.

## Verbotene Zustaende

Ungueltig sind insbesondere:

- weniger oder mehr als zwei Interventionsrollen;
- doppelte, leere oder unbekannte Rollen;
- verschiedene Vorzustaende oder verschiedene Kanten zwischen den Armen;
- nullwertige, negative, nicht endliche oder ungleiche Umbuchungsbetraege;
- eine Umbuchung groesser als die jeweilige Quellrolle;
- eine Aenderung von `capacity`, `bound_unconfigured` oder
  `bound_configured`;
- eine Aenderung von Kanten-, Traeger-, Geometrie- oder Feldreferenzen;
- negative oder nicht endliche Ressourcenrollen;
- verletzte lokale Erhaltung vor oder nach der Intervention;
- sequentieller Teilcommit, Klemmen, Runden, Normalisieren oder Reparieren;
- Erzeugung aus O3, Feldantwort, Baselineergebnis oder Nachereignis;
- Persistenz von Armname oder Interventionsmetadaten im Kandidatenpfad.

## Fail-Closed-Fehlerrollen

Ein spaeterer Validator muss mindestens folgende eindeutige Fehlerrollen
unterscheiden koennen:

```text
PD_INVALID_CAUSAL_SOURCE
PD_INVALID_COMMON_PRESTATE
PD_INVALID_ARM_SET
PD_INVALID_TRANSFER_AMOUNT
PD_INSUFFICIENT_SOURCE_RESOURCE
PD_NON_TARGET_ROLE_CHANGED
PD_PAIR_CONTROL_MISMATCH
PD_LOCAL_CONSERVATION_FAILED
PD_NONFINITE_OR_NEGATIVE_RESOURCE
PD_PARTIAL_COMMIT_ATTEMPT
PD_FORBIDDEN_METADATA_PERSISTENCE
```

Die Fehlerrollen sind in S1-PD nur semantisch gebunden. Numerische Codes,
Serialisierung, Prioritaetsordnung und Implementierung bleiben offen. Kein
Fehler darf einen reparierten Sachzustand erzeugen.

## Aussagegrenze

S1-PD zeigt keine Kandidatenwirkung. Der Vertrag prueft spaeter lediglich,
ob eine kontrollierte Ressourcenaufteilung anatomisch sauber erzeugt werden
kann. Die hypothetische MCM-Memory bleibt eine Entwicklungsrichtung; aus
diesem Schritt folgt keine vorhandene Funktion oder Systemfaehigkeit.

## Naechster erlaubter Schritt

S1-PE darf ausschliesslich eine endliche statische Zweiarm-Fixture binden:
exakte dyadische Vorzustands- und Umbuchungswerte, Arm- und Ereignis-IDs,
kanonische Records, Digestregeln sowie erwartete gueltige Nachzustaende.
Wirkungsgleichung, Bindungsdynamik, Implementierung, Test und Lauf bleiben
gesperrt.
