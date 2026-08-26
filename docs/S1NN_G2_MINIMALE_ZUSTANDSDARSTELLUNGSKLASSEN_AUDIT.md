# S1-NN G2-Audit minimaler Zustandsdarstellungsklassen

## Status

S1-NN auditiert vier minimale Darstellungsfamilien fuer die in S1-NM
gebundene direkte G2-Intervention. Es wird hoechstens eine Klasse
weitergefuehrt. Der Schritt bindet keine Bildungsgleichung, Parameter,
Runtime, Feldrueckwirkung oder Ausfuehrung.

Entscheidung:

```text
SELECT_G2_CONSERVATIVE_BOUND_SUBPARTITION_CLASS_ONLY
```

## Auditkriterien

Jede Darstellung muss gleichzeitig:

1. C0 und C1 bei identischem S/H und identischem aggregiertem
   `free/bound/blocked`-Ledger tragen koennen;
2. lokal, endlich und fail-closed bilanzierbar sein;
3. ohne Rohdaten, Sequenz, Ereignisindex, Label, Reward oder Zielwert
   auskommen;
4. vollstaendig aus dem Feld- und DTS-1-Zustand getrennt ablatierbar sein;
5. die S1-NM-Messgrenze `0 <= local_admissible_engagement <= free`
   nicht verletzen;
6. kleiner sein als eine Mehrkanten- oder Netzwerkdarstellung, solange die
   Einkantenintervention keine solche Struktur benoetigt;
7. eine spaetere Abschwaechung, Loesung und erneute Bildung prinzipiell
   zulassen, ohne dafuer bereits eine Gleichung zu behaupten.

Eine geringe Zahl gespeicherter Werte allein ist kein Minimalitaetsnachweis.

## D1: binaeres Konfigurationsflag

### Form

```text
configuration in {C0, C1}
```

### Audit

Ein Flag kann die beiden F1-Arme unterscheiden und ist endlich. Es besitzt
aber keine eigene Bilanzbeziehung zur lokalen Ressource. Abschwaechung und
Loesung waeren nur diskrete Umschaltungen, und die S1-NM-Zulassungsdifferenz
muesste aus einer externen Falltabelle oder einem festen Adapter stammen.

### Entscheidung

```text
STOP_D1_BINARY_FLAG_IS_UNGROUNDED_SWITCH
```

D1 wird nicht weitergefuehrt.

## D2: unabhaengiger begrenzter Skalar

### Form

Eine zusaetzliche lokale Zahl besitzt einen festen endlichen Wertebereich,
aber keine algebraische Bindung an `free`, `bound` oder `blocked`.

### Audit

D2 kann C0/C1 und graduelle Abschwaechung darstellen. Ohne eine
Ressourcenbindung ist der Skalar jedoch ein zusaetzlicher Integrator- oder
Adapterkandidat. Seine Endlichkeit verhindert keine inhaltlich redundante
Akkumulation. Die eigene F1-Prognose waere nicht durch Anatomie, sondern erst
durch eine spaetere frei gewaehlte Ausgabefunktion begruendet.

### Entscheidung

```text
STOP_D2_INDEPENDENT_SCALAR_NOT_RESOURCE_GROUNDED
```

D2 wird nicht als eigenstaendige Darstellung weitergefuehrt.

## D3: konservative Unterteilung gebundener Ressource

### Form

Die vorhandene aggregierte Rolle `bound` wird intern in genau zwei
nichtnegative lokale Unterrollen zerlegt:

```text
bound = bound_unconfigured + bound_configured
```

Die Gesamtbilanz bleibt:

```text
capacity = free + bound_unconfigured + bound_configured + blocked
```

Der zusaetzliche Zustand ist damit weder neue Gesamtressource noch ein
unabhaengiger ungebundener Skalar. DTS-1 und T1 sehen weiterhin nur
`bound = bound_unconfigured + bound_configured`.

### C0/C1-Kompatibilitaet

Fuer den halbbelegten S1-NM-Vorzustand sind beide Rollenklassen prinzipiell
darstellbar:

```text
C0: bound_configured = 0
    bound_unconfigured = bound

C1: 0 < bound_configured <= bound
    bound_unconfigured = bound - bound_configured
```

Damit bleiben `free`, aggregiertes `bound` und `blocked` zwischen C0 und C1
identisch. Nur die interne Unterteilung unterscheidet sich.

### Audit

D3 erfuellt das F1-Interventionsgate mit genau einer zusaetzlichen
unabhaengigen lokalen Koordinate. Die Koordinate ist durch `bound` hart
begrenzt, verschwindet bei `bound=0` zwingend und kann ohne Aenderung der
Gesamtressource ablatiert werden. Eine spaetere Loesung kann
`bound_configured` reduzieren, ohne bereits festzulegen, wie dieser Wechsel
erfolgt.

D3 beweist noch keine eigene Funktion. Insbesondere ist noch offen, ob eine
faire Leaky-/Integratorbaseline dieselbe spaetere Bildung und Abschwaechung
reproduziert.

### Entscheidung

```text
PASS_D3_TO_STATIC_ANATOMY_AND_CONSERVATION_CONTRACT
```

## D4: relationale Mehrkantenstruktur

### Form

D4 speichert zusaetzliche Beziehungen zwischen mehreren inzidenten Kanten.

### Audit

Die S1-NM-Intervention besitzt genau eine Kante. Eine Mehrkantenrelation ist
dafuer weder erforderlich noch beobachtbar und wuerde Identitaeten,
Symmetrien und Bilanzregeln einfuehren, bevor eine Einkantenprognose technisch
steht. Soweit D4 nur Kantenbetraege speichert, ist es bereits DTS-1; soweit es
mehr speichert, ist es fuer F1 nicht minimal.

### Entscheidung

```text
STOP_D4_MULTI_EDGE_RELATION_PREMATURE_FOR_F1
```

D4 bleibt fuer diesen Kandidatenzweig geschlossen.

## Ausgewaehlte Darstellungsklasse

Weitergefuehrt wird ausschliesslich:

```text
G2_CONSERVATIVE_BOUND_SUBPARTITION
```

Die Klasse bindet nur folgende Struktur:

- eine bestehende lokale Kapazitaet;
- `free` und `blocked` unveraendert als aggregierte Rollen;
- `bound_unconfigured` und `bound_configured` als vollstaendige disjunkte
  Unterteilung der bisherigen `bound`-Rolle;
- keine weitere Ressource, Reserve oder Verlaufsablage.

Noch nicht gebunden sind:

- konkrete C1-Menge innerhalb des S1-NM-Ledgers;
- Bildung, Umwandlung, Abschwaechung oder Loesung;
- Abhaengigkeit der `local_admissible_engagement`-Komponente von der
  Unterteilung;
- Zahlenformat, Schema, Digest oder Fehlercodes;
- Runtime oder Feldkopplung.

## Abgrenzung zu DTS-1 und T1

DTS-1 und T1 tragen nur den aggregierten gebundenen Betrag. Zwei D3-Zustaende
mit gleichem `free`, gleichem aggregiertem `bound` und gleichem `blocked`,
aber verschiedener Unterteilung, sind fuer beide Baselines derselbe
vollstaendige Ressourcenstand.

Die Unterteilung ist nur dann eine eigene Kausalvariable, wenn ein spaeterer
reiner F1-Operator daraus die vorregistrierte negative
`Delta_G2`-Zulassungsdifferenz ableitet und diese Differenz bei Aggregation
oder Ablation exakt verschwindet. Andernfalls wird D3 verworfen.

## Fail-Closed-Grenze

Ein spaeterer D3-Anatomierecord ist bereits auf Vertragsniveau ungueltig bei:

- negativer oder nicht endlicher Unterrolle;
- `bound_unconfigured + bound_configured != bound`;
- veraenderter Gesamtressource gegenueber dem aggregierten Ledger;
- positivem `bound_configured` bei aggregiertem `bound=0`;
- zusaetzlicher versteckter Reserve oder unabhaengigem Skalar;
- Speicherung von S/H, Rohdaten, Sequenz, Label, Reward oder Readout;
- Mehrkantenbeziehung im Einkanten-F1-Vertrag;
- notwendiger Reparatur, Normalisierung oder Ergebnisanpassung.

## Aussagegrenze

S1-NN waehlt nur eine minimale statische Darstellungsklasse. Es gibt keine
G2-Anatomieimplementierung, keine Dynamik, keine Feldwirkung, keine
Lernfunktion und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-NO darf ausschliesslich die statische D3-Anatomie, lokale
Erhaltungsidentitaet, C0/C1-Gueltigkeit, verbotene Zustaende und
Anatomietests binden. Es darf noch keine Transfer- oder Bildungsgleichung,
keine Admissibilitaetsfunktion, Parameter, Runtime oder Feldrueckwirkung
waehlen.
