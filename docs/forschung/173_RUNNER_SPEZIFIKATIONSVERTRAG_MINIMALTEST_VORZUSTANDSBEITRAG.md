# Runner-Spezifikationsvertrag Minimaltest Vorzustandsbeitrag

Stand: 2026-07-30

## 1. Zweck und Geltungsgrenze

Dieses Dokument spezifiziert ausschliesslich die spaetere technische Verdrahtung
des in
`docs/forschung/172_VORREGISTRIERUNG_MINIMALTEST_VORZUSTANDSBEITRAG.md`
vorregistrierten Minimaltests. Es ist kein Runner, kein ausfuehrbares Manifest
und keine Freigabe fuer eine Implementierung oder einen Lauf.

Die Hypothesen, Messmetriken, Schwellen und Entscheidungskriterien werden
unveraendert aus Dokument 172 uebernommen. Bei einem Widerspruch ist Dokument
172 fachlich massgeblich; die Runner-Implementierung muss dann bis zur
schriftlichen Klaerung gesperrt bleiben.

## 2. Verbindliche Laufmatrix

Die spaetere Ausfuehrung muss genau die folgenden 24 Lauf-IDs erzeugen. Jede
Zeile konstruiert ein frisches Feld. Zwischen den Zeilen darf kein Feldzustand,
Generatorzustand, Rezeptorzustand oder Messzustand uebernommen werden.

| Lauf-ID | Tabellenarm | Replikat | Geschichte | Aktueller Kontakt | Vorzustandsoperator |
|---|---|---:|---|---|---|
| `history_a.none.r1` | `history_a.none` | 1 | A | C | `None` |
| `history_a.none.r2` | `history_a.none` | 2 | A | C | `None` |
| `history_b.none.r1` | `history_b.none` | 1 | B | C | `None` |
| `history_b.none.r2` | `history_b.none` | 2 | B | C | `None` |
| `history_a.identity.r1` | `history_a.identity` | 1 | A | C | `"identity"` |
| `history_a.identity.r2` | `history_a.identity` | 2 | A | C | `"identity"` |
| `history_b.identity.r1` | `history_b.identity` | 1 | B | C | `"identity"` |
| `history_b.identity.r2` | `history_b.identity` | 2 | B | C | `"identity"` |
| `history_a.zero.r1` | `history_a.zero` | 1 | A | C | `"zero"` |
| `history_a.zero.r2` | `history_a.zero` | 2 | A | C | `"zero"` |
| `history_b.zero.r1` | `history_b.zero` | 1 | B | C | `"zero"` |
| `history_b.zero.r2` | `history_b.zero` | 2 | B | C | `"zero"` |
| `equalized_a.none.r1` | `equalized_a.none` | 1 | A | C | `None` |
| `equalized_a.none.r2` | `equalized_a.none` | 2 | A | C | `None` |
| `equalized_b.none.r1` | `equalized_b.none` | 1 | A | C | `None` |
| `equalized_b.none.r2` | `equalized_b.none` | 2 | A | C | `None` |
| `permuted_a.none.r1` | `permuted_a.none` | 1 | B | C | `None` |
| `permuted_a.none.r2` | `permuted_a.none` | 2 | B | C | `None` |
| `permuted_b.none.r1` | `permuted_b.none` | 1 | A | C | `None` |
| `permuted_b.none.r2` | `permuted_b.none` | 2 | A | C | `None` |
| `permuted_a.zero.r1` | `permuted_a.zero` | 1 | B | C | `"zero"` |
| `permuted_a.zero.r2` | `permuted_a.zero` | 2 | B | C | `"zero"` |
| `permuted_b.zero.r1` | `permuted_b.zero` | 1 | A | C | `"zero"` |
| `permuted_b.zero.r2` | `permuted_b.zero` | 2 | A | C | `"zero"` |

Die spaetere Laufreihenfolge ist die Tabellenreihenfolge. Sie darf weder von
Zwischenergebnissen noch von bereits erzeugten Messwerten abhaengen. Beide
Replikate eines Arms verwenden byte-identische Konfigurationen und
Ereignisfolgen; es gibt keine Seed-Variation.

## 3. Vorlaufvalidierung

Vor Konstruktion des ersten Feldes muss der Runner alle folgenden Bedingungen
hart validieren:

- Die Laufmatrix enthaelt genau die 24 oben genannten eindeutigen Lauf-IDs.
- Jeder der 12 Tabellenarme besitzt genau `.r1` und `.r2`.
- A und B stimmen in Ereignisbudget, Dauer, Geometrie und Modalitaeten ueberein.
- C ist in allen Armen byte-identisch.
- Generator, Boundary-Bedingung, Feldgeometrie, Zeitparameter und
  Rezeptorverteilung sind zwischen den Operatorarmen identisch konfiguriert.
- Projektions-, Diffusions-, Daempfungs- und Afterimage-Parameter sowie
  Zustandsfortschreibung und Messpfad sind fuer alle Arme unveraendert.
- Hook-Quelle und Hook-Test entsprechen dem vor dem Lauf eingefrorenen Stand
  und sind getrennt von Dissipationsaenderungen identifizierbar.
- `dissipation_config` ist im Laufmanifest explizit vorhanden und sein Wert ist
  exakt `None` beziehungsweise `null` nach Serialisierung.
- Es wird keine `NeutralFieldDissipationConfig` konstruiert, abgeleitet oder als
  impliziter Ersatzwert eingesetzt.
- `numeric_zero` ist exakt `1e-12`; `rtol` ist exakt `0.0`.

Fehlt eine Bedingung oder ist sie nicht maschinell eindeutig pruefbar, darf kein
Feld konstruiert und kein Teillauf gestartet werden.

## 4. Messpunktbindung M0 bis M3

Jeder Lauf muss genau dieselben vier Messpunkte in derselben Reihenfolge
erzeugen:

| Messpunkt | Bindung im Ablauf |
|---|---|
| `M0` | Unmittelbar nach Konstruktion des frischen Feldes und vor dem ersten Ereignis von A oder B. |
| `M1` | Unmittelbar nach Abschluss von A oder B und vor dem ersten Ereignis von C. |
| `M2` | Im C-Schritt nach Bereitstellung der aktuellen C-Eingabe und unmittelbar vor Aufruf des gemeinsamen Integrators. |
| `M3` | Unmittelbar nach der zu M2 gehoerenden Feldfortschreibung und vor jedem weiteren Ereignis. |

An M0 bis M3 duerfen ausschliesslich die in Dokument 172 vorregistrierten
Messrollen erfasst werden:

- kanonischer Snapshot und Digest der Feld- und Schichtzustaende,
- `previous_activation` und `previous_afterimage`,
- `field_tick` und `last_common_interval_s`,
- Digest der Rezeptorverteilung,
- Generator-, Boundary- und Geometrie-Digests, sofern sie bereits zur neutralen
  Messrolle gehoeren,
- daraus abgeleitete paarweise `L-inf`-Differenzen und exakte Digest-Gleichheit.

Die Messung darf keinen Zustand veraendern. Es duerfen keine weiteren Metriken,
Zwischenmesspunkte, Toleranzen oder Auswertungsregeln ergaenzt werden.

## 5. Hook-Verdrahtung

- Arme mit `None` verwenden den unveraenderten neutralen Pfad.
- Arme mit `"identity"` verwenden den isolierten Vorzustands-Hook mit
  Identitaetsoperator.
- Arme mit `"zero"` verwenden denselben isolierten Hook und neutralisieren nur
  `previous_activation` und `previous_afterimage` am vorregistrierten Eingriffspunkt.
- Generator, Boundary-Term, Integrator und anschliessende Fortschreibung muessen
  in allen drei Operatorbedingungen derselbe eingefrorene Pfad bleiben.
- Der Hook darf weder oeffentlich exportiert noch als Produktionsschalter
  verdrahtet werden.

## 6. Harte Abbruchbedingungen

Der spaetere Runner muss ohne Fortsetzung und ohne fachliche Interpretation
abbrechen, sobald mindestens eine der folgenden Bedingungen eintritt:

- Hook oder Hook-Test entsprechen nicht dem eingefrorenen Quellstand.
- Dissipation ist aktiv oder Hook- und Dissipationsaenderungen sind nicht getrennt
  identifizierbar.
- `None` und `"identity"` sind im technischen Aequivalenznachweis nicht bitgleich.
- `.r1` und `.r2` eines Arms unterscheiden sich an M0, M1, M2 oder M3 im
  kanonischen Snapshot-Digest.
- Ein Tabellenarm besitzt nicht genau zwei Replikate oder ein Replikat beginnt
  nicht mit einem frischen Feld.
- A und B unterscheiden sich in Budget, Dauer, Geometrie oder Modalitaeten.
- C ist zwischen Armen nicht byte-identisch.
- Generator, Boundary, Zeitparameter oder Rezeptorverteilung unterscheiden sich
  zwischen Operatorarmen.
- Ein Reset oder eine Aenderung an Projektion, Diffusion, Daempfung,
  Afterimage-Parametern, Zustandsfortschreibung oder Messpfad wird festgestellt.
- Ein Messwert ist nicht endlich oder verletzt eine vorregistrierte normierte
  Domaene.
- Die gleichgesetzte Gegenbaseline ist nicht tatsaechlich gleichgesetzt.
- Ergebnisse werden vor Abschluss aller 24 Laeufe eingesehen oder zur Aenderung
  von A, B, C, Toleranzen oder Messpunkten verwendet.

Bei einem Abbruch sind nur der technische Abbruchgrund, betroffene Lauf-ID,
Messpunkt und vorhandene Diagnosedaten zu protokollieren. Teilresultate duerfen
nicht zur Entscheidung ueber H0, H1, H2 oder P verwendet werden.

## 7. Ergebnisvertrag

Erst nach technisch gueltigem Abschluss aller 24 Laeufe darf eine getrennte,
spaeter freizugebende Auswertung die in Dokument 172 definierten Vergleiche
bilden. Der Runner selbst trifft keine fachliche Entscheidung und erzeugt keine
Aussage zu Feldwirkung, Kontaktgeschichte, Memory, Organisation, Bedeutung,
Semantik, Bewusstsein, Eigenstaendigkeit oder KI.

## 8. Unveraenderte Sperren

Dieser Vertrag gibt nicht frei:

- Runner-Implementierung,
- Effekt- oder Hypothesenlauf,
- Public-AV-Lauf,
- Produktionsschalter,
- Aenderung der Organismus- oder Felddynamik,
- neue Hypothesen, Schwellen, Messmetriken oder Bedeutungszuweisungen.

Eine spaetere Implementierung bedarf einer gesonderten technischen Abnahme gegen
diesen Vertrag und Dokument 172.
