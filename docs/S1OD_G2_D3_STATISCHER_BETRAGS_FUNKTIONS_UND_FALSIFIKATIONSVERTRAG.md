# S1-OD G2/D3 statischer Betrags-Funktions- und Falsifikationsvertrag

## Status

S1-OD bindet ausschliesslich die funktionalen Anforderungen an einen
spaeteren lokalen Umordnungsbetrag fuer die in S1-OC akzeptierte transiente
Grenzklassifikation. Der Schritt waehlt keine Gleichung, Rate, Schwelle,
Rundungsregel oder Parameter und implementiert oder berechnet keinen Betrag.

Entscheidung:

```text
G2_D3_LOCAL_CONTINUATION_REPARTITION_AMOUNT_FUNCTION_AND_FALSIFICATION_BOUND
```

## Technischer Ausgangspunkt

S1-OC kann eine vollstaendig gueltige lokale Zweiintervallgrenze passiv als
eines von drei Ereignissen klassifizieren:

```text
NO_PREDECESSOR
LOCAL_CONTINUATION
LOCAL_SWITCH
```

Der Beleg veraendert keinen D3-Zustand. S1-OD bestimmt nur, welche
Eigenschaften eine spaetere getrennte Betragsregel erfuellen muss, bevor eine
konservative D3-Zielprojektion ueberhaupt auswaehlbar wird.

## Drei getrennte Rollen

Ein spaeterer Bildungspfad muss drei technische Rollen getrennt halten:

1. Der akzeptierte S1-OC-Validator prueft Grenze und D3-Quelle und
   klassifiziert genau ein Ereignis.
2. Eine spaetere reine Betragsregel darf aus einer gueltigen Ereignisrolle und
   dem validierten lokalen D3-Vorzustand hoechstens einen Betrag bestimmen.
3. Ein nochmals getrennter konservativer Operator darf diesen Betrag erst
   nach vollstaendiger Zielvalidierung atomar committen.

Der S1-OC-Beleg ist kein Folgeeingang fuer sich selbst und kein persistenter
Kandidatenzustand. S1-OD hebt diese Sperre nicht auf.

Eine spaetere oeffentliche Betrags-API darf daher keinen extern gelieferten
S1-OC-Beleg akzeptieren. Sie muss die urspruenglichen kanonischen Grenz- und
D3-Bytes samt gebundenen Registries innerhalb desselben reinen Aufrufs durch
den akzeptierten Validator pruefen. Nur das dabei transient erhaltene
gueltige Ereignis darf intern an die Betragsermittlung weitergereicht werden.
Bei Rueckkehr bleibt hoechstens ein neuer passiver technischer Beleg; weder
Ereignis noch Grenzrecord werden zu einem Folge- oder Feldzustand.

## Zulaessige spaetere Eingangsrollen

Eine spaetere Betragsregel darf ausschliesslich lesen:

```text
validated event_role
pre-registered formation_enabled in {true,false}
pre.bound_unconfigured
pre.bound_configured
pre.free
pre.blocked
pre.capacity
```

`formation_enabled` ist ausschliesslich die vorregistrierte binaere
Bildungsablation und kein adaptiver Steuerwert. Kante und Feldreferenz duerfen
nur als bereits validierte Identitaetsbindung dienen, nicht als numerischer
Faktor. Die Kontaktorientierungen X und Y, Intervalldaten, Arm-ID,
H0-/H1-Kennung, Ergebniswerte und fruehere Belege sind keine zulaessigen
Betragsoperanden.

## Gebundene Nullfaelle

Fuer jeden gueltigen D3-Vorzustand muss spaeter exakt gelten:

```text
NO_PREDECESSOR   -> m = 0.0
LOCAL_SWITCH     -> m = 0.0
formation_off    -> m = 0.0
bound_unconfigured = 0.0 -> m = 0.0
invalid input    -> m = not_computable, no commit
```

Ein erster Kontakt oder Wechsel darf weder einen positiven Betrag noch eine
verdeckte negative Gegenbuchung erzeugen. Eine reine Bildungsablation setzt
nur die Betragsermittlung auf den Nullpfad; Grenzklassifikation, Kontakte und
aggregiertes Ledger bleiben unveraendert.

## Positive Fortsetzungsprognose

Fuer eine gueltige lokale Fortsetzung mit positiver verfuegbarer
`bound_unconfigured`-Ressource muss die spaetere ausgewaehlte Betragsfamilie
im gebundenen F2-Fixturbereich einen endlichen positiven Betrag liefern:

```text
LOCAL_CONTINUATION and pre.bound_unconfigured > 0.0
-> 0.0 < m <= pre.bound_unconfigured
```

Fuer die zwei Fortsetzungen in H1 und H1M muss vor Ausfuehrung sichergestellt
werden, dass beide vorgesehenen Commits ohne Clipping, Reparatur oder
Ressourcenverletzung definiert und positiv sind. Fuer den F2-Startwert folgt
deshalb rein funktional:

```text
0.0 < m_first < 0.5
0.0 < m_second <= 0.5 - m_first
```

S1-OD legt weder die Einzelbetraege noch einen Mindestabstand zwischen den
spaeteren Armwerten fest.

## Spiegel- und Verlaufsfreiheit

X/X und Y/Y muessen bei bitgleichem D3-Vorzustand denselben Betrag zulassen.
Da Orientierung kein Betragsoperand ist, folgt fuer die gespiegelt
identischen Ereignis- und D3-Zustandsfolgen:

```text
B_H1 = B_H1M
```

Diese Gleichheit ist eine technische Folge der gebundenen
Spiegelinvarianz. Sie ist keine Behauptung ueber allgemeine Feldsymmetrien.

Der Betrag darf weder von der Anzahl frueherer Fortsetzungen noch von einer
gespeicherten Kontakt- oder Ereignisfolge abhaengen. Unterschiedliche
spaetere Betraege duerfen nur aus unterschiedlichen gueltigen lokalen
D3-Vorzustaenden folgen.

## F2-Gesamtprognose

Alle drei F2-Geschichten beginnen mit:

```text
bound_unconfigured = 0.5
bound_configured = 0.0
```

Aus den gebundenen Ereignisfolgen muss eine spaetere zulaessige
Betragsfamilie vor der identischen Probe ergeben:

```text
H0:  NO_PREDECESSOR, SWITCH, SWITCH, SWITCH
     -> B_H0 = 0.0

H1:  NO_PREDECESSOR, CONTINUATION, SWITCH, CONTINUATION
     -> 0.0 < B_H1 <= 0.5

H1M: NO_PREDECESSOR, CONTINUATION, SWITCH, CONTINUATION
     -> B_H1M = B_H1
```

Damit bleibt die bereits gebundene gerichtete F2-Prognose erhalten, ohne
einen Betrag aus einem erwarteten Ergebnis abzuleiten.

## Konservative Betragsgrenze

Jeder spaetere Einzelcommit muss exakt folgende Zielidentitaeten erfuellen:

```text
post.bound_unconfigured = pre.bound_unconfigured - m
post.bound_configured = pre.bound_configured + m

post.free = pre.free
post.blocked = pre.blocked
post.capacity = pre.capacity

post.bound_unconfigured + post.bound_configured
= pre.bound_unconfigured + pre.bound_configured
```

Der Betrag ist lokal. Es gibt keine Reserve ausserhalb der Kante, keine
negative Ressource, keine Nachnormalisierung und keine globale
Ausgleichsbuchung.

## Anforderungen an eine spaetere Betragsfamilie

Eine in S1-OE auditierbare Familie muss gleichzeitig:

1. alle gebundenen Nullfaelle exakt tragen;
2. im F2-Fixturbereich fuer beide Fortsetzungen positiv und definiert sein;
3. jeden Betrag ohne Clipping innerhalb der aktuellen lokalen Restressource
   halten;
4. X/X und Y/Y bei gleichem D3-Vorzustand bitgleich behandeln;
5. deterministisch aus denselben erlaubten Eingangsrollen denselben Betrag
   liefern;
6. keine Kontaktfolge, Ereignishistorie oder Armkennung benoetigen;
7. kein S/H, keinen Adapteroutput und keinen spaeteren O3-Wert lesen;
8. keine D3-Rolle selbst veraendern oder einen Commit ausloesen;
9. eine reine Nullablation ohne Aenderung der Exposition erlauben;
10. eine vorab gebundene endliche Zahlen- und Rundungsdomane zulassen.

Eine neue Bezeichnung ersetzt keine dieser Anforderungen.

## Gegenbaselines und technische Abgrenzung

### Fixed Adapter

Ein fester Adapter besitzt keine D3-Unterteilung. Ein zustandsbehafteter
Adapter darf spaeter dieselbe transiente Ereignisrolle sehen und ist als
Gegenbaseline zu registrieren. Kann er mit einem Parametersatz den gesamten
spaeteren Lebenszyklus ebenso erklaeren, besitzt die Betragsfamilie keine
eigene Funktionsachse.

### Leaky und Integrator

Beide erhalten dieselbe vollstaendige kausale Vorgeschichte. S1-OD behauptet
nicht, dass eine diskrete Ereignisregel ihnen grundsaetzlich ueberlegen ist.
Der spaetere Kandidat bleibt nur weiterfuehrbar, wenn Bildung,
Abschwaechung, Interferenz und Kapazitaetsfreigabe gemeinsam eine eigene
Gegenprognose tragen.

### O3

O3 liest ausschliesslich einen bereits validierten D3-Zustand und begrenzt
die lokale Zulaessigkeit. O3 darf den Bildungsbetrag weder berechnen noch
rueckwirkend veraendern. Ein O3-Unterschied nach manuell gesetztem D3 ist
kein Bildungsbefund.

### Replay und Lookup

Ein Betrag aus H0-/H1-Kennung, Sequenzindex, Kontaktliste, Lookup-Tabelle oder
frueherem Beobachterbeleg ist unzulaessig. Eine solche Regel wird nicht als
lokale Bildung weitergefuehrt.

## Lebenszyklusgrenze

S1-OD bindet nur die Bildungsrichtung
`bound_unconfigured -> bound_configured`. Abschwaechung, konkurrierende
Interferenz, Loesung und erneute Kapazitaetsbeanspruchung werden weder
implementiert noch aus diesem Betrag abgeleitet.

Eine spaetere Bildungsfamilie darf diese offenen Funktionen jedoch nicht
durch eine zusaetzliche versteckte Ressource, irreversible
Kapazitaetsverletzung oder gespeicherte Kontaktgeschichte ausschliessen.
Die Gegenprognosen aus S1-HH bleiben gesondert pruefpflichtig.

## Verwerfungsbedingungen

Eine Betragsfamilie wird gestoppt, wenn mindestens eine Bedingung gilt:

- Erstkontakt, Wechsel, Ablation oder leere Restressource erzeugt einen
  Nichtnullbetrag;
- eine gueltige F2-Fortsetzung mit verfuegbarer Ressource bleibt ohne den
  vorab gebundenen Grund null;
- H1 oder H1M bleibt gegen H0 ungetrennt;
- Spiegelarme erhalten bei bitgleichem D3-Vorlauf verschiedene Betraege;
- ein Betrag ist negativ, nicht endlich oder groesser als die lokale
  Restressource;
- Clipping, Reparatur oder Nachnormalisierung ist erforderlich;
- aggregiertes `bound`, `free`, `blocked` oder `capacity` aendert sich;
- Orientierung, Armkennung, Sequenz, Ergebnis oder O3-Ausgabe wird als
  Betragsoperand benoetigt;
- der Betrag mutiert selbst einen Zustand oder persistiert ein Ereignis;
- eine nach Ergebniskenntnis geaenderte Formel, Rate oder Schwelle ist
  erforderlich.

Ein Stopp verwirft die jeweilige Betragsfamilie, nicht das gesamte
MCM-Wahrnehmungsfeld.

## Erlaubte spaetere Vertragstests

Vor einer Runtime duerfen spaeter nur reine Tests binden:

- exakte Nullfaelle;
- positive, endliche und lokal begrenzte F2-Fortsetzungsbetraege;
- Spiegelgleichheit;
- deterministische Wiederholung;
- konservative symbolische Vor-/Nachbilanz;
- Fail-Closed-Verhalten fuer ungueltige Rollen und Zahlen;
- Abwesenheit von Mutation, Persistenz, Feld-, O3-, Runner-, Medien-,
  Netzwerk- und I/O-Pfaden.

S1-OD selbst implementiert und fuehrt keinen solchen Test aus.

## Aussagegrenze

S1-OD bindet nur eine technische Funktions- und Falsifikationsgrenze fuer
einen spaeteren Umordnungsbetrag. Es gibt keine Betragsgleichung, keinen
Parameter, keinen berechneten oder gebildeten D3-Nachzustand, keine
Feldwirkung, keine Lernfunktion und keinen Befund zur hypothetischen
MCM-Memory.

## Naechster erlaubter Schritt

S1-OE darf ausschliesslich minimale lokale Betragsfamilien gegen S1-OD
auditieren und hoechstens eine Familie fuer einen spaeteren mathematischen
Vertrag weiterfuehren. Der Audit muss mindestens Nullfamilie, feste
Quantenfamilie, Vollumordnung und restressourcenbezogene Familie vergleichen.

S1-OE darf noch keinen Zahlenparameter, keine Rundungsgrenze, keine
Implementierung, keinen Commit, keine O3-Auswertung und keinen Feld- oder
Runtimelauf auswaehlen oder ausfuehren.
