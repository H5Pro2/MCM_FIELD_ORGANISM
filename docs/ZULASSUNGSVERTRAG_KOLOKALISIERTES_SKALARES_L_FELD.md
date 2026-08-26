# Zulassungsvertrag fuer ein ko-lokalisiertes skalares L-Feld

## Status

```text
Vertragstyp:                         verbindliche Forschungsgrenze
lokale Zusatzdimension:              genau ein Skalar L pro Feldort
Systemgrenze:                        ein gemeinsames mehrkomponentiges MCM-Feld
direkter Rezeptorzugriff durch L:     verboten
eigene L-Kanten oder L-Identitaeten:  verboten
konkrete Gleichung:                  nicht gewaehlt
Schema- oder Runtime-Aenderung:       gesperrt
```

## Zweck

Der skalare Suffizienzaudit schliesst ein isoliertes L-Register, behaelt aber
einen Skalar pro Feldort als verteilte Feldkomponente offen. Dieser Vertrag
bestimmt, welche Informationen eine spaetere L-Naturform lesen darf, wie S
und L dieselbe Kausalgrenze teilen und welche Mechaniken trotz der Oeffnung
verboten bleiben.

Der Vertrag waehlt weder Reaktions-, Fluss- noch Kreuzkopplungsgleichung.

## 1. Gemeinsamer lokaler Gesamtzustand

Fuer jeden bestehenden MCM-Feldort `i` werden funktional unterschieden:

```text
S_i = schnelle aktuelle Activation
H_i = bestehende schnelle Afterimage-Spur
L_i = moegliche langsame lokale konstitutive Feldkonfiguration
```

Verbindliche Einordnung:

- S, H und L gehoeren zu demselben lokalen MCM-Gesamtzustand.
- L erhaelt keine eigene Neuronenschicht und keine separate Runtime.
- L verwendet dieselben Feldorte und dieselbe feste Geometrie wie S.
- H bleibt die vorhandene schnelle Spur und wird nicht in L umbenannt.
- L ist weder Memory noch Organisation, sondern nur ein offener
  konstitutiver Freiheitsgrad.

## 2. Erlaubte Kausalinformationen

Eine spaetere gemeinsame Naturform darf an Ort `i` nur lesen:

1. den abgeschlossenen eigenen Vorzustand `(S_i,H_i,L_i)`;
2. die bereits vorhandenen lokalen S-Vorfeldwerte auf den festen symmetrischen
   Sample-Offsets;
3. lokale L-Vorfeldwerte ausschliesslich auf denselben Sample-Offsets, falls
   eine spaetere Familie deren Notwendigkeit begruendet;
4. den gegenwaertigen lokalen S-Feldantrieb aus normalem Rezeptor- und
   Nachbarschaftspfad;
5. reale Organismusdauer `dt`;
6. feste inhaltsfreie lokale Naturparameter.

### Verbotener Direktzugriff

L darf nicht direkt lesen:

- Receptor-Frame, Carrier-ID oder Rohmedienwert;
- Dock-, Modalitaets- oder Quellenidentitaet als funktionales Signal;
- Episode, Fensterklasse oder Wiederholungszahl;
- Probe, Holdout, Observerwert oder Gegenhistorie;
- Zielmuster, Sollzustand oder spaetere Ausgabe.

Weltkontakt muss L durch den normalen gemeinsamen S-Feldpfad erreichen. Ein
paralleler Rezeptor-zu-L-Schreibkanal waere ein separater Speicherpfad.

### Rolle von H

H darf als Teil des vollstaendigen technischen Vorzustands serialisiert
bleiben. Fuer die erste L-Hypothesenfamilie darf H jedoch keine Bildungsquelle
oder Kopplungssteuerung fuer L sein.

Andernfalls wuerde die bekannte lineare Afterimage-Spur nur durch einen
weiteren Leser zum scheinbaren Entwicklungssubstrat. Eine spaetere Nutzung
von H benoetigte eine eigene unabhaengige Begruendung und Baseline.

## 3. Atomare gemeinsame Fortschreibung

Eine zulaessige Naturform besitzt nur eine gemeinsame Kausalgrenze:

```text
abgeschlossener lokaler Gesamtvorzustand
+ abgeschlossenes lokales Vorfeld
+ S-vermittelter Weltantrieb
+ dt
-> gemeinsamer lokaler Gesamtfolgezustand
```

Dabei muessen S und L aus demselben Vorzustand vorgeschlagen und gemeinsam
abgeschlossen werden. Verboten sind:

- zuerst S berechnen und danach als fertiges Ergebnis in L schreiben;
- zuerst L schreiben und danach durch einen getrennten Leser auf S anwenden;
- besondere Lern-, Konsolidierungs-, Probe- oder Loeschschritte;
- unterschiedliche Gleichungen fuer Bildung, Wirkung und Umbildung;
- innerhalb eines Schritts aktualisierte Nachbarwerte lesen.

Eine spaetere exakte Integration darf interne mathematische Zwischenwerte
verwenden. Diese duerfen keine zusaetzlichen persistenten Organismuszustaende
oder semantischen Phasen bilden.

## 4. Zulaessige raeumliche Grenze

### Gemeinsame Anatomie

L darf nur die bestehende lokale MCM-Geometrie verwenden:

- identische Feldpositionen;
- identische symmetrische Sample-Offsets;
- identische periodische Achsvertraege, falls vorhanden;
- keine neuen ausgezeichneten Orte;
- keine modalitaetsspezifischen L-Gesetze.

### Keine gespeicherte Beziehung

Lokale L-Nachbarschaft ist eine anatomische Feldprobe, keine gespeicherte
Kante. Unzulaessig sind:

- Partner- oder Relations-ID;
- persistentes Kantengewicht;
- lernende Adjazenz;
- Routing oder Gewinnerauswahl;
- vom Observer erzeugte Cluster-Nachbarschaft.

### Raeumliche L-Wirkung ist noch offen

Dieser Vertrag schreibt nicht vor, ob L selbst raeumlich fliesst. Drei
Familien bleiben fuer einen folgenden statischen Vergleich offen:

1. nur S ist raeumlich mobil; L koppelt lokal an S;
2. S und L besitzen je einen symmetrischen lokalen Eigenfluss;
3. S- und L-Unterschiede tragen einen reziproken lokalen Kreuzfluss.

Keine dieser Familien ist durch diesen Vertrag bevorzugt oder zugelassen.

## 5. Symmetrien und Inhaltsfreiheit

Eine konkrete Naturform muss mindestens erhalten:

- Translation der vorhandenen Feldgeometrie;
- Spiegelung;
- Achstausch bei technisch gleichartigen Achsen;
- Umbenennung technischer Neuronenidentitaeten;
- Reihenfolgeneutralitaet atomarer Vorschlaege;
- Gleichheit der Naturform an allen gleichartigen Orten.

Die konkrete L-Konfiguration muss mit einer transformierten Weltgeschichte
entsprechend mittransformieren. Ein fest ausgezeichnetes Muster oder eine
bevorzugte Neuronenfolge ist unzulaessig.

## 6. Nullpfad und Ablationen

### Struktureller Nullpfad

Eine spaetere Hypothese muss die heutige Runtime als exakten verschachtelten
Nullfall enthalten:

```text
L_i = neutral an allen Orten
+ deklarierte S-L-Kopplung bei Konstruktion auf null gesetzt
-> bytegleiches heutiges S-H-Verhalten
```

Die neutrale Kopplung ist eine Forschungsablation beziehungsweise eine fest
konstruierte Baseline. Sie darf kein dynamischer Organismusmodus und keine
laufzeitliche Wenn-X-dann-Y-Schaltung sein.

### Kausale Richtungsablationen

Spaeter muessen getrennt konstruierbar sein:

- `S -> L` entfernt, `L -> S` erhalten;
- `L -> S` entfernt, `S -> L` erhalten;
- L-Nachbarschaftswirkung entfernt;
- L-Zustand neutralisiert;
- L-Zustand zwischen kontrollierten Verlaeufen getauscht.

Diese Eingriffe sind nur Forschungsinstrumente und werden nicht Teil der
Organismusfunktion.

## 7. Endlichkeit und Bilanz

Fest sein duerfen:

- endlicher L-Wertebereich;
- endlicher lokaler Wirkungsradius;
- endlicher Rechenaufwand;
- numerische Validierungsgrenzen;
- lokale Dissipations- oder Passivitaetsbedingungen;
- feste vorregistrierte Parameterbereiche.

Nicht als Befund gelten:

- Clipping oder Saettigung;
- numerisches Einfrieren;
- Schrittweitenabhaengigkeit;
- Grenzwertanhaeufung;
- reine Amplitudenbegrenzung.

Eine globale Grenze muss aus lokalen Bilanzen und Randfluessen folgen. Eine
globale Normalisierung, Ressourcenverteilung oder Gewinnerauswahl ist
verboten.

## 8. Streng verbotene Gleichungsfunktionen

Eine spaetere Gleichungsfamilie erhaelt sofort STOPP, wenn sie:

- L als Kopie, gleitenden Mittelwert oder Leaky-Spur von S definiert;
- L nur als Gain, Receptivity, Zeitkonstante oder Mobilitaet liest;
- S, H, Aktivitaet oder Koaktivitaet lediglich in L integriert;
- feste Attraktorlagen oder eine Hystereseschleife als gewuenschte Zustaende
  einbaut;
- Parameter auf eine Zielwellenlaenge oder Zielmusterfamilie abstimmt;
- Turing-Muster, Flecken, Streifen oder Cluster als Erfolgskriterium nutzt;
- Lernen, Binden, Loeschen oder Wiederpraegen durch Schwelle, Zaehler, Phase
  oder feste Dauer ausloest;
- eine Modalitaet, Episode oder Identitaet bevorzugt;
- L aus Observer- oder Ergebniswerten aktualisiert;
- eine unbegrenzte Eigenanregung ohne Welt- oder vorhandene Feldwirkung
  erzeugt.

## 9. Pflichtbaselines

Vor jeder konkreten L-Gleichung muessen aus ihrer behaupteten Funktion die
relevanten engen Baselines gewaehlt werden. Der Mindestkatalog ist:

1. heutige neutrale S-H-Runtime;
2. lokale L-Leaky-Spur;
3. lokaler L-Integrator und Saettigungsintegrator;
4. adaptiver Gain beziehungsweise Receptivity;
5. variable Zeitkonstante beziehungsweise Mobilitaet;
6. linear reziprokes S-L-Paar;
7. gedaempfter und ungedaempfter S-L-Oszillator;
8. feste skalare Hysterese;
9. klassische Zwei-Komponenten-Reaktions-Diffusion;
10. Ein-Diffusor-Reaktions-Diffusion;
11. feste Attraktor- oder Musterlandschaft;
12. strukturell reduzierte S-L-Ablationen.

Ein Muster, eine lange Nachwirkung oder eine unterschiedliche Probeantwort
genuegt nicht. Der gesamte behauptete Kausal- und Lebenszyklus muss gegen die
passenden Baselines getrennt werden.

## 10. Was aus Weltgeschichte entstehen muss

Nicht fest programmiert werden duerfen:

- konkrete L-Belegung;
- Ort, Richtung und raeumliche Ausdehnung einer L-Konfiguration;
- beteiligte Modalitaeten;
- Staerke und Lebensdauer spaeterer S-Wirkung;
- Zeitpunkt des funktionalen Wirkungsverlusts;
- Form einer spaeteren anderen L-Konfiguration;
- Aehnlichkeit, Klasse oder Bedeutung einer Konfiguration.

Fest programmiert sein duerfen nur lokale Naturform, Geometrie, Symmetrien,
Wertebereiche und technische Kausalordnung.

## 11. Kausale Mindestnachweise einer spaeteren Form

Eine konkrete L-Naturform muss mindestens tragen:

1. **Weltursache:** Ohne S-vermittelten lokalen Weltkontakt entsteht keine
   Kandidatendifferenz.
2. **Mitentwicklung:** S und L entwickeln sich unter derselben atomaren
   Naturgrenze.
3. **Angeglichene S-Lage:** Verschiedene L-Vorgeschichten bleiben nach
   kontrollierter Angleichung des schnellen S unterscheidbar.
4. **Spaetere S-Wirkung:** Identische neue Weltwirkung erzeugt verschiedene
   vollstaendige S-Trajektorien.
5. **Tausch:** Die Wirkung wandert mit L.
6. **Neutralisierung:** Ohne L-Wirkung erscheint der heutige Nullpfad.
7. **Loesung:** Weitere normale Weltgeschichte macht alte Wirkung ohne
   Sonderregel vollstaendig funktionslos.
8. **Wiederpraegung:** Dieselben L-Freiheitsgrade tragen danach eine andere
   Wirkung.
9. **Observerfreiheit:** Diagnose und Probe veraendern die Bildung nicht.
10. **Baselinegrenze:** Keine vorregistrierte engere Baseline reproduziert
    den gesamten Befund.

Vor Abschluss dieser Kette darf nur von einer `substratvermittelten spaeteren
Feldwirkung` gesprochen werden.

## 12. Snapshot- und Fortsetzungsgrenze

Falls spaeter eine konkrete L-Form zugelassen wird, muss L:

- Bestandteil jedes lokalen Gesamtzustands sein;
- vollstaendig in Snapshot, Restore, Digest und exakter Fortsetzung liegen;
- unabhaengig von Observer- oder Reportdateien sein;
- bei Neuronen- und Serialisierungsreihenfolge invariant bleiben;
- ohne versteckte externe Historie fortsetzbar sein.

Diese Anforderungen geben noch keine Schemaaenderung frei.

## Zulassungsentscheidung

Das ko-lokalisierte skalare L-Feld ist als Hypothesenraum zugelassen. Die
Zulassung gilt nur als eine weitere lokale Komponente desselben gemeinsamen
MCM-Feldes und nur unter den oben festgelegten Informations-, Symmetrie- und
Baselinegrenzen.

```text
skalares L pro bestehendem Feldort:  als Hypothesenraum zugelassen
separate L-Runtime oder L-Schicht:   verboten
direkter Welt-zu-L-Schreibpfad:      verboten
L-Nachbarschaft auf gleicher Anatomie: bedingt untersuchbar
konkrete raeumliche Familie:         nicht gewaehlt
konkrete Gleichung:                  nicht zugelassen
Implementierung oder Test:           nicht zugelassen
```

## Bester naechster Schritt

Als naechstes werden die drei verbleibenden **raeumlichen L-Kopplungsfamilien**
statisch verglichen:

1. nur S ist raeumlich mobil, L koppelt lokal an S;
2. S und L besitzen getrennte symmetrische Eigenfluesse;
3. S und L tragen einen reziproken lokalen Kreuzfluss.

Der Vergleich muss jede Familie gegen Leaky-/Gain-Klassen, klassische
Reaktions-Diffusion, Ein-Diffusor-Instabilitaet, Turing-Muster,
Kreuzdiffusion, Oszillation und feste Attraktoren klassifizieren. Danach darf
hoechstens eine Familie fuer einen konkreteren Naturfunktionsvertrag offen
bleiben.
