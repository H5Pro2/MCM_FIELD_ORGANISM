# S1-TX: Statischer Projektions-, Ueberlappungs- und Integratorreduktionsaudit RFM-1

## Auftrag und Grenze

S1-TX praezisiert die in S1-TW gebundene gemeinsame Zwei-Kanten-Tafel. Der
Audit bindet Nullfaktorisierung, Ueberlappung, marginalenerhaltende
Intervention und die genaue Reichweite des Integratorvergleichs.

S1-TX enthaelt keine Dynamikgleichung, Rate, konkreten Parameter,
Runtimeaenderung, Implementierung, Testausfuehrung oder Ergebnisentscheidung.

## Normalisierte Projektionslage

Die gemeinsame Tafel eines aktiven Motivs besitzt vier nichtnegative
Eintraege:

```text
J_pp, J_pn, J_np, J_nn
```

Ihre Summe ist die lokale relationale Normierungsmasse des Motivs. Fuer einen
aktiven anatomischen Record wird sie kanonisch auf eins dargestellt. Die
Zeilen- und Spaltensummen sind dadurch zwei lokale signed
Teilnahmeverteilungen mit jeweils derselben Gesamtmasse.

Diese Normierung ist nur eine lokale Zustandsdarstellung. Sie skaliert weder
S noch H, aendert kein Feldbudget und ist keine globale Normalisierung.
Absolute aktuelle Kantenaktivitaet bleibt eine getrennte, bei Interventionen
wertidentisch zu haltende Feldmarginale.

Bei vollstaendig inaktiver Teilnahme ist nur die atomare Nulltafel aus vier
Nullen zulaessig. Eine teilweise definierte Tafel oder Division durch eine
Nullmasse ist ungueltig.

## Exakte Nullfaktorisierung

Fuer eine aktive Tafel seien die abgeleiteten Zeilensummen

```text
r_p, r_n
```

und die Spaltensummen

```text
c_p, c_n
```

gegeben. Die relationsfreie Nulltafel ist eindeutig das aeussere Produkt:

```text
J0_pp = r_p * c_p
J0_pn = r_p * c_n
J0_np = r_n * c_p
J0_nn = r_n * c_n
```

Die Identitaet besitzt keinen freien Parameter und keine Geschichte. Sie
reproduziert exakt dieselben Zeilen- und Spaltensummen. Fuer die inaktive
Nullmasse gilt ausschliesslich die atomare Nulltafel.

Damit ist fuer jede gueltige Projektionslage genau eine Nullrelation
bestimmt. Armweise Nullwahl oder versteckter Carry ist ausgeschlossen.

## Marginalenerhaltende relationale Intervention

Jede `2x2`-Tafel mit festen Zeilen- und Spaltensummen besitzt genau einen
relationalen Freiheitsgrad. Eine Intervention darf ihn nur entlang der
folgenden gekoppelten Zellenrichtung veraendern:

```text
J_pp -> J_pp + delta
J_pn -> J_pn - delta
J_np -> J_np - delta
J_nn -> J_nn + delta
```

oder exakt in Gegenrichtung. `delta` ist noch kein gebundener Laufparameter.
Eine spaetere Intervention muss ihn so waehlen, dass alle vier Eintraege
nichtnegativ bleiben.

Diese gekoppelte Aenderung erhaelt gleichzeitig:

- beide Zeilensummen;
- beide Spaltensummen;
- die Tafelsumme;
- alle getrennt gebundenen aktuellen Knoten-, Kanten-, S- und H-Werte.

Jede andere Zellaenderung ist keine isolierte RFM-1-Intervention.

## Abgeleiteter Kopplungsgrad

Bei festen Projektionen kann die gemeinsame Tafel vollstaendig durch die
Projektionen plus genau einen abgeleiteten Kopplungsgrad dargestellt werden.
Eine moegliche kanonische Diagnose ist der Diagonal-gegen-Gegendiagonal-
Kontrast:

```text
kappa = J_pp + J_nn - J_pn - J_np
```

`kappa` darf nicht zusaetzlich neben der Tafel gespeichert werden. Er ist
nur eine abgeleitete Diagnose derselben Anatomie.

Diese Feststellung begrenzt den Nichtseparierbarkeitsclaim: RFM-1 besitzt bei
festen Projektionen einen relationalen Freiheitsgrad je Motiv, keine
unbestimmte hoehere Zustandsdimension.

## Exakte Ueberlappungsbindung

Die gemeinsame Kante `e_bc` erscheint als rechte Kante von `M_left` und als
linke Kante von `M_right`. Deshalb gilt fuer jeden gemeinsamen Checkpoint:

```text
M_left.c_p = M_right.r_p
M_left.c_n = M_right.r_n
```

Diese Werte werden als eine gemeinsame Kantenprojektion identifiziert. Sie
werden nicht addiert und nicht als zwei Ressourcenbuchungen behandelt.

Die beiden Motive duerfen unterschiedliche Kopplungsgrade tragen, solange
die gemeinsame Projektion uebereinstimmt. Eine Intervention an einem Motiv
darf die geteilte Projektion nicht veraendern; dadurch bleibt der andere
Motivrecord projektionsgueltig.

## Spiegel- und Interventionstransport

Unter Spiegelung werden `M_left` und `M_right` vertauscht und die Tafel wird
entsprechend der Kantenreihenfolge transponiert. Die Nullfaktorisierung,
Kopplungsdiagnose und marginalenerhaltende Interventionsrichtung muessen
unter dieser Abbildung geschlossen bleiben.

Eine gespiegelte positive `delta`-Intervention darf nicht allein wegen der
Knotennamen ihr Vorzeichen oder ihre fachliche Rolle wechseln.

## Integratorreduktionsbefund

Die S1-TW-Tafel mit festen Projektionen ist mathematisch isomorph zu einem
zusaetzlichen skalaren Kopplungsgrad je Motiv. Daher gilt:

```text
Eine allgemeine multivariate Zustandsmaschine kann die RFM-1-Anatomie
darstellen.
```

Eine absolute Behauptung, RFM-1 sei durch keinen Integrator repraesentierbar,
ist nicht haltbar und wird verworfen. Wissenschaftlich pruefbar ist nur die
Reduktion auf vorab klar begrenzte einfachere Integratorfunktionen.

## Eng begrenzte Integratorbaseline MVI-0

```text
MVI-0_MARGINAL_ONLY_ADDITIVE_LEAKY_VECTOR
```

MVI-0 darf einen endlichen Vektor unabhaengiger additiver oder leaky
Koordinaten tragen. Jede Koordinate wird nur aus aktuellen Knoten-, S/H- oder
Einzelkantenmarginalen fortgeschrieben. Er besitzt:

- keinen gemeinsamen Zwei-Kanten-Tafeleintrag;
- keinen gemischten Kanteninteraktionsterm;
- keine gegenseitige Zustandsmodulation seiner Koordinaten;
- keine Labels, Sequenzpuffer oder armweise Parameter;
- einen festen gemeinsamen Readout ueber alle Arme.

RFM-1 besitzt gegen MVI-0 eine klare Gegenprognose: Wenn der vollstaendige
MVI-0-Zustand, aktuelle Eingabe, S/H und alle Marginalen wertidentisch sind,
darf nur eine unterschiedliche RFM-1-Tafel zu unterschiedlicher
Feldfortsetzung fuehren. MVI-0 muss fuer dieses matched Paar dieselbe
Fortsetzung liefern.

## Engste Retentionsbaseline JLR-1

```text
JLR-1_JOINT_TABLE_LEAKY_RETENTION
```

JLR-1 darf exakt dieselbe Tafel- und Projektionsanatomie wie RFM-1 tragen,
aber nur als passiv gebildete, fest leaky abklingende gemeinsame Spur mit
festem Readout. Es besitzt keine zustandsabhaengige Feld-zu-Tafel-Kopplung,
keine Tafel-zu-Feld-Mitwirkung innerhalb desselben lokalen Ereignisses und
keine Interaktion zwischen `M_left` und `M_right` ausser der gemeinsamen
Projektionsvalidierung.

JLR-1 ist notwendig, weil eine Tafelverschiedenheit allein nur joint
retention zeigen wuerde. RFM-1 bleibt spaeter nur eigenstaendig, wenn ein
gemeinsamer Parametersatz von JLR-1 den vollstaendigen Bildungs-,
Interventions-, Spiegel- und Feldfortsetzungsverlauf nicht reproduziert.

## Abgrenzung zu einem allgemeinen Zustandsmodell

Ein beliebig dimensioniertes nichtlineares Zustandsmodell mit Zugriff auf
alle lokalen Ereignisse koennte jede endliche deterministische
RFM-1-Implementierung nachbilden. Es ist deshalb keine falsifizierbare
einfachere Gegenbaseline.

S1-TX beansprucht Nichtreduzierbarkeit nur gegen explizit registrierte,
einfachere Modellklassen. Jede spaetere Aussage muss die konkret bestandenen
Baselineklassen nennen und darf daraus keine absolute
Nichtdarstellbarkeitsaussage ableiten.

## Verwerfungsregeln

RFM-1 wird bereits vor einer Dynamikgleichung gestoppt, wenn:

- keine eindeutige Nullfaktorisierung fuer jede gueltige Projektionslage
  moeglich ist;
- die marginalenerhaltende Interventionsrichtung die Nichtnegativitaet nicht
  erhalten kann;
- die `e_bc`-Projektionen beider Motive nicht ohne Reparatur uebereinstimmen;
- mehr als ein relationaler Freiheitsgrad je Motiv benoetigt wird, ohne eine
  neue Funktionsprognose zu besitzen;
- MVI-0 bei identischem vollstaendigem Baselinezustand unterschiedliche
  matched Readouts liefern darf;
- JLR-1 nicht als engste passive Joint-Retention-Baseline zugelassen wird;
- RFM-1 nur durch eine absolute Abgrenzung gegen beliebige allgemeine
  Zustandsmodelle begruendet werden kann.

## Auditentscheidung

Nullfaktorisierung, Ueberlappung und eine exakt marginalenerhaltende
Intervention sind strukturell formulierbar. RFM-1 ist gegen eine
marginalenbasierte additive/leaky Integratorbaseline MVI-0 falsifizierbar.

Gleichzeitig ist die Tafel repraesentationsaequivalent zu einem zusaetzlichen
Kopplungsgrad je Motiv. Deshalb bleibt JLR-1 als engste Reduktionsbaseline
verbindlich. RFM-1 ist noch nicht funktional zugelassen; seine spaetere
Eigenstaendigkeit haengt an einer lokalen konjugierten Feldkopplung, die
JLR-1 nicht reproduziert.

## Aussagegrenze

S1-TX ist ein statischer Struktur- und Baselineaudit. Er weist keine
relationale Feldwirkung nach und definiert noch keine Systemfunktion.

## Verbindliche Entscheidung

```text
S1_TX_RFM1_NULL_FACTORIZATION_OVERLAP_AND_MATCHED_INTERVENTION_BOUND
ABSOLUTE_INTEGRATOR_NONREPRESENTABILITY_REJECTED
MVI0_AND_JLR1_MANDATORY_REDUCTION_BASELINES_BOUND
NO_DYNAMICS_NO_PARAMETERS_NO_IMPLEMENTATION_NO_RUN
```

## Naechster Schritt

Der einzige naechste Schritt ist S1-TY als statischer Kausalquellen-,
konjugierter Kopplungs- und engster Baselinevertrag. Er muss vor jeder
Gleichung festlegen:

- welche normale lokale Feldinformation eine Tafelbildung verursachen darf;
- wie Feld-zu-Tafel und Tafel-zu-Feld aus derselben lokalen Wechselwirkung
  folgen muessen;
- welche Wirkung JLR-1 als passive Joint-Retention-Baseline vorhersagt;
- welche gemeinsame Gegenprognose RFM-1 dagegen besitzt;
- welche Kausalquellen und getrennten Schreib-/Lesepfade verboten sind.

Bleibt keine Gegenprognose gegen JLR-1 uebrig, wird RFM-1 als
Joint-Retention-Baseline eingeordnet und gestoppt. S1-TY bindet noch keine
Dynamikgleichung, Rate, Parameter, Runtime oder Ausfuehrung.
