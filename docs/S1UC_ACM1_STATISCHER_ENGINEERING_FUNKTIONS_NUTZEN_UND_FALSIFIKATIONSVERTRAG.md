# S1-UC: ACM-1 statischer Engineering-Funktions-, Nutzen- und Falsifikationsvertrag

## Ausdrueckliche Richtungsentscheidung

Nach dem RFM-1-Zweigstopp in S1-UB ist folgende neue Zielsetzung fachlich
freigegeben:

> ACM-1 wird als MCM-kompatibles Engineeringmodul weiter untersucht. Seine
> Reduzierbarkeit auf einen begrenzten skalaren adaptiven Motivtransport wird
> akzeptiert. Implementierung und Feldlaeufe bleiben gesperrt.

Diese Entscheidung oeffnet keinen RFM-1-Kandidatenzweig und behauptet keine
neue Mechanik. Sie erlaubt nur die technische Untersuchung eines bewusst
konventionellen adaptiven Feldbausteins.

## Auftrag und Grenze

S1-UC bindet vor einer mathematischen Form:

- den praktischen Zweck von ACM-1 im MCM-Wahrnehmungsfeld;
- seine kleinste funktionale Prognose;
- Nutzenkriterien gegen einfachere Engineeringbaselines;
- Null-, Symmetrie-, Passivitaets- und Abschaltgrenzen;
- Verwerfungsbedingungen vor Implementierung.

S1-UC enthaelt keine Dynamikgleichung, Rate, numerischen Parameter,
Runtimeaenderung, Implementierung, Testausfuehrung oder Feldlauf.

## Technischer Zweck

ACM-1 soll pruefbar machen, ob ein lokal begrenzter Zwei-Kanten-Zustand die
vorhandene passive Feldweiterleitung kontrolliert geschichtsabhaengig
umformen kann, ohne den primaeren Feldkern, seine Geometrie oder seine
Rezeptorschnittstellen zu ersetzen.

Der erwartete Engineeringnutzen ist eng:

- gemeinsam auftretende signed Kantenlagen koennen die spaetere lokale
  Transportempfaenglichkeit desselben Motivs verschieben;
- gegenlaeufige spaetere Feldlagen koennen diese Verschiebung veraendern;
- die Wirkung bleibt lokal, begrenzt, passiv und direkt ablatierbar;
- der vollstaendig deaktivierte Pfad bleibt exakt der vorhandene Feldkern.

ACM-1 speichert keine Eingangsrohdaten, Labels oder Ereignisfolgen. Der
Baustein ist kein nachgeschaltetes Archiv und kein Zielsystem.

## Kleinste Zustandsrolle

ACM-1 besitzt pro kanonischem Zwei-Kanten-Motiv genau einen begrenzten signed
Skalar `z`.

`z` ist funktional identisch mit dem S1-UA-Rest `rho`. Die Bezeichnung `z`
trennt die moegliche kompakte Engineeringdarstellung von der weiterhin als
Diagnoseinfrastruktur erhaltenen RFM-1-Tafel.

Verbindlich gilt:

- `z = 0` ist der relationsfreie Zustand;
- positives `z` bezeichnet einen Ueberschuss gleichgerichteter
  Zwei-Kanten-Beteiligung;
- negatives `z` bezeichnet einen Ueberschuss gegengerichteter
  Zwei-Kanten-Beteiligung;
- seine zulaessigen Grenzen ergeben sich aus dem gebundenen endlichen
  Zustandsintervall;
- es gibt keinen zweiten Motivskalar, Zaehler, Phasencode oder
  Ereignispuffer.

Die `2x2`-Tafel darf spaeter fuer Audit, Intervention und Rekonstruktion
verwendet werden. Sie darf nicht parallel als zweite unabhaengige
Zustandsquelle fortgeschrieben werden.

## Funktionsprognose

Die kleinste ACM-1-Prognose lautet:

```text
identischer aktueller Feld-, S/H-, Rezeptor- und Geometriezustand
+ identische aktuelle Einzelkantenwerte
+ unterschiedliche gueltige z-Vorzustaende
+ identischer Zwei-Kanten-Kontakt
-> unterschiedliche passive lokale Feldfortsetzung
```

Die Differenz muss am Motiv und gegebenenfalls an direkt nachgelagerten
Knoten messbar sein. Sie darf nicht aus einem geaenderten Rezeptorwert,
Knotennamen, globalen Selektor oder armweisen Parameter entstehen.

Der Zustandstausch muss die Felddifferenz mitnehmen. Die Neutralisierung auf
`z = 0` muss den relationalen Zusatzbeitrag entfernen.

## Bildung und Gegenwirkung

Die qualitative Zustandsentwicklung bleibt an S1-UA gebunden:

- gleichgerichtete aktuelle Beteiligung beider Motivkanten bewegt `z` in
  positive Richtung;
- gegengerichtete aktuelle Beteiligung beider Motivkanten bewegt `z` in
  negative Richtung;
- eine einzelne aktive Kante veraendert `z` nicht;
- die endlichen Zustandsgrenzen werden ohne Clipping oder Nachnormalisierung
  eingehalten;
- eine gegenlaeufige Paritaetsgeschichte kann einen vorhandenen Zustand zur
  Neutralitaet und gegebenenfalls darueber hinaus bewegen.

Diese Gegenwirkung ist eine normale Folge lokaler Feldbeteiligung. Sie darf
nicht als gesonderte Loesch-, Reset- oder Trainingsphase implementiert
werden.

S1-UC bindet noch nicht, ob ohne Zwei-Kanten-Beteiligung ein passives
Abklingen zulaessig oder erforderlich ist. Diese Frage muss als getrennte
konstitutive Familie gegen einen gehaltenen Zustand verglichen werden.

## Feldwirkung

ACM-1 darf nur den vorhandenen passiven Transport der beiden Motivkanten
zustandsabhaengig umformen. Dabei gilt:

- `z = 0` erzeugt keinen ACM-1-Zusatzbeitrag;
- passendes Vorzeichen von `z` und aktueller Paritaet darf vorhandenen
  passiven Transport verstaerken;
- entgegengesetztes Vorzeichen darf ihn begrenzt abschwaechen;
- der kombinierte lokale Transport bleibt quellenfrei und passiv;
- eine Kante ohne aktuelle Feldtendenz wird nicht durch ACM-1 aktiviert;
- Feld- und Zustandsvorschlag entstehen aus demselben abgeschlossenen
  Vorzustand und werden nur gemeinsam committed.

Ob die Umformung durch gemeinsame Kantenskalierung oder einen passiven
gekreuzten Zwei-Kanten-Operator erfolgt, bleibt in S1-UC offen.

## Exakte Null- und Abschaltgrenzen

| Lage | Verbindliche ACM-1-Folge |
|---|---|
| ACM-1 vollstaendig aus | bitgleicher primaerer Feldkern; kein `z`-Zustand |
| `z = 0` | kein relationaler Feldzusatz |
| uniformes lokales Feld | kein Zustands- und kein Feldvorschlag aus ACM-1 |
| nur eine aktive Motivkante | keine ACM-1-Transaktion |
| Nullintervall | kein Zustands- und kein Feldcommit |
| kein neuer Rezeptorkontakt, aber internes Zwei-Kanten-Feld | lokale ACM-1-Transaktion bleibt prinzipiell zulaessig |
| ungueltiger Zustand oder Vorschlag | atomarer Abbruch ohne Teilausgabe |

Der Abschaltpfad darf weder einen neutralen Container anlegen noch Digests,
Snapshots oder API-Payloads des vorhandenen Feldkerns veraendern.

## Engineeringbaselines

ACM-1 muss nicht gegen beliebige allgemeine Zustandsmodelle eigenstaendig
sein. Sein praktischer Mehrwert wird nur gegen einfachere, konkret gebundene
Module bewertet:

| Baseline | Einfachere Erklaerung oder Umsetzung |
|---|---|
| FG-2 fester Zwei-Kanten-Gain | eine feste lokale Skalierung reicht ohne Zustand |
| IAG-2 unabhaengige adaptive Kantengains | zwei getrennte Kantenwerte reichen ohne gemeinsamen Paritaetszustand |
| JLR-1 passive Joint-Retention | ein zustandsunabhaengiger Schreiber plus fester Readout reicht |
| LCT-1 leaky Korrelationstrace | ein linear passiv abklingender Paritaetsskalar reicht |
| statischer Zweikantenoperator | nur die aktuelle signed Kantenlage bestimmt den Feldbeitrag |
| ACM-OFF | der unveraenderte primaere Feldkern reicht |

ACM-1 darf als Engineeringmodul nur weitergefuehrt werden, wenn mindestens
eine vorab gebundene praktische Funktion gegen FG-2, IAG-2 und den statischen
Operator uebrig bleibt. LCT-1 und JLR-1 bleiben Pflichtvergleich fuer die
spaetere Wahl von Halten oder Abklingen.

## Praktische Gegenprognosen

### Gegen FG-2 und statischen Operator

Zwei wertidentische aktuelle Feldlagen mit unterschiedlichem `z` muessen
unter derselben Probe unterschiedliche passive Fortsetzungen erzeugen. Eine
zustandslose Baseline muss beide gleich fortsetzen.

### Gegen IAG-2

Zwei Geschichten muessen dieselben getrennten Kantenzustandswerte tragen
koennen, waehrend ihr gemeinsamer Paritaetszustand verschieden ist. Nur dann
darf ACM-1 eine andere Motivfortsetzung liefern. Ist diese matched Trennung
nicht konstruierbar, reichen unabhaengige adaptive Kantengains.

### Gegen JLR-1

Unter demselben aktuellen Zwei-Kanten-Kontakt muss die Zustandsfortschreibung
vom noch verfuegbaren Abstand des vorhandenen `z` zur jeweiligen
Zustandsgrenze abhaengen. JLR-1 sagt nach seinem festen Leak dieselbe passive
Schreibkomponente voraus.

### Gegen LCT-1

Halten und passives Abklingen muessen vor einer mathematischen Wahl als zwei
getrennte Familien behandelt werden. Ein spaeterer Nutzenbefund darf nicht
durch nachtraegliche Wahl der guenstigeren Familie entstehen.

## Mess- und Interventionsrollen vor Mathematik

Eine spaetere mathematische Vorregistrierung muss mindestens binden:

- vollstaendigen abgeschlossenen Feld- und `z`-Vorzustand;
- beide aktuelle Kantenbeteiligungen und ihre Paritaetsklasse;
- Zustandsvorschlag, Feldvorschlag und gemeinsamen Ursprungsdigest;
- getrennte aktuelle Kantenwerte und IAG-2-Zustaende;
- `z`-Tausch, `z`-Neutralisierung und ACM-OFF;
- Spiegelung und gemeinsamen Vorzeichenwechsel;
- lokale Quellen-, Passivitaets- und Wertebereichsbilanz;
- identische Exposition und einen Parametersatz je Modellklasse;
- getrennte Rohoutputs vor jeder Comparatorentscheidung.

Ein unterschiedlicher Zustandsdigest ohne unterschiedliche technische
Feldfunktion ist kein Engineeringnutzen.

## Verwerfungsbedingungen

ACM-1 wird vor Implementierung gestoppt oder auf eine einfachere Baseline
reduziert, wenn:

- ein fester Zwei-Kanten-Gain alle gebundenen Feldfortsetzungen reproduziert;
- zwei unabhaengige adaptive Kantengains jede matched Motivwirkung
  reproduzieren;
- die Wirkung nur aus aktueller Kantenlage ohne `z` entsteht;
- `z` lediglich geschrieben wird, aber keine passive Feldfortsetzung
  veraendert;
- eine einzelne aktive Kante Zustand oder Feldwirkung ausloest;
- `z = 0` einen relationalen Zusatzbeitrag erzeugt;
- Passivitaet nur durch Clipping, Reset oder globale Normalisierung entsteht;
- ein zweiter Zustand, Label, Sequenzpuffer oder Ergebniszugriff benoetigt
  wird;
- ACM-OFF den primaeren Feldkern oder seine Serialisierung veraendert;
- Spiegelung, Vorzeichenwechsel oder Motiviterationsreihenfolge das
  fachliche Ergebnis unzulaessig veraendern.

Ein Negativbefund darf nicht durch Umbenennung von RFM-1 oder Erweiterung der
Zustandsdimension innerhalb desselben Schritts repariert werden.

## Vertragsentscheidung

ACM-1 besitzt eine klar begrenzte Engineeringfrage: Ein gemeinsamer
begrenzter Paritaetszustand koennte lokale passive Feldweiterleitung
geschichtsabhaengig umformen und dadurch eine Funktion tragen, die ein fester
Gain, ein statischer Operator oder zwei unabhaengige Kantenzustaende nicht
gleichwertig abbilden.

Das ist noch kein Nutzenbefund. Die naechste statische Stufe muss zuerst
entscheiden, ob getrennte Skalierung oder gekreuzter passiver Transport fuer
diese Funktion minimal erforderlich ist und ob Halten oder Abklingen als
primaere Familie vorregistriert wird.

## Verbindliche Entscheidung

```text
S1_UC_ACM1_CONVENTIONAL_ENGINEERING_DIRECTION_EXPLICITLY_BOUND
BOUNDED_JOINT_PARITY_STATE_WITH_PASSIVE_FIELD_FUNCTION_CONTRACT_BOUND
FG2_IAG2_JLR1_LCT1_AND_STATIC_OPERATOR_ENGINEERING_BASELINES_BOUND
NO_EQUATION_NO_PARAMETERS_NO_IMPLEMENTATION_NO_TEST_NO_FIELD_RUN
```

## Naechster Schritt

Der einzige naechste Schritt ist S1-UD als statischer Minimalfamilien-,
Halten-gegen-Abklingen- und Engineeringreduktionsaudit. Er muss noch ohne
Parameter, Implementierung oder Ausfuehrung entscheiden:

- ob gemeinsame getrennte Kantenskalierung die S1-UC-Funktion bereits
  vollstaendig traegt;
- ob ein gekreuzter passiver Zwei-Kanten-Operator eine zusaetzliche
  vorab messbare Gegenprognose besitzt;
- ob der `z`-Zustand kontaktfrei gehalten oder passiv abklingend als
  primaere Familie untersucht wird;
- welche genau eine Minimalfamilie gegen FG-2, IAG-2, JLR-1 und LCT-1
  weitergefuehrt werden darf.

Bleibt keine praktische Gegenprognose gegen die einfacheren Module, wird
ACM-1 vor einer Gleichung gestoppt.
