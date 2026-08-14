# W6-A: Minimaler Funktionsvertrag der langsamen MCM-Feldkomponente L

Stand: 2026-08-09

Entscheidung: `L_FUNCTION_CONTRACT_BOUND_EXISTING_SCAFFOLD_REUSABLE`

Auditart: statisch und codegestuetzt

Runtimeaenderung: nein

Formaler Forschungslauf: nein

## Forschungs- und Entwicklungsfrage

Welche kleinste funktionale Grenze muss die in W5-E zugelassene langsame
entwicklungsfaehige MCM-Feldkomponente L erfuellen, und welche vorhandene
Projektinfrastruktur kann dafuer wiederverwendet werden, ohne bereits eine
Gleichung oder aktive Runtime auszuwahlen?

## Vollstaendiger lokaler Zustand

Der kleinste gemeinsame Zustand am bestehenden MCM-Ort `i` lautet:

```text
S_i = schnelle aktuelle MCM-Feldwirkung
H_i = vorhandener schneller passiver Nachhall
L_i = langsame lokale Entwicklungsdisposition
```

Fuer die erste Entwicklungsstufe gilt:

- genau ein reeller L-Wert je bestehendem MCM-Neuron;
- `L_i` liegt normiert in `[-1, 1]`;
- der neutrale Zustand ist `L_i = 0`;
- L verwendet exakt dieselben Neuron-IDs und Feldorte wie S;
- L besitzt keine eigenen Kanten, Docks, Rezeptoren oder Modalitaeten;
- H bleibt technisch getrennt und steuert L in der ersten Stufe nicht.

Der Skalar ist eine minimale technische Hypothese. Er behauptet nicht, dass
ein Skalar fuer einen spaeteren Memory-Lebenszyklus ausreicht.

## Lokale Eingangsursache

L darf pro atomarem Schritt nur lesen:

1. den abgeschlossenen lokalen S-Vorzustand;
2. den abgeschlossenen lokalen L-Vorzustand;
3. die bereits fuer S vorhandenen lokalen Vorfeldproben;
4. die normale, bereits auf S reduzierte lokale Weltwirkung;
5. die reale Dauer desselben Organismusschritts;
6. global feste, inhaltsfreie Naturparameter.

L darf keine Rohpixel, PCM-Daten, Browserpayloads, Docks, Modalitaets-IDs,
Episoden, Wiederholungszaehler, Labels, Cluster oder Observerwerte lesen.
Weltkontakt erreicht L ausschliesslich durch den bestehenden lokalen
S-Feldpfad.

## Kausalrichtungen S nach L und L nach S

Beide Richtungen werden aus demselben abgeschlossenen Vorzustand berechnet:

```text
(S_t, H_t, L_t, lokales Vorfeld_t, lokale Weltwirkung_t, dt)
-> gemeinsamer Vorschlag (S_t+1, H_t+1, L_t+1)
-> atomare Uebernahme
```

### S nach L

Normale lokale S-Feldteilnahme muss L kontinuierlich veraendern koennen. Eine
direkte Schreibfunktion aus Medieninhalt oder Versuchszweig ist verboten.

### L nach S

Der abgeschlossene L-Vorzustand muss die spaetere lokale S-Transition als
innerer Feldbeitrag veraendern koennen. Ein nachgeschalteter Leser, Bericht
oder Rezeptorgain genuegt nicht.

### Gemeinsame Wechselwirkung

Die erste Gleichungsfamilie muss beide Richtungen als zwei Seiten desselben
lokalen Austauschs formulieren. Getrennte Schreib- und Leserregeln sind nicht
zulaessig. `L_t+1` darf im selben Schritt nicht sofort wieder `S_t+1`
beeinflussen.

## Begrenzung und Zeit

L darf keine unbegrenzte Quelle oder unbegrenzten Integrator bilden.
Verbindlich sind:

- endlicher Wertebereich `[-1, 1]`;
- endliche Aenderung fuer jeden endlichen gueltigen Vorzustand;
- neutrale Ruhe ohne Weltwirkung und ohne S-L-Austausch;
- keine globale Renormierung ueber alle Feldorte;
- keine ereignisabhaengige Reset- oder Loeschregel;
- dieselbe reale Organismusdauer wie S, ohne eigene Uhr;
- Konvergenz bei technisch aequivalenter Teilung desselben Zeitintervalls.

Ob die erste Gleichung Begrenzung durch Austausch, Saettigung oder
Dissipation realisiert, ist in W6-A noch offen. Diese Form muss in W6-B
explizit bilanziert werden.

## Veraenderbarkeit ohne vorgegebenen Lebenszyklus

Weitere normale Feldgeschichte muss L weiter veraendern koennen. W6-A fordert
noch nicht, dass alte Wirkung vollstaendig verschwindet oder eine neue Wirkung
entsteht. Diese Eigenschaften gehoeren in einen spaeteren Lebenszyklustest.

Unzulaessig sind bereits jetzt:

- feste Praegungs-, Abruf-, Konsolidierungs- oder Loeschphasen;
- Schwellwerte mit der Bedeutung `gespeichert` oder `vergessen`;
- besondere Gegenwelten, die als Reset erkannt werden;
- Zielmuster oder Ergebnisrueckschreibung.

## Nullpfad

Bei deaktivierter S-L-Kopplung muss die heutige schnelle Runtime exakt
entstehen:

```text
L-Kopplung aus
+ identischer S/H-Vorzustand
+ identische lokale Weltwirkung
-> identische S/H-Fortsetzung
```

Ein vorhandener neutraler L-Zustand darf im Nullarm weder S noch H
veraendern. Der Nullpfad muss den Digest der vollstaendigen S/H-
Feldprojektion, die Rezeptorverteilung und die Fortsetzung der heutigen
Schema-1-Runtime erhalten. Der Gesamtdigest eines Schema-3-Snapshots darf
nicht mit dem Schema-1-Gesamtdigest gleichgesetzt werden: Schema 3 enthaelt L
absichtlich als zusaetzlichen digestwirksamen Zustand. Im Nullarm bleibt
dieser getrennte L-Zustand neutral.

## Snapshot- und Interventionsrolle

Ein aktives L muss:

- vollstaendig im gemeinsamen Feld-Snapshot enthalten sein;
- mit jedem MCM-Neuron eindeutig ko-lokalisiert sein;
- JSON-rundreisefaehig und digestwirksam sein;
- bei Restore bitgleich fortgesetzt werden;
- extern fuer Forschungsinterventionen tauschbar und neutralisierbar sein.

Tausch und Neutralisierung sind ausschliesslich Forschungsoperationen. Sie
sind keine Betriebsmodi des Organismus.

## Codegestuetzter Bestandsabgleich

Die technische Zustandsgrenze ist bereits vorhanden:

1. `MCMLocalDevelopmentState` traegt genau einen normierten L-Skalar je
   bestehendem Neuron und eine feste inhaltsfreie Vertragskennung.
2. `SharedMCMField` haelt `development` ko-lokal neben derselben Neuronenschicht.
3. `SharedMCMFieldSnapshot` serialisiert diesen Zustand ausschliesslich in
   Schema 3 und macht ihn digestwirksam.
4. `restore_shared_mcm_field()` stellt Schema 3 ohne Zusatzverhalten wieder
   her.
5. Der normale `SharedMCMField.advance()` lehnt Felder mit `development`
   ausdruecklich ab und verlangt den dedizierten S1-B-Pfad.
6. `s1b_reciprocal_accommodation.py` enthaelt einen opt-in S/H/L-
   Referenzintegrator.
7. `current_api.py` exportiert weder `MCMLocalDevelopmentState` noch den
   S1-B-Integrator. Die aktive kontrollierte API bleibt daher L-frei.

Damit muss W6 keine zweite Zustandsdarstellung oder ein neues Snapshotformat
erfinden. Noch ungeprueft ist, ob die vorhandene S1-B-Gleichung unter dem
W5-E-Entscheid als erster transparenter Referenzprototyp reaktiviert werden
soll.

## Staerkste Baselines

Die unmittelbare staerkste Baseline ist die bereits implementierte lineare
kapazitaetsgewichtete reziproke S1-B-Akkommodation. Sie ist selbst noch kein
neuer Kandidat, sondern der erste moegliche technische Referenzprototyp.

Weitere Pflichtvergleiche bleiben:

- heutige S/H-Runtime ohne L;
- einzelne lokale Leaky-Spur von S;
- langsame identische Feldkopie;
- Produktintegrator mit festem Leser;
- adaptiver lokaler Gain oder Mobilitaetszustand;
- unabhaengige glatte Hysterese.

Baselinegleichheit verhindert Neuheits-, Memory- und Emergenzclaims. Nach
W5-E verhindert sie nicht mehr die Nutzung als offen benannter
Entwicklungsprototyp.

## Technische Abnahme eines spaeteren Prototyps

Vor jeder Funktionsauswertung muessen gemeinsam bestehen:

1. exakter Nullpfad;
2. endliche und begrenzte L-Werte;
3. atomare, reihenfolgeneutrale Fortschreibung;
4. Zeitteilungs-Konvergenz;
5. Observerunabhaengigkeit;
6. Snapshot-/Restore-Gleichheit;
7. L-Tausch und L-Neutralisierung als externe Intervention;
8. getrennte Bilanz von Weltwirkung, S-L-Austausch und Dissipation;
9. keine Rohdaten oder Inhaltsidentitaeten im Zustand;
10. unveraenderte heutige API, solange der Prototyp nicht explizit opt-in ist.

Diese Abnahme belegt nur technische Funktion.

## Sofortige Verwerfung

Eine Gleichungsfamilie wird verworfen, wenn:

- L direkten Medien- oder Observerzugriff erhaelt;
- eine zweite Runtime, Schicht oder Datenbank entsteht;
- S nach L und L nach S getrennte zweckgerichtete Regeln verwenden;
- Tickzahl oder technische Segmentierung die Entwicklung steuert;
- Begrenzung nur durch Reset oder Clipping nach unbeschraenkter Dynamik
  erreicht wird;
- ein bestimmtes Muster oder eine bestimmte Probe die Regel bestimmt;
- der Nullarm die aktuelle S/H-Runtime veraendert.

## Entscheidung

```text
lokale L-Funktionsrolle:                    gebunden
zulaessige Eingangsursachen:                gebunden
S-zu-L- und L-zu-S-Richtung:               gebunden
Begrenzungs- und Zeitgrenze:                gebunden
Nullpfad und Snapshotrolle:                 gebunden
staerkste Baseline:                         S1-B
vorhandenes L-Zustandsgeruest:              wiederverwendbar
vorhandene S1-B-Gleichung reaktiviert:      nein
aktuelle API geaendert:                     nein
```

Entscheidung: `L_FUNCTION_CONTRACT_BOUND_EXISTING_SCAFFOLD_REUSABLE`.

## Aussagegrenze

W6-A belegt keine entwickelte Feldform, Kopplungstopologie, Praegung,
Feldzeit, Memory, innere Wahrnehmung, Organisation, Semantik,
Selbstregulation oder KI. Lauf 197 bleibt reserviert und unberuehrt.

## Bester naechster Schritt

W6-B fuehrt einen statischen Reaktivierungs- und Kompatibilitaetsaudit der
vorhandenen S1-B-Akkommodation gegen W5-E und diesen Vertrag durch. Geprueft
werden Gleichung, Bilanz, Begrenzung, Nullarm, Snapshotformat, aktuelle API
und kontrollierter Browserpayloadpfad. Erst ein positives W6-B-Urteil darf
die bestehende opt-in Implementierung als ersten Referenzprototyp in die
aktive Entwicklungsserie aufnehmen.
