# W7-M: In-Memory-Adapter der Kapazitaetsfunktionsmatrix

Stand: 2026-08-09

Entscheidung: `IN_MEMORY_CAPACITY_FUNCTION_MATRIX_ADAPTER_IMPLEMENTED`

Arbeitsart: additive technische Adapterimplementierung

Hauptmatrix oder Forschungslauf: nein

## Implementierter Umfang

Neu implementiert wurde:

```text
mcm_field_organism/w7m_capacity_function_matrix.py
```

Das Modul baut ausschliesslich die in W7-L vorregistrierten technischen
Eingaenge auf. Es fuehrt keinen Kandidaten- oder Baselinemodellpfad fort und
entscheidet keine Forschungsfrage.

Der Adapter stellt bereit:

- die unveraenderten K2-B-A/B-/G-/P-Rezeptorsequenzen im Arbeitsspeicher;
- ein frisches gemeinsames 84-Orte-Audio-/Videofeld;
- den aktiven CAP-Ausgangszustand mit `C_site = 2/84`;
- source-only bestimmte A-, B- und Gleichstandsregionen;
- ein kanonisches Baseline- und Pfadinventar;
- regionale M- und Freikapazitaetsmessung;
- explizite Observerinterventionen mit erneuerter Fortsetzungsbindung.

Es werden keine Rohbilder, Audiodaten, Trajektorien oder Modellresultate
persistiert.

## Source-only Regionen

Fuer jeden angedockten Feldort wird die zeitintegrierte absolute
Rezeptorwirkung von A und B verglichen. Es gibt keine Schwelle und keinen
Zugriff auf CAP- oder Baselineergebnisse.

Die eingefrorene Aufteilung lautet:

```text
R_A:  38 Feldorte
R_B:  34 Feldorte
R_0:  12 Feldorte
gesamt: 84 Feldorte

region_digest:
e88fd217abd969af87e28d4e0faee7364930f6fc3a1f0d21cd908874ca51bbf2
```

Die Mengen sind disjunkt, vollstaendig und kanonisch nach Neuronen-ID
geordnet. Sie bleiben reine Observerrollen.

## Kapazitaet und Anfangsbilanz

Fuer `M_total = 1` gilt:

```text
C_site = 2 / 84 = 0.023809523809523808
homogene lokale Masse = 1 / 84
homogene freie lokale Kapazitaet = 1 / 84
gesamte freie Kapazitaet = 1
```

Die technische Anfangsmessung schliesst exakt:

```text
M_R_A = F_R_A = 38 / 84
M_R_B = F_R_B = 34 / 84
M_R_0 = F_R_0 = 12 / 84
```

Die Messfunktion liest nur den vorhandenen M-Vektor und gibt nichts an die
Runtime zurueck.

## Eingefrorene Matrix

Die sieben Pfade sind:

```text
AB, AG, BA, BG, UA, UB, UG
```

Jeder Pfad besitzt genau fuenf Checkpoints. Die Baselinekennungen sind:

```text
CAP, P0, LEAK, LIN, F3, CONST-V, SAT, MOB, NORM,
ETA0, KAPPA0, SIGN
```

Jeder Arm besitzt nun neben Parametern eine kanonische Gleichungsbindung.
Insbesondere sind festgelegt:

- CONST-V: unveraenderte F3-Gleichung mit `lambda_sm = 0.5`;
- LEAK: unabhaengige lokale lineare Spur ohne Rueckwirkung;
- SAT: lokale Leaky-Variable mit festem tanh-Leser;
- MOB: quellenbelegungsabhaengige Mobilitaet ohne freie Zielkapazitaet;
- NORM: externe globale L1-Normalisierung als unzulaessige Gegenkontrolle.

Diese Bindungen verhindern spaetere Ergebnisanpassung. LEAK, SAT, MOB und
NORM sind in W7-M noch keine ausgefuehrten Evaluatoren und keine
Organismusfunktionen.

Der vollstaendige Adapterdigest lautet:

```text
a1e3f8a08fbef760c8f0b147f99cbebfcc05621c2265a70d853dd3d4863ffb6a
```

## Observerinterventionen

W7-M verwendet vorhandene MCM-F3-Helfer und bindet sie enger:

- `fast-aligned`: setzt auf einer Kopie nur S und H auf null;
- `m-neutral`: setzt auf einer Kopie nur M homogen;
- `m-transplant`: uebertraegt M nur zwischen gleicher Geometrie,
  gleichem Budget und exakt gleichem Modellarm;
- `eta0`: erhaelt M und setzt nur eta auf null;
- `kappa0`: erhaelt M und setzt nur kappa auf null;
- `sign`: erhaelt M und invertiert kappa einmal fuer den ganzen Arm.

Nach jeder Intervention wird der veraenderte Snapshot erneut gegen denselben
Kapazitaetsvertrag validiert und mit einem neuen externen
Snapshot-/Konfigurationsnachweis gebunden. Die alte Bindung kann dadurch
nicht stillschweigend weiterverwendet werden.

## Technische Abnahme

Geprueft sind:

- feste Quellen-, Regions- und Matrixdigests;
- vollstaendige disjunkte Regionspartition;
- exakte homogene M-/Freikapazitaetsbilanz;
- kanonisches Baseline- und Pfadinventar;
- feste CONST-V-Rate und MOB-Gleichungsbindung;
- deterministischer Wiederaufbau des gesamten Adapters;
- M-Erhaltung und Kapazitaetsgrenze aller Interventionen;
- erneuerte passende Fortsetzungsbindung nach Intervention;
- erfolgreiche spaetere W7-K-Fortsetzung eines intervenierten Feldes;
- Ablehnung von M-Transplantation zwischen verschiedenen Modellarmen;
- fehlender Export aus `current_api`.

Der technische Verbund aus W7-M, W7-K, W7-I, W7-G, bestehender F3-Runtime,
K2-B-Quellen-/Planvertraegen und allen vier API-/Architekturverbrauchersuiten
besteht mit:

```text
68 tests, OK
```

## Unveraenderte Grenzen

Unveraendert blieben:

- Produktionsruntime und Snapshot-Schemata;
- `mcm_field_organism.__init__` und `current_api`;
- Browser-, Video-, Audio- und Rezeptorpfade;
- Reports und Forschungslaeufe;
- alle Memory-, Feldzeit-, Organisations-, Semantik- und KI-Sperren.

W7-M belegt nur, dass die vorregistrierten Eingaenge und Interventionen
technisch geschlossen und reproduzierbar aufgebaut werden koennen. Es gibt
noch keinen CAP-Verlauf, keinen Baselinevergleich und keinen funktionalen
Befund.

## Naechster Schritt

W7-N darf die in W7-M bereits eingefrorenen LEAK-, SAT-, MOB- und
NORM-Gleichungen als reine technische Baselinekerne implementieren und die
bestehenden LIN-/F3-/CONST-V-Funktionen daran anschliessen. Es darf weiterhin
keine A/B-Hauptmatrix auswerten, keinen Browser starten und keinen Report
schreiben.
