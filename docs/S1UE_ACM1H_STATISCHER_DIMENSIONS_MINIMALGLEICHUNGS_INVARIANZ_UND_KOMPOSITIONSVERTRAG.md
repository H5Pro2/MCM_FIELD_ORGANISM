# S1-UE: ACM-1H statischer Dimensions-, Minimalgleichungs-, Invarianz- und Kompositionsvertrag

## Auftrag und Grenze

S1-UE bindet fuer die in S1-UD ausgewaehlte ACM-1H-Familie genau eine
symbolische Minimalform. Geprueft werden Dimensionen, Wertebereiche,
donorbegrenzte Zustandsfortschreibung, passiver Feldreadout, Ueberlappung
auf `e_bc` und der noch offene IAG-2-Zustandsmatch.

Der Vertrag enthaelt keine numerischen Parameterwerte, Runtimeaenderung,
Implementierung, Testausfuehrung oder Feldlauf. ACM-1H bleibt ein bewusst
konventionelles Engineeringmodul und keine eigenstaendige neue Mechanik.

## Abgeschlossener Vorzustand

Alle Groessen eines atomaren Intervalls werden aus demselben abgeschlossenen
Vorzustand `TX_PRE` gelesen. Fuer ein kanonisch orientiertes Motiv `M` mit
den Kanten `e_1` und `e_2` seien:

```text
Phi_1, Phi_2   primaere signed Kantenfluesse aus TX_PRE
Delta_tau      positive technische Feldzeit des Intervalls
z              abgeschlossener ACM-1H-Motivzustand
```

`Phi_1` und `Phi_2` besitzen dieselbe Flussdimension. Ihr Vorzeichen gilt
relativ zur kanonischen Motivorientierung. Der ACM-1H-Vorschlag darf weder
einen bereits modifizierten Kantenfluss noch `z_next` desselben Intervalls
zuruecklesen.

## Zustands- und Parameterrollen

Der Motivzustand ist dimensionslos und abgeschlossen begrenzt:

```text
z in [-1, 1]
```

Die einzigen konstitutiven Rollen der Minimalform sind:

```text
gamma_z > 0     inverse Einheit einer uebertragenen Feldmenge
beta in (0, 1]  dimensionslose Readoutstaerke
```

`gamma_z` und `beta` sind modellweit gebundene Rollen. Sie duerfen nicht je
Motiv, Arm, Geschichte oder Ergebnis verschieden sein. S1-UE weist ihnen
keine Zahlenwerte zu. `beta = 0` bleibt nur eine exakte Readoutablation und
ist kein aktiver ACM-1H-Parametersatz.

Es gibt keinen zweiten Motivzustand, Zaehler, Zeitstempel, Sequenzpuffer,
Normalisierungszustand oder Ergebniszugriff.

## Lokale Beteiligung und Paritaet

Aus den primaeren Vorzustandsfluessen werden ausschliesslich ephemere
Groessen gebildet:

```text
u_M = min(abs(Phi_1), abs(Phi_2))
```

Falls `Delta_tau <= 0` oder `u_M = 0`, liegt keine ACM-1H-Transaktion vor.
Andernfalls gilt:

```text
sigma_M = sign(Phi_1 * Phi_2) in {-1, +1}
theta_M = 1 - exp(-gamma_z * u_M * Delta_tau)
```

Damit ist `theta_M` dimensionslos und fuer jede endliche gueltige
Beteiligung strikt zwischen null und eins. `min` waehlt nur die gemeinsam
verfuegbare Zwei-Kanten-Beteiligung; es clippt und repariert keinen Zustand.

## Donorbegrenzte Zustandsfortschreibung

Fuer eine aktive Zwei-Kanten-Beteiligung lautet die einzige
Zustandsfortschreibung:

```text
z_next = (1 - theta_M) * z + theta_M * sigma_M
```

Ohne aktive Zwei-Kanten-Beteiligung gilt exakt:

```text
z_next = z
```

Die aktive Form ist eine konvexe Kombination aus dem gueltigen Vorzustand
und genau einer Intervallgrenze. Daraus folgen ohne Clipping:

```text
z in [-1, 1] -> z_next in [-1, 1]

sigma_M = +1 -> z_next - z = theta_M * (1 - z)
sigma_M = -1 -> z_next - z = -theta_M * (1 + z)
```

Der Abstand zur jeweils angesteuerten Grenze begrenzt die Aenderung. Eine
bereits erreichte Grenzlage besitzt in derselben Richtung keinen weiteren
Zustandsvorschlag. Entgegengesetzte Beteiligung bewegt denselben Zustand
ohne Reset oder gesonderte Loeschphase zur Gegenrichtung.

## Gemeinsamer passiver Motivreadout

Der Feldreadout verwendet `z` aus `TX_PRE`, nicht `z_next`. Fuer ein aktives
Motiv gilt der gemeinsame Faktor:

```text
r_M = 1 + beta * sigma_M * z
```

Ohne aktive Zwei-Kanten-Beteiligung gilt `r_M = 1`. Derselbe Faktor wird auf
beide vorhandenen primaeren Motivkanten angewandt. Es wird kein Fluss der
jeweils anderen Kante gekreuzt erzeugt.

Aus `z in [-1,1]`, `sigma_M in {-1,+1}` und `beta in (0,1]` folgt:

```text
0 <= r_M <= 2
z = 0 -> r_M = 1
```

Passende Paritaet kann den Betrag des vorhandenen passiven Flusses
vergroessern, Gegenparitaet kann ihn bis zur neutralen Kante abschwaechen.
Der Faktor kann das Flussvorzeichen nicht umkehren und keine zuvor inaktive
Kante aktivieren.

## Symmetrische Kantenkomposition

Fuer jede vorhandene Kante `e` sei `Inc(e)` die endliche Menge aktiver
ACM-1H-Motive, die diese Kante enthalten. Der vollstaendige Faktor lautet:

```text
R_e = Produkt ueber M in Inc(e) von r_M
```

Fuer eine Kante ohne aktives Motiv ist das leere Produkt eins. Der
komponierte Kantenfluss lautet:

```text
Phi_e_combined = R_e * Phi_e_primary
Delta_Phi_e_ACM = (R_e - 1) * Phi_e_primary
```

Damit wird `Phi_e_primary` genau einmal angelegt. Die provenancegetrennten
Motivvorschlaege liefern nur Faktoren. Multiplikation ist kommutativ und
assoziativ; Motiviterationsreihenfolge und die Benennung als linkes oder
rechtes Motiv koennen das Ergebnis nicht veraendern.

Fuer die gemeinsame Kante gilt insbesondere:

```text
R_bc = r_M_left * r_M_right
Phi_bc_combined = R_bc * Phi_bc_primary
```

Es gibt weder eine doppelte Primaerbuchung noch eine nachtraegliche
Mittelung oder Normalisierung. Wegen der endlichen Motivkardinalitaet und
`0 <= r_M <= 2` bleibt jeder gueltige komponierte Faktor endlich und
nichtnegativ.

## Quellenfreiheit und Passivitaet

Der primaere Feldkern bilanziert jeden Kantenfluss an seinen beiden Enden
mit entgegengesetztem Vorzeichen. ACM-1H aendert nur dessen nichtnegativen
Leitwertfaktor. Deshalb bleiben fuer jede Kante erhalten:

```text
Knotenbeitrag_tail + Knotenbeitrag_head = 0
```

Ist der primaere dissipative Kantenanteil proportional zu
`-k_e * (Delta S_e)^2` mit `k_e >= 0`, so wird er durch ACM-1H zu:

```text
-R_e * k_e * (Delta S_e)^2 <= 0
```

ACM-1H kann daher den passiven Ausgleich beschleunigen, abschwaechen oder
neutralisieren, aber keine interne positive Feldquelle erzeugen. Dieser
Beleg benoetigt weder Clipping noch einen globalen Ausgleich.

## Null-, Spiegel- und Vorzeicheninvarianten

### Exakte Nullpfade

- ACM-OFF laesst Zustand, Schema und primaeren Feldfluss unberuehrt.
- `z = 0` ergibt fuer jedes aktive Motiv exakt `r_M = 1`.
- Eine inaktive Motivkante ergibt `u_M = 0`, `z_next = z` und `r_M = 1`.
- `Delta_tau = 0` ergibt keinen Zustands- und keinen Feldcommit.
- Ein uniformes lokales Feld besitzt keine aktiven Kantenfluesse und damit
  keinen ACM-1H-Vorschlag.

### Gemeinsamer Vorzeichenwechsel

Beim gemeinsamen Wechsel `Phi_1 -> -Phi_1` und `Phi_2 -> -Phi_2` bleiben
`u_M`, `sigma_M`, `theta_M`, `z_next` und `r_M` wertidentisch. Die
komponierten Fluesse wechseln nur zusammen mit ihren primaeren Fluessen das
Vorzeichen.

### Spiegelung

Eine kanonische Spiegelung vertauscht Motiv- und Kantenrollen, erhaelt aber
`u_M`, die Paritaet, Zustandsfortschreibung und Faktoren. Das Produkt auf
`e_bc` bleibt wertidentisch. Zweifache Spiegelung fuehrt zum Ausgangsrecord
zurueck.

## Exakte Registrierung von IAG-2

Der Name IAG-2 bezeichnet ab S1-UE ausschliesslich folgende enge
Engineeringbaseline:

```text
IAG-2_INDEPENDENT_SIGN_BLIND_ACTIVITY_GAINS
```

Jede Kante `e` besitzt einen eigenen dimensionslosen Gainzustand
`g_e in [0,1]`. Er liest nur den Betrag seines eigenen primaeren Flusses:

```text
theta_e = 1 - exp(-gamma_g * abs(Phi_e) * Delta_tau)
g_e_next = (1 - theta_e) * g_e + theta_e
```

`gamma_g > 0` besitzt dieselbe Dimensionsrolle wie `gamma_z`, ist aber ein
eigener gemeinsam gebundener Baselineparameter. Bei inaktiver Kante oder
Nullintervall gilt `g_e_next = g_e`. Der spaetere IAG-2-Readout darf jede
Kante nur als feste Funktion ihres eigenen `g_e` und aktuellen
Primaerflusses skalieren.

IAG-2 wird hier als einfachste reine Aktivitaetsgainbaseline bewusst
vorzeichenblind gebunden. Unabhaengigkeit allein verbietet nur den Zugriff
auf die gemeinsame Paritaet, nicht zwingend das Vorzeichen der eigenen
Kante. Ein vorzeichen- oder ordnungssensitiver Einzelkantenadapter ist daher
eine breitere andere Baselineklasse und wird durch den folgenden Match weder
ausgeschlossen noch widerlegt.

## Algebraischer IAG-2-Zustandsmatch

Fuer beliebig viele Intervalle besitzt IAG-2 die geschlossene Form:

```text
1 - g_e(n)
= (1 - g_e(0))
  * exp(-gamma_g * Summe_t(abs(Phi_e(t)) * Delta_tau(t)))
```

Der Endzustand haengt damit nur von der kumulierten absoluten Aktivitaet der
eigenen Kante ab, nicht von Vorzeichen, Reihenfolge oder gemeinsamer
Paritaet.

Die kleinste vorregistrierte Paarung verwendet von `z(0) = 0` aus zwei
gleich lange Intervalle mit demselben endlichen Flussbetrag `Q > 0`:

```text
Geschichte G:  (+Q, +Q), (-Q, -Q)
Geschichte O:  (+Q, -Q), (-Q, +Q)
```

Auf jeder einzelnen Kante sind Dauer, absolute Aktivitaet sowie positive
und negative Marginale gleich. Daher sind beide vollstaendigen
IAG-2-Kantenzustaende nach G und O exakt wertidentisch.

Fuer ACM-1H ist in beiden Intervallen derselbe Wert `theta` aktiv. Es gilt:

```text
z_G = +(1 - (1 - theta)^2)
z_O = -(1 - (1 - theta)^2)
```

Bei einer anschliessenden wertidentischen positiven Zwei-Kanten-Probe sagt
ACM-1H deshalb die Faktoren `1 + beta*abs(z_G)` und
`1 - beta*abs(z_G)` voraus. IAG-2 besitzt dagegen in beiden Armen denselben
vollstaendigen Gainzustand und muss bei derselben Probe dieselbe Fortsetzung
liefern.

Der in S1-UD offene IAG-2-Match ist damit fuer die nun exakt registrierte
enge Baseline geschlossen. Er ist keine Aussage gegen beliebige
unabhaengige adaptive Zustandsmodelle.

## Reduktions- und Aussagegrenzen

- ACM-1H bleibt ein begrenzter skalarer adaptiver Motivgain.
- Die Gleichung belegt noch keinen praktischen Nutzen im Feldbetrieb.
- Der G/O-Unterschied ist eine symbolische Gegenprognose, kein Messbefund.
- IAG-2 wird nur in seiner registrierten vorzeichenblinden Form getrennt.
- LCT-1 bleibt die autonome Abklingbaseline; ACM-1H besitzt keinen Leak.
- RFM-1 bleibt geschlossen und wird durch diese Gleichung nicht
  wiedereroeffnet.
- Es werden keine Memory-, Lern-, KI- oder biologischen Faehigkeiten
  behauptet.

## Fail-closed-Regeln

ACM-1H ist vor einem spaeteren Commit ungueltig, wenn:

- `z`, `Phi_e`, `Delta_tau` oder ein Parameter nicht endlich ist;
- `z` ausserhalb `[-1,1]` liegt;
- `Delta_tau < 0`, `gamma_z <= 0` oder `beta` ausserhalb `(0,1]` liegt;
- eine Einzelkante Zustand oder Motivreadout ausloest;
- `z_next` fuer den Feldreadout desselben Intervalls verwendet wird;
- ein Motiv den bereits modifizierten Fluss eines anderen Motivs liest;
- die gemeinsame Kante den primaeren Fluss mehr als einmal erhaelt;
- ein Faktor negativ wird oder ein komponierter Wert nicht endlich ist;
- Clipping, Reset oder Nachnormalisierung eine Verletzung reparieren soll;
- Motiviterationsumkehr das numerische Ergebnis veraendert.

Ein Fehler erzeugt weder Feld- noch ACM-1H-Teilzustand.

## Vertragsentscheidung

Die Minimalform ist ohne zusaetzlichen gespeicherten Zustand und ohne
Nachnormalisierung geschlossen. Die Zustandsgrenzen folgen aus einer
konvexen donorbegrenzten Fortschreibung. Die multiplikative
Kantenkomposition ist passiv, symmetrisch und legt den Primaerfluss auch auf
`e_bc` genau einmal an.

Der vollstaendige G/O-Zustandsmatch ist fuer die exakt registrierte enge
IAG-2-Aktivitaetsgainbaseline algebraisch bewiesen. ACM-1H bleibt deshalb
als Engineeringmodul fuer eine spaetere Implementierungspruefung zulaessig.

```text
S1_UE_ACM1H_MINIMAL_EQUATION_AND_INVARIANT_DOMAIN_BOUND
DONOR_BOUNDED_HOLDING_STATE_UPDATE_WITHOUT_CLIPPING_BOUND
SYMMETRIC_MULTIPLICATIVE_SHARED_EDGE_COMPOSITION_BOUND
EXACT_G_O_MATCH_PROVED_FOR_REGISTERED_SIGN_BLIND_IAG2_BASELINE
NO_NUMERIC_VALUES_NO_IMPLEMENTATION_NO_TEST_NO_FIELD_RUN
```

## Naechster Schritt

Der einzige naechste Schritt ist S1-UF als statischer Parameterrollen-,
Diskretisierungs-, Orakel- und Implementierungszulassungsvertrag. Er darf
noch keine Runtime aendern und keinen Test oder Feldlauf ausfuehren. Zu
binden sind:

- ein kleiner endlicher numerischer Parameterkandidatenraum fuer
  `gamma_z`, `beta` und die IAG-2-Baseline;
- Einheitenabbildung auf die vorhandenen primaeren Kantenfluesse und die
  technische Feldzeit;
- reine Referenzorakel fuer Zustand, Faktoren, `e_bc` und G/O-Match;
- Fail-Closed-Fehlercodes und atomare Ausgabefelder;
- eine minimale spaetere Implementierungs- und synthetische Testmatrix;
- harte Sperre jedes Feldlaufs bis zur getrennten technischen Abnahme.

Falls die vorhandene Runtime keine eindeutige Fluss- oder Feldzeitabbildung
ohne neuen Normalisierungszustand besitzt, wird die Implementierung gesperrt
und ACM-1H bleibt ausschliesslich symbolische Engineeringreferenz.
