# S1-UD: ACM-1 statischer Minimalfamilien-, Halte- und Engineeringreduktionsaudit

## Auftrag und Grenze

S1-UD waehlt aus den in S1-UC offengehaltenen Transport- und
Zustandsfamilien genau eine minimale ACM-1-Engineeringfamilie. Geprueft
werden gemeinsame Kantenskalierung gegen gekreuzten Transport sowie
beteiligungsfreies Halten gegen autonomes passives Abklingen.

Der Audit enthaelt keine Dynamikgleichung, Rate, numerischen Parameter,
Runtimeaenderung, Implementierung, Testausfuehrung oder Feldlauf.

## Verbindliche Minimalitaetsregel

Eine breitere Familie ist nur zulaessig, wenn sie vor ihrer mathematischen
Form eine technische Feldprognose besitzt, welche die engere Familie nicht
reproduzieren kann und die fuer den S1-UC-Zweck erforderlich ist.

Mehr Freiheitsgrade, groessere Ausdrucksstaerke oder moegliche spaetere
Effekte sind allein keine Begruendung.

## Zwei Transportfamilien

### T1: Gemeinsame getrennte Kantenskalierung

T1 erhaelt die beiden vorhandenen passiven Kantenbeitraege. Ein einziger aus
`z` und aktueller Paritaet abgeleiteter Motivmodifikator wirkt gemeinsam auf
beide Kanten, ohne ihre Feldtendenzen miteinander zu mischen.

Verbindliche Eigenschaften:

- ein `z`-Zustand pro Motiv;
- ein gemeinsamer Modifikator fuer beide Motivkanten;
- jede Kante behaelt ihren eigenen primaeren signed Feldbeitrag;
- keine Kante erzeugt einen Beitrag aus der Feldtendenz der anderen;
- ohne gleichzeitige Beteiligung beider Kanten entsteht kein
  ACM-1-Zusatzbeitrag;
- die kombinierte Feldwirkung bleibt lokal quellenfrei und passiv.

T1 kann die S1-UC-Funktionsprognose tragen: Derselbe aktuelle
Zwei-Kanten-Kontakt wird bei unterschiedlichem `z` verschieden, aber auf
beiden Kanten gemeinsam umgeformt.

### T2: Passiver gekreuzter Zwei-Kanten-Transport

T2 erlaubt zusaetzlich, dass die Feldtendenz einer Motivkante die
Transportgroesse der anderen Kante mitbestimmt. Damit koennte eine
Kreuzsuszeptibilitaet gemessen werden, die T1 definitionsgemaess nicht
besitzt.

Diese zusaetzliche Prognose ist technisch formulierbar, aber fuer den in
S1-UC gebundenen Zweck nicht erforderlich. Geschichtsabhaengige gemeinsame
Motivempfaenglichkeit, IAG-2-Trennung, Gegenwirkung, Nullpfad und Passivitaet
sind bereits mit T1 darstellbar.

T2 wuerde ausserdem eine weitere konstitutive Kopplungswahl und einen
staerkeren Passivitaetsnachweis benoetigen. Ohne vorab erforderliche
Kreuzprognose waere dies unbegruendete Komplexitaet.

## Transportentscheidung

T1 wird als einzige primaere ACM-1-Transportfamilie weitergefuehrt:

```text
ACM1_COMMON_EDGE_SCALING
```

T2 wird nicht implementiert und nicht als Ergebnisalternative offengehalten.
Es bleibt lediglich eine dokumentierte spaetere Erweiterungsklasse, fuer die
ein neuer Funktions- und Falsifikationsvertrag erforderlich waere.

Diese Entscheidung behauptet nicht, T1 sei eine eigenstaendige neue
Mechanik. T1 ist bewusst ein gemeinsamer adaptiver Zwei-Kanten-Gain mit
einem gemeinsamen Paritaetszustand.

## Ueberlappung auf der gemeinsamen Kante

`M_left` und `M_right` duerfen je einen T1-Modifikationsvorschlag fuer ihre
gemeinsame Kante `e_bc` erzeugen. Dabei gilt:

- beide Vorschlaege lesen denselben abgeschlossenen primaeren
  Kantenbeitrag;
- keiner liest den Vorschlag des anderen Motivs;
- der primaere `e_bc`-Beitrag wird nicht zweimal angelegt;
- nur die beiden provenancegetrennten ACM-1-Aenderungsvorschlaege werden vor
  dem Commit deterministisch zu einer gemeinsamen Aenderung komponiert;
- die Komposition ist unabhaengig von der Motiviterationsreihenfolge;
- der vollstaendige resultierende Kantenbeitrag muss weiterhin passiv und
  endlich sein.

S1-UD waehlt noch keine numerische Kompositionsregel. Eine spaetere
Minimalgleichung muss genau eine symmetrische, reihenfolgeunabhaengige Regel
binden und gegen Doppelanwendung des primaeren Kantenbeitrags pruefen.

## Zwei kontaktfreie Zustandsfamilien

`Kontaktfrei` wird in diesem Audit praezise als fehlende gleichzeitige
Zwei-Kanten-Beteiligung verstanden. Fehlender neuer Rezeptorkontakt allein
reicht nicht, solange das interne Feld beide Motivkanten weiter antreibt.

### H1: Beteiligungsfreies Halten

H1 laesst `z` unveraendert, wenn keine gleichzeitige Zwei-Kanten-Beteiligung
vorliegt. Nur eine neue lokale Paritaetslage darf den Zustand verschieben.

H1 besitzt:

- keine autonome Abklingrate;
- keinen Zeitablauf ohne lokale Feldursache;
- Gegenwirkung ausschliesslich durch entgegengesetzte spaetere Paritaet;
- einen parameterfreien beteiligungsfreien Zustandsnullvorschlag.

### H2: Autonomes passives Abklingen

H2 fuehrt `z` ohne aktuelle Zwei-Kanten-Beteiligung in Richtung Neutralitaet.
Es benoetigt mindestens eine Abklingzeit oder eine gleichwertige
konstitutive Festlegung.

H2 ist als LCT-1 bereits eine Pflichtbaseline. S1-UC verlangt keine autonome
Erholung und keine bestimmte Haltedauer. H2 wuerde deshalb vor dem ersten
Funktionsvergleich einen zusaetzlichen freien Zeitmassstab einfuehren.

## Halteentscheidung

H1 wird als primaere ACM-1-Zustandsfamilie weitergefuehrt:

```text
ACM1_PARTICIPATION_GATED_HOLD
```

H2 bleibt als LCT-1-Gegenbaseline erhalten. Ein spaeterer Negativbefund darf
nicht durch nachtraegliches Umschalten von H1 auf H2 repariert werden.

Halten ist keine Aussage ueber dauerhafte Funktion. `z` kann durch
gegenlaeufige spaetere Zwei-Kanten-Beteiligung abgeschwaecht, neutralisiert
oder umgerichtet werden. S1-UD bindet lediglich keinen autonomen Zerfall ohne
solche Beteiligung.

## Ausgewaehlte Minimalfamilie

Die einzige weitergefuehrte Familie lautet:

```text
ACM-1H_COMMON_EDGE_SCALING_WITH_PARTICIPATION_GATED_HOLD
```

Sie besitzt:

- genau einen begrenzten signed Paritaetszustand `z` pro Motiv;
- donorbegrenzte Zustandsbewegung nur bei gleichzeitiger
  Zwei-Kanten-Beteiligung;
- beteiligungsfreies Halten;
- gemeinsame zustandsabhaengige Skalierung beider vorhandener
  Motivkantenbeitraege;
- keine gekreuzte Erzeugung eines Kantenbeitrags aus der anderen Kante;
- geschlossene Vorzustandsordnung und atomaren Feld-/Zustandscommit;
- exakten ACM-OFF- und `z = 0`-Nullpfad.

## Vorregistrierte G/O-Trennung und offene IAG-2-Angleichung

Die kleinste Expositionskonstruktion lautet:

- **Geschichte G:** enthaelt gleichgerichtete `pp`- und `nn`-Beteiligungen;
- **Geschichte O:** enthaelt gegengerichtete `pn`- und `np`-Beteiligungen;
- jede einzelne Kante besitzt ueber beide Geschichten dieselben positiven
  und negativen Teilnahmemarginalen;
- Dauer, Betrag, Feldrandwerte und Einzelkantenmodelle werden angeglichen;
- nur die gemeinsame Paritaetszuordnung ist verschieden.

Gleiche Einzelkantenmarginalen beweisen vor einer IAG-2-Gleichung noch nicht
denselben vollstaendigen IAG-2-Endzustand. Eine zustandsabhaengige
Einzelkantenfortschreibung koennte auf die zeitliche Ordnung ihrer jeweils
eigenen Kante reagieren.

Die G/O-Konstruktion wird deshalb nur vorregistriert. S1-UE muss entweder
fuer die exakt gebundene IAG-2-Familie einen wertidentischen vollstaendigen
Endzustand beider Kantengains herleiten oder die Gegenprognose als nicht
matched verwerfen. Ein nachtraeglicher Wechsel der Geschichten ist nicht
zulaessig.

Nur bei bestandenem IAG-2-Zustandsmatch darf ACM-1H verschiedenes `z` tragen
und unter derselben spaeteren Zwei-Kanten-Probe eine unterschiedliche
gemeinsame Skalierung vorhersagen. Der praktische Engineeringnutzen gegen
IAG-2 ist damit formulierbar, aber noch nicht geschlossen.

## Trennung der Pflichtbaselines

| Baseline | Gegenprognose der ausgewaehlten Familie |
|---|---|
| ACM-OFF | kein `z`, keine geschichtsabhaengige gemeinsame Skalierung |
| FG-2 | gleiche feste Skalierung fuer G und O |
| statischer Zweikantenoperator | gleiche Ausgabe bei wertidentischer aktueller Probe |
| IAG-2 | nur bei nachgewiesen wertidentischen getrennten Kantenzustaenden darf die gemeinsame Skalierung als Gegenprognose gelten |
| JLR-1 | zustandsunabhaengige Kontaktschreibung nach festem Leak |
| LCT-1 | autonomes Abklingen waehrend beteiligungsfreier Intervalle |
| T2-Kreuztransport | zusaetzliche Kreuzsuszeptibilitaet; nicht Teil der primaeren ACM-1H-Familie |

## Verwerfungsregeln

ACM-1H wird vor Implementierung gestoppt oder reduziert, wenn:

- T1 die S1-UC-Funktionsprognose nicht ohne Kreuztransport tragen kann;
- die G/O-Geschichten nicht mit identischen Einzelkantenmarginalen
  konstruierbar sind;
- IAG-2 trotz vollstaendig angeglichener Einzelkantenzustaende eine freie
  unterschiedliche Ausgabe erhalten darf;
- beteiligungsfreies Halten eine versteckte Uhr, Phase oder
  Ereignisinformation benoetigt;
- eine einzelne aktive Kante `z` oder den ACM-1-Feldanteil veraendert;
- der gemeinsame Modifikator die zwei Kanten unterschiedlich oder
  namensabhaengig skaliert;
- `e_bc` den primaeren Kantenbeitrag doppelt erhaelt;
- die gemeinsame Komposition von der Motiviterationsreihenfolge abhaengt;
- der resultierende Transport nicht passiv, endlich oder lokal quellenfrei
  gehalten werden kann;
- ein Negativbefund nachtraeglich durch T2 oder H2 repariert werden soll.

## Auditentscheidung

Gemeinsame getrennte Kantenskalierung traegt die gesamte in S1-UC gebundene
ACM-1-Funktion. Gekreuzter Transport besitzt zwar eine zusaetzliche
Kreuzprognose, sie ist fuer den freigegebenen Engineeringzweck aber nicht
notwendig. Beteiligungsfreies Halten ist gegenueber autonomem Abklingen die
sparsamere primaere Zustandsfamilie und laesst LCT-1 als klare Gegenbaseline
erhalten.

ACM-1H bleibt daher als genau eine minimale Engineeringfamilie offen. Die
IAG-2-Gegenprognose steht noch unter dem Pflichtgate eines exakten
vollstaendigen Baselinezustandsmatches. Es existieren weiterhin weder
Gleichung noch Parameter, Implementierung oder Funktionsbefund.

## Verbindliche Entscheidung

```text
S1_UD_ACM1H_COMMON_EDGE_SCALING_SELECTED_OVER_CROSS_TRANSPORT
PARTICIPATION_GATED_HOLD_SELECTED_OVER_AUTONOMOUS_LEAK
JOINT_PARITY_HISTORY_PAIR_BOUND_PENDING_EXACT_IAG2_STATE_MATCH
NO_EQUATION_NO_PARAMETERS_NO_IMPLEMENTATION_NO_TEST_NO_FIELD_RUN
```

## Naechster Schritt

Der einzige naechste Schritt ist S1-UE als statischer Dimensions-,
Minimalgleichungs-, Invarianz- und Kompositionsvertrag fuer ACM-1H. Er darf
symbolische Gleichungsformen, aber noch keine numerischen Werte,
Implementierung oder Ausfuehrung binden. Vorab festzulegen sind:

- dimensionslose Definition und exakter Wertebereich von `z`;
- donorbegrenzte, bereichserhaltende Zustandsfortschreibung ohne Clipping;
- gemeinsamer passiver Kantenmodifikator mit exaktem `z = 0`-Nullwert;
- symmetrische Komposition beider Motivvorschlaege auf `e_bc`;
- Halteidentitaet ohne Zwei-Kanten-Beteiligung;
- algebraische Passivitaets-, Spiegel- und Vorzeicheninvarianten;
- exakte IAG-2-Fortschreibung und den Nachweis oder die Verwerfung des
  vollstaendigen G/O-Baselinezustandsmatches.

Falls keine solche Minimalform ohne zusaetzlichen Zustand oder
Nachnormalisierung existiert, wird ACM-1H vor Implementierung gestoppt.
