# S2-B: Technischer Runnervertrag der Referenzcharakterisierung

Stand: 2026-08-07

Status: `S2B_TECHNICAL_RUNNER_CONTRACT_BOUND_S2C_CORE_IMPLEMENTED`

Implementierung: Kern umgesetzt, produktiver Einzel-Executor offen

Ausfuehrung: gesperrt

## Zweck

S2-B bindet den technischen Aufbau, mit dem die in S2-A vorregistrierte
Wiederholungs- und Dauerkontaktcharakterisierung spaeter reproduzierbar
ausgefuehrt werden kann.

Dieser Vertrag:

- implementiert noch keinen Runner;
- erzeugt keine Audio- oder Videowelt;
- speist keine Rezeptoren;
- reserviert keine numerische Laufnummer;
- schreibt keine Ergebnisdatei;
- trifft keine Forschungsentscheidung.

Die fachliche Quelle ist die
[S2-A-Vorregistrierung](S2A_VORREGISTRIERUNG_WIEDERHOLUNG_DAUERKONTAKT_REFERENZCHARAKTERISIERUNG.md).
Bei einem Widerspruch darf die Implementierung S2-A nicht stillschweigend
veraendern. Dann ist S2-B zu stoppen und der Vertrag sichtbar zu korrigieren.

## 1. Technische Schichten

Der spaetere Runner wird in sechs strikt getrennte Schichten zerlegt:

```text
S2-A-Vertrag
-> kanonischer Weltplan
-> neutraler Audio-/Video-Rezeptorpfad
-> Modellarm B0 bis B5
-> externe Testintervention
-> passiver Metrikobserver
-> skalares technisches Paket
```

Keine Schicht darf eine Metrik, Entscheidung oder erwartete Wirkung in die
Welt, Rezeptoren, S/H/L-Dynamik oder eine andere vorgelagerte Schicht
zurueckgeben.

## 2. Geplante Module

S2-C darf genau folgende neue technische Module anlegen:

```text
mcm_field_organism/s2_reference_worlds.py
mcm_field_organism/s2_reference_baselines.py
mcm_field_organism/s2_reference_runner.py
tests/test_s2_reference_worlds.py
tests/test_s2_reference_baselines.py
tests/test_s2_reference_runner.py
```

Ein CLI, ein `run_id`, ein Reportmodul und ein Schreibpfad sind in S2-C
verboten. Oeffentliche Exporte in `mcm_field_organism/__init__.py` duerfen
erst nach fokussierter technischer Abnahme ergaenzt werden.

## 3. Kanonisches Weltinventar

`s2_reference_worlds.py` baut ausschliesslich Instanzen der vorhandenen
`ControlledAudioVideoTestWorld`. Alle numerischen Werte stammen unveraendert
aus S2-A.

Das Inventar enthaelt genau elf eindeutige Bildungsgeschichten:

```text
r1.a, c1.a
r2.a, c2.a
r4.a, c4.a
r8.a, c8.a
r8.b, c8.b
n8
```

Die Reihenfolge oben ist kanonisch. `R` und `C` sind nur technische
Versuchsadressen. Weder Welt noch Runtime erhalten Begriffe wie Wiederholung,
Dauerkontakt, bekannt, neu oder Ziel.

Jede Welt muss vor einer Feldfortschreibung folgende Kontrollen bestehen:

- Gesamtdauer exakt 8.0 s;
- Puls- und Neutralzeiten gemaess S2-A;
- ganzzahlige Audio-Hops und Videoframes je Phase;
- identisches Kontaktbudget innerhalb jedes `rn.a/cn.a`-Paars;
- identischer zeitlicher Kontaktschwerpunkt innerhalb jedes Paars;
- fester kanonischer Welt-Digest;
- frischer Quellenaufbau je Aufgabe;
- keine Rohdatenpersistenz.

Die Probe P ist kein Bestandteil des achtsekundigen Weltobjekts. Sie wird als
eigener kanonischer Weltabschnitt aufgebaut, damit die S/H-Angleichung und
L-Intervention genau zwischen Bildung und Probe liegen. Ihre Ereignisse
beginnen zwingend am Zeitoffset `8.0 s` desselben Organismustakts; der
Probeabschnitt darf keinen neuen Takt bei null beginnen.

## 4. Gemeinsamer Start und Zeitpfad

Jede physische Aufgabe beginnt aus einem frisch aufgebauten neutralen
Schema-3-Feld:

```text
S = 0
H = 0
L = 0
rho = 8
g = 0.25 / s
84 gemeinsame Feldorte
ein benannter gemeinsamer Organismustakt
```

Die Bildung und Probe verwenden denselben Takt. Tickzahl, Geometrie,
Dockinventar und letzte Rezeptorverteilung duerfen durch Angleichung,
Intervention, Observer oder Snapshot-Wiederaufnahme nicht neu adressiert
werden.

Audio- und Videoabschluesse werden ueber die bestehende gemeinsame
Ereigniszeitlinie zusammengefuehrt. Die Deklarationsreihenfolge unabhaengiger
Quellen darf weder Ereignisordnung noch Endzustand veraendern.

## 5. Exakte Modellvertraege B0 bis B5

Fuer die folgende Definition bezeichnet

```text
F(S,U) = G(U)S + b(U) - lambda_S*S
```

den vorhandenen lokalen schnellen MCM-Generator waehrend eines konstanten
Rezeptorintervalls. `H` behaelt in allen Armen unveraendert:

```text
dH/dt = r_H*S - (r_H + lambda_S)H
```

### B0 - schneller Nullpfad

```text
dS/dt = F(S,U)
kein wirksames L
```

B0 muss den historischen Schema-1-Fastpfad digestgleich reproduzieren. Ein
technisch angehaengtes Null-L darf dieses Ergebnis nicht veraendern.

### B1 - einseitige Leaky-Spur

```text
dS/dt = F(S,U)
dL/dt = (g/rho)(S-L)
```

S/H werden mit dem vorhandenen Fastpfad integriert. L wird aus derselben
stetigen S-Loesung modal exakt integriert. L wirkt nicht auf S oder H zurueck.

### B2 - lineare reziproke Referenz

```text
dS/dt = F(S,U) - g(S-L)
dL/dt = (g/rho)(S-L)
```

B2 ruft den vorhandenen S1-B-Pfad auf. Zusaetzlich wird fuer die technische
Abnahme eine unabhaengige B2-Referenzprojektion verwendet. Der produktive
Pfad und die Referenz duerfen keine gemeinsame Integratorfunktion teilen.

### B3 - begrenzter einseitiger Integrator

```text
dS/dt = F(S,U)
dL/dt = (g/rho)(1-L^2)S
```

S/H verwenden wieder den vorhandenen Fastpfad. Fuer `abs(L)<1` wird L lokal
ueber

```text
L(t+dt) = tanh(atanh(L(t)) + (g/rho) * integral(S(tau) d tau))
```

fortgeschrieben. Die S-Integrale stammen aus derselben modalen
Exaktintegration wie der Fastpfad. `L=+1` und `L=-1` sind unveraenderliche
Randzustaende. Clipping darf die Gleichung nicht ersetzen.

### B4 - zustandsabhaengiger Gain

Die dimensionslose Kopplung wird vor Implementierung eindeutig korrigiert:

```text
tau_ref = 1.0 s
beta    = g * tau_ref / rho = 0.03125
dS/dt   = (1 + beta*L) * F(S,U)
dL/dt   = (g/rho)(S-L)
```

Die Multiplikation ist komponentenweise. `beta` ist kein freier Parameter
und darf nicht anhand spaeterer Ergebnisse veraendert werden. Bei `L=0`
besitzt B4 exakt denselben momentanen Generator wie B0.

B4 ist nicht linear. S2-C muss deshalb eine feste klassische RK4-Integration
des gemeinsamen S/H/L-Zustands implementieren:

```text
primaere Unterteilung:       16 gleiche Schritte je kleinstem Ereignisintervall
Kontrollunterteilung:        32 gleiche Schritte je kleinstem Ereignisintervall
akzeptierter Teilungsfehler: <= 2e-12 im Maximum ueber S, H und L
```

Scheitert diese Grenze, ist der technische Arm ungueltig. Die Unterteilung
oder Toleranz wird nicht nach Einsicht in Weltwirkungen angepasst.

### B5 - Rueckwirkungsablation

```text
dS/dt = F(S,U) - gS
dL/dt = (g/rho)(S-L)
```

S/H/L werden modal exakt integriert. B5 behaelt die S-nach-L-Entwicklung und
dieselbe zusaetzliche S-Dissipation wie B2, entfernt aber ausschliesslich
`+gL` aus der S-Gleichung.

## 6. Bildung, Angleichung und Probe

Jede Aufgabe besitzt vier unverwechselbare Abschnitte:

```text
fresh       neutraler gemeinsamer Start
formation   genau eine der elf achtsekundigen Geschichten
boundary    externe S/H-Angleichung und optionale L-Intervention
probe       exakt 0.4 s kanonische Probe P
```

An der Grenze wird ein vollstaendiger Snapshot aufgenommen. Die
Hauptauswertung ersetzt nur die Werte aller S- und H-Komponenten durch exakt
null. Vollstaendig erhalten bleiben:

- L und sein Vertrag;
- Layer- und Neuronenidentitaeten;
- Layer-Tick;
- Docks und Geometrie;
- gemeinsamer Takt und letzter gueltiger Zeitabschluss.

Diese Funktion muss technisch `equalize_fast_state_for_probe` heissen. Sie
ist nur im S2-Runner importierbar und wird nicht als Organismusfunktion
exportiert.

## 7. L-Interventionen

Die Interventionen greifen ausschliesslich zwischen Angleichung und Probe.

### Intakt

Der eigene vollstaendige L-Zustand bleibt unveraendert.

### Neutral

Alle L-Komponenten werden mit der vorhandenen externen S1-B-Intervention auf
exakt null gesetzt.

### Tausch

Der vollstaendige L-Zustand wird nach folgender festen Involution getauscht:

```text
r8.a <-> r8.b
c8.a <-> c8.b
n8   <-> n8
```

Der N8-Selbsttausch ist eine technische Nullkontrolle. Es gibt keinen
teilweisen, skalierten oder ortsselektiven Tausch.

### Observer aus

Der gesamte Aufbau wird ohne Observer wiederholt. Das Ergebnis muss dem
beobachteten Aufbau exakt entsprechen.

### Wiederaufnahme

Der Boundary-Snapshot wird kanonisch serialisiert, restauriert und erst dann
mit P fortgesetzt. Direkter und restaurierter Pfad muessen exakt
uebereinstimmen.

B5 ist ein Modellarm und keine nachtraegliche Zustandsintervention. Der
Begriff `B5` in S2-A wird im Runner deshalb als Probe desselben gebildeten
B5-Zweigs umgesetzt.

## 8. Aufgabeninventar und Deduplikation

Das logische Inventar besteht aus:

```text
66 Hauptzellen:       11 Welten * 6 Modellarme, jeweils intakte Probe
15 B2-Interventionen: 5 n=8-Welten * swap, neutral, resume
5 Observerkontrollen: 5 n=8-Welten unter B2 ohne Observer
66 Reproduktionen:    frischer identischer Neuaufbau jeder Hauptzelle
```

Gesamt: 152 logische Aufgaben.

Die direkte B2-Probe der fuenf n=8-Welten ist bereits in den 66 Hauptzellen
enthalten und wird nicht doppelt ausgefuehrt. N8-Selbsttausch bleibt als
eigene Nullkontrolle erhalten. Aufgaben werden in kanonischer Reihenfolge
aufgebaut, duerfen aber fuer einen Ordnungsneutralitaetstest intern
permutiert und anschliessend ueber ihre technische ID zuruecksortiert werden.

Keine Aufgabe darf den Endzustand einer anderen Aufgabe als Startzustand
verwenden. Nur der explizite L-Tausch liest zwei abgeschlossene
Boundary-Snapshots und erzeugt daraus zwei neue Zweige.

## 9. Interne Messpunkte

Der passive Observer darf waehrend einer Aufgabe nur folgende fluechtige
Vektoren halten:

```text
L am Ende der Bildung vor Angleichung
S/H/L direkt nach Angleichung oder Intervention
S/H waehrend der Probe
S/H/L am Ende der Probe
```

Aus ihnen werden unmittelbar die in S2-A gebundenen Skalare `D_L`, `D_S`,
`D_H`, `D_pair`, `swap_error`, `neutral_error`, `resume_error` und
`reproduction_error` berechnet. Nach Paketbildung werden die Vektoren
verworfen.

## 10. Technisches Paketformat

`s2_reference_runner.py` liefert ein unveraenderliches In-Memory-Paket mit
Schema:

```text
mcm.s2.reference.packet.v1
```

Das Paket enthaelt ausschliesslich:

- Schema- und Vertragskennung;
- kanonische Aufgabenanzahl;
- Welt-, Probe-, Modell- und Implementierungsdigests;
- technische IDs der Welt-, Modell- und Interventionsarme;
- Start-, Boundary- und Endsnapshot-Digests;
- Ereignis-, Audiohop-, Videoframe- und Feldtickzahlen;
- skalare Metriken aus S2-A;
- maximale Bilanz-, Bereichs-, Teilungs- und Reproduktionsfehler;
- boolesche technische Kontrollen;
- einen Paketdigest.

Ausgeschlossen sind:

- Audio- oder Videosamples;
- Pixel, Frames oder Rezeptorvektoren;
- S/H/L-Vektoren oder Trajektorien;
- Labels, Bedeutungen, Zielwerte oder Rewards;
- `run_id`, Laufnummer oder Dateipfad;
- eine Forschungsentscheidung;
- Memory-, Praegungs-, Feldzeit-, Organisations-, Topologie-, Semantik-
  oder KI-Claimflags mit positivem Wert.

Eine reine Projektionsfunktion muss vor jeder spaeteren Persistenz pruefen,
dass keine ausgeschlossenen Schluessel oder nichtendlichen Zahlen vorkommen.
S2-C selbst persistiert das Paket nicht.

## 11. Digestbindung

Alle Digests verwenden SHA-256 ueber ASCII-kompatibles kanonisches JSON:

```text
sort_keys=True
separators=(",", ":")
allow_nan=False
UTF-8
```

Dokumenttexte werden fuer ihren Inhaltsdigest vorab auf UTF-8 ohne BOM und
LF-Zeilenenden normalisiert. Dadurch veraendert ein rein technischer
CRLF/LF-Wechsel keinen Vertragsdigest.

Gebunden werden getrennt:

1. S2-A-Vertrag;
2. S2-B-Vertrag;
3. jede Welt und Probe;
4. jeder Modellvertrag;
5. das Aufgabeninventar;
6. die spaetere Implementierungsdateiliste;
7. das fertige technische Paket.

Der Implementierungsdigest wird aus Pfad und Inhalt der in Abschnitt 2
genannten drei Produktionsmodule aufgebaut. Tests, Dokumente, Reports und
Git-Metadaten gehoeren nicht in diesen Digest.

## 12. Technische Stoppreihenfolge

Der spaetere Paketaufbau stoppt in dieser Reihenfolge:

1. Vertrags-, Welt- oder Implementierungsdigest ungebunden;
2. Aufgabeninventar unvollstaendig oder doppelt;
3. Weltbudget, Ereignis-Handoff oder gemeinsamer Takt verletzt;
4. Nullpfad oder S1-B/B2-Unabhaengigkeit verletzt;
5. S/H-Angleichung nicht exakt;
6. L-Intervention veraendert einen anderen Zustand;
7. Bilanz, Bereich oder B4-Teilung ausser Toleranz;
8. Observer-, Reihenfolge-, Resume- oder Reproduktionskontrolle verletzt;
9. nichtendlicher oder verbotener Ergebniswert;
10. unvollstaendige skalare Paketprojektion.

Bei einem Stopp wird kein Teilpaket als Forschungsresultat interpretiert.
Eine spaetere Auswertung muss dann ausschliesslich
`INVALID_TECHNICAL_RUN` liefern.

## 13. Technische Abnahme von S2-C

S2-C gilt erst als technisch gebunden, wenn fokussierte Tests nachweisen:

- elf korrekte Weltplaene und einen korrekten Probeplan;
- 152 eindeutige logische Aufgaben;
- digestgleiche Reproduktion;
- B0-Nullpfadgleichheit;
- unabhaengige B2-Referenzgleichheit innerhalb `2e-12`;
- B1-, B3- und B5-Bilanz beziehungsweise Bereich;
- B4-Teilungsfehler innerhalb `2e-12` auf analytischen Nullfixtures;
- exakte S/H-Angleichung bei unveraendertem L und unveraenderter Identitaet;
- vollstaendigen L-Tausch und reine L-Neutralisierung;
- Observer-, Deklarations- und Auswertungsneutralitaet;
- exakte Snapshot-Wiederaufnahme;
- ein endliches skalares Paket ohne ausgeschlossene Daten;
- keinen Aufruf der realen 152-Aufgaben-Vollmatrix in Tests.

Tests duerfen kleine analytische Fixtures und Ersatz-Executoren verwenden.
Sie duerfen die elf kontrollierten Welten strukturell aufbauen und deren
Digests pruefen, aber keinen Forschungsbefund berechnen oder persistieren.

## 14. Ausfuehrungssperre

Auch nach erfolgreicher S2-C-Implementierung bleiben gesperrt:

```text
reale 152-Aufgaben-Vollmatrix
Forschungsentscheidung
Reportdatei
Laufnummer
one-shot Einstieg
```

Dafuer waeren ein gesonderter S2-D-Auswertungs- und
Ausfuehrungssperrvertrag, gebundene reale Nulltoleranzen und eine
ausdrueckliche Benutzerentscheidung erforderlich.

Der reservierte Z4-A-Lauf 197 bleibt unberuehrt. S2-B verwendet bewusst nur
die technische Schema-ID `mcm.s2.reference.packet.v1` und keine numerische
Laufadresse.

## Aussagegrenze

S2-B ist eine technische Verdrahtungsspezifikation. Der Vertrag weist weder
eine spaetere Feldwirkung noch Praegung, Memory, relative Feldzeit,
Organisation, Topologie, Semantik, Selbstregulation oder KI nach.

## Entscheidung

```text
S2-A-Uebernahme:                 gebunden
Welt- und Aufgabeninventar:      gebunden
B0- bis B5-Modellvertraege:      gebunden
S/H-Angleichung:                 gebunden
L-Interventionen:                gebunden
skalare Paketprojektion:         gebunden
Digest- und Stopplogik:          gebunden
Runnerimplementierung:           nein
Ausfuehrung:                     gesperrt
Forschungslauf:                  nein
```

## Bester naechster Schritt

Die drei Produktionsmodule und Testsuiten sind als S2-C-Kern umgesetzt.
S2-C2 bis S2-C8 binden B0/B2-Batch, r1.a/c1.a, S/H-Angleichung, Probe P,
N8, Observer und Einpaardistanzen; S2-C9 bis S2-C16 schliessen die
A/B-Referenz bis zur kanonischen End-to-End-Komposition. Der
S2-Zwischenentscheid stoppt weitere Referenzerweiterung. Als naechstes folgt
der statische S1-C-Kandidatenvertrag. Keine Vollmatrix, Ergebnisdatei oder
Laufnummer.
