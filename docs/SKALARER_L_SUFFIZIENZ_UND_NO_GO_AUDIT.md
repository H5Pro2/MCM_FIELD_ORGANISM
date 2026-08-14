# Skalarer L-Suffizienz- und No-Go-Audit

## Status

```text
Auditart:                         statisch / mathematisch-konzeptionell
isolierter lokaler Skalar:        als eigenstaendige Physik nicht ausreichend
ein Skalar pro Feldort:           als verteiltes Zustandsfeld ausreichend
kleinster nichtleerer Rest:       ko-lokalisierte raeumliche S-L-Mitentwicklung
Memory- oder Organisationsclaim:  nein
konkrete Gleichung:               nicht gewaehlt
Runtime-Aenderung:                nein
```

## Prueffrage

Der Freiheitsgradaudit bestimmt einen zusaetzlichen lokalen Skalar `L_i` als
kleinste moegliche Schemaerweiterung. Dieser Audit fragt:

> Kann ein einzelner skalarer Wert pro Feldort eine unabhaengige physische
> Funktion tragen, die nicht nur Spur, Gain, Mobilitaet, Integrator,
> Hysterese oder Oszillator ist?

Dabei muessen zwei Bedeutungen getrennt werden:

1. `L_i` als isoliertes Register an einem Feldort;
2. die Gesamtheit aller `L_i` als raeumlich verteiltes ko-lokalisiertes Feld.

Nur die zweite Lesart laesst einen nichtleeren Kandidatenraum uebrig.

## 1. Ausgangsarchitektur

Die heutige lokale schnelle Runtime besitzt:

```text
S_i = activation am Feldort i
H_i = nachgelagerte schnelle afterimage-Spur
```

`H_i` wirkt nicht auf `S_i` zurueck. Die kleinste Erweiterung waere daher:

```text
X_i = (S_i, H_i, L_i)
```

`L_i` darf keine Bedeutung, Partner-ID, Kante, Episode oder Zielrolle tragen.
Sein neutraler Wert muss den heutigen S-H-Pfad exakt erhalten.

## 2. No-Go fuer den isolierten lokalen Skalar

Wird `L_i` nur aus dem Zustand desselben Ortes und dessen gegenwaertiger
Zufuhr fortgeschrieben, entstehen folgende kleinste Funktionsklassen.

### Einweg S nach L

```text
S_i beeinflusst L_i
L_i beeinflusst S_i nicht
```

Dann ist L eine Diagnose, Spur oder ein wirkungsloser interner Zustand. Er
traegt keine substratvermittelte spaetere schnelle Feldwirkung.

### Einweg L nach S

```text
L_i beeinflusst S_i
S_i beeinflusst L_i nicht
```

Dann ist L eine feste Anfangsbedingung, ein Bias oder ein externer
Steuerparameter. Seine konkrete Form entsteht nicht aus Feldgeschichte.

### L skaliert eine vorhandene Wirkung

Wenn L nur Rezeptorzufuhr, Nachbarschaftswirkung oder Antwortgeschwindigkeit
skaliert, ist L funktional:

- adaptiver Gain;
- Receptivity;
- variable Zeitkonstante;
- zustandsabhaengige Mobilitaet.

### L sammelt eine lokale Groesse

Wenn L Aktivitaet, Energie, Differenz oder Koaktivitaet summiert und spaeter
gelesen wird, ist L:

- Integrator;
- Saettigungsintegrator;
- Leaky-Spur;
- Produkt- oder Momentenspur.

### L besitzt mehrere bevorzugte Lagen

Dann entsteht eine feste Attraktor- oder Hystereselandschaft. Die konkrete
Historie waehlt eine vorbereitete Lage, erzeugt aber nicht die Menge der
moeglichen Lagen.

### Reziprokes lokales S-L-Paar

Eine lineare oder konservativ-dissipative Kreuzkopplung ergibt gekoppelte
Relaxation, Viskoelastik oder Oszillation. Eine beliebige rein lokale
nichtlineare Kreuzkopplung kann komplexere Phasenportraits tragen, liefert
aber ohne raeumliche Mitentwicklung noch kein unabhaengiges Prinzip fuer eine
offene verteilte Feldorganisation.

### Entscheidung

**Ein isolierter skalarer Registerzustand wird als eigenstaendige
Substratphysik geschlossen.**

Er bleibt als Pflichtbaseline zulaessig und notwendig.

## 3. Warum ein Skalar pro Feldort mehr als ein Register ist

Die Menge

```text
L = {L_i fuer alle Feldorte i}
```

ist kein einzelner Skalar, sondern ein skalares Feld auf derselben Geometrie
wie Activation. Seine konkrete raeumliche Belegung kann Gradienten, lokale
Moden und verteilte Konfigurationen tragen, ohne Partner- oder Kanten-IDs zu
speichern.

Der lokale Zustandsraum bleibt minimal um genau eine Komponente erweitert.
Der globale Freiheitsgrad entsteht aus der bereits vorhandenen Feldgeometrie,
nicht aus einer Liste gespeicherter Beziehungen.

### Mathematischer Existenzhinweis

Zwei gekoppelte skalare Felder mit lokaler Reaktion und raeumlicher Diffusion
koennen kollektive raeumliche Instabilitaeten und Muster tragen, obwohl ihre
lokalen Gesetze ueberall gleich sind. Turings Reaktions-Diffusionsanalyse ist
der klassische Existenzbeleg fuer diese Moeglichkeit.

Auch Systeme mit nur einer diffundierenden Komponente koennen unter
bestimmten Bedingungen diffusionsgetriebene Instabilitaet zeigen. Damit ist
ein zweiter identischer Diffusionspfad keine mathematische
Mindestvoraussetzung.

Diese Ergebnisse beweisen nur, dass ein skalarer Zusatz pro Ort fuer
kollektive raeumliche Entwicklung prinzipiell genuegen kann. Sie beweisen
nicht:

- MCM-Memory;
- organische Entwicklung;
- entstandene Topologie;
- Bedeutung;
- Feldzeitverdichtung;
- funktionale Loesung oder Wiederpraegung.

## 4. Kleinster nichtleerer physischer Rest

Nach Abzug der isolierten Registerklassen bleibt als kleinste offene Funktion:

> Ein ko-lokalisiertes skalares konstitutives Feld L entwickelt sich auf der
> vorhandenen MCM-Geometrie gemeinsam mit dem schnellen Feld S, wobei lokale
> S-L-Wechselwirkung und lokale raeumliche Feldwirkung atomar dieselbe
> Folgetrajektorie bestimmen.

Kurzform:

```text
lokaler Vorzustand (S_i,L_i)
+ vorhandenes lokales S- und gegebenenfalls L-Vorfeld
+ lokaler Weltkontakt
+ dt
-> gemeinsamer Folgezustand (S_i',L_i')
```

`H_i` bleibt eine nachgelagerte schnelle Spur und ist nicht das neue
Substratfeld.

## 5. Ein Feld mit zwei Rollen, nicht zwei Systeme

Die zulaessige Lesart ist:

```text
ein gemeinsames MCM-Feld
mit lokalem mehrkomponentigem Zustand (S,H,L)
```

Nicht zulaessig waere:

```text
schnelles MCM-Netz
+ separates Memory-Netz
+ nachgeschalteter Leser
```

S und L muessen dieselben Feldorte, dieselbe Kausalgrenze, denselben Snapshot
und dieselbe atomare Fortschreibung teilen. Unterschiedliche funktionale
Zeitskalen machen daraus keine getrennten Produkte.

## 6. Was noch nicht festgelegt werden darf

Der Audit legt nicht fest:

- ob und wie L raeumlich diffundiert;
- ob S- und L-Fluss dieselbe Rate besitzen;
- ob Kreuzdiffusion existiert;
- welche Reaktions- oder Austauschfunktion gilt;
- ob homogene Lagen stabil oder instabil sind;
- welche Wellenlaenge oder Musterform bevorzugt wird;
- ob Metastabilitaet entsteht;
- welche konkrete Feldgeschichte erhalten bleibt.

Insbesondere darf keine Turing-Wellenlaenge, Attraktorkarte oder
Musterfamilie als Ziel einprogrammiert werden.

## 7. Neue staerkste Pflichtbaselines

Ein spaeterer ko-lokalisierter skalarer L-Kandidat muss mindestens gegen diese
engen Klassen abgegrenzt werden:

1. heutiger S-H-Nullpfad;
2. unabhaengige lokale Leaky-Spur L ohne raeumliche L-Wirkung;
3. lokaler adaptiver Gain oder Receptivity;
4. lokale variable Mobilitaet oder Zeitkonstante;
5. linear reziprokes lokales S-L-Paar;
6. lokaler S-L-Oszillator;
7. feste skalare Hysterese;
8. klassische Zwei-Komponenten-Reaktions-Diffusion;
9. diffusionsgetriebene Instabilitaet mit nur einer mobilen Komponente;
10. feste Muster- oder Attraktorlandschaft;
11. Ablation der L-Nachbarschaftswirkung;
12. Ablation jeder Kreuzrichtung `S -> L` und `L -> S`.

Ein entstandenes raeumliches Muster allein ist kein positiver Befund. Es kann
vollstaendig durch eine Turing- oder andere Reaktions-Diffusionsbaseline
erklaert sein.

## 8. Kriterium fuer eine spaetere unabhaengige Funktion

Eine konkrete Naturform waere nur interessant, wenn dieselbe unveraenderte
lokale Physik gemeinsam zeigen kann:

1. Weltgeschichte erzeugt eine konkrete verteilte L-Konfiguration.
2. Bei angeglichener schneller S-Lage veraendert diese Konfiguration die
   spaetere vollstaendige S-Trajektorie.
3. Die Wirkung wandert mit L und verschwindet bei experimenteller
   Neutralisierung von L.
4. Weitere normale Weltgeschichte macht die alte Wirkung ohne Sonderregel
   funktionslos.
5. Dieselben lokalen Freiheitsgrade tragen danach eine andere Wirkung.
6. Keine engere Pflichtbaseline reproduziert diesen gesamten Lebenszyklus.

Bis dahin lautet der maximal zulaessige Ausdruck:

> ko-lokalisierter skalarer konstitutiver Feldkandidat

Nicht zulaessig sind `Memory-Feld`, `Organisation`, `Topologie` oder `KI`.

## 9. Auditentscheidung

```text
isoliertes skalares L-Register:       geschlossen
verteiltes skalares L-Feld:           als Hypothesenraum offen
zusaetzliche lokale Dimension:        eine kann prinzipiell genuegen
konkrete L-Naturform:                  nicht gewaehlt
Reaktions-Diffusionsmuster als Beleg:  nein
Schema, Runtime oder Test:             nicht freigegeben
```

Eine hoehere lokale L-Dimension ist derzeit nicht zwingend begruendet. Sie
darf erst eingefuehrt werden, wenn der skalare verteilte Raum eine konkrete
notwendige Funktion nachweislich nicht darstellen kann.

## Quellen

- A. M. Turing,
  [The Chemical Basis of Morphogenesis](https://www.damtp.cam.ac.uk/user/gold/pdfs/teaching/turing1952.pdf),
  Philosophical Transactions of the Royal Society B 237, 1952. Zeigt, dass
  lokal gleichartige gekoppelte Reaktions-Diffusionsgesetze kollektive
  raeumliche Muster erzeugen koennen.
- H. Miyazako, Y. Hori und S. Hara,
  [Turing Instability in Reaction-Diffusion Systems with a Single Diffuser](https://arxiv.org/abs/1309.0111),
  2013. Charakterisiert diffusionsgetriebene Instabilitaet, wenn nur eine
  Systemkomponente raeumlich mobil ist.

Die Uebertragung auf einen moeglichen MCM-Hypothesenraum ist eine Ableitung
dieses Audits. Die Quellen liefern keinen Nachweis fuer MCM-Memory oder
organische digitale Entwicklung.

## Bester naechster Schritt

Als naechstes wird ein **Zulassungsvertrag fuer ein ko-lokalisiertes skalares
L-Feld** formuliert. Er muss vor jeder Gleichung festlegen:

1. welche lokalen S-, L- und Nachbarschaftsinformationen gelesen werden
   duerfen;
2. wie S und L atomar im selben Feldzustand fortgeschrieben werden;
3. welche Symmetrien, Bilanzen und Nullpfade verbindlich sind;
4. wie klassische Reaktions-Diffusion, Turing-Muster, Gain, Mobilitaet,
   Hysterese und Oszillation als Baselines erhalten bleiben;
5. welche Gleichungsformen wegen Zielmuster oder vorprogrammiertem
   Lebenszyklus sofort ausgeschlossen sind.

Der Vertrag darf noch keine konkrete Reaktions-, Fluss- oder
Kreuzkopplungsgleichung waehlen.
