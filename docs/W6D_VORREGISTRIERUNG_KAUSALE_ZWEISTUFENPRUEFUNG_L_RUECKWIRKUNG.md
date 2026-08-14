# W6-D: Vorregistrierung der kausalen Zweistufenpruefung fuer L-Rueckwirkung

Stand: 2026-08-09

Entscheidung: `W6D_CAUSAL_TWO_STAGE_PROTOCOL_PREREGISTERED_NO_EXECUTION`

Arbeitsart: statische Vorregistrierung

Runtimeaenderung: nein

Ausfuehrung oder Forschungslauf: nein

## Forschungsfrage

Veraendert ein durch normalen kontrollierten Weltkontakt entstandener lokaler
S1-B-L-Zustand die spaetere schnelle Feldtrajektorie kausal, wenn der
schnelle Ausgangszustand und die spaetere Rezeptorprobe identisch gehalten
werden?

Die Frage betrifft ausschliesslich die implementierte lineare
S1-B-Referenzmechanik. Sie fragt noch nicht nach Memory, Wiedererkennung oder
Feldzeit.

## Weltgrenze

Zulaessig ist genau eine neue kontrollierte audiovisuelle Browser-Testwelt
mit drei getrennt gebundenen Sequenzteilen:

- `H_A`: primaere audiovisuelle Formationsgeschichte;
- `H_B`: geometrisch und zeitlich gleich lange, in den Rezeptorwerten andere
  audiovisuelle Donorgeschichte;
- `P`: fuer alle Vergleichsarme exakt identische spaetere Probe.

Die Sequenzen muessen vor Eintritt in S1-B bereits durch die bestehenden
visuellen und auditiven Rezeptoren reduziert sein. S1-B erhaelt keine
Browser-, Bild-, Audio-, Phasen- oder Welt-ID. Kamera, Live-Mikrofon,
physische Sensorik und oeffentliche Medien sind fuer diese erste Pruefung
nicht erforderlich und bleiben unbenutzt.

Die neue Welt darf keinen historischen W1-O-, W1-Q-, S2- oder 213ZZ-
Versuch ausfuehren oder fortsetzen. Alte Ergebnisse werden nur als
Ausschluss- und Methodenhinweis gelesen.

## Fest gebundene technische Geometrie

Alle drei Sequenzteile verwenden:

```text
Canvas:                    120 x 80
visuelles Rezeptorgitter:  3 x 2
visuelle Rate:             30 Hz
Audio-Abtastrate:          8000 Hz
Audio-Hop:                 80 Samples
auditive Baender:          8 logarithmische Baender
Feldantwortzeit:           1.0 s
Nachhallzeit:              0.5 s
kontinuierliche Leckage:   aus
L-Kapazitaetsverhaeltnis:  rho = 8.0
aktiver Kopplungswert:     k = 0.25 / s
Nullarm:                   k = 0.0 / s
```

H_A, H_B und P muessen dieselbe Feldgeometrie, dieselben Neuron-IDs, dieselbe
Organismusuhr und disjunkte, streng aufeinanderfolgende Zeitfenster besitzen.
Die konkrete Renderfolge und ihre Digests werden erst in W6-E implementiert
und vor jeder Browserausfuehrung statisch gebunden.

## Stufe 1: Formation

Aus demselben neutralen Anfangsfeld entstehen drei unabhaengige
Formationsfelder:

```text
F_A = aktiver S1-B-Arm nach H_A
F_B = aktiver S1-B-Arm nach H_B
F_0 = S1-B-Nullarm nach H_A
```

Pflichtpruefungen vor der Verzweigung:

1. alle eindeutigen Quellstuetzen wurden genau einmal zugewiesen;
2. kein Rohpayload wurde im Feld oder Report gespeichert;
3. F_A und F_B tragen denselben festen L-Vertrag;
4. F_A und F_B besitzen identische Geometrie und Neuronreihenfolge;
5. der S/H-Projektionsdigest von F_0 stimmt exakt mit einer unabhaengigen
   neutralen Ausfuehrung von H_A ueberein;
6. `L_A = F_A.development` und `L_B = F_B.development` sind endlich und
   normiert.

## Intervention und vier Arme

Von F_A und F_B werden vor P ausschliesslich folgende externe
Forschungsinterventionen abgeleitet:

```text
R = F_A unveraendert                     (retained L_A)
N = F_A mit neutralisiertem L             (L = 0)
X = F_A mit dem vollstaendigen L_B         (getauschtes L)
Z = F_0 unveraendert                       (Kopplungs-Nullarm)
```

R, N und X muessen unmittelbar vor P exakt denselben S/H-Projektionsdigest,
dieselbe Feldgeometrie, denselben Tick und denselben aktiven Naturvertrag
besitzen. Nur der vollstaendige L-Zustand darf verschieden sein. Einzelne
L-Orte duerfen nicht selektiv editiert werden.

X entsteht ausschliesslich durch den vorhandenen vollstaendigen L-Tausch
zwischen F_A und F_B. Der zweite Tauschpartner wird archiviert, aber in dieser
Minimalpruefung nicht fortgesetzt. Z besitzt den Nullvertrag und ist deshalb
keine kausale Einvariablenkontrolle fuer R; Z ist die Architekturbaseline.

## Stufe 2: Gemeinsame Probe

P wird ab demselben Organismuszeitpunkt und mit exakt denselben reduzierten
Rezeptorstuetzen unabhaengig auf R, N, X und Z angewandt. Die Quellobjekte
duerfen zwischen den Armen geteilt werden, Feldzustand und mutable
Rezeptorinstanzen nicht.

Ein passiver Observer darf nach jeder Rezeptorvervollstaendigung und am
Probeende nur Kopien folgender Vektoren erfassen:

```text
S(t), H(t), L(t), completion_tick
```

Der Observer darf weder Feldzustand veraendern noch Messwerte in die Runtime
zurueckschreiben.

## Vorregistrierte Messgroessen

Vor P:

```text
l_a_linf       = ||L_A||_inf
l_b_linf       = ||L_B||_inf
l_ab_linf      = ||L_A - L_B||_inf
fast_r_n_equal = digest(S/H_R) == digest(S/H_N)
fast_r_x_equal = digest(S/H_R) == digest(S/H_X)
```

Waehrend P, ueber alle identischen Observerzeitpunkte:

```text
d_rn_s = max_t ||S_R(t) - S_N(t)||_inf
d_rx_s = max_t ||S_R(t) - S_X(t)||_inf
d_xn_s = max_t ||S_X(t) - S_N(t)||_inf
d_rn_h = max_t ||H_R(t) - H_N(t)||_inf
d_rx_h = max_t ||H_R(t) - H_X(t)||_inf
```

Zusaetzlich wird die S/H-Projektionsgleichheit des Nullarms mit der neutralen
Runtime nach Formation und nach P digestgenau geprueft.

Technische Nachweisgrenze fuer skalare Differenzen ist `1e-12`. Werte bis zu
dieser Grenze gelten als numerisch nicht unterscheidbar. Es gibt keine
nachtraegliche Schwellwertwahl und keine Aggregation zu einem Erfolgswert.

## Entscheidungslogik

### Technisch nicht auswertbar

`STOP_TECHNICAL_INVALID` gilt bei einem verletzten Digest-, Geometrie-,
Handoff-, Zeit-, Endlichkeits-, Restore- oder Observervertrag.

`STOP_NONINFORMATIVE_FORMATION` gilt, wenn:

```text
l_a_linf <= 1e-12
oder
l_ab_linf <= 1e-12
```

Das ist kein negativer Kausalbefund, sondern eine ungeeignete Formation.

### Kein aufgeloester kausaler Unterschied

`NO_DETECTABLE_L_CAUSAL_EFFECT_IN_THIS_CONTRACT` gilt, wenn alle drei
S-Kontraste `d_rn_s`, `d_rx_s` und `d_xn_s` hoechstens `1e-12` betragen.

### Technische L-Rueckwirkung

`LOCAL_L_STATE_CAUSALLY_ALTERS_LATER_S_TRAJECTORY_IN_S1B_REFERENCE` gilt nur,
wenn:

1. R/N und R/X vor P exakt gleiche S/H-Projektionen besitzen;
2. Nullarm und neutrale Runtime exakt uebereinstimmen;
3. mindestens `d_rn_s` oder `d_rx_s` groesser als `1e-12` ist;
4. alle Observer-, Handoff- und Zeitvertraege bestehen.

Dieses Urteil bestaetigt nur die technisch erwartete L-nach-S-Kausalitaet der
implementierten Gleichung. Es ist kein Neuheits- oder Memorybefund.

## Gegenbaselines und Grenzen

Pflichtbaselines dieser Minimalpruefung sind:

- neutrale aktuelle S/H-Runtime ohne L;
- S1-B-Nullarm mit neutralem L;
- aktiver Arm mit nach Formation neutralisiertem L;
- aktiver Arm mit vollstaendig getauschtem L.

Leaky-Spur, langsame Feldkopie, fester Integrator, adaptiver Gain und glatte
Hysterese werden noch nicht ausgefuehrt. Sie werden erst benoetigt, wenn nach
der technischen L-Rueckwirkung eine weitergehende Funktionsrolle untersucht
wird.

Nicht zulaessig sind Aussagen ueber Praegung, Wiedererkennung,
Rekonstruktion, Vergessen, Feldzeit, innere Wahrnehmung, Organisation,
Topologie, Semantik, Selbstregulation oder KI.

## Implementierungsfreigabe

W6-D erlaubt noch keinen Browser- oder Forschungslauf. Freigegeben ist nur
W6-E als technische Umsetzung dieses unveraenderten Vertrags:

- neue kontrollierte Welt- und Sequenzvertraege;
- vollstaendige L-Neutralisierung und L-Tausch als explizite
  Referenzoperationen;
- passiver S/H/L-Trajektorienobserver;
- unveraenderlicher Ergebniscontainer mit den vorregistrierten Skalarwerten;
- Tests unter deterministischen Fakes und direkt konstruierten reduzierten
  Sequenzen.

## Aussagegrenze

W6-D erzeugt keine Evidenz. Es bindet nur die erste kausale Funktionspruefung
des neuen Entwicklungswegs. Lauf 197 bleibt reserviert und unberuehrt.

## Bester naechster Schritt

W6-E implementiert den Pruefadapter und seine technischen Akzeptanztests ohne
Browserstart. Erst nach bitgenauer Vertragsabnahme darf ein eigener,
ausdruecklich freigegebener kontrollierter Browserlauf geplant werden.
