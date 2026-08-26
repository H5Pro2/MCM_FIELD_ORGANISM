# S2-A: Vorregistrierung Wiederholung gegen Dauerkontakt

Stand: 2026-08-07

Status: `S2A_REFERENCE_CHARACTERIZATION_PREREGISTERED`

Ausfuehrung: gesperrt

## Zweck

S2-A registriert die erste kontrollierte Weltkontaktcharakterisierung des in
S1-B implementierten langsamen L-Zustands vor.

Die Frage lautet:

> Welche spaetere schnelle Feldwirkung erzeugen `1, 2, 4 oder 8` getrennte
> audiovisuelle Kontakte im Vergleich zu einem kontaktzeitgleichen
> Dauerkontakt, wenn aktueller Weltkontakt sowie S und H vor der Probe exakt
> angeglichen werden?

S1-B ist exakt die lineare reziproke B2-Pflichtbaseline. S2-A kann deshalb
keine eigenstaendige Memory-Mechanik bestaetigen. Die Vorregistrierung prueft
zuerst nur Weltursache, L-Traegerschaft, Tausch, Neutralisierung,
Reproduzierbarkeit und die erwartete vollstaendige B2-Erklaerung.

## 1. Kontrollierte audiovisuelle Testwelt

Verwendet wird die bestehende prozedurale
`ControlledAudioVideoTestWorld`. Sie erzeugt Audio und Video deterministisch,
reduziert beide Quellen ueber die vorhandenen neutralen Rezeptoren und
persistiert keine Rohmedien.

Gebundene technische Konfiguration:

```text
audio sample rate:       4000 Hz
audio window size:       400 Samples
audio hop size:          40 Samples
audio receptor bands:    12
visual source:            24 x 16 x 3
visual receptor grid:     6 x 4 x 3
visual rate:              10 Hz
gemeinsame Feldorte:      84
fast response time:       1.0 s
afterimage time:          0.5 s
fast field dissipation:   0.0 / s
```

Kein Browser, keine Kamera, kein Mikrofon, keine reale Sensorik und keine
oeffentliche Medienquelle werden fuer S2-A benoetigt.

## 2. Inhaltsfreie Weltkontakte

### Kontakt A

```text
audio frequency:         320 Hz
audio amplitude:         0.25
visual origin:           (2, 3)
visual velocity:         (0, 0)
visual extent:           (6, 5)
visual channels:         (220, 70, 45)
```

Die visuelle Lage ist statisch. Dadurch unterscheiden sich getrennte und
kontinuierliche Arme nicht durch verschiedene Bewegungsbahnen. Die
Audiofrequenz vollendet innerhalb eines 0.4-s-Pulses eine ganzzahlige
Periodenzahl; jeder getrennte Puls beginnt deshalb ohne Phasensprung gegen
seinen kontinuierlichen Vergleich.

### Kontakt B

Kontakt B ist die gleich budgetierte Weltkontrolle:

```text
audio frequency:         760 Hz
audio amplitude:         0.25
visual origin:           (15, 8)
visual velocity:         (0, 0)
visual extent:           (6, 5)
visual channels:         (45, 120, 230)
```

B besitzt keine Bedeutung und kein Label in der Runtime. Die Bezeichnung ist
nur eine observerseitige Versuchsadresse.

### Neutrale Phase N

```text
audio frequency:         0 Hz
audio amplitude:         0.0
visual channels:         (16, 16, 16)
visual background:       (16, 16, 16)
```

N ist technisch kontaktfrei. Sie darf keine gespeicherte Weltlage abspielen.

### Probe P

```text
duration:                0.4 s
audio frequency:         1120 Hz
audio amplitude:         0.20
visual origin:           (8, 2)
visual velocity:         (0, 0)
visual extent:           (5, 6)
visual channels:         (65, 210, 105)
```

P ist in allen Zweigen bytegleich beziehungsweise nach der bestehenden
Rezeptorreduktion digestgleich. Sie ist keine Zielantwort und wird von der
Runtime nicht als Probe erkannt.

## 3. Zeit- und Kontaktordnung

Jede Bildungsgeschichte besitzt exakt 8.0 s Weltzeit. Die Pulsdauer ist
fest `0.4 s`.

Fuer `n in {1,2,4,8}` werden zwei Weltformen gebunden.

### Getrennter Arm Rn

```text
n Kontakte A zu je 0.4 s
zwischen zwei Kontakten genau 0.4 s N
gesamte Kontaktzeit: n * 0.4 s
gesamter Kontaktblock: (2*n - 1) * 0.4 s
Block zeitlich um t=4.0 s zentriert
restliche Zeit symmetrisch als N vor und nach dem Block
```

### Kontinuierlicher Arm Cn

```text
ein Kontakt A mit Dauer n * 0.4 s
Kontakt zeitlich um t=4.0 s zentriert
restliche Zeit symmetrisch als N vor und nach dem Kontakt
```

Damit sind innerhalb jedes Paars `Rn/Cn` gebunden:

- identische Gesamtdauer;
- identische aktive Audio- und Videozeit;
- identische Amplitude, Geometrie und Rezeptoren;
- identischer zeitlicher Schwerpunkt;
- unterschiedliche Zahl getrennter Kontaktgrenzen.

Die Paare mit verschiedenen `n` besitzen bewusst unterschiedliche aktive
Kontaktbudgets. Ein Trend ueber `n` ist deshalb eine Dosischarakterisierung,
kein isolierter Wiederholungsnachweis. Nur `Rn` gegen `Cn` isoliert bei
gleichem `n` die zeitliche Trennung.

## 4. Weltkontrollarme

Zusaetzlich werden fuer `n=8` gebunden:

- `R8-B`: acht getrennte B-Kontakte mit demselben Zeitplan wie `R8`;
- `C8-B`: ein kontinuierlicher B-Kontakt mit demselben Zeitplan wie `C8`;
- `N8`: acht Sekunden ausschliesslich N;
- `reproduction`: frischer identischer Neuaufbau jedes Arms;
- `declaration-permutation`: gleiche Weltgeschichte bei vertauschter
  Deklarationsreihenfolge unabhaengiger Audio-/Videoquellen.

Kontakt B prueft nur Geschichtsspezifitaet. Eine unterschiedliche Wirkung von
A und B ist noch keine Bedeutung oder Semantik.

## 5. Fast-State-Angleichung vor P

Nach den 8.0 s Bildung werden fuer die kausale Hauptauswertung in jedem Zweig
S und H durch eine externe Testintervention auf denselben gebundenen
Neutralzustand gesetzt. L bleibt unveraendert.

```text
vor Angleichung:  (S_history, H_history, L_history)
nach Angleichung: (S_common=0, H_common=0, L_history)
```

Die Intervention:

- findet ausserhalb der Organismusfunktion statt;
- veraendert weder Naturparameter noch L;
- wird fuer jeden Zweig identisch angewendet;
- ist kein Reset-, Vergessens- oder Abrufmechanismus des Organismus;
- muss den gemeinsamen Tick, die Geometrie und die letzte neutrale
  Rezeptorverteilung konsistent erhalten.

Parallel wird ein rein natuerlicher Fortsetzungsarm ohne S/H-Angleichung
beobachtet. Er darf die kausale Hauptentscheidung nicht ersetzen, weil dort
schneller Nachhall und L-Wirkung vermischt bleiben.

## 6. Pflichtmodelle B0 bis B5

Jede Weltgeschichte wird unter festen, vorab gebundenen Modellarmen
ausgewertet.

### B0 - schneller MCM-Nullpfad

```text
g = 0
kein wirksames L
heutige S/H-Runtime
```

### B1 - einseitige Leaky-Spur

```text
dS/dt = vorhandene schnelle MCM-Wirkung
dL/dt = (g/rho)(S-L)
keine L-nach-S-Wirkung
```

### B2 - reziproke lineare Referenz

```text
dS/dt = vorhandene schnelle MCM-Wirkung - g(S-L)
dL/dt = (g/rho)(S-L)
```

B2 ist identisch mit S1-B und kein unabhaengiger Kandidat.

### B3 - begrenzter Integrator

```text
dS/dt = vorhandene schnelle MCM-Wirkung
dL/dt = (g/rho)(1-L^2)S
keine L-nach-S-Wirkung
```

B3 ist eine inhaltsfreie Saettigungsintegrator-Baseline. Bereichsgrenzen
werden durch die stetige Gleichung und nicht durch eine Lebenszyklusregel
getragen.

### B4 - zustandsabhaengiger Gain

```text
tau_ref = 1.0 s
beta = g*tau_ref/rho = 0.03125
dS/dt = vorhandene schnelle MCM-Wirkung * (1 + beta*L)
dL/dt = (g/rho)(S-L)
```

Der Gain wirkt nur auf den vorhandenen lokalen Feldantrieb, nicht direkt auf
Rohrezeptoren. Die dimensionslose Einheitenkorrektur und die genaue
Generatorform sind im S2-B-Runnervertrag gebunden. B4 besitzt bei `L=0`
denselben momentanen Generator wie B0.

### B5 - Rueckwirkungsablation

```text
dS/dt = vorhandene schnelle MCM-Wirkung - gS
dL/dt = (g/rho)(S-L)
```

B5 entfernt nur den Term `+gL`, behaelt aber S-nach-L-Entwicklung und die
gleiche zusaetzliche S-Dissipation.

### Gemeinsame Parameter

```text
rho = 8
g   = 0.25 / s
```

Es gibt kein Parametersweeping und kein Nachjustieren nach Einsicht in
Ergebnisse. Die fuer B4 algebraisch notwendige Einheitenkorrektur ist vor
Implementierung in S2-B festgelegt; danach werden alle Digests gebunden.

## 7. Kausale Interventionen

Fuer `R8-A`, `C8-A`, `R8-B`, `C8-B` und `N8` werden nach der S/H-Angleichung
zusaetzlich erzeugt:

1. `intact`: eigener L-Zustand bleibt im eigenen Zweig;
2. `swap`: vollstaendiger L-Zustand wird zwischen A und B getauscht;
3. `neutral`: L wird observerseitig exakt null gesetzt;
4. `B5`: L entwickelt sich, besitzt aber keine L-nach-S-Rueckwirkung;
5. `observer-off`: identischer Verlauf ohne Beobachter;
6. `resume`: Snapshot und Wiederaufnahme direkt vor P.

Eine Wirkung gilt nur als L-vermittelt, wenn sie beim Tausch mit L wandert,
bei Neutralisierung verschwindet und bei B5 nicht auftritt.

## 8. Persistierte Daten und Observablen

Nicht persistiert werden:

- Audioframes oder Samples;
- Videoframes oder Pixel;
- vollstaendige Rezeptorsequenzen;
- vollstaendige S/H/L-Trajektorien;
- rekonstruierbare Medienwerte.

Persistiert werden duerfen:

- Vertrags- und Implementierungsdigests;
- Welt-, Modell- und Interventions-ID;
- Supportzahlen und Laufzeitbudgets;
- Start- und Enddigests vollstaendiger Snapshots;
- skalare technische Distanzen;
- Bilanz-, Bereichs-, Nullpfad- und Reproduktionsfehler;
- eine vorregistrierte technische Entscheidung.

Gebundene skalare Metriken:

```text
D_L(history, neutral) = ||L_history - L_N8||_inf vor S/H-Angleichung
D_S(P)                = max_t ||S_history(t) - S_N8(t)||_inf waehrend P
D_H(P)                = max_t ||H_history(t) - H_N8(t)||_inf waehrend P
D_pair(n)             = max(D_S, D_H) zwischen Rn und Cn
swap_error             = Rest gegen die mit L erwartete vertauschte Wirkung
neutral_error          = Rest gegen B0 nach L-Neutralisierung
resume_error           = Rest zwischen direkt und aus Snapshot fortgesetzt
reproduction_error     = Rest zweier frischer identischer Ausfuehrungen
```

Metriken sind Observerwerte und werden von der Runtime nicht gelesen.

## 9. Technische Toleranzen

Vor dem ersten S2-Lauf werden aus Nullarm, identischer Wiederholung und
Zeitteilung genau einmal numerische Toleranzen gebunden.

Bis dahin gelten fuer die Implementierungsabnahme:

```text
digestgleiche Pfade:            exakt gleich
lineare Exaktintegration:       abs error <= 2e-12
Bilanz und Bereich:             abs error <= 2e-12
```

Die Toleranz darf nicht nach Einsicht in einen Weltarm erweitert werden.

## 10. Vorregistrierte Entscheidungen

### `INVALID_TECHNICAL_RUN`

Mindestens eine Pflichtbedingung scheitert:

- Quellen- oder Implementierungsdigest falsch;
- Rohdaten persistiert;
- S/H vor Hauptprobe nicht exakt angeglichen;
- Nullpfad, Bilanz, Bereich, Reproduktion oder Resume ausser Toleranz;
- Observer, Deklarationsreihenfolge oder Auswertungsreihenfolge veraendert
  den Zustand;
- Zeit-, Energie-, Parameter- oder Zustandsbudget nicht eingehalten.

### `NO_L_HISTORY_EFFECT`

Nach S/H-Angleichung liegt fuer alle S1-B-Historien `D_S(P)` und `D_H(P)`
innerhalb der Nulltoleranz.

### `LINEAR_REFERENCE_EFFECT_CONFIRMED`

Mindestens eine Geschichte erzeugt nach S/H-Angleichung eine reproduzierbare
spaetere S/H-Wirkung, die beim L-Tausch mitwandert, bei Neutralisierung und
B5 verschwindet und vollstaendig dem identischen B2-Modell entspricht.

Dies bestaetigt nur den technischen Referenztraeger.

### `REFERENCE_IMPLEMENTATION_MISMATCH`

S1-B und die unabhaengige B2-Berechnung unterscheiden sich oberhalb der
gebundenen Toleranz. Dann wird nicht interpretiert; Implementierung und
Vorregistrierung muessen statisch geprueft werden.

### Keine positive Memory-Entscheidung

S2-A besitzt absichtlich keine Entscheidung `PRAEGUNG`, `MEMORY`,
`FELDZEITVERDICHTUNG` oder `ORGANISATION`. Da S1-B identisch mit B2 ist,
waere eine solche Entscheidung methodisch unzulaessig.

## 11. Ausfuehrungssperre

Vor einer Ausfuehrung fehlen noch:

1. der gebundene S2-C4-Pfad fuer S/H-Angleichung und Probe P nach dem
   S2-C3-r1.a-Weltadapter;
2. die vertraglich exakt festgelegten B1-, B3-, B4- und B5-Integratoren;
3. die externe S/H-Angleichungsintervention;
4. feste Welt-, Implementierungs- und Vertragsdigests;
5. ein skalares Ergebnisschema ohne Rohtrajektorien;
6. ein eindeutiger neuer Laufbezeichner ohne Kollision mit dem reservierten
   Z4-A-Lauf 197 und historischen Dokumentnummern;
7. eine ausdrueckliche spaetere Ausfuehrungsentscheidung.

Bis dahin werden keine Welten erzeugt, keine Rezeptoren gespeist und kein
Forschungslauf gestartet.

## Aussagegrenze

S2-A ist eine Vorregistrierung fuer eine lineare Referenzcharakterisierung.
Selbst `LINEAR_REFERENCE_EFFECT_CONFIRMED` bedeutet nur:

```text
kontrollierte Weltgeschichte
-> unterschiedlicher L-Zustand
-> kausal unterschiedliche spaetere schnelle Feldwirkung
```

Es bedeutet nicht:

```text
organisches Memory
Feldzeitverdichtung
Wiedererkennung
innere Syntax
Semantik
Gefuehl oder Erleben
KI
```

## Entscheidung

```text
Forschungsfrage:                    gebunden
kontrollierte AV-Welt:              gebunden
Rn/Cn-Zeit- und Kontaktbudget:      gebunden
B0 bis B5:                          funktional gebunden
S/H-Angleichung:                    gebunden
Tausch und Neutralisierung:         gebunden
Metriken und Entscheidungen:        gebunden
Memory-Entscheidung:                ausgeschlossen
Runnerkern und Baselines:           implementiert
B0/B2-Einzelbatchpfad:              implementiert
kanonischer r1.a-AV-Weltadapter:    implementiert
Probe-P-Fortsetzung:                implementiert
Ausfuehrung:                        gesperrt
Forschungslauf:                     nein
```

## Bester naechster Schritt

S2-B bindet Weltarme, Modellarme, S/H-Angleichung, Interventionen, Digests
und skalares Paket; S2-C-Kern und S2-C2-Einzelbatchpfad sind implementiert.
S2-C3 bis S2-C8 binden `r1.a/c1.a`, S/H-Angleichung, Probe P, N8, Observer,
Einpaardistanzen, A/B-Container, `D_world_pair(8)` und die kanonische
End-to-End-Komposition. Der S2-Zwischenentscheid stoppt die weitere
Referenzerweiterung bis zu einem konkreten neuen Kandidaten, ohne die Vollmatrix
auszufuehren, eine Ergebnisdatei zu schreiben oder eine Laufnummer zu
vergeben.
