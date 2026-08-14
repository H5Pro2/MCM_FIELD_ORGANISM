# Vergleich raeumlicher L-Kopplungsfamilien

## Status

```text
Auditart:                         statisch / mathematisch-konzeptionell
verglichene Familien:             drei
bedingt offene Familie:           R1 - nur S raeumlich mobil
R2 eigener L-Eigenfluss:          als erster Kandidat geschlossen
R3 reziproker Kreuzfluss:         als erster Kandidat geschlossen
konkrete Gleichung:               nicht gewaehlt
Runtime-Aenderung:                nein
```

## Prueffrage

Der Zulassungsvertrag fuer das ko-lokalisierte skalare L-Feld laesst drei
raeumliche Familien offen:

1. nur S ist raeumlich mobil, L koppelt lokal an S;
2. S und L besitzen getrennte symmetrische Eigenfluesse;
3. S und L tragen einen reziproken lokalen Kreuzfluss.

Der Vergleich fragt:

> Welche Familie fuegt die kleinste neue Naturannahme hinzu, die eine
> L-vermittelte spaetere S-Wirkung prinzipiell pruefbar macht, ohne bereits
> eine Musterphysik, Mobilitaetsregel oder neue Topologie vorzugeben?

Musterbildung ist kein Auswahlziel.

## Gemeinsame Grenze

Alle Familien verwenden denselben lokalen Gesamtzustand:

```text
X_i = (S_i,H_i,L_i)
```

Dabei gilt:

- S ist die vorhandene schnelle Activation.
- H bleibt die nachgelagerte schnelle Afterimage-Spur.
- L ist ein skalarer konstitutiver Zustand am selben Feldort.
- Weltkontakt erreicht L nur durch den normalen S-Feldpfad.
- Alle raeumlichen Wirkungen verwenden ausschliesslich die vorhandene
  symmetrische MCM-Geometrie.
- Keine Familie erhaelt Partner-IDs, adaptive Kanten, Zielmuster oder
  Lebenszyklusphasen.

## R1: Nur S ist raeumlich mobil

### Naturannahme

S behaelt die vorhandene symmetrische lokale Feldwirkung. L besitzt keinen
eigenen direkten Nachbarschaftsfluss. An jedem Ort entwickelt sich L nur in
der atomaren lokalen Wechselwirkung mit dem dortigen S-Gesamtverlauf.

Raeumliche Kausalitaet entsteht damit ausschliesslich ueber den vorhandenen
Pfad:

```text
S-Nachbarschaft
-> lokaler gemeinsamer S-L-Zustand
-> S-Nachbarschaft
```

L ist ortsgebundene konstitutive Feldkonfiguration, kein separates
transportiertes Signal.

### Unabhaengige Funktion

R1 fuegt genau eine moegliche Funktion hinzu:

> Derselbe lokale schnelle S-Zustand kann je nach eigener lokaler
> konstitutiver Vorgeschichte L unter identischer weiterer Feldwirkung anders
> fortgesetzt werden.

Die Familie fuegt keine neue raeumliche Anatomie und keinen neuen
Transportkoeffizienten hinzu.

### Methodische Grenze

R1 ist mathematisch eine Familie lokal identischer dynamischer Einheiten, die
ueber die bereits mobile S-Komponente gekoppelt sind. Damit liegt sie nahe an
Reaktions-Diffusionssystemen mit nur einer mobilen Komponente.

Ein raeumliches Muster, eine Instabilitaet oder ein langer lokaler Rest kann
daher vollstaendig durch eine Ein-Diffusor-Baseline erklaert sein. Besonders
hochfrequente oder gitterabhaengige Muster waeren ein Warnsignal, kein
Entwicklungsbefund.

### Vorteile

- kleinste neue Naturannahme;
- keine neue L-Transportphysik;
- keine L-Nachbarschaft oder L-Kante;
- bestehende S-Geometrie bleibt einzige raeumliche Ursache;
- klarer Nullpfad durch Entfernung der lokalen S-L-Kreuzwirkung;
- L-Tausch und L-Neutralisierung sind lokal definierbar.

### Baselinekollisionen

| Gegenmodell | Risiko |
|---|---|
| Leaky-Spur/Integrator | hoch bei einseitiger S-zu-L-Bildung |
| Gain/Mobilitaet | hoch, wenn L S nur skaliert |
| Oszillator | hoch bei konservativer lokaler Kreuzkopplung |
| Hysterese/Attraktor | hoch bei mehreren lokalen Ruhelagen |
| Ein-Diffusor-Reaktions-Diffusion | sehr hoch fuer kollektive Muster |
| klassische Zwei-Diffusor-Turingform | geringer, da L keinen Eigenfluss hat |
| Kreuzdiffusion | nein, solange L keine Nachbarschaft liest |

### Entscheidung

**R1 bleibt bedingt als einzige Familie fuer einen weiteren
Naturfunktionsvertrag offen.**

Die Entscheidung bevorzugt nicht Musterbildung. Sie bevorzugt die kleinste
Architekturerweiterung, mit der eine L-vermittelte spaetere S-Wirkung kausal
formulierbar wird.

## R2: Getrennte symmetrische S- und L-Eigenfluesse

### Naturannahme

Neben der vorhandenen S-Feldwirkung erhaelt L einen eigenen symmetrischen
lokalen Fluss auf denselben Sample-Offsets.

Abstrakt entstehen zwei raeumliche Eigenpfade:

```text
S-Unterschiede -> S-Fluss
L-Unterschiede -> L-Fluss
```

Lokale S-L-Wechselwirkung verbindet beide Komponenten am jeweiligen Ort.

### Zusaetzliche Vorannahmen

R2 benoetigt mindestens:

- eine neue physische L-Transportfaehigkeit;
- eine L-Flussskala oder ein Verhaeltnis zur S-Flussskala;
- eine Bilanz fuer L-Transport;
- Rand- und Nullbedingungen fuer L-Fluss.

Keine dieser Annahmen folgt aus der heutigen MCM-Runtime.

### Baselinekollision

R2 ist die direkte Struktur klassischer Zwei-Komponenten-Reaktions-Diffusion.
Unterschiedliche Eigenfluesse koennen diffusionsgetriebene Instabilitaeten und
Turing-Muster erzeugen. Deren Wellenlaenge und Stabilitaetsbereich folgen aus
Geometrie und Parametern der festen Naturform.

Eine entstandene raeumliche Inhomogenitaet waere daher zunaechst ein
Reaktions-Diffusionsbefund, keine entwickelte L-Organisation.

### Entscheidung

**R2 wird als erster MCM-L-Kandidat geschlossen.**

R2 bleibt eine starke Pflichtbaseline. Es darf spaeter nur wieder betrachtet
werden, wenn R1 nachweislich eine notwendige Funktion wegen fehlenden
L-Transports nicht darstellen kann.

## R3: Reziproker lokaler Kreuzfluss

### Naturannahme

R3 erlaubt raeumliche Kreuzwirkungen:

```text
lokaler L-Unterschied -> Beitrag zum S-Fluss
lokaler S-Unterschied -> Beitrag zum L-Fluss
```

Reziprozitaet soll verhindern, dass nur ein gerichteter L-Leser auf S wirkt.

### Konstanter linearer Kreuzfluss

Bei einer konstanten symmetrischen positiven Flussmatrix kann die
raumbezogene S-L-Wirkung durch einen festen lokalen Komponentenwechsel in
Eigenmoden zerlegt werden. In diesen Koordinaten entstehen getrennte
Eigenfluesse.

Der konstante reziproke Fall ist damit keine eigenstaendige Familie jenseits
von R2. Er ist eine andere Darstellung zweier fester raeumlicher Moden.

### Zustandsabhaengiger Kreuzfluss

Haengt die Flussmatrix vom lokalen Zustand ab, entsteht eine
zustandsabhaengige Transportgeometrie. Das kann reichere Dynamik tragen,
kollidiert aber unmittelbar mit:

- zustandsabhaengiger Mobilitaet;
- adaptivem Gain in Gradientenform;
- Kreuzdiffusionsmusterbildung;
- verdeckter richtungsabhaengiger Materialstruktur.

Die eigentliche Entwicklungsannahme laege dann in der gewaehlten
Zustandsabhaengigkeit der Flussmatrix.

### Physikalische Einordnung

Reziproke Kreuzwirkungen sind in der linearen irreversiblen Thermodynamik als
Kopplung verschiedener Fluesse und Kraefte bekannt. Diese physikalische
Moeglichkeit begruendet jedoch keine MCM-spezifische Kreuzflussgleichung.

Cross-Diffusion kann selbst in einfachen Reaktions-Diffusionssystemen
raeumliche und raumzeitliche Muster erzeugen. Solche Muster waeren erneut
eine direkte Standarderklaerung.

### Entscheidung

**R3 wird als erster MCM-L-Kandidat geschlossen.**

Der konstante reziproke Fall reduziert auf Eigenfluesse. Der
zustandsabhaengige Fall fuegt mehr unbegruendete Materialphysik als R1 hinzu
und besitzt eine starke Mobilitaets- und Kreuzdiffusionskollision.

## Gesamtvergleich

| Familie | neue raeumliche Annahme | staerkste Baseline | neue Parameterlast | Entscheidung |
|---|---|---|---:|---|
| R1 nur S mobil | keine zusaetzliche raeumliche L-Physik | Ein-Diffusor-Reaktions-Diffusion | niedrig | bedingt offen |
| R2 S-/L-Eigenfluss | eigener L-Transport | klassische Turing-/Reaktions-Diffusion | mittel | geschlossen als erster Kandidat |
| R3 reziproker Kreuzfluss | neue Kreuztransportphysik | Eigenfluss oder Cross-Diffusion | hoch | geschlossen als erster Kandidat |

## Warum R1 trotz lokaler No-Go-Grenze offen bleibt

Der vorherige Audit schliesst ein isoliertes L-Register. R1 ist nicht nur eine
Menge unabhaengiger Register:

```text
S_i beeinflusst L_i lokal
S transportiert Feldwirkung zwischen Orten
L_i beeinflusst die weitere lokale S_i-Fortsetzung
```

Damit sind die ortsgebundenen L-Zustaende indirekt ueber das vorhandene
S-Feld gekoppelt. Die verteilte Gesamtfunktion kann nicht durch Betrachtung
eines einzelnen isolierten L-Registers entschieden werden.

Gleichzeitig bleibt R1 vollstaendig gegen eine Ein-Diffusor-
Reaktions-Diffusionsbaseline zu pruefen. Die Offenheit ist eine
Forschungsmoeglichkeit, kein positiver Befund.

## Verbindliche Stopplinien fuer R1

Eine spaetere R1-Form erhaelt sofort STOPP, wenn:

1. L Nachbar-L-Werte oder eigene L-Kanten liest;
2. L den Rezeptorkontakt direkt statt durch S erhaelt;
3. L nur Spur, Integral, Gain, Mobilitaet oder Zeitkonstante ist;
4. die lokale S-L-Dynamik auf einen festen Oszillator reduziert;
5. mehrere Zielruhelagen oder eine Hysteresekurve eingebaut werden;
6. Parameter nach Muster, Wellenlaenge oder Instabilitaetserfolg gewaehlt
   werden;
7. ein hochfrequentes oder gitterabhaengiges Muster als Organisation
   interpretiert wird;
8. Loesung oder Wiederpraegung eine Sonderphase, Schwelle oder feste Dauer
   benoetigt;
9. der heutige S-H-Nullpfad nicht exakt konstruiert werden kann;
10. die Ein-Diffusor-Baseline nicht gleich budgetiert formulierbar ist.

## Forschungsentscheidung

```text
R1 weiter statisch praezisieren:  ja
R2 als erster Kandidat:           nein
R3 als erster Kandidat:           nein
L-Eigenfluss implementieren:      nein
Kreuzfluss implementieren:        nein
konkrete lokale S-L-Gleichung:    nicht freigegeben
```

Die geschlossenen Familien bleiben Pflichtbaselines und duerfen nicht als
positive R1-Eigenschaft umbenannt werden.

## Quellen

- A. M. Turing,
  [The Chemical Basis of Morphogenesis](https://www.damtp.cam.ac.uk/user/gold/pdfs/teaching/turing1952.pdf),
  1952. Primaerquelle fuer raeumliche Muster aus gekoppelter Reaktion und
  Eigenfluesse.
- H. Miyazako, Y. Hori und S. Hara,
  [Turing Instability in Reaction-Diffusion Systems with a Single Diffuser](https://arxiv.org/abs/1309.0111),
  2013. Zeigt Moeglichkeiten und Stabilitaetsgrenzen von Systemen mit nur
  einer raeumlich mobilen Komponente.
- L. Onsager,
  [Reciprocal Relations in Irreversible Processes II](https://doi.org/10.1103/PhysRev.38.2265),
  1931. Physikalische Grundlage reziproker linearer Kopplungen irreversibler
  Transportprozesse.
- V. K. Vanag und I. R. Epstein,
  [Cross-diffusion and pattern formation in reaction-diffusion systems](https://doi.org/10.1039/B813825G),
  2009. Dokumentiert Cross-Diffusion als eigenstaendige Quelle raeumlicher
  und raumzeitlicher Muster.

Die Auswahl R1 fuer den naechsten MCM-Schritt ist eine methodische Ableitung
dieses Audits. Die Quellen belegen weder MCM-Memory noch eine organische
Feldentwicklung.

## Bester naechster Schritt

Als naechstes wird ein **R1-Naturfunktionsvertrag fuer ortsgebundene lokale
S-L-Mitentwicklung unter bestehendem S-Feldfluss** formuliert.

Er muss ohne Gleichungswahl festlegen:

1. welche unabhaengige physische Funktion L jenseits von Spur, Gain,
   Mobilitaet, Integrator und Oszillator besitzen soll;
2. welche lokalen S-L-Kreuzwirkungen prinzipiell zulaessig sind;
3. welche Eigenschaften der Ein-Diffusor-Reaktions-Diffusionsbaseline
   zugerechnet werden;
4. welche Beobachtung einen spaeteren R1-Kandidaten von dieser Baseline
   unterscheiden koennte;
5. ob nach dieser Abgrenzung ueberhaupt ein nichtleerer R1-Raum verbleibt.

Nur bei einem nichtleeren Rest darf anschliessend eine konkrete lokale
Schliessungsfamilie verglichen werden.
