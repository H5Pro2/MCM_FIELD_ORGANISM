# S2-HZ - Statischer Funktions- und Falsifikationsvertrag

## Status

`STATIC_TWO_AREA_CONFLICT_SIGNAL_CONTRACT_BOUND`

S2-HZ bindet ausschliesslich ein privates read-only Konflikt- und
Konsistenzsignal fuer gleichzeitig bereitgestellte `A_RECENT`- und
`B_STABLE`-Kontexte. Das Signal macht Ambiguitaet sichtbar. Es bestimmt keinen
Gewinner, fuellt keine Probe und veraendert keinen Speicherzustand.

Noch nicht freigegeben sind Implementierung, Tests, Runner, Zustandsaufrufe,
automatische Kontextwahl, API, Snapshot oder Feldintegration.

## Funktionsfrage

Fuer dieselbe validierte maskierte visuelle Probe und dasselbe validierte
S2-GI-Zwei-Bereich-Bundle wird getrennt bestimmt:

1. Ist der oeffentliche A-Kandidat fuer die sichtbaren Probenwerte verwendbar?
2. Ist der oeffentliche B-Kandidat fuer dieselben sichtbaren Werte verwendbar?
3. Wuerden beide verwendbaren Kandidaten auf den maskierten Positionen dieselbe
   oder eine unterschiedliche Ergaenzung liefern?

Das Ergebnis ist nur ein Signal ueber diese Beziehung. Es enthaelt keine
Auswahlentscheidung und keinen zusammengefuehrten Wahrnehmungszustand.

## Zulaessige Eingaben

Der spaetere Signalgeber darf genau zwei bereits validierte, unveraenderliche
Eingaben akzeptieren:

- ein `MaskedVisualProbe` mit 18 Positionen, neun sichtbaren und neun
  maskierten Werten;
- ein `TwoAreaContextBundle` mit exakt den kanonischen Bereichen
  `A_RECENT` und `B_STABLE`.

Probe- und Bundlequelle werden durch Probe-, Quellen-, Konfigurations-,
Composite-Zustands-, Bundle- und Vor-/Nachzustandsdigests gebunden. Die
Bundle-Invariante `prestate_digest == poststate_digest ==
composite_state_digest` muss vor und nach der Signalerzeugung gelten.

Nicht zulaessig sind Zielwerte, Falllabels, Sollentscheidungen, externe
Folgenkennungen, Rohbilder oder ein `requested_area`-Wert. Das Fehlen von
`requested_area` ist verbindlich: S2-HZ untersucht beide Bereiche symmetrisch
und adressiert keinen davon als bevorzugt.

## Bereichsrollen

### `A_RECENT`

A darf ausschliesslich den oeffentlichen `B4_RECENT`-Kandidaten aus
`AreaARecentFinding.recent_content` verwenden. Er muss
`AVAILABLE_COMPLETE`, eindeutig und als gemeinsamer AV-Bestand mit 26 Werten
gebunden sein; die visuellen Werte sind exakt die letzten 18 Werte.

`fast_internal` und die Kurzfolge bleiben transparente A-Evidenz, sind aber
weder Ersatzkandidat noch zweite A-Stimme.

### `B_STABLE`

B darf ausschliesslich den `TSPM_SLOW`-Kandidaten aus
`AreaBStableFinding.stable_content` verwenden. Der Befund darf
`AVAILABLE_COMPLETE` oder `AVAILABLE_PARTIAL` sein, muss aber genau eine
stabile visuelle Komponente mit 18 Werten enthalten.

`ABSENT_VALID` ist eine gueltige Abwesenheit und kein Fehler. Instabile,
mehrdeutige oder nicht visuelle Slow-Komponenten sind kein zulaessiger
B-Kandidat.

## Verwendbarkeit je Bereich

Jeder Bereich erzeugt genau einen internen, unveraenderlichen
`AreaApplicabilityFinding` mit:

- Bereichsrolle;
- `APPLICABLE`, `ABSENT_VALID` oder `VISIBLE_CONFLICT`;
- Bereichs-, Rollen-, Kandidaten- und Komponentendigest, soweit vorhanden;
- Probe- und Bundledigest;
- Digest der neun moeglichen Maskenergaenzungen nur bei `APPLICABLE`;
- identischen Vor-/Nachzustandsdigests;
- eigenem Findingdigest.

`APPLICABLE` gilt nur, wenn Kandidat und visuelle Komponente vollstaendig
gueltig sind und alle neun sichtbaren Probenwerte exakt den entsprechenden
Kandidatenwerten entsprechen.

`ABSENT_VALID` gilt nur bei einer kanonisch dokumentierten Abwesenheit ohne
Kandidat. `VISIBLE_CONFLICT` gilt bei einem strukturell gueltigen Kandidaten,
dessen sichtbare Werte der Probe widersprechen. Der Kandidat darf dann keine
Maskenergaenzung liefern.

Beschadigte, fremde, mehrdeutige oder widerspruechlich gebundene Belege sind
keine dieser drei Bereichslagen. Sie stoppen die gesamte Funktion fail-closed.

## Vier Signale

Das unveraenderliche Ergebnisobjekt `TwoAreaConflictSignal` darf exakt einen
der folgenden Statuswerte besitzen:

| Status | Vorab gebundene Bedingung |
| --- | --- |
| `CONSISTENT` | A und B sind `APPLICABLE`; ihre neun Maskenergaenzungen sind positionsweise identisch. |
| `CONFLICT` | A und B sind `APPLICABLE`; mindestens eine der neun Maskenpositionen unterscheidet sich. |
| `SINGLE_SOURCE` | Genau ein Bereich ist `APPLICABLE`; der andere ist `ABSENT_VALID` oder `VISIBLE_CONFLICT`. |
| `NO_CONTEXT` | Kein Bereich ist `APPLICABLE`; beide sind jeweils `ABSENT_VALID` oder `VISIBLE_CONFLICT`. |

Bei `CONFLICT` duerfen ausschliesslich die abweichenden Maskenpositionen und
die beiden Ergaenzungsdigests ausgewiesen werden. Die Werte werden nicht
verschmolzen. Bei `SINGLE_SOURCE` darf `applicable_areas` transparent den
einzigen verwendbaren Bereich nennen; dies ist keine Auswahl- oder
Priorisierungsempfehlung. Bei `NO_CONTEXT` bleiben die beiden getrennten
Abwesenheits- beziehungsweise Konfliktgruende sichtbar.

Das Ergebnis enthaelt verbindlich:

- Status und Signaldigest;
- Probe-, Quellen-, Bundle-, Konfigurations- und Zustandsdigests;
- A- und B-Findingdigest in kanonischer Reihenfolge;
- `applicable_areas` als leeres, ein- oder zweielementiges Tupel;
- abweichende Maskenpositionen nur bei `CONFLICT`;
- `selected_area = None`, `recommended_area = None` und
  `automatic_selection = None`;
- Ressourcenledger;
- identische Vor-/Nachzustandsdigests.

Es gibt kein Feld `BEST_MEMORY`, keine Rangzahl, kein Konfidenzgewicht und
keinen kombinierten Ausgabewert.

## Starke Direktbaseline

Die staerkste Engineeringbaseline ist ein unabhaengiger direkter Vergleich
der beiden rollenadressierten visuellen Kandidaten:

1. dasselbe Bundle und dieselbe Probe validieren;
2. A und B unabhaengig gegen die sichtbaren Positionen pruefen;
3. fuer jeden verwendbaren Kandidaten ausschliesslich die neun maskierten
   Werte als private Vergleichsprojektion bilden;
4. beide Projektionen positionsweise vergleichen;
5. dieselbe Vier-Status-Tabelle anwenden.

Die Baseline darf weder den S2-HZ-Signalgeber noch dessen Zwischen- oder
Endergebnis aufrufen beziehungsweise uebernehmen. Umgekehrt darf S2-HZ kein
Baselineergebnis verwenden. Beide Arme erhalten identische funktionale
Budgets und dieselben Eingabedigests.

Gleichheit mit dieser Direktbaseline ist der erwartbare Engineeringbefund.
Sie falsifiziert den praktischen Nutzen des Signals nicht, schliesst aber
einen Claim auf einen eigenstaendigen MCM-spezifischen Mechanismus aus.

## Gebundene Fallmatrix

Ein spaeterer neutraler Vertragstest muss mindestens folgende symmetrische
Faelle materialisieren:

| Fall | A | B | Erwartetes Signal |
| --- | --- | --- | --- |
| C1 | passend X | passend X | `CONSISTENT` |
| C2 | passend X | passend Y | `CONFLICT` |
| C3 | passend X | `ABSENT_VALID` | `SINGLE_SOURCE` |
| C4 | `ABSENT_VALID` | passend X | `SINGLE_SOURCE` |
| C5 | `ABSENT_VALID` | `ABSENT_VALID` | `NO_CONTEXT` |
| C6 | passend X | sichtbarer Konflikt | `SINGLE_SOURCE` |
| C7 | sichtbarer Konflikt | passend X | `SINGLE_SOURCE` |
| C8 | sichtbarer Konflikt | sichtbarer Konflikt | `NO_CONTEXT` |

Zusaetzlich sind Rollentausch und Kandidatentausch zu pruefen. Der Status darf
sich nur aufgrund der beiden Bereichslagen und ihrer Maskenergaenzungen
aendern, niemals aufgrund der Reihenfolge A/B, einer Fall-ID oder eines
Sollwerts.

Mindestens je eine Einzelmutation von Probe-, Bundle-, Zustands-, Bereichs-,
Kandidaten-, Komponenten- und Findingdigest muss vor jeder Signalausgabe
fail-closed enden. Eine gueltige Abwesenheit darf dabei nicht als Beschaedigung
behandelt werden; eine Beschaedigung darf nicht zu `ABSENT_VALID` herabgestuft
werden.

## Ressourcen- und Read-only-Grenze

Die spaetere Implementierung muss folgende endliche Obergrenzen einhalten:

```text
validierte Proben             = 1
validierte Zwei-Bereich-Bundle = 1
Bereichslookups               = 2
Kandidatenreferenzen          <= 2
Komponentenreferenzen         <= 2
sichtbare Vergleiche          <= 18
private Maskenprojektionen    <= 2
projizierte Maskenwerte       <= 18
bereichsuebergreifende Vergleiche <= 9
Signalobjekte                 = 1
Speicher- oder Lernaufrufe    = 0
```

Validierungs-, Vergleichs- und Digestarbeit muss fuer S2-HZ und Direktbaseline
getrennt und vollstaendig gezaehlt werden. Ein fehlender Kandidat reduziert
die tatsaechliche Arbeit, erhoeht aber kein anderes Budget. Die konkrete
Implementierungsbindung muss die noch offenen Digest- und Serialisierungszahlen
vor Code oder Ausfuehrung exakt materialisieren.

Vor und nach beiden Bereichspruefungen muessen Probe-, Bundle-, B4-, Fast-,
Slow- und Composite-Zustandsdigests identisch sein. Der Signalgeber darf keine
Speicher-, Rezeptor-, Projektions- oder Lernfunktion aufrufen.

## Nichtzirkularitaet

Der zulaessige Digestgraph lautet:

```text
validierte Probe + validiertes S2-GI-Bundle
-> A-Anwendbarkeitsbefund
-> B-Anwendbarkeitsbefund
-> symmetrischer Maskenvergleich
-> TwoAreaConflictSignal

dieselben unabhaengigen Eingabewurzeln
-> direkte A-Pruefung + direkte B-Pruefung
-> BaselineSignal

vorab versiegelte Sollmatrix + beide fertigen Signale
-> spaeterer reiner Auswertungsbefund
```

Kein Anwendbarkeitsbefund darf den anderen als Quelle verwenden. Sollstatus,
Zielwerte und Baselineergebnis duerfen erst dem spaeteren Auswerter bekannt
sein. Ein Rollen- oder Kandidatendigest darf nicht aus dem erwarteten Signal
rekonstruiert werden.

## Falsifikation und methodische Ungueltigkeit

Bei vollstaendig gueltiger Beweiskette ist die Funktion falsifiziert, wenn
mindestens eines gilt:

- die Vier-Status-Tabelle wird in einem gebundenen Fall verletzt;
- A/B-Tausch veraendert ein symmetrisch gleiches Ergebnis;
- `CONSISTENT` wird trotz verschiedener Maskenergaenzungen ausgegeben;
- `CONFLICT` wird trotz identischer Maskenergaenzungen ausgegeben;
- `SINGLE_SOURCE` oder `NO_CONTEXT` erfindet eine fehlende Ergaenzung;
- ein Ergebnis enthaelt Gewinner, Rangfolge, Verschmelzung oder Rueckfall;
- S2-HZ und die Direktbaseline unterscheiden sich bei gleichen gueltigen
  Eingaben;
- ein Probe-, Bundle- oder Speicherzustand wird veraendert.

`NOT_EVALUABLE` gilt dagegen bei Typ-, Schema-, Quellen-, Probe-,
Dimensions-, Masken-, Status-, Owner-, Digest-, Ressourcen-, Read-only- oder
Aufzeichnungsbruch. Beschaedigte Belege duerfen niemals als funktionales
`NO_CONTEXT` interpretiert werden.

Der maximal zulaessige positive Befund lautet:

```text
S2HZ_TWO_AREA_CONFLICT_SIGNAL_VALID_DIRECT_COMPARISON_EXPLAINS
```

Er bestaetigt ausschliesslich Ambiguitaetstransparenz zwischen zwei
bereitgestellten perzeptiven Kontextbereichen. Er belegt keine automatische
Kontextwahl, keine Relevanzentscheidung, keine neue Memory-Mechanik und keine
MCM-Feldwirkung.

## Freigabegrenze

S2-HZ ist mit diesem Dokument statisch gebunden. Der naechste zulaessige
Schritt ist ein enger statischer Materialisierbarkeits- und
Nichtzirkularitaetsaudit der konkreten vorhandenen S2-GI-Datentypen, der
Bereichsabwesenheiten, der Fallmatrix und der exakten Ressourcenformen.

Implementierung, Tests und Ausfuehrung bleiben bis zu einer gesonderten
Freigabe gesperrt.
