# S1-UB: RFM-1 statischer konstitutiver Familien-, Freiheitsgrad- und Reduktionsaudit

## Auftrag und Grenze

S1-UB prueft, ob nach S1-UA eine kleinste RFM-1-Schliessung mit eigener
technischer Gegenprognose verbleibt. Geprueft werden Tafelanatomie,
donorbegrenzte Umlagerung, passiver Feldtransfer und atomare Transaktion gegen
engere adaptive Zwei-Kanten-Modellklassen.

Der Audit bindet keine Dynamikgleichung, Rate, numerischen Parameter,
Runtimeaenderung, Implementierung oder Testausfuehrung.

## Auditfrage

Verbindlich ist nur folgende Frage:

> Besitzt RFM-1 nach Einfuehrung einer fairen adaptiven
> Zwei-Kanten-Transportbaseline noch eine Funktion, die nicht durch einen
> begrenzten skalaren Motivzustand mit zustandsabhaengiger Fortschreibung und
> passivem Feldreadout rekonstruiert werden kann?

Eine neue Zustandsrolle, Geometrie, Quelle oder Ergebnisachse darf waehrend
dieses Audits nicht ergaenzt werden.

## Exakte Reduktion der Tafel

S1-TX hat bereits gezeigt: Eine gueltige `2x2`-Tafel besitzt bei festen
Zeilen- und Spaltenprojektionen genau einen relationalen Freiheitsgrad.
S1-UA korrigiert diesen Freiheitsgrad gegen die eindeutige Nulltafel und
bezeichnet ihn als `rho`.

Damit gilt eine eindeutige beidseitige Zuordnung:

```text
feste Projektionen + gueltiges rho
<->
genau eine gueltige RFM-1-Tafel
```

Die Nichtnegativitaet der vier Tafeleintraege begrenzt `rho` auf ein
geschlossenes Intervall, dessen Enden bereits durch die Projektionen
bestimmt sind. Es entsteht keine zusaetzliche Kapazitaets-, Ressourcen- oder
Energierolle.

Folge: Die Vier-Zellen-Darstellung ist eine transparente anatomische
Darstellung eines begrenzten Skalars. Sie besitzt bei festgehaltenen
Projektionen keine weitere funktionale Zustandsdimension.

## Reduktion der donorbegrenzten Umlagerung

S1-UA bindet:

- aktuelle Zwei-Kanten-Paritaet bestimmt die Umlagerungsrichtung;
- vorhandene Masse in den abgebenden Zellen begrenzt die Umlagerung;
- Projektionen bleiben unveraendert;
- leere Donorzellen sperren weitere Bewegung in derselben Richtung.

Unter der eindeutigen Tafel-`rho`-Zuordnung ist dies vollstaendig als
begrenzte skalare Fortschreibung formulierbar:

- gleichgerichtete Teilnahme treibt den Skalar in die positive Richtung;
- gegengerichtete Teilnahme treibt ihn in die negative Richtung;
- die zustandsabhaengige Entfernung zur jeweiligen Intervallgrenze bildet
  exakt die Donorbegrenzung ab;
- Einzelkanten- und Nullintervallgrenzen ergeben einen Nullvorschlag.

Die donorbegrenzte Tafelbewegung besitzt daher keine Gegenprognose gegen eine
begrenzte adaptive Korrelationstrace. Die vier Zellen machen die Bilanz
sichtbar, erweitern aber nicht die Funktion.

## Reduktion des Feldtransfers

S1-UA erlaubt dem relationalen Feldanteil nur:

- den aktuellen passiven Zwei-Kanten-Transport abhaengig von `rho`
  umzuformen;
- bei passendem Vorzeichenrest zu verstaerken;
- bei entgegengesetztem Vorzeichenrest begrenzt abzuschwaechen;
- lokal quellenfrei und insgesamt dissipativ oder neutral zu bleiben.

Diese Rolle ist exakt eine zustandsabhaengige passive
Zwei-Kanten-Transportabbildung. Zwei Unterfamilien decken alle in S1-UA
zugelassenen Faelle ab:

1. **Getrennte Kantenskalierung:** `rho` moduliert die beiden vorhandenen
   passiven Kantenbeitraege. Das ist ein gemeinsamer adaptiver
   Zwei-Kanten-Gain.
2. **Gekreuzte Kantentransformation:** Eine Kante darf den passiven Beitrag
   der anderen innerhalb derselben lokalen Bilanz mitbestimmen. Das ist ein
   passiver zustandsabhaengiger Zwei-Kanten-Transportoperator.

Die zweite Unterfamilie ist breiter als unabhaengige Kantengains, aber keine
neue RFM-spezifische Funktionsklasse. Sie ist eine uebliche endliche
Zustandsraumdarstellung eines lokal gekoppelten Transports.

## Atomaritaet erzeugt keinen weiteren Freiheitsgrad

Die S1-TZ-Geschwistertransaktion verlangt, dass Tafel- und Feldvorschlag aus
demselben `TX_PRE` entstehen und gemeinsam committed werden. Diese Ordnung
ist fuer Kausalitaet und Fail-Closed-Verhalten notwendig.

Sie fuegt jedoch keinen Zustand und keine eigene Ausgangsprognose hinzu. Ein
einziger lokaler Uebergangsoperator kann aus demselben Vorzustand zugleich
den naechsten begrenzten Skalar und den passiven Feldbeitrag erzeugen. Der
gemeinsame Wechselwirkungsbeleg ist definitionsgemaess ephemer.

Atomaritaet trennt RFM-1 daher von einem fehlerhaften getrennten
Write-/Read-Pfad, nicht von einer korrekt gebauten adaptiven
Zwei-Kanten-Baseline.

## Engste faire Reduktionsbaseline ACM-1

S1-UB registriert die kleinste Modellklasse, die alle bereits erlaubten
RFM-1-Rollen ohne Tafelterminologie traegt:

```text
ACM-1_ADAPTIVE_CORRELATIONAL_MOTIF_TRANSPORT
```

ACM-1 besitzt pro Motiv:

- genau einen begrenzten signed Skalar;
- dieselben festen Einzelkantenprojektionen und dieselbe Geometrie;
- dieselbe Paritaetsrichtung fuer seine zustandsabhaengige Fortschreibung;
- dieselben donorentsprechenden Intervallgrenzen;
- einen passiven zustandsabhaengigen Zwei-Kanten-Transport;
- dieselbe `TX_PRE`-Ordnung und denselben atomaren Feld-/Zustandscommit;
- dieselben Null-, Spiegel-, Vorzeichen- und Ueberlappungsregeln;
- einen gemeinsamen Parametersatz ueber alle spaeteren Vergleichsarme.

ACM-1 besitzt keine Labels, Sequenzpuffer, Rohdaten, globale Auswahl oder
zusaetzliche Zustandsrolle. Sein Skalar ist ueber die eindeutige Zuordnung
wertgleich zu `rho`.

## Konstruktive Reproduktion

Fuer jeden gueltigen RFM-1-Vorzustand kann ACM-1 seinen Skalar auf denselben
`rho`-Wert setzen. Danach gelten gemeinsam:

- derselbe aktuelle Feld-, S/H-, Rezeptor- und Geometriezustand;
- dieselbe Paritaetsklasse;
- dieselben zulaessigen Skalargrenzen wie Tafelgrenzen;
- dieselbe donorbegrenzte Zustandsfortschreibung;
- dieselbe passive Zwei-Kanten-Feldtransformation;
- derselbe atomare Commit und dieselben Ablationsresultate.

Umgekehrt kann jeder gueltige ACM-1-Skalar bei festen Projektionen wieder in
genau eine RFM-1-Tafel zurueckuebersetzt werden. Die Reduktion ist deshalb
nicht nur eine qualitative Aehnlichkeit, sondern eine zustands- und
ausgangserhaltende Umparametrisierung.

Ein Feldlauf ist fuer diesen strukturellen Befund nicht erforderlich.

## Audit der bisherigen Gegenbaselines

| Vergleich | Urteil nach S1-UB |
|---|---|
| MVI-0 | bleibt enger; kann den gemeinsamen relationalen Skalar nicht tragen |
| JLR-1 | bleibt enger; seine passive Schreibkomponente ist vom Vorzustand unabhaengig |
| JLR-1 mit nichtlinearem Readout | kann den Feldteil, aber nicht zwingend die donorabhaengige Schreibung tragen |
| begrenzte adaptive Korrelationstrace | reproduziert die Tafelentwicklung exakt im Skalarraum |
| adaptiver Zwei-Kanten-Gain | reproduziert alle getrennt skalierenden passiven Feldformen |
| passiver adaptiver Kreuztransport | reproduziert auch die breitere gekoppelte Zwei-Kanten-Feldform |
| ACM-1 | reproduziert Zustand, Fortschreibung, Feldwirkung und Atomaritaet gemeinsam |
| allgemeines reziprokes Zustandsmodell | bleibt wie bereits in S1-TX festgestellt eine umfassende Darstellungsform |

RFM-1 kann weiterhin gegen MVI-0 und die engere JLR-1-Baseline verschieden
sein. Dieser Unterschied reicht aber nicht aus, sobald ACM-1 als faire
naechste Modellklasse zugelassen wird.

## Verbleibende Informationen ohne Kandidatenfunktion

Folgende RFM-1-Artefakte bleiben technisch nuetzlich:

- die explizite `2x2`-Tafel als transparente Darstellung gemeinsamer
  signed Kantenbelegung;
- Nullfaktorisierung und `rho` als saubere Diagnostik;
- marginalenerhaltende Interventionen;
- Projektions- und Ueberlappungsvalidatoren;
- Spiegel- und Vorzeichenregeln;
- geschlossene Vorzustands- und Atomaritaetsvertraege;
- lokale Bilanz- und Passivitaetsanforderungen;
- MVI-0, JLR-1 und ACM-1 als gestufte Gegenbaselineklassen.

Diese Rollen sind Forschungs- und Vergleichsinfrastruktur. Sie sind kein
Beleg fuer eine eigenstaendige RFM-1-Funktion.

## Zweigstopp

Nach Zulassung der fairen ACM-1-Baseline verbleibt keine
nichtreduzierbare RFM-1-Gegenprognose. Jede in S1-TV bis S1-UA gebundene
Wirkungsrolle kann durch einen begrenzten skalaren Motivzustand mit
donorabhaengiger Fortschreibung und passivem Zwei-Kanten-Transport
rekonstruiert werden.

Der RFM-1-Zweig wird deshalb vor Gleichungswahl, Parameterbindung,
Implementierung und Feldlauf als eigenstaendige Kandidatenentwicklung
gestoppt.

Gesperrt sind:

- eine RFM-1-Gleichung oder RFM-1-Runtime;
- Parameterwahl oder Suche innerhalb derselben skalaren Rollen;
- Umbenennung von `rho` oder ACM-1 zu einer neuen Kandidatenfunktion;
- ein RFM-1-Feldlauf oder eine Ergebnisentscheidung;
- eine weitergehende Funktionsaussage aus Tafel- oder Digestverschiedenheit.

Erhalten bleiben die oben genannten Dokumentations-, Diagnose-,
Interventions-, Validator- und Baselinefunktionen.

## Methodische Bedeutung

Der Zweigstopp ist kein negativer Befund zum primaeren MCM-Wahrnehmungsfeld.
Er zeigt vielmehr fruehzeitig, dass die untersuchte Zwei-Kanten-Tafel bei
festen Marginalen funktional nur einen skalaren adaptiven Zusammenhang
traegt.

ACM-1 koennte als bewusst konventionelles Engineeringmodul technisch
nuetzlich sein. Eine solche Umsetzung waere jedoch eine andere Zielsetzung:
Sie wuerde nicht mehr nach einer eigenstaendigen Kandidatenfunktion fragen,
sondern nach einem praktisch MCM-kompatiblen adaptiven Feldbaustein. Dieser
Wechsel darf nicht innerhalb des Reduktionsaudits automatisch erfolgen.

## Verbindliche Entscheidung

```text
S1_UB_RFM1_EXACTLY_REDUCIBLE_TO_BOUNDED_SCALAR_ADAPTIVE_MOTIF_TRANSPORT
ACM1_FAIR_CLOSEST_BASELINE_REPRODUCES_STATE_UPDATE_FIELD_ROLE_AND_ATOMICITY
RFM1_CANDIDATE_BRANCH_STOPPED_BEFORE_EQUATION_IMPLEMENTATION_AND_RUN
RFM1_ARTIFACTS_RETAINED_AS_INACTIVE_RESEARCH_AND_BASELINE_INFRASTRUCTURE
```

## Erforderliche Richtungsentscheidung

Nach S1-UB beginnt kein neuer Forschungsabschnitt automatisch. Insbesondere
reicht `ok weiter` an dieser Grenze nicht als fachliche Richtungswahl.

Eine neue ausdrueckliche Entscheidung muss genau eine der folgenden
Zielsetzungen binden:

1. **Feldkern konsolidieren:** Die vorhandene MCM-Feldarchitektur,
   Schnittstellen, technische Feldzeit, Passivitaetsbelege und
   Reproduzierbarkeit werden ohne neuen adaptiven Kandidaten verdichtet.
2. **ACM-1 als Engineeringmodul untersuchen:** Die Reduzierbarkeit wird
   akzeptiert; Ziel ist ein transparenter MCM-kompatibler adaptiver
   Zwei-Kanten-Baustein, nicht eine eigenstaendige neue Mechanik.
3. **Neue Kandidatenanatomie suchen:** Eine neue Funktion muss vor ihrer
   Anatomie eine Gegenprognose besitzen, die nicht durch einen begrenzten
   skalaren Motivzustand oder adaptiven lokalen Transport reproduziert wird.

Bis zu dieser Entscheidung bleiben der primaere Feldkern aktiv, die
Kandidatenhuelle inaktiv und RFM-1 geschlossen.
