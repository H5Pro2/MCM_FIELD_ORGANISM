# W7-N: Implementierung reiner Kapazitaetsfunktions-Baselinekerne

Stand: 2026-08-09

Entscheidung: `PURE_CAPACITY_FUNCTION_BASELINES_IMPLEMENTED`

Arbeitsart: additive technische Vergleichsimplementierung

Runtime- oder Hauptmatrixausfuehrung: nein

## Implementierter Umfang

Neu implementiert wurde:

```text
mcm_field_organism/w7n_capacity_function_baselines.py
```

Das Modul implementiert nur die in W7-M bereits eingefrorenen
Baselinegleichungen. Es kennt keine A/B-/G-/P-Quellen, Pfade, Checkpoints,
Entscheidungsschwellen oder Forschungsclaims.

Zwei klar getrennte Vergleichsflaechen sind vorhanden:

- exakte lokale Zustandskerne fuer LEAK, SAT und NORM;
- atomare Kopplungsableitungen fuer LIN, F3, CONST-V und MOB.

Kein Kern schreibt einen `SharedMCMField` fort oder persistiert Zustand.

## LEAK

LEAK besitzt genau einen unabhaengigen Zustand je Feldort:

```text
dz_i/dt = (S_i - z_i) / tau
R_i = 0
```

Fuer waehrend eines Intervalls konstantes S wird exakt fortgeschrieben:

```text
r = exp(-dt/tau)
z_i_neu = r*z_i_alt + (1-r)*S_i
```

LEAK hat keine Rueckwirkung auf das schnelle Feld. Sein Ausgang ist nur der
lokale z-Vektor.

## SAT

SAT verwendet dieselbe exakte lokale Fortschreibung fuer den einzigen
latenten Zustand u und einen festen punktweisen Leser:

```text
du_i/dt = (S_i - u_i) / tau
z_i = tanh(u_i)
R_i = 0
```

Die Begrenzung erzeugt weder Transport noch ein Ressourcenledger. Der
tanh-Ausgang wird nicht in u oder S zurueckgeschrieben.

## NORM

NORM verwendet den LEAK-Zustand und bildet ausschliesslich eine externe
globale Observerausgabe:

```text
o_i = z_i / (epsilon + Summe_j abs(z_j))
```

Die Normalisierung veraendert den latenten Zustand nicht und ist nicht als
Organismusfunktion zugelassen. Sie bleibt eine absichtlich unzulaessige
Erklaerungsbaseline fuer global erzeugte Konkurrenz.

## LIN, F3 und CONST-V

LIN und F3 rufen ausschliesslich die vorhandenen reinen Funktionen auf:

```text
compute_mcm_f3_linear_coupled_baseline
compute_mcm_f3_coupling
```

CONST-V verwendet ebenfalls die vorhandene F3-Funktion, jedoch auf einer
unveraenderlichen technischen Armkopie mit:

```text
lambda_sm = 0.5
kappa = 0.5
eta = 1.0
```

Alle Parameter werden aus dem eingefrorenen Baselinevertrag erzeugt. Sie
werden nicht aus einem uebergebenen Modellarm oder Ergebnis uebernommen.

## MOB

MOB implementiert eine quellenbelegungsabhaengige Mobilitaet ohne freie
Zielkapazitaet:

```text
mu_i = 1 - M_i / C_site
q_i_to_j = lambda_sm * M_i * mu_i * (1 + kappa*dS_ij)
```

Die Gegenrichtung wird mit derselben Regel aus j berechnet. Kantenweise
antisymmetrische Verbuchung erhaelt die Gesamtmasse. Die S-Rueckarbeit bleibt
wie bei F3 an die lokale M-Rate gebunden.

MOB verwendet `C_site` nur als feste Vergleichsskala der Quelle. Die freie
Kapazitaet des Ziels kommt in der Rate nicht vor. Ein bereits volles Ziel
kann deshalb weiterhin positiven Nettozufluss erhalten. Genau diese fehlende
Zielsperre trennt MOB mechanisch von CAP.

## Exakte Anfangsangleichung

Im W7-M-Ausgangszustand gilt an jedem Ort:

```text
M_i = M_total/N
C_site = 2*M_total/N
V_i = 1 - M_i/C_site = 0.5
mu_i = 1 - M_i/C_site = 0.5
```

Damit besitzen CAP, CONST-V und MOB bei gleichem S fuer jede Kante exakt
dieselben gerichteten Anfangsraten. Ein spaeterer Unterschied kann nicht aus
einer bereits am Start verschiedenen Zeitskala stammen. Er kann erst nach
veraenderter lokaler Belegung entstehen.

## Technische Abnahme

Geprueft sind:

- exakte LEAK-/SAT-Fortschreibung unter konstanter Evidenz;
- semigruppengleiche ganze und geteilte Zeitintervalle;
- getrennter SAT-Leser ohne Zustandsrueckschreibung;
- NORM nur als globale Observerprojektion;
- Ablehnung geaenderter Gleichungsvertraege und falscher Zustandsrollen;
- identische CAP-/CONST-V-/MOB-Anfangsableitung auf allen 84 Feldorten;
- konservative MOB-Massenrate;
- fehlende MOB-Zielsperre an einem voll belegten Ziel;
- unveraenderte Eingaben bei LIN, F3 und CONST-V;
- vollstaendig aus Baselinevertraegen erzeugte Armparameter;
- fehlender Export aus `current_api`.

Der erweiterte technische Verbund aus W7-N, W7-M, W7-K, W7-I, W7-G,
vorhandenen F3-/Baselinekopplungen, K2-B-Vertraegen und allen vier
API-/Architekturverbrauchersuiten besteht mit:

```text
91 tests, OK
```

## Unveraenderte Grenzen

Unveraendert blieben:

- Produktionsruntime, Feldzustand und Snapshot-Schemata;
- `mcm_field_organism.__init__` und `current_api`;
- Quellen-, Browser-, Video-, Audio- und Rezeptorpfade;
- Reports und Forschungslaeufe.

W7-N belegt nur, dass die engen Gegenbaselines mathematisch und technisch
reproduzierbar berechnet werden koennen. Es belegt keinen Vorteil von CAP,
keine funktionale Freisetzung oder Wiederverwendung und keinen Memory-,
Feldzeit-, Organisations-, Semantik- oder KI-Befund.

## Naechster Schritt

W7-O muss vor jeder Pfadausfuehrung statisch binden, welche gemeinsame
Messflaeche fuer gekoppelte S/H/M-Modelle und rein observerseitige
LEAK-/SAT-/NORM-Ausgaenge zulaessig ist. Observerausgaben duerfen dabei nicht
als schnelle S/H-Probe oder Organismuswirkung ausgegeben werden. W7-O
implementiert und startet noch keine Hauptmatrix.
