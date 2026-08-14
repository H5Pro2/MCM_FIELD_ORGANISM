# S1-CC: E1 E3-identische Probe und Entscheidungsvertrag

## Status

Statische Vorregistrierung der Probe fuer die in S1-CB vorbereiteten
Zustandsarme. Die spaetere Implementierung und einmalige Ausfuehrung sind in
S1-CD dokumentiert. Dieses Dokument bleibt der unveraenderte Vorvertrag und
enthaelt selbst keinen Memory-, Vergessens-, Lern-, Organismus- oder
KI-Befund.

## Forschungsfrage

Veraendern die drei kontrollierten E1-Zustaende `HOLD`, `RELEASE` und
`COMPETE` unter einer identischen spaeteren Feldprobe den S/H-Feldverlauf
unterschiedlich, nachdem Freigabe und konkurrierende Wiederbindung bereits
getrennt auf Zustandsebene kontrolliert wurden?

Untersucht wird nur die technische kausale Wirkung der konstruierten
E1-Ressourcenmechanik.

## Unveraenderte Voraussetzungen

S1-CD darf ausschliesslich folgende bestehende Bausteine komponieren:

```text
S1-BX  linker Achtkontakt-E1-Geschichtszustand
S1-CB  HOLD-, RELEASE-, COMPETE- und NEUTRAL-Zustandsarme
S1-BW  eingefrorener aktiver und ablatierter Probeoperator
S1-BY  frisches Probefeld, Probe P und Zeitverfeinerung
P0     neutraler S/H-Feldpfad
```

E1-Vertrag, Feldparameter, Kontakte, Dauern und Toleranzen bleiben
unveraendert. Der S1-BZ-Ergebniscontainer wird nicht als Eingang verwendet
und der S1-BZ-Einmallauf wird nicht wiederholt.

## Frisches gemeinsames Probefeld

Das Probefeld `F*` wird wie in S1-BY aus einer frischen Kopie des neutralen
Anfangsfeldes durch genau einen neutralen Vorbereitungsschritt erzeugt:

```text
Vorbereitung Q          = (0.30, -0.20, 0.60)
Intervall               = Tick 0 bis 20
Dauer                   = 1.0 s
ticks_per_second        = 20.0
```

Danach werden zehn tiefe, objektgetrennte Kopien mit identischem
Snapshot-Digest gebildet. Historische S/H-Endfelder aus S1-BX oder S1-CB
duerfen nicht in die Probe eingehen.

## Identische Probe

```text
Probe P                 = (0.75, -0.25, 0.25)
Intervall               = Tick 20 bis 40
Dauer                   = 1.0 s
ticks_per_second        = 20.0
```

Alle Hauptarme erhalten denselben Payload einschliesslich `snapshot_id`,
Quelluhr, Organismusuhr und Wertefolge. Die Objekte bleiben getrennt.

## Zehn Hauptarme

```text
P0   neutrales Feld ohne E1

H0   HOLD, Rueckwirkung aus
R0   RELEASE, Rueckwirkung aus
C0   COMPETE, Rueckwirkung aus

H1   HOLD, Rueckwirkung an
R1   RELEASE, Rueckwirkung an
C1   COMPETE, Rueckwirkung an

G_H  fester Adapter aus H1, ohne E1-Zustandsentwicklung
G_R  fester Adapter aus R1, ohne E1-Zustandsentwicklung
G_C  fester Adapter aus C1, ohne E1-Zustandsentwicklung
```

Kein Arm liest den Ausgang eines anderen Arms. G_H, G_R und G_C duerfen nur
den im jeweiligen aktiven Arm angewendeten unveraenderlichen Adapter
uebernehmen.

## Zeitverfeinerung

Jeder feste Adapter G_H, G_R und G_C wird zusaetzlich mit derselben
konstanten Probe in zwei und vier Teilintervallen ausgefuehrt:

```text
n=1: 1 * 20 Ticks, primaerer Hauptarm
n=2: 2 * 10 Ticks
n=4: 4 * 5 Ticks
```

Fuer jeden Zustand werden S- und H-Linf zwischen n=2 und n=4 gebildet. Der
globale Numerikrest ist das Maximum ueber HOLD, RELEASE und COMPETE.

## Exakte Identitaetskontrollen

Der Lauf ist ohne Ergebnisentscheidung ungueltig, wenn eine der folgenden
Kontrollen scheitert:

```text
alle zehn F*-Kopien besitzen vor der Probe denselben Digest
P0 == H0 == R0 == C0 im Felddigest
H1 == G_H im Felddigest
R1 == G_R im Felddigest
C1 == G_C im Felddigest
alle eingefrorenen E1-Zustaende bleiben objektidentisch
S1-CB liefert E3_STATE_ARMS_READY_FOR_PROBE
keine historischen S/H-Endfelder werden als Probeobjekt verwendet
```

## Rohmetriken

Der unveraenderliche Ergebniscontainer fuehrt mindestens:

```text
pre_probe_s_linf
pre_probe_h_linf
ablation_p0_s_linf
ablation_p0_h_linf
fixed_gain_s_linf
fixed_gain_h_linf
refinement_s_linf
refinement_h_linf

hold_p0_s_linf
hold_p0_h_linf
release_p0_s_linf
release_p0_h_linf
compete_p0_s_linf
compete_p0_h_linf

release_hold_s_linf
release_hold_h_linf
compete_release_s_linf
compete_release_h_linf
compete_hold_s_linf
compete_hold_h_linf
```

Zusaetzlich wird der vollstaendige S1-CB-Zustandsarmcontainer unveraendert
referenziert. Der E3-Ergebniscontainer speichert keine Interpretation und
keinen Erfolgsstatus.

## Toleranz und technischer Effektboden

Unveraendert gilt:

```text
absolute_tolerance = 1e-12
relative_tolerance = 0
```

Ein technischer Paarunterschied gilt nur oberhalb des jeweils groesseren
Werts aus globalem Numerikrest und `1e-12` als nachweisbar.

```text
floor_S = max(refinement_s_linf, 1e-12)
floor_H = max(refinement_h_linf, 1e-12)
```

Die Grenze darf nach dem Lauf nicht angepasst werden.

## Vorregistrierte Entscheidung

Die Entscheidung wird ausserhalb des Ergebniscontainers in dieser festen
Reihenfolge getroffen:

### INVALID_RUN

Mindestens eine Identitaets-, Zustandsarm-, Bilanz-, analytische Freigabe-,
Ablations-, Fixed-Gain- oder Toleranzkontrolle scheitert.

### E3_RELEASE_AND_RESOURCE_REUSE

Alle Kontrollen bestehen und beide Bedingungen sind erfuellt:

```text
release_hold_s_linf > floor_S
oder release_hold_h_linf > floor_H
```

und

```text
compete_release_s_linf > floor_S
oder compete_release_h_linf > floor_H
```

Damit waeren programmierte Freigabe, erneute Ressourcenbindung und zwei
getrennte spaetere technische Feldwirkungen im ersten Korridor gemeinsam
belegt.

### E3_RELEASE_ONLY

Alle Kontrollen und der RELEASE/HOLD-Unterschied bestehen, aber COMPETE ist
unter der identischen Probe nicht oberhalb des Effektbodens von RELEASE
unterscheidbar.

### NO_E3_EFFECT_IN_FIRST_CORRIDOR

Alle Kontrollen bestehen, aber RELEASE ist unter der identischen Probe nicht
oberhalb des Effektbodens von HOLD unterscheidbar.

Die Richtung einzelner Aktivierungen oder Bindungen ist kein Erfolgskriterium.

## Aussagegrenze

Auch `E3_RELEASE_AND_RESOURCE_REUSE` bezeichnet nur einen technischen
Lebenszyklus der programmierten E1-Ressource. Der Befund waere staerker als
E2, aber weiterhin kein Nachweis fuer MCM-Memory, organisches Vergessen,
Rekonstruktion, Semantik, Selbstwahrnehmung oder KI.

Insbesondere bleiben offen:

```text
Rekonstruktion durch Teilhinweis
selektive Stabilisierung durch Wiederholung
Kapazitaetsverhalten bei mehreren konkurrierenden Mustern
Erklaerung gegen leaky, Integrator, F3 und CONST-V im selben Korridor
```

## Einmaligkeitsregel

S1-CD darf die Komposition zuerst implementieren und durch synthetische
Vertragspruefungen absichern. Der kanonische E3-Ergebnislauf wird danach
genau einmal ausgefuehrt. Bei `INVALID_RUN` oder fehlendem Effekt werden
Parameter und Schwellen nicht nachtraeglich angepasst.

## Bester naechster Schritt

S1-CD hat den privaten E3-Probekompositor implementiert und den kanonischen
Lauf genau einmal gueltig ausgefuehrt. S1-CE bindet als naechsten Schritt den
gesamten dynamischen Verlauf gegen transparente Pflichtbaselines.
