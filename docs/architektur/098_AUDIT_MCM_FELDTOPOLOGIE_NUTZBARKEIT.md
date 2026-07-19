# Audit der MCM-Feldtopologie-Nutzbarkeit

## Zweck

Dieser Audit prüft, ob die bisherige Suche nach einem Memory-Träger die
eigentliche Organisationsmöglichkeit des gemeinsamen MCM-Feldes zu stark
verengt hat.

Er ergänzt keine Runtime-Funktion und keine Zustandsrolle.

## Drei getrennte Ebenen

### 1. Aktuelle Feldform

Die aktuelle Feldform besteht aus:

```text
räumlicher activation
+ räumlichem afterimage
+ lokalen Proben des unmittelbar vorherigen Feldtakts
```

Diese Ebene ist technisch vorhanden.

### 2. Laufende Feldorganisation

Eine laufende Feldorganisation liegt im engen technischen Sinn vor, wenn
lokale Feldlagen die nächste Feldbildung beeinflussen.

Die Live-Runtime besitzt diese Wirkung bereits. Der
`NeutralLocalFieldSubstrate` bildet aus der festen Nachbarschaftsmatrix einen
symmetrischen Diffusionsgenerator und integriert den vorherigen
Aktivierungszustand über die reale Organismusdauer.

Die öffentliche `MCMFieldPerception` stellt dieselbe lokale Vorfeldinformation
als Nachbarproben bereit. Die exakte Live-Integration verwendet jedoch direkt
den mathematisch äquivalenten festen Generator.

Damit gilt:

```text
lokaler Vorzustand
+ feste Nachbarschaft
+ feste Reaktionszeit
+ aktueller Rezeptorkontakt
-> nächste Feldform
```

Diese Ebene ist technisch vorhanden, aber vollständig festgelegt.

### 3. Entwickelte MCM-Feldtopologie

Eine entwickelte Feldtopologie würde verlangen:

```text
frühere Welt- und Feldgeschichte
-> veränderte funktionale Feldorganisation
-> andere spätere Aufnahme oder Weiterleitung
```

Diese Wirkung müsste über die aktuelle schnelle Feldlage hinaus tragen,
begrenzt bleiben, Wirkung verlieren und unter anderer Weltgeschichte anders
neu entstehen können.

Diese Ebene ist nicht vorhanden. Evidenzstand bleibt `E0`.

## Welche Funktionen lokale Feldproben lesen

### Aktive Runtime

Die aktive Audio-Video-Runtime verwendet:

- `advance_neutral_shared_field_transient`;
- optional `advance_neutral_fast_shared_field_transient`;
- eine feste symmetrische Nachbarschaftsmatrix;
- positive lineare Diffusion;
- optional einen festen schnellen Nachhall.

Die lokale Wirkung ist real und kausal. Sie ist aber vollständig durch
Geometrie, Reaktionszeit, aktuellen schnellen Zustand und Rezeptorkontakt
bestimmt.

### Transportbaseline

`receptor_projection_baseline` ignoriert lokale Feldproben vollständig:

```text
activation = aktueller Rezeptorkontakt
afterimage = 0
```

Sie eignet sich nur für Transport- und Nullkontrollen.

### Forschungsfunktionen

Mehrere passive Forschungsproben lesen lokale Feldproben ausdrücklich,
darunter:

- minimale lokale Feldwirkung;
- zeitliche Richtungsleser;
- instantaner Feldfluss;
- passive Feldkontrollen;
- verworfene Rezeptivitäts- und Synapsenkandidaten.

Diese Funktionen sind keine aktive Live-Mechanik. Wo sie eine Wirkung
erzeugten, blieb diese durch feste Leser, Diffusion, Nachhall oder Integrator
erklärbar.

## Mathematische Grenze der aktiven Feldkopplung

Die aktive schnelle Feldgleichung besitzt die Form:

```text
dx/dt = Gx + b
```

Dabei sind:

- `x` die aktuelle Aktivierungsverteilung;
- `G` der feste symmetrische Diffusionsgenerator;
- `b` die aktuelle Rezeptorrandwirkung.

Für gegebenes `x`, `G` und `b` ist die weitere Feldwirkung eindeutig. Der
Generator verändert sich nicht durch Feldgeschichte.

Der vorhandene
[Redundanzbefund des instantanen Feldflusses](../forschung/009_INSTANTANER_FELDFLUSS_REDUNDANZBEFUND.md)
zeigt, dass jeder momentane lokale Fluss vollständig aus `x`, fester
Nachbarschaft und fester Reaktionszeit rekonstruiert wird.

Der
[Passivitäts-Nullbefund](../forschung/010_PASSIVITAET_DES_BESTEHENDEN_FELDES_NULLBEFUND.md)
zeigt zusätzlich, dass kontaktfreie Feldformen durch die bestehende positive
Diffusion dissipieren. Die Passivitätsbilanz trägt keinen weiteren
Organisationszustand.

## Richtige Kritik an der bisherigen Richtung

Die Forschung wurde konzeptionell zu stark auf folgende Frage verengt:

```text
Wo liegt ein zusätzlicher Memory-Träger?
```

Dadurch wurde laufende Feldorganisation teilweise nur als Vorstufe behandelt.
Für das Projektziel ist die richtige erste Frage:

```text
Kann das gemeinsame Feld seine funktionale Organisation
durch fortlaufende lokale Welt- und Feldwirkung verändern?
```

Memory wäre danach keine separate Datenbank, sondern die nachweisbare
Dauerwirkung einer solchen veränderten Feldorganisation.

## Was die Richtungsänderung nicht bedeutet

Die neue Sichtweise reaktiviert keine verworfene Mechanik:

- C1 bleibt ein begrenzter Produktintegrator.
- Der Synapsenkandidat bleibt eine fest definierte Kantenfortschreibung.
- Instantaner Feldfluss bleibt zum schnellen Zustand redundant.
- Positive Diffusion bleibt eine feste dissipative Kopplung.
- Kontaktmorphologie bleibt ohne begründete Materialphysik passiv.
- Zeitrichtungsleser bleiben feste Observerfunktionen.

Diese Gegenbefunde gelten unabhängig davon, ob sie als Memory- oder
Topologiekandidaten bezeichnet werden.

## Ungenutzte und fehlende Freiheitsgrade

### Bereits nutzbar

- gemeinsames Feld statt getrennter Sinnesfelder;
- lokale Vorfeldwahrnehmung;
- fortlaufende Weltzeit;
- atomare gemeinsame Feldtakte;
- räumlich verteilte Aktivierungs- und Nachhallformen;
- modalitätsübergreifende Nachbarschaft im selben Feld.

### Fest und nicht entwickelbar

- Neuronenpositionen;
- lokale Nachbarschaft;
- Diffusionsrichtung und Diffusionsstärke;
- Reaktionszeit;
- Nachhallzeit;
- Zahl und Bedeutung der Zustandsrollen.

### Tatsächlich fehlend

Es fehlt ein feldinterner Freiheitsgrad, durch den Feldgeschichte die spätere
lokale Feldwirkung verändern kann.

Dieser Freiheitsgrad darf nicht als fertige Kante, Gewicht, Beziehung,
Memory-Slot oder Zieltopologie eingeführt werden. Er müsste:

- aus lokaler Feldteilnahme hervorgehen;
- die spätere Feldbildung kausal verändern;
- gegen feste Diffusion, Nachhall und Integratoren bestehen;
- begrenzt und vollständig lösbar sein;
- keine Bedeutung oder gewünschte Struktur enthalten.

Der Audit identifiziert diese Funktionslücke, aber keine zulässige digitale
Darstellung.

## Entscheidung

Die aktuelle Feldmechanik nutzt MCM-Lokalität für momentane Feldformen und
feste laufende Diffusion. Sie nutzt die MCM-feldtopologische Möglichkeit
nicht für entwickelbare funktionale Organisation.

Die Ursache ist nicht ein übersehener vorhandener Leser. Die aktive
Feldgleichung besitzt dafür keinen veränderlichen Freiheitsgrad.

Damit gilt:

```text
Transportbaseline:                 behalten
feste lokale Diffusion:            behalten
schneller Nachhall:                behalten
separaten Memory-Träger suchen:    stoppen
Topologie direkt programmieren:    verboten
feldinterne Organisationsfunktion: konzeptionell offen
```

## Richtungsentscheidung

Die Forschung wird neu geordnet:

```text
nicht zuerst Memory einbauen
-> vorhandene Feldorganisation offenlegen
-> feste Feldwirkung von entwickelbarer Organisation trennen
-> fehlenden feldinternen Freiheitsgrad funktional begründen
-> erst danach einen passiven Kandidaten zulassen
```

## Wie es am besten weitergeht

Als nächster Schritt darf ausschließlich ein konzeptioneller
**Freiheitsgrad-Zulassungsvertrag für feldinterne Organisation** entstehen.

Er darf noch keine Variable oder Gleichung auswählen. Er muss zuerst
festlegen, welche beobachtbare Funktion ein solcher Freiheitsgrad zusätzlich
zur aktuellen Feldform erfüllen müsste und wodurch seine Veränderung aus
realer lokaler Feldteilnahme kausal begründet wäre.

Kann keine solche unabhängige Feldfunktion benannt werden, bleibt die
Mechanikerweiterung geschlossen.
