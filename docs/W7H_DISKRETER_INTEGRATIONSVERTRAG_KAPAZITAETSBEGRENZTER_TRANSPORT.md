# W7-H: Diskreter Integrationsvertrag fuer kapazitaetsbegrenzten Transport

Stand: 2026-08-09

Entscheidung: `CAPACITY_INVARIANT_SSPRK33_CORRIDOR_BOUND`

Arbeitsart: statischer Integrations- und Diagnosevertrag

Runtimeaenderung: nein

Forschungslauf: nein

## Ausgangspunkt

W7-F beweist die kontinuierliche Invarianz von
`0 <= M_i <= C_site`. W7-G implementiert die zugehoerige reine
Ableitungsfunktion. W7-H bindet nun die hinreichende diskrete Schrittgrenze,
bevor diese Funktion einen Feldzustand fortschreiben darf.

Der bestehende K2/F3-Korridor verwendet bereits SSPRK(3,3), kanonische
Kantenbuchung, eine globale Forward-Euler-Grenze und eine feste
Sicherheitsmarge. W7-H ersetzt diesen Integrator nicht. Es erweitert seinen
Invarianzvertrag um die lokale Obergrenze.

## Zwei nichtnegative Bilanzgroessen

Neben der vorhandenen Masse wird die freie Kapazitaetsmenge betrachtet:

```text
A_i = C_site - M_i
V_i = A_i / C_site
```

`A_i` und `V_i` sind abgeleitet und werden nicht gespeichert. Der zulaessige
M-Zustandsraum ist aequivalent zu:

```text
M_i >= 0
A_i >= 0
```

Eine diskrete Stufe ist nur zulaessig, wenn sie beide Ungleichungen
konstruktiv erhaelt.

## Forward-Euler-Zerlegung fuer M

Fuer einen abgeschlossenen Vorzustand kann die lokale M-Ableitung geschrieben
werden als:

```text
dM_i/dt = Eingabe_i - M_i * alpha_out_i

alpha_out_i = lambda_sm * Summe_j [
    V_j * (1 + kappa*(S_j-S_i))
]
```

Alle Summanden sind nichtnegativ. Da `0 <= V_j <= 1` und jeder Feldfaktor
hoechstens 2 ist, gilt bei maximalem ungewichteten Knotengrad `d_max`:

```text
0 <= alpha_out_i <= 2 * lambda_sm * d_max
```

Der Forward-Euler-Schritt

```text
M_i_next = M_i * (1 - h*alpha_out_i) + h*Eingabe_i
```

bleibt nichtnegativ, wenn `h*alpha_out_i <= 1`.

## Forward-Euler-Zerlegung fuer freie Kapazitaet

Wegen `dA_i/dt = -dM_i/dt` ist materieller Zufluss nach i der Ausfluss aus
der freien Kapazitaetsmenge. Die negative A-Komponente lautet:

```text
dA_i/dt = Freigabe_i - A_i * alpha_fill_i

alpha_fill_i = lambda_sm * Summe_j [
    (M_j/C_site) * (1 + kappa*(S_i-S_j))
]
```

Auch hier sind alle Summanden nichtnegativ und wegen
`0 <= M_j/C_site <= 1` gilt:

```text
0 <= alpha_fill_i <= 2 * lambda_sm * d_max
```

Der Forward-Euler-Schritt fuer A bleibt daher unter derselben Grenze
nichtnegativ. Damit reicht fuer beide Seiten des Kapazitaetsintervalls:

```text
rho_M_capacity = 2 * lambda_sm * d_max
h <= 1 / rho_M_capacity
```

Bei `rho_M_capacity = 0` existiert keine aktive M-Bewegung; der aktive
Integrationskorridor wird dann nicht aus dieser Rate begrenzt.

## Gemeinsame S/H/M-Schrittgrenze

Die neuen gerichteten Raten sind jeweils die bisherigen K2/F3-Raten
multipliziert mit einem Faktor in `[0,1]`. Die vorhandene konservative
S-Rueckarbeitsabschaetzung bleibt deshalb hinreichend. Fuer den ersten
Runtimekorridor gelten unveraendert:

```text
a       = 1 / response_time_seconds
ell     = leak_rate_per_second
tau_h   = afterimage_time_constant_seconds
dock    = 1 bei kontinuierlicher Dockgrenze, sonst 0

rho_S = a*(d_max + dock)
        + ell
        + 4*eta*lambda_sm*d_max

rho_H = 1/tau_h + ell

rho_M = 2*lambda_sm*d_max
```

Die gemeinsame hinreichende technische Grenze bleibt:

```text
h_safe = 0.5 / max(rho_S, rho_H, rho_M)
```

Die feste Marge `0.5` ist kein lernbarer Organismusparameter. Sie darf nicht
an ein gewuenschtes Ergebnis angepasst werden.

## Vererbung durch SSPRK(3,3)

Die bestehende Shu-Osher-Form lautet:

```text
Y1 = Y0 + h*F(Y0)
Y2 = 3/4*Y0 + 1/4*(Y1 + h*F(Y1))
Y3 = 1/3*Y0 + 2/3*(Y2 + h*F(Y2))
```

Jeder Klammerausdruck ist ein Forward-Euler-Bild mit derselben Schrittweite
h. Der gemeinsame zulaessige Zustandsraum

```text
S_i in [-1,1]
H_i in [-1,1]
M_i in [0,C_site]
Summe_i M_i = M_total
```

ist konvex. Wenn jede Forward-Euler-Auswertung bei `h <= h_safe` in diesem
Raum bleibt, bleiben auch die konvexen SSPRK-Kombinationen darin.

Jede Stufe muss S, H und M aus genau demselben abgeschlossenen Stufenzustand
auswerten. Neu berechnete Kantenraten duerfen nicht innerhalb derselben
Stufe erneut gelesen werden.

## Massenbilanz in den Stufen

Jede Ableitung besitzt durch antisymmetrische Kantenbuchung
`Summe_i T_i = 0`. Daher bewahrt jedes Forward-Euler-Bild die Gesamtmasse.
Die affinen SSPRK-Kombinationen verbinden nur Zustaende mit demselben
`M_total` und bewahren diese Masse ebenfalls bis zum gebundenen
Gleitkommafehler.

M darf weder zwischen Stufen noch beim Commit normalisiert oder geclippt
werden.

## Ereignisausrichtung

Fuer jedes vorhandene ereignisfreie Intervall der Dauer T gilt wie im
K2/F3-Korridor:

```text
n = ceil(T / h_safe)
h = T / n
```

Subschrittgrenzen werden aus den festen Intervallanteilen berechnet. Der
letzte Subschritt endet exakt an der vorhandenen Rezeptorereignisgrenze.
Punktkontakte veraendern nur den bestehenden schnellen S-Pfad und niemals M
oder `C_site` direkt.

Verfeinerungsarme verwenden `n`, `2n` und `4n` bei identischem Weltkontakt
und identischen Materialparametern.

## P0- und Parametergrenze

Bei `lambda_sm = 0` muss die spaetere opt-in Runtime direkt den bestehenden
exakten neutralen S/H-Pfad verwenden. Sie darf weder SSPRK aufrufen noch ein
M-Schema simulieren.

`C_site` bleibt ein expliziter unveraenderlicher Runtimevertrag ausserhalb
des Feldsnapshots. Eine Fortsetzung nach Restore ist nur mit exakt demselben
Kapazitaetsvertrag zulaessig. Ein fehlender oder abweichender Vertrag fuehrt
vor der ersten Stufe zum Abbruch.

## Pflichtdiagnosen

Nach jedem vollstaendigen SSPRK-Stufenzustand werden passiv erfasst:

- Subschrittzahl und maximale verwendete Schrittweite;
- gebundene sichere Schrittweite;
- maximaler absoluter Gesamtmassenfehler;
- kleinstes M;
- groesstes M;
- kleinste freie Kapazitaet `C_site - max(M)`;
- groesste lokale Kapazitaetsueberschreitung;
- maximale absolute S- und H-Auslenkung;
- unveraenderliche Kapazitaet und ihr technischer Digest.

Diagnosen duerfen keinen Zustand korrigieren und nicht in die naechste
Ableitung zurueckwirken.

## Harte Abbruchbedingungen

Vor Zustandsuebernahme wird abgebrochen, wenn mindestens eines gilt:

- nichtendlicher S-, H-, M- oder Diagnosewert;
- S oder H ausserhalb `[-1,1]`;
- M kleiner als null oder groesser als `C_site`;
- Gesamtmassenfehler groesser als die vorab gebundene technische Toleranz;
- Clipping, Renormierung oder nachtraegliche Kapazitaetskorrektur waere
  erforderlich;
- Ereignisgrenze wird nicht exakt getroffen;
- Kapazitaetsvertrag fehlt oder weicht nach Restore ab;
- P0 weicht in seiner S/H-Projektion vom bestehenden Exaktpfad ab.

Eine Abbruchdiagnose ist kein Forschungsbefund.

## Implementierungsgrenze

W7-H aendert keinen Code. Eine spaetere Implementierung muss additiv bleiben:

- eigene opt-in Runtimeoberflaeche;
- vorhandene reine W7-G-Kopplungsfunktion als einzige neue Ableitungsquelle;
- bestehende K2/F3-Runtime unveraendert;
- kein Export ueber `current_api` vor fokussierter technischer Abnahme;
- keine Browser-, Audio-, Video-, Runner- oder Reportanbindung.

## Entscheidung

```text
M-Untergrenze diskret gebunden:       ja
M-Obergrenze diskret gebunden:        ja
gemeinsame FE-Grenze:                 ja
SSPRK(3,3)-Vererbung:                 ja
Massenbilanz:                         ja
Ereignisausrichtung:                  gebunden
P0-Exaktpfad:                         verpflichtend
Kapazitaetsdiagnosen:                 gebunden
Runtimeimplementierung:               nein
Forschungslauf:                       nein
```

`CAPACITY_INVARIANT_SSPRK33_CORRIDOR_BOUND` bedeutet, dass ein hinreichend
begrenzter diskreter Engineeringkorridor statisch vorliegt. Es belegt kein
Weltverhalten, keine Verdichtung, Loesung, Feldzeit oder Memory.

## Verwendete Projektquellen

- [W7-F mathematischer Minimalvertrag](W7F_MATHEMATISCHER_MINIMALVERTRAG_KAPAZITAETSBEGRENZTER_KANTENAUSTAUSCH.md)
- [W7-G reine Kopplungsimplementierung](W7G_IMPLEMENTIERUNG_REINE_KAPAZITAETSBEGRENZTE_KOPPLUNG.md)
- [K2/F3 Integratorfamilien-Audit](K2_F3_INTEGRATORFAMILIEN_AUDIT.md)
- [K2/F3 SSPRK-Runtimevertrag](K2_F3_SCHEIBE_C_SSPRK_RUNTIME_VERTRAG.md)

## Bester naechster Schritt

W7-I implementiert eine getrennte opt-in Integrationsscheibe fuer
zustandsfreie technische Vektoren. Sie verwendet W7-G als einzige neue
Kopplungsquelle und prueft FE-Grenze, drei SSPRK-Stufen, Masse, beide
Kapazitaetsgrenzen, Zeitverfeinerung und deterministische Wiederholung. Noch
keine `SharedMCMField`-Runtimeintegration, kein `current_api`, kein Browser
und kein Forschungslauf.
