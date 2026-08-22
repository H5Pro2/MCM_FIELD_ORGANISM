# S1-UA: RFM-1 statischer Vorzeichen-, Null-, Bilanz- und Passivitaetsvertrag

## Auftrag und Grenze

S1-UA bindet die qualitative Wirkungsordnung der in S1-TZ beschriebenen
lokalen Transaktion. Der Vertrag legt signed Teilnahme, relationale
Umlagerungsrichtung, Symmetrien, Nullgrenzen, lokale Feldbilanz und
Passivitaet vor jeder mathematischen Schliessung fest.

S1-UA enthaelt keine Dynamikgleichung, Rate, numerischen Parameter,
Runtimeaenderung, Implementierung, Testausfuehrung oder Ergebnisentscheidung.

## Vorhandene Feldkonvention

Der primaere Feldkern verwendet eine symmetrische Nachbarschaft und einen
dissipativen Transport zwischen benachbarten Knoten. Rezeptorkontakt ist eine
getrennt bilanzierte aeussere Zufuhr. RFM-1 darf diese Rollen nicht
umdefinieren.

Fuer jedes kanonische Zwei-Kanten-Motiv werden die beiden Kanten vom linken
Endknoten ueber den Mittelknoten zum rechten Endknoten orientiert. Das
Vorzeichen einer Kantenbeteiligung bezeichnet ausschliesslich die aktuelle
gerichtete Feldtendenz relativ zu dieser Orientierung.

## Vier signed Zwei-Kanten-Lagen

Bei nichtverschwindender Teilnahme beider Kanten existieren genau vier
Vorzeichenlagen:

| linke Kante | rechte Kante | lokale Klasse | Tafelrichtung |
|---|---|---|---|
| positiv | positiv | gleichgerichtet | zur Diagonale |
| negativ | negativ | gleichgerichtet | zur Diagonale |
| positiv | negativ | gegengerichtet | zur Gegendiagonale |
| negativ | positiv | gegengerichtet | zur Gegendiagonale |

`zur Diagonale` bedeutet ausschliesslich die positive
marginalenerhaltende Interventionsrichtung aus S1-TX: Masse wird aus
`J_pn` und `J_np` gemeinsam nach `J_pp` und `J_nn` umgelagert.

`zur Gegendiagonale` bezeichnet exakt die Gegenrichtung. Es gibt keine
fuenfte Lage, keinen richtungslosen Sonderfall und keine von Knotennamen
abhaengige Wahl.

## Warum nur die Paritaetsklasse gebunden wird

Die S1-TX-Tafel besitzt bei festen Projektionen genau einen relationalen
Freiheitsgrad. Sie kann deshalb nur unterscheiden, ob gemeinsame Teilnahme
relativ mehr diagonal oder gegendiagonal belegt ist. Sie kann innerhalb der
Diagonale nicht zusaetzlich `pp` gegen `nn` und innerhalb der Gegendiagonale
nicht `pn` gegen `np` frei waehlen.

Eine Regel, die eine einzelne Zelle bevorzugt, wuerde die gebundenen
Marginalen veraendern oder einen zweiten versteckten Freiheitsgrad
einfuehren. Beides ist unzulaessig.

## Relationaler Rest gegen die Nulltafel

Die rohe Diagnose `kappa` aus S1-TX ist bei ungleichen Marginalen nicht
notwendig null, selbst wenn die Tafel relationsfrei faktorisiert ist.
Deshalb darf sie nicht allein als relationale Wirkung gelesen werden.

Verbindliche Diagnose ist nur der Unterschied zwischen:

- dem Diagonal-gegen-Gegendiagonal-Kontrast der aktuellen Tafel;
- demselben Kontrast ihrer eindeutig zugeordneten Nullfaktorisierung.

Dieser abgeleitete Unterschied heisst in den folgenden statischen Audits
`rho`. Seine exakte Diagnoseidentitaet lautet:

```text
rho = kappa(aktuelle Tafel) - kappa(zugehoerige Nullfaktorisierung)
```

Das ist keine Dynamikgleichung. `rho` wird nicht gespeichert. Es gilt
qualitativ:

- `rho` positiv: diagonaler Ueberschuss gegen die Nulltafel;
- `rho` negativ: gegendiagonaler Ueberschuss gegen die Nulltafel;
- `rho` null: relationsfreie Tafel bei denselben Projektionen.

Diese Korrektur verhindert, dass blosse signed Kantenmarginalen als
relationale Feldwirkung fehlgedeutet werden.

## Zustandsabhaengige Tafelumlagerung

Der aktuelle Feldkontakt bestimmt die Umlagerungsrichtung. Der vorhandene
Tafelzustand bestimmt, wie viel Masse in den abgebenden Zellen ueberhaupt
verfuegbar ist:

- bei gleichgerichteter Teilnahme koennen nur gegendiagonale Zellen Masse
  abgeben;
- bei gegengerichteter Teilnahme koennen nur diagonale Zellen Masse abgeben;
- leere abgebende Zellen erlauben keine weitere Umlagerung in derselben
  Richtung;
- Empfaenger duerfen niemals durch Clipping oder Nachnormalisierung
  korrigiert werden.

Damit ist die Kontaktschreibung bereits qualitativ vom Tafelvorzustand
abhaengig. JLR-1 sagt dagegen nach seinem fest gebundenen Leak eine vom
Tafelvorzustand unabhaengige passive Schreibkomponente voraus.

S1-UA bindet noch nicht, welcher Anteil der verfuegbaren Masse pro
Feldintervall umgelagert wird.

## Kopplung an den Feldtransfer

Der aktuelle signed Zwei-Kanten-Kontakt und `rho` duerfen gemeinsam den
relationalen Feldtransfervorschlag bestimmen. Dabei gelten folgende
Richtungsgrenzen:

- eine Tafel mit `rho` null erzeugt keinen relationalen Zusatztransfer;
- positiver `rho` passt zur gleichgerichteten Paritaetsklasse;
- negativer `rho` passt zur gegengerichteten Paritaetsklasse;
- eine Tafel, deren relationaler Rest zur aktuellen Paritaetsklasse passt,
  darf den vorhandenen passiven Motivtransport verstaerken;
- eine Tafel mit entgegengesetztem relationalem Rest darf den vorhandenen
  passiven Motivtransport abschwaechen;
- die Abschwaechung darf den gesamten lokalen Transport nicht gegen seine
  passive Bilanzrichtung umkehren;
- RFM-1 darf keine Kante aktivieren, auf der keine aktuelle Feldtendenz
  vorliegt;
- die aktuelle Tafelumlagerung und der Feldtransfervorschlag bleiben
  Geschwister aus `TX_PRE`; die Folgetafel wird nicht zurueckgelesen.

`Verstaerken` und `abschwaechen` sind hier nur qualitative
Gegenprognoserollen. Ihre mathematische Groesse ist noch nicht gewaehlt.

## Lokale Feldbilanz

Jeder relationale Kantenbeitrag wird an den beiden Endknoten mit
entgegengesetztem Vorzeichen bilanziert. Fuer ein vollstaendiges Motiv gilt:

- der relationale Beitrag erzeugt keine neue Knotenmasse;
- die Summe seiner drei Knotenbeitraege ist exakt null;
- Beitraege auf der gemeinsamen Kante `e_bc` werden vor dem Feldcommit zu
  genau einem Kantenbeitrag komponiert;
- der relationale Kompositor besitzt weder Rezeptorquelle noch globalen
  Ausgleichstopf;
- Dissipation und aeussere Rezeptorzufuhr bleiben getrennt ausweisbar.

Eine lokale Nullsumme allein reicht nicht als Passivitaetsbeleg. Auch ein
quellenfreier Transfer koennte eine vorhandene Feldabweichung aktiv
vergroessern.

## Passivitaetsgrenze

RFM-1 besitzt in der aktuellen Anatomie keinen eigenen bilanzierten
Energiespeicher. Deshalb darf sein kombinierter Feldtransfer nach Abzug der
Rezeptorzufuhr die quadratische Feldgroesse nicht erhoehen.

Verbindlich ist:

- der relationale Beitrag darf passiven Ausgleich umverteilen, verstaerken
  oder begrenzt abschwaechen;
- der vollstaendige kombinierte Kantenoperator muss dissipativ oder neutral
  bleiben;
- eine positive interne Feldzufuhr ist ohne neue, vorab bilanzierte
  Speicherrolle unzulaessig;
- Tafelnormalisierung ist keine Energie und darf nicht als Quelle
  verrechnet werden;
- Clipping, globale Normalisierung, Reset oder nachtraegliche Skalierung
  duerfen Passivitaet nicht herstellen.

Passivitaet wird spaeter am vollstaendigen vorgeschlagenen Kantenoperator
geprueft, nicht an isolierten Zwischenbeitraegen oder nur am Endwertbereich.

## Exakte Nullgrenzen

### Uniformes lokales Feld

Sind alle drei Motivknoten wertgleich, besitzen beide Kanten keine signed
Feldtendenz. Tafelumlagerung und relationaler Feldtransfer sind exakt null.

### Einzelkantenkontakt

Ist nur eine der beiden Motivkanten aktiv, entsteht keine relationale
Transaktion. Eine Einzelkantenwirkung bleibt Aufgabe des primaeren Feldkerns
oder einer registrierten Einzelkantenbaseline.

### Relationsfreie Tafel

Bei `rho` null bleibt der relationale Feldtransfer exakt null. Ein echter
Zwei-Kanten-Kontakt darf jedoch eine Tafelumlagerung aus der
Nullfaktorisierung heraus vorschlagen. Der zugehoerige Feldvorschlag ist in
diesem ersten relationsfreien Schritt ein vorhandener, aber numerisch
neutraler Geschwistervorschlag.

### Kein neuer Rezeptorkontakt

Fehlender Rezeptorkontakt erzwingt nicht automatisch eine Nulltransaktion.
Solange der abgeschlossene Feldvorzustand auf beiden Motivkanten signed
Tendenzen traegt, darf die interne lokale Feldfortsetzung RFM-1 antreiben.
Erst die fehlende Zwei-Kanten-Feldteilnahme bindet den relationalen Nullpfad.

### Nullintervall

Ein Feldintervall ohne positive Dauer darf weder Tafel noch Feld
fortschreiben.

### RFM-OFF und RFM-NULL

`RFM-OFF` reproduziert exakt den unveraenderten primaeren Feldkern ohne
RFM-1-Zustand. `RFM-NULL` verwendet die relationsfreie Nullfaktorisierung bei
wertidentischen Projektionen und erzeugt keinen relationalen
Zusatztransfer.

## Symmetriebindung

### Gemeinsamer Vorzeichenwechsel

Werden alle lokalen Feldvorzeichen gemeinsam umgekehrt:

- `pp` und `nn` tauschen ihre Rollen;
- `pn` und `np` tauschen ihre Rollen;
- gleichgerichtet bleibt gleichgerichtet;
- gegengerichtet bleibt gegengerichtet;
- `rho` und die Tafelumlagerungsrichtung bleiben unveraendert;
- alle vorgeschlagenen Feldtransferzeichen kehren sich um.

### Spiegelung

Unter der in S1-TW gebundenen Linienspiegelung werden Motivrollen,
Kantenreihenfolge und Tafelzellen kanonisch transportiert. Die
Paritaetsklasse, `rho`, Umlagerungsrichtung und Passivitaetsentscheidung
bleiben invariant. Der Feldtransfer wird raeumlich gespiegelt.

Zweimalige Vorzeichenumkehr oder zweimalige Spiegelung muss exakt zum
Ausgangsrecord zurueckkehren.

## Gegenprognosen

S1-UA schaerft die bisherigen Gegenbaselines:

| Baseline | Gebundene Null- oder Gegenprognose |
|---|---|
| MVI-0 | bei identischen Marginalen und identischem Baselinezustand keine `rho`-abhaengige Fortsetzung |
| JLR-1 | passive Kontaktschreibkomponente nach Leak bleibt vom Tafelvorzustand unabhaengig |
| unabhaengige Kantengains | koennen jede Kante skalieren, besitzen aber keine gemeinsame Paritaetsumlagerung bei festen Marginalen |
| statischer Zweikantenoperator | reagiert auf aktuelle Paritaet, besitzt aber keinen `rho`-abhaengigen Folgezustand |
| allgemeines reziprokes Zustandsmodell | kann die gebundene Rolle darstellen und bleibt ausdruecklich keine ausschliessbare Universalbaseline |

RFM-1 bleibt nur offen, wenn spaeter unter einem Parametersatz zugleich die
donorseitige Tafelabhaengigkeit und der passive `rho`-abhaengige
Feldtransfer bestehen.

## Verwerfungsregeln

RFM-1 wird vor einer Gleichung gestoppt, wenn:

- eine einzelne aktive Kante eine relationale Umlagerung ausloest;
- gleichgerichtete und gegengerichtete Teilnahme keine eindeutigen
  Gegenrichtungen besitzen;
- eine einzelne Tafelzelle ohne Marginalenausgleich veraendert werden muss;
- rohe `kappa`-Werte statt des Nulltafelrests `rho` als Wirkung gelten;
- `rho` null einen relationalen Feldtransfer erzeugt;
- der kombinierte interne Feldtransfer die passive Bilanzrichtung umkehrt;
- Feldwirkung nur durch Clipping, globale Normierung oder Reset begrenzt
  werden kann;
- die gemeinsame Kante doppelt fortgeschrieben wird;
- Vorzeichenumkehr oder Spiegelung die Paritaets- oder
  Passivitaetsentscheidung veraendert;
- Zielwert, Fehler, Ergebnislabel, Phase oder Wiederholungszahl fuer die
  Vorzeichenwahl benoetigt wird.

Ein Negativbefund darf in S1-UA nicht durch eine neue Speicher-, Quellen-
oder Ressourcenrolle repariert werden.

## Vertragsentscheidung

Eine eindeutige Vorzeichen- und Bilanzordnung bleibt formulierbar. Die
aktuelle Zwei-Kanten-Paritaet bestimmt die einzige zulaessige
Tafelumlagerungsrichtung; der nulltafelkorrigierte relationale Rest `rho`
bestimmt qualitativ Verstaerkung oder Abschwaechung des vorhandenen passiven
Motivtransports. Null- und Symmetriegrenzen sind geschlossen formulierbar.

RFM-1 wird deshalb nicht gestoppt. Eine konkrete konstitutive Form ist noch
nicht zugelassen. Insbesondere muss der naechste Audit klaeren, ob jede
moegliche Schliessung lediglich auf einen zustandsabhaengigen
Zwei-Kanten-Gain oder eine bekannte adaptive Transportform zurueckfaellt.

## Verbindliche Entscheidung

```text
S1_UA_RFM1_SIGN_PARITY_NULL_AND_LOCAL_BALANCE_BOUND
NULL_FACTORIZATION_CORRECTED_RELATIONAL_RESIDUAL_RHO_BOUND
PASSIVE_FIELD_TRANSFER_WITHOUT_INTERNAL_SOURCE_BOUND
NO_EQUATION_NO_PARAMETERS_NO_IMPLEMENTATION_NO_RUN
```

## Naechster Schritt

Der einzige naechste Schritt ist S1-UB als statischer konstitutiver
Familien-, Freiheitsgrad- und Reduktionsaudit. Er muss ohne Parameter oder
Runtime pruefen:

- welche kleinste Form gleichzeitig donorbegrenzte Tafelumlagerung und
  passiven `rho`-abhaengigen Feldtransfer tragen koennte;
- ob ein gemeinsamer skalarer Kopplungsgrad dafuer ausreicht;
- ob jede zulaessige Form bereits ein adaptiver Zwei-Kanten-Gain, eine
  passive Korrelationstrace oder JLR-1 mit nichtlinearem Readout ist;
- welche genau eine Form, falls ueberhaupt, eine eigene Gegenprognose gegen
  diese engeren Baselines behaelt.

Bleibt keine eigenstaendige Gegenprognose uebrig, wird RFM-1 vor einer
Gleichung gestoppt. S1-UB bindet noch keine Parameter, Runtime,
Implementierung oder Testausfuehrung.
