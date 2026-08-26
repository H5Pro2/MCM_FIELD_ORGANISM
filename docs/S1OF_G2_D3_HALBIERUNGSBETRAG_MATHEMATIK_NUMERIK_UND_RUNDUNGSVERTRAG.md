# S1-OF G2/D3 Halbierungsbetrag: Mathematik-, Numerik- und Rundungsvertrag

## Status

S1-OF bindet ausschliesslich die statische mathematische und numerische Form
fuer die in S1-OE ausgewaehlte strikt innere restressourcenbezogene Familie
A3. Gebunden werden ein fester dyadischer Parameter, die exakte
Rechendomaene, Operationsordnung, F2-Zielwerte und Fail-Closed-Grenzen.

Der Schritt implementiert keine Produktions- oder Test-API, erzeugt keinen
D3-Nachzustand und fuehrt keinen Commit, keine O3-Auswertung und keinen Feld-
oder Runtimelauf aus.

Entscheidung:

```text
G2_D3_CONTINUATION_RESIDUAL_HALVING_MATHEMATICS_AND_EXACT_NUMERIC_DOMAIN_BOUND
```

## Notwendige Praezisierung von S1-OE

Eine endliche Maschinendarstellung besitzt einen kleinsten positiven Wert.
Fuer diesen Wert kann kein ebenfalls darstellbarer Betrag strikt zwischen
null und der Restressource liegen. Die universelle Formulierung ueber jede
positive maschinell darstellbare Restressource waere daher unerfuellbar.

S1-OF bindet stattdessen:

```text
gueltiger D3-Zustand
+ Wert liegt in der vorab definierten exakten Operationsdomaene
-> Betrag ist definiert

gueltiger D3-Zustand ausserhalb dieser Operationsdomaene
-> amount = not_computable
-> kein Zielzustand
-> kein Commit
```

Die Korrektur erweitert keinen Claim und passt keinen Ergebniswert an. Sie
schliesst einen numerisch unmoeglichen Randfall vor Implementierung.

## Gebundene mathematische Form

Bezeichnungen:

```text
U = pre.bound_unconfigured
C = pre.bound_configured
rho = 1/2
```

Die einzige ausgewaehlte Betragsform lautet:

```text
after complete boundary and D3 validation:

formation_enabled = false -> m = 0
event in {NO_PREDECESSOR, LOCAL_SWITCH} -> m = 0
U = 0 -> m = 0

formation_enabled = true
and event = LOCAL_CONTINUATION
and U > 0
and exact_domain = true
-> m = rho * U = U / 2
```

Eine unbekannte oder nicht validierte Ereignisrolle erreicht keinen Nullpfad,
sondern scheitert vor der Betragsermittlung mit `not_computable`.

`rho=1/2` ist ein vorab gewaehlter technischer Parameter. Er wurde nicht aus
einem Versuchsergebnis angepasst. Andere Anteile, Raten oder eine spaetere
Optimierung sind fuer diese Familie gesperrt.

## Begruendung der Auswahl

Der Faktor `1/2` ist die einfachste symmetrische dyadische Innenaufteilung mit den
fuer F2 erforderlichen Eigenschaften:

- fuer jedes positive U in der exakten Domaene gilt `0<m<U`;
- nach dem ersten F2-Ereignis bleibt positive Restressource;
- die zweite F2-Fortsetzung bleibt ohne Schwelle positiv;
- es gibt kein absolutes Quantum und keine Fixtureskala;
- X/X und Y/Y verwenden dieselbe Operation;
- die F2-Werte sind in binaerer Gleitkommadarstellung exakt repraesentierbar.

Diese Einfachheit ist keine Evidenz fuer eine besondere natuerliche
Mechanik. Sie minimiert nur den ersten kontrollierten mathematischen
Kandidaten.

## Kanonische Zahlendarstellung

Das akzeptierte D3-Schema liest kanonische JSON-Zahlen als Python-`int` oder
als binary64-`float`. Die positive S1-OF-Operationsdomaene ist enger:

```text
pre.capacity
pre.free
pre.bound_unconfigured
pre.bound_configured
pre.blocked

muessen nach kanonischem JSON-Parsing jeweils type(value) is float erfuellen
```

Zusaetzlich muessen diese Werte bereits vom D3-Validator als endlich,
nichtnegativ, nichtboolesch und kanonisch akzeptiert sein. Ein anatomisch
gueltiger Integerrecord bleibt gueltig, liegt aber ausserhalb der positiven
Halbierungsdomaene und erzeugt fuer diesen Operator fail-closed keinen Betrag.
Die gebundenen F2-Fixtures liegen vollstaendig in der Floatdomaene.

Fuer die Betragsermittlung kommt eine strengere exakte Operationsdomaene
hinzu. Bei positiver Fortsetzung muessen alle folgenden Bedingungen vor einem
Zielwert gelten:

```text
m = U * 0.5 is finite
m > 0.0
m + m == U
```

`m+m==U` ist die gebundene dyadische Roundtrip-Bedingung. Sie sperrt
Unterlauf und eine gerundete Halbierung. Ein fehlgeschlagener Roundtrip wird
nicht repariert.

## Feste Operationsordnung

Eine spaetere reine Zielprojektion muss exakt in dieser Reihenfolge arbeiten:

```text
1. Grenzbytes und D3-Bytes mit akzeptierten Registries validieren
2. Ereignis innerhalb desselben Aufrufs transient klassifizieren
3. Nullpfade vor jeder positiven Arithmetik entscheiden
4. m = U * 0.5 berechnen
5. dyadischen Roundtrip m + m == U pruefen
6. target_U = U - m berechnen
7. target_C = C + m berechnen
8. exakte rationale Vor-/Nachbilanz der binary64-Werte pruefen
9. erst danach einen passiven Zielbeleg bilden
```

Ein extern gelieferter S1-OC-Beleg ist weiterhin keine vertrauenswuerdige
Eingabe. Die Validierung muss im selben reinen Aufruf erfolgen.

## Exakte Bilanzpruefung

Binary64-Addition allein reicht nicht als Beweis exakter Erhaltung. Fuer die
spaetere technische Pruefung wird jeder beteiligte Float ueber sein exaktes
Ganzzahlverhaeltnis interpretiert. Mathematisch muss gelten:

```text
R(target_U) + R(target_C) = R(U) + R(C)

R(pre.free) + R(U) + R(C) + R(pre.blocked)
= R(pre.capacity)

R(pre.free) + R(target_U) + R(target_C) + R(pre.blocked)
= R(pre.capacity)
```

`R(x)` bezeichnet den exakten rationalen Wert des binary64-Werts, nicht eine
gerundete Dezimalanzeige. Eine spaetere Implementierung darf dafuer nur eine
reine exakte Standardbibliotheksdarstellung verwenden.

Scheitert eine Identitaet, lautet das Ergebnis `not_computable`; Clipping,
Nachnormalisierung oder Korrekturbuchung sind verboten.

## Gebundene F2-Zielwerte

Alle Geschichten starten exakt mit:

```text
U = 0.5
C = 0.0
```

### H0 Alternating

```text
NO_PREDECESSOR -> m0 = 0.0 -> U=0.5, C=0.0
LOCAL_SWITCH   -> m1 = 0.0 -> U=0.5, C=0.0
LOCAL_SWITCH   -> m2 = 0.0 -> U=0.5, C=0.0
LOCAL_SWITCH   -> m3 = 0.0 -> U=0.5, C=0.0

B_H0 = 0.0
```

### H1 Grouped

```text
NO_PREDECESSOR    -> m0 = 0.0   -> U=0.5,   C=0.0
LOCAL_CONTINUATION -> m1 = 0.25  -> U=0.25,  C=0.25
LOCAL_SWITCH       -> m2 = 0.0   -> U=0.25,  C=0.25
LOCAL_CONTINUATION -> m3 = 0.125 -> U=0.125, C=0.375

B_H1 = 0.375
```

### H1M Mirrored

H1M besitzt dieselben Ereignisrollen und dieselben D3-Vorzustaende wie H1:

```text
B_H1M = 0.375
```

Damit sind vor jeder Ausfuehrung gebunden:

```text
B_H0 = 0.0
B_H1 = B_H1M = 0.375
aggregate bound = 0.5 in allen drei Armen
```

Diese Zahlen sind konstruktive Vertragserwartungen und keine Messergebnisse.

## Statische Folge fuer die spaetere Probe

Der bereits akzeptierte O3-Vertrag wuerde fuer dieselben gueltigen
D3-Zielwerte spaeter rein rechnerisch ergeben:

```text
A_H0 = 0.5
A_H1 = A_H1M = 0.125
```

S1-OF fuehrt O3 nicht aus. Die Werte sind nur eine vorab gebundene
Kompositionsprognose und kein Feld- oder Funktionsbefund.

## Null- und Ablationswerte

Verbindlich gelten fuer dieselben Eingaben:

```text
formation_enabled = false
-> all m = 0.0
-> B_H0 = B_H1 = B_H1M = 0.0

event = NO_PREDECESSOR or LOCAL_SWITCH
-> m = 0.0 independent of positive U

U = 0.0
-> m = 0.0 independent of event
```

Die Ablation veraendert weder Grenzklassifikation noch S/H, Exposition,
aggregiertes Ledger oder Baselinezustand.

## Angepasste Gegenbaseline

Der spaetere Vergleich muss einen zustandsbehafteten Adapter- oder Leaky-Arm
mit derselben Ereignisfolge und demselben fest gebundenen Faktor `1/2`
enthalten. Er darf nicht pro Geschichte oder nach Ergebniskenntnis angepasst
werden.

Fuer F2 allein ist deshalb dieselbe rekursive Zahlenfolge als Gegenprognose
zugelassen. Eine eigene Kandidatenfunktion kann erst aus dem vollstaendigen
Lebenszyklus mit direkter Ressourcenintervention, Abschwaechung,
Interferenz, Loesung und Kapazitaetsfreigabe abgegrenzt werden.

## Fail-Closed-Grenzen

Kein positiver Betrag und kein Zielwert entstehen bei:

- ungueltiger Grenze oder ungueltigem D3-Record;
- extern geliefertem oder veraendertem S1-OC-Beleg;
- unbekannter Ereignisrolle;
- booleschem, negativem, nicht endlichem oder negativ-nullwertigem Operand;
- `m<=0` bei positiver Fortsetzung in der Operationsdomaene;
- gescheitertem Roundtrip `m+m==U`;
- nicht exakt repraesentierbarem `target_U` oder `target_C`;
- Verletzung einer rationalen Erhaltungsidentitaet;
- Betrag groesser oder gleich U bei positiver Fortsetzung;
- erforderlichem Clipping, Unterlauf, Ueberlauf oder Nachnormalisieren;
- Zugriff auf Orientierung, Arm-ID, Historie, Ergebnis, O3 oder Feldzustand;
- Mutation eines Eingangsobjekts oder Dateischreibzugriff.

Fehler werden nicht durch eine alternative Formel oder einen Ersatzbetrag
behandelt.

## Aussagegrenze

S1-OF bindet eine bewusst konstruierte technische Halbierungsregel und ihre
exakte numerische Domaene. Es gibt noch keine implementierte Betragsermittlung,
keinen D3-Nachzustand, keinen Commit, keine ausgefuehrte O3- oder Feldwirkung,
keine Lernfunktion und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OG darf ausschliesslich Schema, Digests, Registry, Fehlercodes und einen
passiven Belegvertrag fuer eine spaetere reine Halbierungsbetragsermittlung
binden. Die oeffentliche API muss kanonische Grenz- und D3-Bytes selbst
validieren und darf keinen externen S1-OC-Beleg akzeptieren.

S1-OG darf noch keinen Betragsoperator implementieren, keinen D3-Zielzustand
oder Commit erzeugen und keine O3-, Feld-, Runner- oder Runtimeausfuehrung
starten.
