# K2/F3: statischer Integratorfamilien-Audit

Stand: 2026-08-05

Status:

- statischer Methodenvergleich;
- bedingte Auswahl, keine Implementierung;
- keine Ausfuehrung und kein numerischer Test;
- keine Freigabe eines AV-Forschungslaufs;
- keine Memory-, Organisations-, Topologie-, Semantik- oder KI-Behauptung.

## 1. Forschungsfrage

Welche Integratorfamilie kann die aktive K2/F3-Dynamik als eine gemeinsame
S/H/M-Rechte-Seite fortschreiben und dabei die bereits analytisch
festgelegten Zustandsgrenzen technisch pruefbar erhalten?

Bewertet werden:

1. atomare Kopplung von S, H und M;
2. Gesamtmassenerhaltung von M;
3. Nichtnegativitaet von M;
4. Intervallinvarianz von S und H;
5. deterministische Ereignis- und Restore-Grenzen;
6. kontrollierbare Zeitverfeinerung;
7. Anschluss an die vorhandene NumPy-basierte Laufzeit;
8. Trennbarkeit von Naturhypothese und numerischem Verfahren.

## 2. Ausgangssystem

Zwischen zwei bestehenden Rezeptor-Ereignisgrenzen gilt ein autonomes
Anfangswertproblem fuer den kanonischen Gesamtzustand

```text
Y = (S_1..S_N, H_1..H_N, M_1..M_N).
```

Die gemeinsame Rechte-Seite ist:

```text
dS/dt = F_current(S, world_boundary) + R(S,M)
dH/dt = F_afterimage(S,H)
dM/dt = C(S,M)
```

`C` wird innerhalb einer Auswertung genau einmal berechnet und sowohl fuer
dM als auch fuer R verwendet. Eine Methode, die S und M nacheinander aus
unterschiedlichen Zwischenzustaenden fortschreibt, verletzt diesen Vertrag.

## 3. Bewertete Familien

| Familie | Erhaltung | Positivitaet / Intervalle | Ereignisse / Restore | Ergebnis |
|---|---|---|---|---|
| bisheriger spektraler Exaktschritt | exakt fuer lineares S/H | S/H bisher analytisch kontrolliert | sehr gut | nur P0; fuer nichtlineares F3 nicht anwendbar |
| klassisches festes RK4 | lineare Erhaltung bis Rundungsfehler | keine allgemeine Invariantengarantie | deterministisch und einfach ausrichtbar | nicht als Hauptverfahren |
| adaptive RK23/RK45/DOP853 | gute lokale Fehlerkontrolle | keine automatische Positivitaets- oder Intervallgarantie | Ereignisse moeglich, adaptive Neustarts methodisch relevant | nur Referenz-/Konvergenzvergleich |
| Radau/BDF/LSODA | fuer steife Systeme geeignet | keine automatische M-Positivitaet | komplexere Solver- und Neustartgrenze | vorerst gesperrt; Steifheit nicht belegt |
| Operator-/Strang-Splitting | Teilsysteme getrennt behandelbar | teils strukturtreu | reihenfolgeabhaengige Zwischenzustaende | verworfen: verletzt kleinsten atomaren C/R-Vertrag |
| Modified Patankar RK | konservativ und positiv fuer Produktions-/Destruktionssysteme | starke M-Eigenschaften | zusaetzliche gekoppelte Diskretisierung fuer S/R noetig | Reservekandidat, nicht erster Gesamtintegrator |
| SSPRK(3,3) mit bewiesener FE-Grenze | konservative Ableitungen bleiben konservativ | erhaelt konvexe Invarianten unter derselben FE-Grenze | feste, ereignisausgerichtete Schritte | bedingter Hauptkandidat |

## 4. Warum allgemeine adaptive Solver nicht genuegen

`solve_ivp` stellt explizite Runge-Kutta-Verfahren sowie Radau, BDF und LSODA
mit Fehlersteuerung bereit. Die Auswahl zwischen expliziten und impliziten
Verfahren richtet sich dort wesentlich nach Steifheit und Genauigkeit. Daraus
folgt jedoch keine automatische Garantie fuer die spezielle positive,
konservative M-Komponente oder die Intervalle von S und H.

Ein adaptiver Solver kann spaeter als unabhaengiger Genauigkeitsvergleich
nuetzlich sein. Er ist aber nicht der erste Naturpfad, solange seine
Zustandsinvarianten nur durch nachtraegliche Ereignisse, Clipping oder
Normalisierung erzwungen wuerden.

## 5. Warum Patankar nicht zuerst gewaehlt wird

Modified-Patankar-Verfahren sind fuer positive konservative
Produktions-/Destruktionssysteme entwickelt worden. Das passt unmittelbar zur
M-Gleichung. Die K2/F3-Hypothese bindet jedoch dieselbe realisierte
M-Mengenrate C gleichzeitig als R an S.

Eine Patankar-Behandlung nur von M und eine gewoehnliche Behandlung von S
wuerden zuerst einen zusaetzlichen diskreten Kopplungsvertrag erfordern:

```text
Welcher diskrete M-Fluss ist der fuer R massgebliche Fluss?
```

Diese Zusatzentscheidung waere groesser als der aktuelle Minimalvertrag.
Patankar bleibt deshalb ein Reservekandidat, falls ein gemeinsames explizites
SSP-Verfahren die erforderliche Schrittgrenze praktisch nicht tragen kann.

## 6. Bedingte Auswahl: SSPRK(3,3)

Der erste aktive Integratorkandidat ist das dreistufige explizite
SSPRK(3,3)-Verfahren in Shu-Osher-Form:

```text
Y1 = Y0 + h F(Y0)
Y2 = 3/4 Y0 + 1/4 (Y1 + h F(Y1))
Y3 = 1/3 Y0 + 2/3 (Y2 + h F(Y2))
```

Jede Auswertung `F(Yk)` bildet S, H und M gemeinsam und atomar. Die Methode
ist eine konvexe Kombination von Forward-Euler-Schritten. Sie uebertraegt
deshalb eine konvexe Invariante des Forward-Euler-Schritts, wenn dieselbe
zulaessige Schrittgrenze eingehalten wird.

Die Auswahl ist **bedingt**, weil vor Implementierung die gemeinsame
Forward-Euler-Grenze aus den vorhandenen Feldraten feststehen muss.

## 7. Statische Forward-Euler-Grenze

Fuer den ersten Korridor gelten:

```text
a       = 1 / response_time_seconds
tau_h   = afterimage time_constant_seconds
ell     = leak_rate_per_second
lambda  = lambda_sm_per_second
d_max   = maximale gewichtete Knotengradzahl
eta     = feste Rueckarbeitsstaerke
```

Da `abs(kappa) <= 1/2`, liegt jeder F3-Ratenfaktor zwischen 0 und 2. Fuer die
kanonischen nichtnegativen Kantengewichte folgt als ausreichende globale
Abschaetzung:

```text
|C_i| / M_total <= 2 * lambda * d_max.
```

Die M-Forward-Euler-Positivitaet ist damit hinreichend geschuetzt durch:

```text
h * (2 * lambda * d_max) <= 1.
```

Die Rueckarbeit laesst sich fuer ein gegebenes Vorzeichen als Bewegung zu
einer der Grenzen `-1` oder `1` schreiben. Ihr maximaler auswaerts gerichteter
Koeffizient ist hinreichend beschraenkt durch:

```text
4 * eta * lambda * d_max.
```

Zusammen mit lokaler S-Ausbreitung, maximal einem Rezeptordock je Feldort und
Dissipation ist eine hinreichende S-Grenze:

```text
rho_S = a * (d_max + 1) + ell + 4 * eta * lambda * d_max.
```

Fuer H gilt aus Tracking und Dissipation:

```text
rho_H = 1 / tau_h + ell.
```

Fuer M gilt:

```text
rho_M = 2 * lambda * d_max.
```

Der erste technische Korridor verwendet nur Schritte mit:

```text
h <= h_safe
h_safe = 0.5 / max(rho_S, rho_H, rho_M)
```

Der Faktor `0.5` ist eine feste technische Sicherheitsmarge gegen die
hinreichende Grenze 1. Er ist kein Organismusparameter und darf nicht aus
Ergebnissen angepasst werden.

Sonderfaelle:

- Bei `lambda = 0` wird diese Grenze nicht verwendet; P0 laeuft ueber den
  bestehenden Exaktpfad.
- Bei `d_max = 0` ist das aktive F3-Feld unzulaessig, weil der erste Korridor
  eine zusammenhaengende Nachbarschaft mit mehr als einem Feldort verlangt.
- Nichtendliche oder nichtpositive Ratenvertraege werden vor der
  Schrittplanung abgelehnt.

## 8. Ereignisausrichtung

Fuer jedes bereits vorhandene kontinuierliche Intervall der Dauer `T` wird
deterministisch gewaehlt:

```text
n = ceil(T / h_safe)
h = T / n
```

Die spaetere Implementierung bildet jeden Subschritt aus den rationalen
Intervallanteilen `k/n` und summiert nicht wiederholt eine Gleitkommazeit auf.
Damit endet der letzte Subschritt an der vorhandenen Ereignisgrenze.
Ein Rezeptorereignis bleibt ein externer S-Sprung nach dem bestehenden
Vertrag und aendert M nicht direkt.

Die Verfeinerungsarme desselben Intervalls verwenden:

```text
n
2*n
4*n
```

Sie veraendern weder Weltkontakt noch F3-Parameter.

## 9. Erhaltung und Zustandskontrolle

### 9.1 M-Gesamtmasse

Wenn jede Stufenableitung `sum(C) = 0` besitzt, behalten auch die affinen
SSPRK-Kombinationen die Gesamtmasse bis zu Gleitkomma-Summationsfehlern. Die
Kanten werden in fester kanonischer Reihenfolge verarbeitet; derselbe
Kantenfluss wird mit entgegengesetztem Vorzeichen auf beide Endpunkte
gebucht.

M wird niemals renormalisiert oder geclippt. Eine spaeter vorregistrierte
Toleranzverletzung bricht den technischen Lauf ab.

### 9.2 Nichtnegativitaet und S/H-Intervalle

Die Schrittgrenze soll die konvexe Invarianz konstruktiv erhalten. Zusaetzlich
werden nach jeder vollstaendigen SSPRK-Stufe nur Diagnosen ausgefuehrt.
Diagnosen duerfen den Zustand nicht korrigieren.

Ein negativer M-Wert oder ein S/H-Wert ausserhalb seines Intervalls oberhalb
der reinen Rundungstoleranz fuehrt zum Abbruch.

## 10. Determinismus und Restore

Determinismus wird durch folgende Festlegungen begrenzt:

- kanonische Zustands- und Kantenreihenfolge;
- festes SSPRK-Stufenschema;
- feste Schrittgrenze und Sicherheitsmarge;
- deterministische ganzzahlige Subschrittzahl je Ereignisintervall;
- keine adaptive Historie und kein solverinterner Zustand im Snapshot;
- Restore nur an vollstaendigen vorhandenen Ereignisgrenzen.

Da auch ein ununterbrochener Lauf an jeder Rezeptor-Ereignisgrenze ein neues
Intervall beginnt, darf Restore keine andere Schrittplanung als die
ununterbrochene Fortsetzung erzeugen.

## 11. Verbindliche Vergleichsarme

Vor einem Forschungsbefund muessen spaeter mindestens verglichen werden:

| Arm | Zweck |
|---|---|
| P0 Exaktpfad | beweist unveraenderte S/H-Nullprojektion |
| SSP-n | erster aktiver technischer Pfad |
| SSP-2n | Zeitverfeinerung |
| SSP-4n | zweite Zeitverfeinerung |
| RK-Referenz | unabhaengiger Genauigkeitsvergleich, nicht Naturpfad |
| eta-null | trennt M-Transport von S-Rueckwirkung |
| kappa-null | trennt S-getriebenen Transport von neutraler Diffusion |

Ein externer RK-Referenzsolver darf erst nach eigener Abhaengigkeits- und
Versionsfixierung verwendet werden. Sein Ergebnis ersetzt keine
Invariantengarantie des Hauptpfads.

## 12. Abbruch- und Korrekturbedingungen

Die bedingte SSPRK-Auswahl wird korrigiert oder verworfen, wenn:

- die gemeinsame Forward-Euler-Grenze mathematisch nicht bestaetigt werden
  kann;
- die erforderliche Subschrittzahl fuer kontrollierte AV-Intervalle praktisch
  untragbar wird;
- M trotz eingehaltener Grenze negativ wird;
- S oder H trotz eingehaltener Grenze das Intervall verlaesst;
- Massenerhaltung systematisch statt nur auf Rundungsniveau driftet;
- Restore eine andere Subschrittplanung erzeugt;
- SSP-n, SSP-2n und SSP-4n keine geordnete Konvergenz zeigen;
- ein beobachteter Effekt unter Verfeinerung verschwindet oder sein Vorzeichen
  instabil wechselt;
- die Implementierung S und M in getrennten Operatorfolgen aktualisieren
  muss.

In diesem Fall ist Modified Patankar fuer die gemeinsame diskrete C/R-Bindung
neu zu untersuchen. Es erfolgt kein stiller Methodenwechsel.

## 13. Quellen

Projektquellen:

- `docs/K2_MATHEMATISCHER_F3_MINIMALVERTRAG.md`
- `docs/K2_F3_STATISCHE_IMPLEMENTIERUNGSSPEZIFIKATION.md`
- `docs/K2_F3_IMPLEMENTIERUNGS_UND_FALSIFIKATIONSSCHEIBEN.md`
- `mcm_field_organism/neutral_local_field_substrate.py`
- `mcm_field_organism/neutral_asynchronous_field_runtime.py`
- `requirements.txt`

Numerische Primaer- und Referenzquellen:

- SciPy-Dokumentation zu `solve_ivp` und den Familien RK23, RK45, DOP853,
  Radau, BDF und LSODA:
  <https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html>
- Izzo und Jackiewicz, Darstellung von SSP-RK-Verfahren als konvexe
  Kombination von Forward-Euler-Schritten:
  <https://link.springer.com/article/10.1007/s41980-022-00731-x>
- Kopecz und Meister, Ordnungsbedingungen fuer konservative und positive
  Modified-Patankar-RK-Verfahren:
  <https://arxiv.org/abs/1702.04589>
- Isherwood, Grant und Gottlieb, SSP-Integrating-Factor-RK fuer Systeme mit
  unterschiedlich schnellen linearen und nichtlinearen Anteilen:
  <https://epubs.siam.org/doi/10.1137/17M1143290>

## 14. Ergebnis

Der erste aktive K2/F3-Integrator ist **bedingt SSPRK(3,3)** auf einem festen,
an vorhandenen Rezeptorereignissen ausgerichteten Subschrittraster. Die
Auswahl ist klein, NumPy-kompatibel, atomar und besitzt eine statisch
formulierbare Invariantengrenze.

Noch nicht freigegeben sind Implementierung, Toleranzen fuer
Gleitkomma-Diagnosen, Runtimeausfuehrung oder AV-Forschung. Vor Code muss
Scheibe A als exakter API-, Schema- und Migrationsvertrag ausformuliert
werden. Danach kann getrennt entschieden werden, ob ihre Implementierung
freigegeben wird.
