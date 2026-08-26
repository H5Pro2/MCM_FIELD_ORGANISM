# S1-NU G2/D3 minimaler reiner Admissibilitaetsoperatorvertrag

## Status

S1-NU waehlt und bindet ausschliesslich eine minimale reine Operatorform fuer
die in S1-NM vorregistrierte Komponente `local_admissible_engagement`. Der
Schritt implementiert und berechnet nichts, bucht keinen Transfer und fuehrt
keinen Feldschritt aus.

Entscheidung:

```text
SELECT_G2_D3_CONSERVATIVE_FREE_MINUS_CONFIGURED_OPERATOR
```

## Gebundener Geltungsbereich

Der Operator gilt zunaechst nur fuer die direkte statische F1-Intervention auf
genau einer einzeln gueltigen D3-Kante. Der S1-NM-Probenzustand mit lokaler
Beteiligung `p=1.0` ist fest. Der Operator ist keine allgemeine Kontakt-,
Transfer-, Bildungs- oder Feldgleichung.

Eingabe sind ausschliesslich die bereits validierten lokalen Rollen:

```text
free
bound_configured
```

Kantenkennung, Traegerkennung, S/H, Adapter, Digest, Ergebnisrolle und
Fixture-ID duerfen den Sachwert nicht veraendern.

## Audit minimaler Operatorfamilien

### O0: nur freie Ressource

```text
A = free
```

O0 bleibt fuer C0 und C1 bitgleich und verletzt damit die vorregistrierte
negative `Delta_G2`-Prognose.

```text
STOP_O0_NO_G2_DIFFERENCE
```

### O1: C0/C1-Falltabelle

Eine feste Tabelle koennte unterschiedliche Werte ausgeben, wuerde die
Wirkung aber aus einem Rollenlabel statt aus der D3-Ressourcenanatomie bilden.

```text
STOP_O1_LABEL_LOOKUP_IS_FIXED_ADAPTER
```

### O2: normierte konfigurierte Fraktion

Eine Quotientenform mit `bound_configured / bound` ist endlich formulierbar,
benoetigt aber bereits eine Sonderregel fuer `bound=0` und eine nicht fuer F1
erforderliche Normierung.

```text
STOP_O2_NORMALIZED_RATIO_NOT_MINIMAL_FOR_F1
```

### O3: konservative Restzulassung

```text
A_D3 = max(0.0, free - bound_configured)
```

O3 verwendet nur zwei gleich dimensionierte lokale Ressourcenrollen, besitzt
keinen Parameter und ist fuer jede gueltige D3-Anatomie endlich und begrenzt:

```text
0.0 <= A_D3 <= free
```

Ausgewaehlt wird ausschliesslich O3.

## Technische Bedeutung

`A_D3` ist eine read-only obere Zulassungsgrenze fuer einen spaeteren atomaren
Transfer von `free` nach `bound`. Die Subtraktion veraendert weder `free` noch
`bound_configured` und wird nicht in das Ledger zurueckgeschrieben. Es entsteht
keine zweite Ressource und keine negative Buchung.

Die Operatorform behauptet nur: Bereits konfigurierte gebundene Ressource
begrenzt unter der festen F1-Probe die zusaetzlich lokal zulaessige
Beanspruchung. Wie `bound_configured` entsteht oder wieder abnimmt, bleibt
vollstaendig offen.

## Vorregistrierte F1-Werte

### C0

```text
free = 0.5
bound_configured = 0.0
A_C0 = max(0.0, 0.5 - 0.0) = 0.5
```

### C1

```text
free = 0.5
bound_configured = 0.5
A_C1 = max(0.0, 0.5 - 0.5) = 0.0
```

### Gerichtete Differenz

```text
Delta_G2 = A_C1 - A_C0 = -0.5
```

Damit erfuellt O3 die vor S1-NN gebundene Richtung `Delta_G2 < 0.0` ohne
Fit, Parameterwahl oder Rundungstoleranz.

### Gemischte Kontrollunterteilung

```text
free = 0.5
bound_configured = 0.25
A_MIXED = 0.25
```

Der gemischte Wert ist eine statische Kontrollprognose, keine
Abschwaechungs- oder Bildungstrajektorie.

## Null- und Randfaelle

Verbindlich gelten:

- `bound_configured=0` ergibt `A_D3=free`;
- `free=0` ergibt `A_D3=0`;
- `bound=0` erzwingt anatomisch `bound_configured=0` und damit `A_D3=free`;
- `bound_configured>=free` ergibt `A_D3=0`;
- wachsendes `bound_configured` darf bei festem `free` `A_D3` nie erhoehen;
- wachsende freie Ressource darf bei festem `bound_configured` `A_D3` nie
  verringern.

Nicht endliche, negative oder nicht validierte Rollen erreichen den Operator
nicht. Der Operator repariert, clippt oder normalisiert keine Eingabe; `max`
begrenzt nur den gueltigen berechneten Sachwert auf seine Nullgrenze.

## Aggregation, Ablation und Gegenprognosen

Die reine Dreirollenaggregation entfernt `bound_configured`. Ein aggregiertes
KFS-1-, DTS-1- oder T1-Record darf deshalb nicht an O3 uebergeben und ein
fehlendes D3-Feld nicht still als null ergaenzt werden. Die Gegenbaselines
sehen in C0 und C1 bitgleich `(free,bound,blocked)=(0.5,0.5,0.0)` und behalten
ihre gebundene Nullprognose:

```text
Delta_baseline = 0.0
```

Die reine G2-Ablation ueberfuehrt C1 exakt in C0. Danach gilt:

```text
A_ablated_C0 = 0.5
A_ablated_C1 = 0.5
Delta_G2_ablated = 0.0
```

Fixed Adapter, Leaky und Integrator erhalten in beiden direkten Armen ihre
bitgleichen vollstaendigen Vorzustaende. O3 darf weder in diese Baselines
kopiert noch als armweise verschiedener Adapter ausgegeben werden.

## Fail-Closed- und Verwerfungsgrenze

O3 wird gestoppt, wenn eine spaetere reine Implementierung:

- einen anderen Sachwert fuer C0, C1 oder MIXED liefert;
- ausser `free` und `bound_configured` weitere Sachwerte liest;
- aggregierte Records akzeptiert oder fehlende D3-Rollen ergaenzt;
- Eingaben oder Registry mutiert;
- einen Transfer bucht oder Feldzustand fortschreibt;
- Parameter, Lookup-Tabelle, Rollenlabel oder Ergebniswissen verwendet;
- die Wertebereichs- oder Monotoniegrenzen verletzt;
- bei reiner C1-Ablation eine Differenz behaelt.

Auch bei korrekter Implementierung bleibt G2 zu verwerfen, falls spaetere
faire Bildungsgeschichten zeigen, dass Fixed Adapter, Leaky oder Integrator
Bildung, Spaetwirkung, Abschwaechung, Interferenz und Loesung vollstaendig
reproduzieren.

## Aussagegrenze

S1-NU bindet nur eine statische direkte F1-Zulassungsfunktion. Die Formel ist
fuer sich ein einfacher zustandsabhaengiger Begrenzer und noch keine
eigenstaendige Substratfunktion. Es gibt keine endogene Bildung, Dynamik,
Feldwirkung, Musterbildung, Lernfunktion und keinen Befund zur hypothetischen
MCM-Memory.

## Naechster erlaubter Schritt

S1-NV darf ausschliesslich den isolierten Implementierungs-, Fixture- und
Testbudgetvertrag fuer O3 binden. Er muss Dateigrenze, reine API, exakte
C0/C1/MIXED-Erwartungen, Randfaelle, Aggregationsablehnung, Ablationsnull und
ein endliches Einmalausfuehrungsbudget vorab schliessen.

S1-NV darf O3 noch nicht implementieren oder ausfuehren und keine Transfer-,
Bildungs-, Abschwaechungs-, Interferenz- oder Feldgleichung einfuehren.
