# S1-TY: RFM-1 statischer Kausalquellen-, Kopplungs- und JLR-1-Gegenvertrag

## Auftrag und Grenze

S1-TY prueft, ob die in S1-TX gebundene relationale Tafel eine lokale
Ursache-Wirkungs-Rolle besitzen kann, die enger ist als eine passive
Joint-Retention. Der Vertrag bindet zulaessige Kausalquellen, die gemeinsame
Kopplungsgrenze und eine Gegenprognose zu JLR-1.

S1-TY enthaelt keine Dynamikgleichung, Rate, numerischen Parameter,
Runtimeaenderung, Implementierung, Testausfuehrung oder Ergebnisentscheidung.

## Lokale Kausalgrenze

Ein RFM-1-Ereignis ist auf genau ein kanonisches Zwei-Kanten-Motiv begrenzt:

```text
Endknoten -- Mittelknoten -- Endknoten
```

Zulaessige Vorzustandsinformation ist ausschliesslich:

- der abgeschlossene aktuelle Feldzustand der drei Motivknoten;
- die dort bereits vorhandenen schnellen S/H-Rollen;
- die beiden aktuellen gerichteten Feldbeitraege der Motivkanten;
- der aktuelle Rezeptorbeitrag an diesen drei Knoten;
- die gueltige gemeinsame RFM-1-Tafel dieses Motivs;
- die kanonische Geometrie, Orientierung und Feldschrittdauer.

Die Feldschrittdauer ist nur eine lokale Fortschreibungsdauer. Eine Uhrzeit,
Episodennummer oder externe Phase ist keine Kausalquelle.

Information eines benachbarten Motivs darf nur zur Validierung der
gemeinsamen `e_bc`-Projektion gelesen werden. Sie darf weder Richtung noch
Staerke eines RFM-1-Vorschlags bestimmen.

## Normale Feldursache

Die einzige zulaessige Bildungsursache ist die gleichzeitige signed
Teilnahme beider vorhandener Motivkanten an derselben lokalen
Feldfortsetzung. Eine einzelne aktive Kante, eine bloss hohe Knotenamplitude
oder eine Wiederholungszahl reicht nicht aus.

Die Ursache ist damit ein gegenwaertiger lokaler Feldvorgang. Sie enthaelt
kein erkanntes Muster und keine gespeicherte Eingabe. Gleiche gueltige
Vorzustaende und derselbe lokale Feldkontakt muessen denselben atomaren
Vorschlag erzeugen.

## Eine gekoppelte lokale Transaktion

RFM-1 darf nicht als Schreiber plus spaeterer Leser konstruiert werden.
Zulaessig ist nur eine atomare lokale Transaktion mit einem gemeinsamen
Ursprungsbeleg:

1. Der abgeschlossene Vorzustand von Feld und Tafel wird gemeinsam gelesen.
2. Genau ein lokaler Motivwechselwirkungsbeleg wird daraus gebildet.
3. Dieser eine Beleg erzeugt gemeinsam einen marginalenerhaltenden
   Tafelvorschlag und einen signed Feldtransfervorschlag.
4. Beide Vorschlaege werden zusammen validiert und gemeinsam uebernommen
   oder zusammen verworfen.

Die Reihenfolge beschreibt nur die kausale Transaktionsgrenze. Sie ist keine
numerische Integrationsvorschrift.

## Gebundene Kopplungseigenschaften

Die Tafel- und Feldseite derselben Transaktion muessen gemeinsam folgende
Eigenschaften besitzen:

- **Lokalitaet:** Es werden nur die drei Motivknoten und zwei Motivkanten
  beruehrt.
- **Marginalenerhaltung:** Die Tafelveraenderung folgt ausschliesslich der
  in S1-TX gebundenen marginalenerhaltenden Interventionsrichtung.
- **Feldquellenfreiheit:** Der relationale Feldbeitrag wird als gerichteter
  Austausch entlang vorhandener Kanten bilanziert und erzeugt keine
  ungebundene globale Feldquelle.
- **Zustandsabhaengigkeit:** Die aktuelle Tafel darf den gemeinsamen
  Austausch beeinflussen; andernfalls bleibt nur passive Ablage.
- **Reziprozitaet:** Derselbe Austausch muss zugleich die Tafelentwicklung
  beeinflussen; andernfalls bleibt nur ein fester Tafelreadout.
- **Spiegelaequivarianz:** Spiegelung transportiert Tafel- und Feldvorschlag
  gemeinsam, ohne namensabhaengiges Vorzeichen.
- **Atomaritaet:** Ein gueltiger Tafelvorschlag ohne zugehoerigen
  Feldvorschlag oder umgekehrt darf nicht committed werden.

`Reziprozitaet` bezeichnet hier nur diese technische wechselseitige
Abhaengigkeit innerhalb einer lokalen Feldtransaktion.

## Verbindliche JLR-1-Funktion

JLR-1 traegt dieselbe Tafelanatomie und dieselben Projektionen wie RFM-1,
bleibt aber eine passive Retentionsbaseline. Fuer jeden lokalen Kontakt gilt:

- der vorhandene Tafelrest klingt nach einer festen, armuebergreifend
  identischen Regel ab;
- der gegenwaertige Zwei-Kanten-Kontakt liefert eine feste passive
  Schreibkomponente;
- diese Schreibkomponente haengt nicht von der vorhandenen relationalen
  Tafelbelegung ab;
- der Feldbeitrag ist ein fester Readout des abgeschlossenen
  Tafeldatenstands;
- der aktuelle Schreibvorgang und der aktuelle Feldreadout besitzen keinen
  gemeinsamen Wechselwirkungsbeleg;
- der innerhalb eines Kontakts neu geschriebene Anteil wirkt nicht bereits
  als Teil desselben lokalen Ereignisses auf das Feld zurueck.

JLR-1 verwendet ueber alle Vergleichsarme genau einen Parametersatz und eine
gemeinsame kausale Aktualisierungsordnung. Ein armweise geaenderter Readout
oder Leak ist keine zulaessige Baseline.

## Kleinste Gegenprognose zu JLR-1

Der spaetere Vergleich benoetigt ein matched Tafelpaar. Beide Arme besitzen
denselben Feld-, S/H-, Rezeptor-, Geometrie-, Projektions- und
Kantenmarginalenzustand. Sie unterscheiden sich nur im zulaessigen
relationalen Freiheitsgrad ihrer Tafel und erhalten denselben lokalen
Zwei-Kanten-Kontakt.

JLR-1 sagt fuer dieses Paar voraus:

- Nach Abzug des fuer jeden Arm vorab bestimmten passiven Tafelabklingens
  ist die durch den aktuellen Kontakt neu eingebrachte Schreibkomponente in
  beiden Armen identisch.
- Eine Feldabweichung kann nur aus dem festen Readout der bereits
  unterschiedlichen Tafeln stammen.
- Schreibabweichung und Feldabweichung bilden daher keine neue gemeinsame
  kontaktabhaengige Wechselwirkung.

RFM-1 besitzt die entgegengesetzte, vorab falsifizierbare Prognose:

- Die verschiedene Tafelbelegung veraendert unter demselben Kontakt den
  gemeinsamen lokalen Austausch.
- Deshalb unterscheiden sich sowohl die marginalenerhaltende
  Tafelumlagerung als auch der zugehoerige signed Feldtransfer.
- Beide Unterschiede muessen mit demselben lokalen Wechselwirkungsbeleg
  mitwandern, unter Spiegelung gemeinsam transformieren und bei dessen
  Ablation gemeinsam verschwinden.

Eine blosse unterschiedliche Feldantwort bei unveraenderter passiver
Schreibkomponente bestaetigt nur JLR-1 oder einen festen Tafelreadout und
reicht fuer RFM-1 nicht aus.

## Pflichtablationen

Vor einer spaeteren Funktionsausfuehrung muessen mindestens diese drei
getrennten technischen Eingriffe spezifiziert werden:

| Eingriff | Verbindliche Erwartung |
|---|---|
| gesamte RFM-1-Transaktion aus | unveraenderter primaerer Feldkern; kein RFM-1-Zustand wird fortgeschrieben |
| nur relationale Kopplung neutralisiert | relationsfreie Nullfaktorisierung bei unveraenderten Projektionen; kein relationaler Zusatztransfer |
| matched Tafelintervention | nur der relationale Freiheitsgrad wechselt; die gekoppelte Tafel- und Feldantwort muss gemeinsam mitwechseln |

Eine produktive Runtime darf keinen nur schreibenden oder nur lesenden
RFM-1-Modus anbieten. Solche Trennungen sind ausschliesslich instrumentierte
Auditablationen und duerfen keine Ergebnisarme ersetzen.

## Verbotene Kausalquellen und Architekturen

Unzulaessig sind:

- A-/B-, Arm-, Ergebnis-, Phasen- oder Ereignislabels;
- Episodengrenzen, Wiederholungszaehler oder externe Uhrzeit;
- Comparator-, Schwellen- oder spaetere Readoutinformationen;
- Replay, Sequenzpuffer oder gespeicherte Rezeptordaten;
- ein globaler Selektor, Optimierer oder Zuteiler;
- ein separater Tafel-Schreibpfad und nachgelagerter Tafel-Lesepfad;
- ein Tafelupdate ohne lokalen Feldtransfervorschlag;
- ein Feldzusatz aus der Tafel ohne zugehoerige lokale Tafelreaktion;
- armweise Vorzeichen, Parameter, Korrekturen oder Nachnormalisierung;
- stille Reparatur einer ungueltigen Projektion oder Teiltransaktion.

## Reduktionsgrenze

Die gebundene Gegenprognose trennt RFM-1 funktional von JLR-1 und MVI-0,
sofern sie spaeter unter einem gemeinsamen Parametersatz besteht. Sie trennt
RFM-1 nicht von einem allgemeinen nichtlinearen reziproken Zustandsmodell.
RFM-1 bleibt eine konkrete technische Feldmechanikhypothese innerhalb dieser
allgemeineren Modellklasse.

Es ist daher unzulaessig, aus einem spaeteren Baselineunterschied absolute
Nichtdarstellbarkeit oder eine allgemeine neue Faehigkeit abzuleiten.

## Verwerfungsregeln

RFM-1 wird vor einer Gleichung gestoppt, wenn:

- die Tafel nur passiv geschrieben und spaeter fest ausgelesen werden kann;
- die aktuelle Tafel den lokalen Austausch nicht beeinflusst;
- der lokale Austausch die Tafelumlagerung nicht beeinflusst;
- Tafel- und Feldvorschlag getrennte Kausalbelege benoetigen;
- die JLR-1-Schreibkomponente bereits jede beobachtbare Tafelentwicklung
  reproduzieren darf;
- nur eine Feldabweichung, aber keine gekoppelte Tafelumlagerung
  vorhergesagt werden kann;
- der relationale Zusatztransfer eine unbilanzierte Feldquelle benoetigt;
- Projektionen, Marginalen oder Spiegelregeln verletzt werden;
- Labels, Replay, externe Phasen oder armweise Regeln erforderlich werden.

Ein solcher Negativbefund darf in demselben Schritt nicht durch eine neue
Zustandsrolle oder eine erweiterte Baseline repariert werden.

## Auditentscheidung

Eine eng begrenzte Gegenprognose zu JLR-1 bleibt formulierbar: RFM-1 verlangt
eine zustandsabhaengige gemeinsame lokale Transaktion, deren
marginalenerhaltende Tafelumlagerung und signed Feldtransfer gemeinsam auf
die vorhandene Tafel und den aktuellen Zwei-Kanten-Kontakt reagieren. JLR-1
sagt dagegen eine vom Tafelvorzustand unabhaengige passive
Kontaktschreibkomponente plus getrennten festen Readout voraus.

RFM-1 wird deshalb nicht gestoppt, ist aber weiterhin weder mathematisch noch
funktional zugelassen. Die naechste Stufe muss zeigen, dass diese
Transaktionsrolle ohne versteckte Zusatzinformation und mit eindeutiger
kausaler Aktualisierungsordnung darstellbar ist.

## Verbindliche Entscheidung

```text
S1_TY_RFM1_LOCAL_CAUSAL_SOURCE_AND_CONJUGATE_TRANSACTION_BOUND
JLR1_PASSIVE_WRITE_FIXED_READOUT_COUNTERPREDICTION_BOUND
RFM1_REMAINS_OPEN_BUT_NOT_FUNCTIONALLY_ADMITTED
NO_EQUATION_NO_PARAMETERS_NO_IMPLEMENTATION_NO_RUN
```

## Naechster Schritt

Der einzige naechste Schritt ist S1-TZ als statischer atomarer
Transaktions-, Aktualisierungsordnungs- und Ablationsanatomie-Audit. Er muss
ohne Gleichung festlegen:

- welche unveraenderlichen Vorzustandswerte eine Transaktion liest;
- welche Tafel- und Feldvorschlagsrollen sie atomar erzeugt;
- wie Read-before-write, gemeinsame Validierung und gemeinsamer Commit ohne
  algebraischen Kreis geordnet sind;
- wie Nulltransaktion, Kopplungsablation und matched Tafelintervention
  anatomisch getrennt werden;
- welche minimalen Records spaeter die RFM-1/JLR-1-Gegenprognose pruefbar
  machen.

Falls dafuer ein zweiter Kausalpfad, versteckter Zustand oder ein aktueller
Write-then-read-Kreis notwendig wird, wird RFM-1 gestoppt. S1-TZ bindet noch
keine Dynamikgleichung, Parameter, Runtime, Implementierung oder
Testausfuehrung.
