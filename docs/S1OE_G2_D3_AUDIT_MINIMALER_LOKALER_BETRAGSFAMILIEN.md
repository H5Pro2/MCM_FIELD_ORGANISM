# S1-OE G2/D3 Audit minimaler lokaler Betragsfamilien

## Status

S1-OE auditiert vier minimale Betragsfamilien gegen den statischen
S1-OD-Funktions- und Falsifikationsvertrag. Hoechstens eine Familie wird fuer
einen spaeteren mathematischen Vertrag weitergefuehrt. Der Schritt bindet
keinen Zahlenparameter, keine Rundungsregel, keine Implementierung, keinen
Commit und keine Ausfuehrung.

Entscheidung:

```text
SELECT_G2_D3_STRICT_INTERIOR_RESIDUAL_RELATIVE_REPARTITION_FAMILY_ONLY
```

## Auditkriterien

Eine weiterfuehrbare Familie muss gleichzeitig:

1. fuer Erstkontakt, Wechsel, Bildungsablation und leere Restressource exakt
   null bleiben;
2. fuer beide Fortsetzungen des F2-Gruppenarms positiv definiert sein;
3. fuer jede gueltige positive `bound_unconfigured`-Restressource definiert
   sein und jeden Betrag ohne Clipping innerhalb dieser Ressource halten;
4. X/X und Y/Y bei bitgleichem D3-Vorzustand gleich behandeln;
5. ohne Kontaktfolge, Ereigniszaehler, Arm-ID oder Ergebniswissen auskommen;
6. deterministisch und rein aus der aktuellen validierten lokalen
   Restressource ableitbar sein;
7. keinen Zustand selbst mutieren und keinen Commit ausloesen;
8. eine spaetere endliche, exakt vorregistrierbare Zahlen- und
   Rundungsdomane zulassen;
9. die F2-Prognose `B_H0=0` und `B_H1=B_H1M>0` tragen;
10. gegen einen angepassten Leaky- und zustandsbehafteten Adapterarm
    falsifizierbar bleiben.

Eine Familie wird nicht deshalb eigenstaendig, weil ihr Betrag in einer
Ressourcenrolle gespeichert werden koennte.

## A0: Nullfamilie

Signatur:

```text
m = 0 fuer jedes Ereignis und jeden D3-Vorzustand
```

Die Familie erfuellt alle Nullfaelle und ist konservativ. Sie kann jedoch
weder die erste noch die zweite Fortsetzung positiv abbilden. Damit bleiben
H0, H1 und H1M in D3 identisch.

```text
STOP_A0_ZERO_FAMILY_FAILS_POSITIVE_F2_CONTINUATION
```

## A1: Festes positives Quantum

Signatur:

```text
LOCAL_CONTINUATION -> ein fester positiver Betrag q
```

Ein global festes `q` ist fuer beliebig kleine positive Restressourcen nicht
total definiert. `q` muss dann entweder die Ressource ueberschreiten, durch
`min` oder Clipping repariert, unterhalb einer Schwelle auf null gesetzt oder
durch eine zweite Fallregel ersetzt werden.

Eine nur auf den F2-Startwert zugeschnittene Quantengrenze waere ausserdem
eine absolute Fixtureskala und noch keine allgemeine lokale Betragsfamilie.

```text
STOP_A1_FIXED_QUANTUM_REQUIRES_THRESHOLD_CLIP_OR_FIXTURE_SCALE
```

## A2: Vollumordnung

Signatur:

```text
LOCAL_CONTINUATION -> gesamte aktuelle bound_unconfigured-Ressource
```

Die erste Fortsetzung im Gruppenarm wuerde die Startressource vollstaendig
nach `bound_configured` ueberfuehren. Fuer die zweite Fortsetzung bliebe keine
positive Restressource. Damit verletzt A2 die vorab gebundene Forderung, dass
beide F2-Fortsetzungen positiv und ohne Sonderfall definiert bleiben.

Die sofortige Saettigung wuerde zudem jede spaetere graduelle
Fortsetzungspruefung in diesem Fixturbereich entfernen.

```text
STOP_A2_FULL_REPARTITION_EXHAUSTS_SECOND_F2_CONTINUATION
```

## A3: Strikt innere restressourcenbezogene Familie

Familiensignatur:

```text
NO_PREDECESSOR or LOCAL_SWITCH or formation_off -> m = 0

LOCAL_CONTINUATION and U > 0
-> m is a deterministic local function of U
-> 0 < m < U

U = pre.bound_unconfigured
```

Zusaetzlich muss die Familie skalenrelativ sein: Eine gemeinsame positive
Skalierung der lokalen D3-Betraege darf keinen absoluten Quantensprung oder
eine versteckte Schwelle einfuehren. Der spaetere mathematische Vertrag muss
diese Eigenschaft formal und fuer eine endliche Zahlendomaene binden.

A3 erfuellt auf Familienebene:

- erster Kontakt und alle Switches bleiben exakt null;
- die erste Fortsetzung laesst positive Restressource fuer die zweite uebrig;
- die zweite Fortsetzung bleibt positiv;
- Spiegelarme durchlaufen dieselben Ereignisrollen und D3-Betraege;
- kein Orientierungslabel oder Ereigniszaehler ist erforderlich;
- jeder spaetere Betrag liegt vor einem Commit strikt im Inneren der
  verfuegbaren Ressource.

```text
PASS_A3_TO_MATHEMATICAL_NUMERIC_AND_ROUNDING_CONTRACT
```

A3 wird als einzige Familie weitergefuehrt.

## Warum A3 noch keine Gleichung ist

S1-OE bindet nur:

```text
event-gated
local
deterministic
scale-relative
strictly interior to current residual resource
```

Nicht gebunden werden:

- eine konkrete Funktion von `U`;
- ein Anteil oder Zahlenwert;
- lineare, nichtlineare oder stueckweise Form;
- Flieszahlen-, Festkomma- oder Rationaldarstellung;
- Rundung, Unterlauf oder Mindestrest;
- ein Nachzustand oder Commitoperator.

Eine Formel darf erst in S1-OF nach separater numerischer
Erhaltungspruefung gebunden werden.

## F2-Folgen auf Familienebene

Fuer H0 sind alle drei Grenzereignisse nach dem Erstkontakt Switches. Daher
bleibt unabhaengig von der spaeteren A3-Form:

```text
B_H0 = 0.0
```

H1 und H1M besitzen je zwei Fortsetzungen. Die erste laesst wegen `m<U`
positive Restressource, die zweite liefert deshalb ebenfalls einen positiven
Betrag. Da beide Arme aus demselben D3-Zustand dieselbe Ereignisrollenfolge
durchlaufen:

```text
0.0 < B_H1 < 0.5
B_H1M = B_H1
```

Diese Aussagen sind Familienfolgen und keine berechneten Versuchswerte.

## Zwingende Gegenbaseline

Eine restressourcenbezogene wiederholte Umordnung kann im reinen
Bildungsabschnitt mathematisch durch einen Leaky-Skalar oder einen
zustandsbehafteten Ereignisadapter nachgebildet werden. S1-OE behauptet daher
keine eigenstaendige Funktionsachse aus F2 allein.

Vor einem spaeteren Kandidatenurteil muss mindestens eine Gegenbaseline
registriert werden, die:

- dieselben gueltigen Ereignisse sieht;
- mit einem Parametersatz alle H0-, H1- und H1M-Arme verarbeitet;
- ihren internen Zustand offenlegt;
- nicht armweise angepasst wird;
- dieselbe spaetere Probe erhaelt;
- gemeinsam auch Abschwaechung, Interferenz, Loesung und
  Kapazitaetsfreigabe erklaeren muss.

Wenn diese Baseline den gesamten gebundenen Lebenszyklus reproduziert, wird
A3 gestoppt. Eine konservative D3-Benennung allein reicht nicht als
Abgrenzung.

## Numerischer Engpass vor einer Formel

Die spaetere Rechnung muss gleichzeitig einen strikt positiven Betrag,
positive Restressource und exakte lokale Erhaltung darstellen. Allgemeine
binaere Fliesskommazahlen garantieren fuer wiederholte Subtraktion und
Addition nicht automatisch bitgleiche Bilanzidentitaeten.

S1-OF muss deshalb vor Implementierung festlegen:

- eine endliche kanonische Zahlendomaene;
- einen repraesentierbaren Familienparameter oder eine andere vollstaendig
  gebundene Funktionsform;
- die exakte Reihenfolge der arithmetischen Operationen;
- eine Rundungs- und Unterlaufregel ohne Clipping oder Nachnormalisierung;
- die Mindestrestbedingung fuer beide F2-Fortsetzungen;
- erwartete Einzel-, Rest- und Summenwerte fuer H0, H1 und H1M.

Kann dies nicht ohne Bilanzreparatur gebunden werden, wird A3 vor
Implementierung verworfen.

## Lebenszyklusgrenze

A3 beschreibt nur die Bildungsrichtung innerhalb der D3-Unterteilung. Die
Familie enthaelt keine Abschwaechungs-, Interferenz-, Loesungs- oder
Freigaberegel und darf keine dieser Funktionen sprachlich vorwegnehmen.

Eine spaetere Gesamtarchitektur muss fuer diese Rollen getrennte lokale
Ressourcenprognosen und Ablationen binden. Wird dafuer lediglich eine
Kontaktgeschichte, ein Replaypuffer oder ein ungebundener Integratorskalar
hinzugefuegt, wird der Zweig gestoppt.

## Verwerfungsbedingungen

A3 wird verworfen, wenn:

- keine endliche exakte Zahlendomaene ohne Bilanzreparatur gefunden wird;
- die erste F2-Fortsetzung die gesamte Restressource verbraucht;
- die zweite F2-Fortsetzung null oder nicht berechenbar wird;
- H1 und H1M bei bitgleichem Vorlauf verschiedene Werte erhalten;
- ein absoluter Fixturewert, eine Ergebnisschwelle oder Clipping erforderlich
  wird;
- andere Rollen als Ereignis und lokaler validierter D3-Vorzustand gelesen
  werden;
- Betragsermittlung selbst D3 oder Feld mutiert;
- ein externer S1-OC-Beleg als vertrauenswuerdige Folgeeingabe angenommen
  werden muss;
- eine registrierte Baseline spaeter den gesamten Funktionsvertrag mit einem
  Parametersatz reproduziert;
- die Formel nach Kenntnis eines Versuchsergebnisses angepasst werden muss.

## Aussagegrenze

S1-OE waehlt nur eine minimale Betragsfamilie fuer einen spaeteren
mathematischen Vertrag. Es gibt noch keine Betragsgleichung, keinen
Zahlenparameter, keinen D3-Nachzustand, keine Bildungsausfuehrung, keine
Feldwirkung, keine Lernfunktion und keinen Befund zur hypothetischen
MCM-Memory.

## Naechster erlaubter Schritt

S1-OF darf ausschliesslich einen statischen mathematischen, numerischen und
Rundungsvertrag fuer genau A3 binden. Er muss vor jeder Implementierung eine
kanonische endliche Zahlendomaene, genau eine Funktionsform, einen festen
Parameter, Operationen, F2-Erwartungswerte und Fail-Closed-Grenzen festlegen.

S1-OF darf noch keine Produktions- oder Testimplementierung, keinen
Umordnungscommit, keine O3-Auswertung und keinen Feld-, Runner- oder
Runtimelauf ausfuehren.
