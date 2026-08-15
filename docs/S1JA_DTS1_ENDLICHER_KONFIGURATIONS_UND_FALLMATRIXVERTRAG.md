# S1-JA: Endlicher DTS-1-Konfigurations- und Fallmatrixvertrag

## Zweck

S1-JA bindet vor jeder Baselineimplementierung die unveraenderten
Konfigurationsquellen, exakten Werte, Digests, Refinementstufen und die 24
Baseline-Rollen-Block-Faelle. Der Zustand implementiert und startet keinen
Adapter oder Modellkern.

## Gebundene Konfigurationen

Die sieben Rollen verwenden jeweils genau einen kanonischen
Konfigurationsdigest:

| Rolle | Kernwerte | Digest |
|---|---|---|
| DTS-1 | Bindung `0.4`, Umsatz `0.3`, Freigabe `0.2` | `4d7f19683f8c5b6c5ac0a62f0d9a89b9082cb325e06a9d97734c5c18efca382f` |
| B1 Fixed Adapter | leitend `0.4` fuer P_IE/P_IH, `(0.2,0.2)` fuer P_IK/P_IN | `698b6a42216915f10c40b597f40bd9cf773b845a38b35bccc176daa3362a2afa` |
| B2 S2 Integrator | Kapazitaetsverhaeltnis `8`, Kopplung `0.25`, H-Zeit `0.5` | `47915f1981d1c8220319afa6b8d819d6488dcb29ebfcba1fb2fc334b308d6dfd` |
| B3 F3 Local Leaky | `lambda=1`, `kappa=0.5`, `eta=1` | `e80711e16fbac78279f5b8ab43031ff71b1adea181db15fecfb03b22551679d9` |
| B4 F3 Linear Coupled | `lambda=1`, `kappa=0.5`, `eta=1` | `fa36b68073f4bef8405496b1dd42cd2fd85af6d5bfedd99146efb25443ca6f06` |
| B5 F3 Full | `lambda=1`, `kappa=0.5`, `eta=1` | `f7c463f8c4d167704d6c150610b2678ecac83e4df19042843b70c62253f02225` |
| B6 CONST-V | `lambda=0.5`, `kappa=0.5`, `eta=1` | `dba608c0c01cf8b5080b6735bd71e8952fd6b3a4a382223619cda28ad832b30d` |

Feldantwortzeit `1.0`, Nachhallzeit `0.5` und Dissipation `0.0` bleiben fuer
die betroffenen Rollen gleich. B2 beginnt mit neutralem L gleich null; B3
bis B6 beginnen mit gleichfoermig verteilter M-Gesamtmasse `1.0`.

B1 darf ausschliesslich die gemeinsamen leitenden Vor-Divergenz-Werte lesen.
Freie, refraktaere, transferierte oder spaetere DTS-1-Koordinaten sind aus
seiner Konfiguration ausgeschlossen.

## Refinement

Fuer DTS-1 und B1 bis B6 gelten einheitlich die Stufen `2`, `4` und `8`;
Stufe 4 ist das vorregistrierte Primaerprofil, 2 und 8 sind Pflichtkontrollen.
Alle Stufen decken dasselbe physische Intervall mit identischem Startzustand,
Kontakt und Ereignisgrenzen ab.

Die gemeinsame S/H-Grenze wird genau einmal vor dem gesamten Intervall
gesetzt und nicht an internen Subschritten wiederholt. DTS-1 darf innerhalb
des Intervalls Beteiligung und Adapter nur aus dem jeweiligen abgeschlossenen
internen Vorzustand neu ableiten. B1 behaelt dagegen seinen einmal fixierten
Adapter.

Spaeter muessen die vollstaendigen vorzeichenbehafteten r2-r4- und
r4-r8-Profilresiduen berichtet werden. S1-JA bindet dafuer noch keine
Ergebnisschwelle und erlaubt keine Parameteranpassung.

## 24-Fall-Matrix

Die kanonische Reihenfolge ist B1 bis B6 und innerhalb jeder Rolle:

1. P_IE, zwei Knoten, acht Profilkomponenten,
2. P_IH, zwei Knoten, acht Profilkomponenten,
3. P_IK, drei Knoten, sechs Profilkomponenten,
4. P_IN, drei Knoten, sechs Profilkomponenten.

Damit sind 24 eindeutige Baselinefaelle und das korrigierte
28-Komponentenprofil gebunden. Jeder Fall besitzt derzeit den Status
`BOUND_NOT_IMPLEMENTED_NOT_EXECUTED`. Spaetere technische Inkompatibilitaet
muss als Ergebnis erhalten bleiben und darf nicht durch Austausch, Reparatur
oder Auslassung eines Modells verdeckt werden.

## Entscheidung

`SEVEN_CONFIGURATIONS_AND_TWENTY_FOUR_BASELINE_CASES_BOUND_NO_IMPLEMENTATION_OR_EXECUTION`

Kanonischer Vertragsdigest:

`331168f2a6f937b454742d2be57de3f022f75ca5ca521fbff31f101bd4ea1fbc`

Numerische Zulaessigkeit, Baselinepassung, Baselineabschluss und
Kandidatenvorteil sind nicht gezeigt. Speicher-, Lern- und KI-Claims bleiben
gesperrt.

## Naechster zulaessiger Schritt

S1-JB darf ausschliesslich die sechs privaten, informationsarmen
Baselineadapter gegen S1-IT und S1-JA implementieren und technisch testen.
Noch keine 24-Fall-Ausfuehrung, kein Profilvergleich, keine Runtime und keine
Forschungsprobe.
