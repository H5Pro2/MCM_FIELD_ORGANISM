# S1-YD: Statische Engineeringeinordnung und dynamische Baselineauswahl

## Ausgangspunkt

S1-YC hat den privaten S1-YB-Ablauf statisch geschlossen. S1-YD fuehrt
keinen Zustand, keine Probe und keinen Runner aus. Es werden weder Gleichung
noch Parameter, Implementierung oder Feldpfad eingefuehrt.

## Entwicklungswert von S1-YB

S1-YB zeigt belastbar, dass der private technische Grundpfad funktioniert:

- geordnete Bildung und spaetere Aktualisierung;
- begrenzte Kapazitaet und deterministische Verdraengung;
- unveraenderliche read-only Proben;
- atomare Receipts und Fail-Closed-Grenzen.

Der Vergleich war jedoch bewusst asymmetrisch: PPB-1 durfte sich waehrend
der Aktualisierungsphase veraendern, die Gegenbaseline blieb eingefroren.
Damit ist die technische Funktion bestaetigt, aber noch nicht ihre
Wettbewerbsfaehigkeit gegen eine ebenfalls aktualisierende Standardloesung.

## Vergleich der Baselinefamilien

| Familie | Einordnung fuer dieselbe Funktionsfrage |
|---|---|
| No-Memory oder statische Prototypbank | zu schwach, da keine Aktualisierung |
| Replay | unfair staerkeres Informationsbudget durch Rohhistorie |
| Nachhall oder gleitende Skalarstatistik | bildet mehrere Prototypen, Konflikt und Verdraengung nicht vollstaendig ab |
| Attraktor | fuehrt Mustervervollstaendigung als zusaetzliche Funktion ein |
| Reservoir | fuehrt einen hoeherdimensionalen Zeitverlauf und eine neue Readoutfrage ein |
| adaptive Online-Prototypbank | deckt mit minimaler Zusatzannahme denselben Aktualisierungsumfang ab |

## Genau eine ausgewaehlte Gegenbaseline

Ausgewaehlt wird `AOPB-1`: eine kapazitaetsgleiche adaptive
Online-Prototypbank. Sie ist eine Engineeringbaseline und kein neuer
Forschungskandidat.

PPB-1 und AOPB-1 muessen dieselben reduzierten Eingaben in derselben
Reihenfolge, dieselbe Bildungsgeschichte, dieselben
Aktualisierungsexpositionen, dieselbe Kapazitaet, dieselbe Distanz- und
Matchoberflaeche, dieselbe Konflikt- und Verdraengungsmoeglichkeit sowie
dieselben spaeteren read-only Proben erhalten. Rohhistorie, zusaetzliche
Slots, zusaetzliche Proben, Semantik und Feldzustand sind fuer beide
ausgeschlossen.

## Gegenprognose und Stoppgrenze

Die entscheidende Frage lautet:

> Bleibt fuer PPB-1 ein vorab gebundener Verhaltensvorteil bestehen, wenn
> die Gegenbaseline unter demselben Informations-, Kapazitaets- und
> Probebudget ebenfalls online aktualisieren darf?

Wenn AOPB-1 die verpflichtenden H1- bis H5-Verhaltensrollen reproduziert,
ist PPB-1 in diesem Funktionsumfang als normale adaptive
Online-Prototypkomponente erklaert. Weitere Mechanikarbeit an dieser
Differenz wird dann gestoppt. Nur ein vorab definierter Verhaltensunterschied,
der nicht aus Budget-, Parameter- oder Informationsasymmetrie entsteht,
kann eine weitere Untersuchung begruenden.

## Entscheidung und Grenze

Alle `21 von 21` statischen Auswahlrollen sind erfuellt:

`PASS_SELECT_AOPB1_AS_SINGLE_STRONGER_DYNAMIC_ENGINEERING_BASELINE`

S1-YD erzeugt keinen neuen Memory-, Wahrnehmungs- oder Feldwirkungsbefund.
Der kanonische Auditdigest lautet
`f80050b014c1fde4f176af67df040569c98072d7198121eb947771dd526efff0`.

## Naechster Schritt

S1-YE darf ausschliesslich statisch Nichtduplizierung, Informationsbudget
und beobachtbare Aequivalenz von AOPB-1 gegen PPB-1 binden. Erst dabei muss
geprueft werden, ob ueberhaupt eine faire, unabhaengige Gegenprognose
materialisierbar ist. Implementierung und Ausfuehrung bleiben gesperrt.
