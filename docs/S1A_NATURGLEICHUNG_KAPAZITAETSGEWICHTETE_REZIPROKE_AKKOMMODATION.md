# S1-A: Kapazitaetsgewichtete reziproke S-L-Akkommodation

Stand: 2026-08-07

Status: `S1A_REFERENCE_EQUATION_BOUND`

## Zweck und Einordnung

Dieses Dokument waehlt die erste konkrete inhaltsfreie Naturgleichung fuer
den in S0 gebundenen langsamen Freiheitsgrad `L`.

Die Gleichung ist bewusst eine lineare, kapazitaetsgewichtete und reziproke
Zweizustandsdynamik. Sie ist damit zugleich Pflichtbaseline `B2` aus S0. Sie
wird nicht als neue Memory-Mechanik oder als organische Entwicklung
ausgegeben.

Ihr Zweck ist technischer und kausaler:

- erstmals einen echten ko-lokalisierten L-Zustand aufbauen;
- `S -> L` und `L -> S` innerhalb derselben Feldtransition realisieren;
- langsame Entwicklung ohne Wiederholungszaehler herstellen;
- Bilanz, Snapshot, Tausch und Neutralisierung technisch pruefbar machen;
- eine belastbare Referenz fuer spaetere nichtlineare Substratphysik schaffen.

## 1. Bestehende schnelle Feldform

Fuer alle vorhandenen Feldorte wird die heutige schnelle lineare
MCM-Feldentwicklung abstrakt geschrieben als:

```text
dS/dt = A(U) S + b(U) - lambda_S S
```

Dabei sind:

- `A(U)` der bereits vorhandene lokale symmetrische Diffusions- und
  Kontaktgenerator;
- `b(U)` der bestehende reduzierte lokale Rezeptorantrieb;
- `lambda_S >= 0` die bereits vorhandene optionale Felddissipation;
- `U` ausschliesslich der aktuelle technisch reduzierte Weltkontakt.

S1-A veraendert weder Rezeptorreduktion, Geometrie, Sample-Offsets noch die
Bedeutung dieser vorhandenen Terme.

Der bestehende schnelle Nachhall bleibt:

```text
dH/dt = r_H S - (r_H + lambda_S) H
r_H   = 1 / tau_H
```

`H` wirkt in S1-A nicht als Bildungsquelle fuer `L`.

## 2. Neue lokale Naturgleichung

Fuer jeden Feldort `i` gilt der interne S-L-Austausch:

```text
C_S * dS_i/dt |_X = -g * (S_i - L_i)
C_L * dL_i/dt |_X = +g * (S_i - L_i)
```

Mit der Normierung

```text
C_S = 1
rho = C_L / C_S
rho > 1
g > 0
```

ergibt sich die gemeinsame Gleichung:

```text
dS/dt = A(U) S + b(U) - lambda_S S - g(S - L)
dL/dt = (g / rho)(S - L)
dH/dt = r_H S - (r_H + lambda_S)H
```

Alle rechten Seiten lesen denselben abgeschlossenen Vorzustand. Es gibt keine
sequentielle Schreib- und Ruecklesephase.

## 3. Physische Rollen der Parameter

```text
g   = lokale Austauschleitfaehigkeit zwischen S und L
rho = dimensionsloses Verhaeltnis langsamer zu schneller Wirkungskapazitaet
```

`rho > 1` macht L langsamer, ohne eine zweite Uhr einzufuehren:

```text
|dL/dt| = |dS/dt |_X| / rho
```

Die Parameter sind global, inhaltsfrei und waehrend eines gesamten Verlaufs
unveraendert. Sie duerfen nicht aus Probe, Wiederholung, Aktivitaetsklasse
oder Observerwert angepasst werden.

### Technischer S1-B-Zeuge

Fuer reine Implementierungs- und Invarianztests wird gebunden:

```text
rho = 8
g   = 0.25 pro Sekunde
```

Diese Werte sind keine Forschungsparameter und werden nicht als optimal
bezeichnet. Vor S2 muss ein Parametersatz zusammen mit allen Baselines neu
vorregistriert und ohne Ergebnistuning fixiert werden.

## 4. Reziproke Bilanz

Fuer den isolierten internen Austausch gilt an jedem Ort exakt:

```text
d/dt (S_i + rho * L_i) |_X = 0
```

Die Kopplung erzeugt deshalb keine zweite Welteingabe. Sie verteilt nur den
kapazitaetsgewichteten lokalen Zustand zwischen schneller und langsamer Rolle.

Fuer die lokale Differenz

```text
Delta_i = S_i - L_i
```

gilt im isolierten Austausch:

```text
dDelta_i/dt = -g(1 + 1/rho) Delta_i
```

und fuer

```text
E_i = 0.5 * Delta_i^2
```

folgt:

```text
dE_i/dt = -g(1 + 1/rho) Delta_i^2 <= 0
```

Die Akkommodationsdifferenz ist passiv. Ein gemeinsam getragener Rest kann
ohne weitere Welt- oder Felddissipation erhalten bleiben; seine konkrete Lage
folgt der Feldgeschichte und keinem programmierten Zielzustand.

## 5. Bereichsinvarianz

Wenn `S_i` und `L_i` vor dem isolierten Austausch in `[-1,1]` liegen, bleibt
ihre exakte Austauschloesung eine konvexe Kombination der beiden Vorwerte.
Damit bleibt auch `L_i` ohne Clip in `[-1,1]`.

Die gemeinsame Feldgleichung besitzt:

- nichtnegative Uebergangsraten zwischen S- und L-Komponente;
- die vorhandene lokale MCM-Diffusion;
- Rezeptorrandwerte innerhalb des bereits gebundenen normierten Bereichs;
- ausschliesslich nichtnegative Dissipation.

S1-B muss die Bereichsinvarianz aus dem gemeinsamen Generator erhalten. Ein
ereignisabhaengiger Reset oder ein als Organismusfunktion wirkender Clip ist
nicht zulaessig. Ein Toleranzclip bis zur bereits verwendeten numerischen
Rundungsgrenze bleibt technische Schutzhandlung und muss berichtet werden.

## 6. Exakte gemeinsame Integrationsform

Fuer `N` Feldorte wird der S-L-Teil als Blockgenerator geschrieben:

```text
G_SL = [ A(U) - lambda_S I - g I      g I       ]
       [ (g/rho) I                    -(g/rho) I ]

B_SL = [ b(U) ]
       [   0  ]
```

Mit der skalierten Koordinate

```text
Y = sqrt(rho) * L
```

wird der Kopplungsblock symmetrisch:

```text
G_SY = [ A(U) - lambda_S I - g I      (g/sqrt(rho)) I ]
       [ (g/sqrt(rho)) I              -(g/rho) I      ]
```

Damit kann S1-B die vorhandene spektrale Exaktintegration erweitern, ohne
Euler-Schritt und ohne eine von der Aufrufzahl abhaengige Organismuswirkung.

`H` wird im selben Intervall aus der gekoppelten S-Trajektorie integriert.
Eine nachtraegliche H-Aktualisierung aus nur dem Endwert von S ist nicht
gleichwertig und fuer S1-B unzulaessig.

## 7. Atomare Zustandsgrenze

Ein S1-B-Schritt muss genau diese Ordnung besitzen:

```text
1. abgeschlossenen Zustand (S_t,H_t,L_t) und Weltkontakt U_t lesen
2. gemeinsamen Blockgenerator und Randantrieb bilden
3. (S,H,L) ueber dasselbe dt gemeinsam integrieren
4. vollstaendigen Folgezustand atomar uebernehmen
```

Verboten sind:

- erst L aus `S_t+1` schreiben und danach S erneut berechnen;
- L mehrmals pro S-Schritt fortschreiben;
- H oder Observerwerte als versteckte L-Schreibursache verwenden;
- zwischen Kontakt-, Ruhe-, Probe- oder Wiederholungsphasen Parameter
  wechseln.

## 8. Exakter Nullpfad

Die Konfiguration benoetigt einen ausdruecklichen technischen Nullarm:

```text
g = 0
```

Bei `g = 0` wird kein L-Block in den schnellen Integrationspfad eingeschleift.
S und H muessen dann mit dem bisherigen Runtimepfad bitgleich fortsetzen.

`L = 0` bei `g > 0` ist kein Nullarm, weil ein nichtneutrales S den Austausch
sofort anregt. Diese beiden Faelle duerfen in Tests nicht verwechselt werden.

## 9. Einordnung gegen die Pflichtbaselines

### B0: heutiger schneller Nullpfad

Wird durch `g = 0` exakt reproduziert.

### B1: einzelne Leaky-Spur

Wenn die L-nach-S-Wirkung entfernt wird, folgt L einer linearen Spur von S.
S1-A ist durch seine Rueckwirkung kausal breiter, bleibt aber linear.

### B2: lineare reziproke Zweizustandskopplung

S1-A ist exakt B2. Es wird kein Unterschied behauptet.

### B3: begrenzter Integrator

Bei unterdrueckter Rueckwirkung und verschwindender L-Relaxation entsteht
eine Integratornaehe. Diese Ablation bleibt als Gegenmodell erforderlich.

### B4: adaptiver Gain

S1-A addiert einen internen Austauschbeitrag und multipliziert weder
Rezeptorantrieb noch Diffusionsrate. Ein fester Leser kann die lineare
Gesamtdynamik dennoch als Zustandsraummodell darstellen.

### B5: L-nach-S-Ablation

Setzt nur den Term `+gL` in der S-Gleichung auf null, waehrend L unter
derselben S-Geschichte fortschreitet. Diese Intervention ist nur Testlogik,
keine Organismusphase.

## 10. Erwartbare und nicht erlaubte Aussagen

S1-A kann technisch erzeugen:

- einen von S verschiedenen langsamen lokalen Zustand;
- geschichtsabhaengige spaetere S-Fortsetzung;
- mit L wandernde Wirkung bei einem externen Zustandstausch;
- Ueberschreibung oder Umlagerung durch weitere Weltgeschichte;
- eine langsamere kausale Entwicklungsordnung als S und H.

Diese Eigenschaften bleiben vollstaendig durch eine lineare reziproke
Zweizustandsdynamik erklaert. Sie sind deshalb kein Nachweis fuer organisches
Memory, Feldzeitverdichtung, Cluster, Rekonstruktion, Semantik oder KI.

Insbesondere wird passives Fortbestehen nicht `Praegung` und linearer
Zustandsabbau nicht `Vergessen` genannt.

## 11. Technische Verwerfungskriterien

S1-A beziehungsweise ihre Implementierung wird verworfen, wenn:

- die interne Bilanz `S + rho L` im isolierten Austausch nicht schliesst;
- `rho > 1` nicht zu einer kleineren momentanen L-Aenderung fuehrt;
- ein Zustand ausserhalb der numerischen Toleranz `[-1,1]` verlaesst;
- Zeitteilung bei konstantem Generator einen anderen Endzustand erzeugt;
- `g = 0` den bisherigen S/H-Pfad veraendert;
- Snapshot und Wiederaufnahme L nicht vollstaendig tragen;
- die Aktualisierung von Schleifenreihenfolge oder Observer abhaengt;
- L Rohdaten, IDs, Wiederholungszahl oder Auswertungswerte enthaelt;
- die Implementierung die bestehende Substratmasse M als L umdeutet.

## Entscheidung

```text
S1-A Gleichungsfamilie:             gebunden
S1-A konkrete Gleichung:            gebunden
engste Baseline:                    B2 / identisch
technischer Parameterzeuge:         rho=8, g=0.25/s
gemeinsame Exaktintegration:         algebraisch gebunden
Memory- oder Entwicklungsclaim:     nein
Runtime-Aenderung:                  noch nein
Forschungslauf:                     nein
```

## Bester naechster Schritt

S1-B ist in der
[technischen Implementierung der reziproken Akkommodation](S1B_TECHNISCHE_IMPLEMENTIERUNG_REZIPROKE_AKKOMMODATION.md)
gebunden. S2-A/S2-B sind vorregistriert und der S2-C-Kern ist umgesetzt.
S2-C2 bis S2-C8 binden Einzelbatch, r1.a/c1.a, S/H-Angleichung, Probe P, N8,
Observer und Einpaardistanzen; S2-C9 bis S2-C16 schliessen die A/B-Referenz
bis zur kanonischen End-to-End-Komposition. Der S2-Zwischenentscheid verweist
als naechsten Schritt auf den statischen S1-C-Kandidatenvertrag. Noch keinen
Versuch ausfuehren und keine Praegung behaupten.
