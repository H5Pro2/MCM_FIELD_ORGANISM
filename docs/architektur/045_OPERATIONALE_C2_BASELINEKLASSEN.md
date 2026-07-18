# Operationale C2-Baselineklassen

## Status

Methodischer Vergleichsvertrag auf `E0 / NO_CANDIDATE_SELECTED`.

Dieses Dokument schließt die in
[Kandidatenfamilien und C2-Baselinegrenze](044_KANDIDATENFAMILIEN_UND_C2_BASELINEGRENZE.md)
offengelegte Unschärfe. Es definiert endliche Gegenmodelle für einen späteren
passiven Memory-Kandidaten. Es ergänzt weder Zustand noch Gleichung in der
Runtime und wählt keine Kandidatenfamilie aus.

## Forschungsrolle

Die MCM stellt die gemeinsame Feldwahrnehmung bereit. Ein späteres organisches
Memory müsste als lern- und bindungsfähige Zustandsrolle desselben fortlaufend
weltberührten Feldes hinzukommen. Die Baselines prüfen, ob eine beobachtete
Geschichtswirkung bereits durch einfachere feste Zustände oder Leser erklärbar
ist.

Gesucht werden mit diesen Baselines weder Feldtopologie noch Feldintelligenz.
Eine mögliche Entwicklung wäre erst ein späterer Befund aus dem Zusammenspiel
von Feldwahrnehmung und Memory.

## Gemeinsamer Budgetvertrag

Vor jeder Kandidatenimplementierung wird ein endliches Vergleichsbudget
vorregistriert:

```text
S = persistente skalare Zustandswerte je Neuron
R = maximal gelesener lokaler Feldradius
P = freie skalare Parameter
Q = numerische Präzision und Wertebereich
H = verfügbares kausales Zeitpräfix
L = Leseradius und Zahl der Leseroperationen
```

Für C2 und B1 bis B6 gelten:

- dieselben Neuronen und dieselbe Geometrie;
- dieselben Rezeptorabschlüsse und dieselbe Organismuszeit;
- höchstens `S` persistente Werte je Neuron;
- höchstens Radius `R` bei Bildung und Leser;
- höchstens `P` freie skalare Parameter;
- identische Präzision, Schutzgrenzen und Initialisierung;
- kein Zugriff auf zukünftige Daten oder zusätzliche Historien;
- derselbe Snapshotumfang;
- dieselben Bildungs-, Lösungs-, Wiederbindungs- und Holdout-Phasen;
- keine nachträgliche Auswahl einer günstigeren Baselineklasse.

Kann eine Baseline ihr Budget strukturell nicht vollständig verwenden, wird
dies berichtet. Ihr ungenutztes Budget darf nicht durch zusätzliche
Historien, Kanten, Partnerkennungen oder einen zweiten Leser ersetzt werden.

## Parameterfestlegung

Parameter dürfen ausschließlich auf dem vorregistrierten Kalibrierpräfix
bestimmt werden. Danach werden sie eingefroren.

```text
Kalibrierpräfix -> Parameter festlegen
Interventionen  -> keine Anpassung
Lösung          -> keine Anpassung
Wiederbindung   -> keine Anpassung
Holdout-Probe   -> keine Anpassung
```

Berichtet werden sowohl der beste zulässige Baselinewert als auch die
vollständige Parametersuche. Vor dem Lauf muss entweder ein endliches
Parameterraster oder ein deterministischer Optimierer mit festen Grenzen,
Startpunkten, Abbruchkriterium und maximaler Auswertungszahl feststehen. Eine
Auswahl anhand der Holdout-Antwort macht den Vergleich ungültig.

## B0: unveränderte neutrale Feldruntime

```text
zusätzlicher persistenter Zustand = 0
zusätzlicher Leser                = 0
```

B0 prüft, ob Aktivierung, schneller Nachhall, heutige lokale Felddynamik und
aktuelle Weltkontakte den vollständigen Verlauf bereits erklären.

Trägt B0 den Effekt, liegt kein zusätzlicher Memory-Befund vor.

## B1: unabhängige lineare Leaky-Zustände

Jedes Neuron darf bis zu `S` voneinander unabhängige Zustände tragen:

```text
a_q(dt)     = exp(-dt / tau_q)
z_q(t + dt) = a_q(dt) * z_q(t) + (1 - a_q(dt)) * e_q(t)
```

Zulässig sind:

- feste Zeitkonstanten;
- affine lokale Evidenz aus den bereits verfügbaren Feldrollen;
- feste Begrenzung auf den gemeinsamen Wertebereich.

Nicht zulässig sind:

- Zustandsaustausch zwischen Neuronen;
- Kopplung zwischen den `z_q`;
- zustandsabhängige Koeffizienten;
- Partner- oder Kantenidentitäten.

B1 deckt gewöhnliche Einzelspuren und mehrere feste Zeitlagen ab.

## B2: unabhängige Produktintegratoren

B2 verwendet dieselbe unabhängige Fortschreibung wie B1. Die lokale Evidenz
darf zusätzlich aus vorregistrierten Produkten höchstens zweiten Grades
bestehen:

```text
e_q in {
  x,
  y,
  x * y,
  x * x,
  y * y
}
```

`x` und `y` müssen bereits vorhandene lokale Feldrollen am selben Neuron und
zur selben abgeschlossenen Zeit sein.

Nicht zulässig sind Produkte mit:

- fremden persistenten Zuständen;
- zukünftigen Feldwerten;
- variablen Partnern;
- nachträglich ausgewählten Merkmalen.

B2 deckt lokale Koinzidenz- und Eligibility-Trace-Erklärungen ab.

## B3: unabhängige begrenzte Nichtlinearität

B3 verwendet die zeitkontinuierliche Leaky-Fortschreibung aus B1 und erlaubt
pro Zustand genau eine vorregistrierte punktweise Begrenzung ihres
unbegrenzten Ergebnisses:

```text
clip
tanh
oder rationale Saettigung: u / (1 + abs(u))
```

Die Klasse bleibt neuronweise faktorisiert. Jeder nächste Zustand hängt nur
vom eigenen Vorzustand, lokaler aktueller Evidenz und realer Dauer ab.

Nicht zulässig sind:

- Kopplung mehrerer persistenter Zustände;
- lokale Nachbarschaftssummen;
- adaptive Schwellen;
- wechselnde Nichtlinearitäten während des Laufs.

B3 prüft, ob Sättigung allein scheinbare Konkurrenz, Lösung oder
Ressourcenfreigabe erzeugt.

## B4: fester lokaler Leser

B4 ergänzt keinen eigenen persistenten Zustand. Er darf B0 bis B3 mit einer
vorregistrierten lokalen Leserform auswerten:

```text
affine Summe
produktive Modulation ersten Grades
feste punktweise Begrenzung
```

Der Leser:

- erhält höchstens Radius `R`;
- verwendet höchstens das Budget `L`;
- verändert keinen Zustand;
- wird erst nach der zu prüfenden Bildungsphase ausgewertet;
- bleibt über Tausch, Lösung, Wiederbindung und Holdout unverändert.

Entsteht der Funktionsunterschied erst in B4, ist nur eine feste Leserwirkung
gezeigt. Das erfüllt den C2-Vertrag nicht.

## B5: feste lokale Rekurrenz

B5 ist die stärkste zulässige dynamische Gegenbaseline. Sie besitzt bis zu `S`
Zustände je Neuron und genau eine feste lokale Fortschreibungsstufe pro
physischer Zeitintegration:

```text
u_i = A * z_i + Summe_{j in Radius R}(K_ij * z_j) + C * e_i
z_i_neu = phi(u_i, dt)
```

Verbindliche Begrenzungen:

- `A`, `K` und `C` sind nach dem Kalibrierpräfix konstant;
- `K` hängt nur von relativer lokaler Geometrie ab;
- dieselbe Regel gilt an allen übersetzbaren Feldorten;
- `phi` ist genau eine vorregistrierte Funktion aus B3;
- pro Integrationsabschnitt gibt es keine verborgene innere Iterationsschleife;
- Koeffizienten werden weder durch Zustand noch Geschichte verändert;
- es gibt keine multiplikative Kopplung verschiedener Nachbarzustände;
- es gibt keine Kante, Partnerkennung, Kapazitäts- oder Gewinnervariable.

B5 darf damit feste Diffusion, feste laterale Kopplung und ein einfaches
lokales rekurrentes Feld darstellen. B5 umfasst ausdrücklich nicht jede
beliebige nichtlineare lokale Zustandsmaschine. Eine Mechanik mit
zustandsabhängig veränderter Kopplung wäre Teil der Kandidatenbehauptung und
müsste kausal abgetragen werden, nicht nachträglich in B5 verschwinden.

## B6: feste lokale Normalisierung

B6 darf die aktuelle lokale Ausgabe von B1 bis B5 innerhalb Radius `R` durch
genau eine vorregistrierte Norm begrenzen:

```text
L1-Summennorm
L2-Norm
oder divisive Norm mit festem epsilon
```

Die Normalisierung:

- besitzt keinen eigenen persistenten Zustand;
- verwendet feste Koeffizienten;
- bezeichnet keine Ressource;
- verändert keine späteren Updateparameter;
- bleibt unter allen Phasen identisch.

B6 prüft, ob eine programmierte lokale Konkurrenz den beobachteten Effekt
vollständig erklärt. Trägt B6, ist keine natürliche Ressourcenfreigabe oder
Wiederbindung gezeigt.

## Abgrenzung der Klassen

| Klasse | Eigene Geschichte | Nachbarschaft | Zustandsabhängige Kopplung | Persistente Beziehung |
|---|---:|---:|---:|---:|
| B0 | nur heutige Runtime | heutige Runtime | nein | nein |
| B1 | unabhängige lineare Spuren | nein | nein | nein |
| B2 | unabhängige lokale Produktspuren | nein | nein | nein |
| B3 | unabhängige begrenzte Spuren | nein | nein | nein |
| B4 | keine neue Geschichte | fester Leser | nein | nein |
| B5 | feste gekoppelte Rekurrenz | ja, bis `R` | nein | nein |
| B6 | wie Trägerbaseline | feste lokale Norm | nein | nein |

B1 bis B3 prüfen faktorisiertes lokales Memory. B4 prüft eine nachgeschaltete
Lesererklärung. B5 prüft feste gekoppelte Felddynamik. B6 prüft programmierte
lokale Konkurrenz.

## Pflichtkontrollen

Jede Baseline und ein späterer Kandidat müssen bestehen unter:

- grober und feiner Zeitteilung derselben realen Dauer;
- Spiegelung und Übersetzung;
- umgekehrter Neuronen- und Zweigreihenfolge;
- identischem vollständigem Neuaufbau;
- Snapshot und Wiederaufnahme;
- entferntem Observer;
- konstruktiver Angleichung von Aktivierung und schnellem Nachhall;
- getauschter, gleichgesetzter und neutralisierter Kandidatenlage;
- Lösung ohne Reset;
- Wiederbindung nur durch neue lokale Weltgeschichte.

## Entscheidungsmatrix

```text
B0 traegt den Effekt
-> kein zusaetzlicher Memory-Zustand notwendig

B1 bis B3 tragen den Effekt
-> unabhaengige lokale Spur genuegt

B4 traegt den Effekt
-> feste Leserwirkung, C2 nicht getragen

B5 traegt den Effekt
-> feste lokale Rekurrenz genuegt

B6 traegt den Effekt
-> programmierte Normalisierung erklaert Konkurrenz

keine Baseline traegt den Effekt
-> nur Zulassung zu weiterer kausaler Pruefung
```

Das Scheitern aller Baselines beweist weder organisches Memory noch natürliche
Organisation. Es beseitigt nur diese vorregistrierten einfacheren
Alternativerklärungen.

## Freigabegrenze

```text
B1 bis B6 operational definiert:  ja
gemeinsamer Budgetvertrag:        ja
B5 endlich abgegrenzt:            ja
C2-Kandidat ausgewählt:           nein
Updategleichung festgelegt:       nein
persistenter Zustand ergänzt:     nein
Runtime verändert:                nein
```

## Nächster Schritt

Als Nächstes darf ausschließlich geprüft werden, ob die bedingt offene Familie
K6 unter diesem Vertrag überhaupt einen kleinsten darstellungsoffenen
Kandidatenvorschlag zulässt. Vor jeder Gleichung muss erklärt werden:

1. welche Zustandsfunktion über B0 bis B6 hinaus fehlt;
2. warum die Wirkung bereits während identischer B-Evidenz entsteht;
3. wie sie ohne Reset vollständig an Wirkung verliert;
4. wie neue lokale Weltgeschichte danach eine andere Wirkung tragen kann;
5. weshalb keine Kante, Ressource, Zieltopologie oder Semantik vorgegeben wird.

Bleibt eine dieser Fragen offen, wird kein C2 implementiert.
