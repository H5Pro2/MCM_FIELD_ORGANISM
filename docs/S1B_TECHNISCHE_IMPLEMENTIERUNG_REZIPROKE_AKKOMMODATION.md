# S1-B: Technische Implementierung der reziproken Akkommodation

Stand: 2026-08-07

Status: `S1B_REFERENCE_SUBSTRATE_TECHNICALLY_BOUND`

## Zweck

S1-B implementiert den in S0 gebundenen lokalen L-Traeger und die in S1-A
festgelegte kapazitaetsgewichtete reziproke S-L-Akkommodation als optionalen
technischen Referenzpfad.

Die Implementierung ist kein Forschungsversuch und kein Nachweis von
Praegung, Memory, Feldzeitverdichtung, Organisation oder KI.

## Implementierte Komponenten

### Lokaler L-Zustand

Datei:

```text
mcm_field_organism/mcm_local_development_state.py
```

Gebunden sind:

- `MCMLocalDevelopmentContract` mit Gleichungsidentitaet, `rho` und `g`;
- genau ein signierter Wert `L_i` in `[-1,1]` pro bestehendem Feldneuron;
- kanonische ASCII-Payloads und SHA-256-Digests;
- strikte Ablehnung unbekannter Felder und versteckter Nutzdaten;
- Nullaufbau und expliziter Aufbau aus vollstaendigen L-Werten.

Der Zustand enthaelt keine Rohframes, Audiosamples, Episoden, Labels,
Cluster, Wiederholungszaehler oder Auswertungswerte.

### Gemeinsamer Schema-3-Feldzustand

`SharedMCMField` und `SharedMCMFieldSnapshot` tragen optional genau einen
vollstaendigen L-Zustand.

```text
Schema 1 = historischer schneller S/H-Zustand
Schema 2 = historischer S/H-Zustand plus technische M-Masse
Schema 3 = S/H-Zustand plus neuer L-Entwicklungszustand
```

Schema 1 und 2 bleiben unveraendert lesbar. M und L duerfen in der ersten
S1-B-Scheibe nicht gleichzeitig vorliegen. Die schnelle Projektion eines
Schema-3-Snapshots entfernt L vollstaendig und reproduziert die historische
Schema-1-Darstellung.

Snapshot, JSON-Roundtrip und Wiederaufnahme tragen Zustand und Naturparameter
vollstaendig.

### Exakte gemeinsame Integration

Datei:

```text
mcm_field_organism/s1b_reciprocal_accommodation.py
```

Der opt-in Pfad integriert:

```text
dS/dt = A(U)S + b(U) - lambda_S*S - g(S-L)
dL/dt = (g/rho)(S-L)
dH/dt = r_H*S - (r_H+lambda_S)H
```

Mit `Y=sqrt(rho)L` ist der S/Y-Block symmetrisch und wird spektral exakt
integriert. H wird aus der gesamten gekoppelten S-Trajektorie desselben
Intervalls berechnet. Es gibt keine Euler-Schrittweite und keine
Ruecklesephase von `L_(t+1)` nach `S_(t+1)`.

### Nullarm

Bei `g=0` wird der bisherige schnelle Integrator direkt verwendet. L bleibt
unveraendert und die schnelle Schema-1-Projektion ist digestgleich zum
historischen Pfad.

Der allgemeine `SharedMCMField.advance()`-Pfad lehnt einen angehaengten
L-Zustand ab. Dadurch kann L nicht versehentlich ohne seine reziproke
Naturgleichung mitgefuehrt werden.

### Technische Interventionen

Observerseitig und ausserhalb der Organismusfunktion sind implementiert:

- vollstaendiger L-Zustandsersatz bei identischem Naturvertrag;
- Neutralisierung aller L-Werte auf null;
- Tausch vollstaendiger kompatibler L-Zustaende zwischen zwei Feldern.

Diese Funktionen sind Testinterventionen. Die Runtime ruft sie nicht selbst
auf und besitzt keine Schreib-, Abruf- oder Loeschphase.

## Technische Abnahme

Neue fokussierte Suite:

```text
tests/test_s1b_reciprocal_accommodation.py
9 passed
```

Geprueft wurden:

1. Schema-3-Roundtrip und vollstaendige Wiederaufnahme;
2. digestgleicher schneller Nullpfad bei `g=0`;
3. Bilanz `S + rho*L` im isolierten Austausch;
4. langsamere momentane L-Aenderung;
5. Invarianz gegen Zeitteilung bei konstantem Generator;
6. Observerpassivitaet trotz mutierter Beobachtungskopien;
7. L-Tausch und L-Neutralisierung ohne Aenderung des schnellen Zustands;
8. Sperre des generischen Advance-Pfads und der M/L-Kombination;
9. Ablehnung versteckter Payloads, Bereichsverletzung und Vertragswechsel.

Bestehende Kernregressionen:

```text
47 passed, 12 subtests passed
```

Geprueft wurden bestehendes Shared Field, Schema 1/2, M-Nullarm, neutrale
Feldsitzung sowie synchrone und asynchrone S/H-Runtime.

Oeffentliche API und Syntax:

```text
33 passed
py_compile bestanden
```

Alle Pytest-Laeufe melden die bereits vorhandene Cachewarnung, dass der Pfad
`.pytest_cache/v/cache` unter Windows nicht neu angelegt werden kann. Sie
veraendert die Testergebnisse nicht.

## Grenze der globalen Testsammlung

Die vollstaendige Projektsuite kann im aktuellen Bestand nicht gesammelt
werden. Mindestens 20 Public-AV-Testmodule scheitern bereits beim Import, weil
`mcm_field_organism.public_av_six_arm_field_execution` den von ihnen
erwarteten privaten Namen `_sequences` nicht exportiert.

Diese vorhandene Public-AV-Luecke liegt ausserhalb S1-B. Sie wurde weder
veraendert noch umgangen. Die S1-B-Abnahme stuetzt sich deshalb auf die direkt
betroffenen neuen Tests, Shared-Field-Regressionen und den aktuellen
Architektur-API-Test.

## Aktuelle technische Grenzen

- S1-B ist ein opt-in Pfad fuer atomare gemeinsame Rezeptorintervalle;
- transiente asynchrone Einzelabschlussintegration von L ist noch nicht
  implementiert;
- der Pfad ist noch an keinen S2-Testweltrunner gebunden;
- Parameter sind nicht fuer einen Forschungsversuch vorregistriert;
- B1, B3, B4 und B5 sind noch nicht als gemeinsamer S2-Vergleichsrunner
  implementiert;
- die Gleichung bleibt exakt die lineare B2-Referenzbaseline.

Diese Grenzen verhindern keinen kontrollierten S2-Aufbau mit festen
Rezeptorintervallen. Sie verhindern aber jede Aussage ueber eine allgemeine
audiovisuelle oder asynchrone Organismusfunktion.

## Aussagegrenze

Technisch vorhanden ist nun:

```text
Weltkontakt -> S/H-Feld -> langsamer L-Zustand -> spaetere S/H-Feldwirkung
```

Noch nicht nachgewiesen sind:

```text
Praegung
Memory
relative Feldzeit
Rekonstruktion
Cluster oder Abstraktion
Organisation oder KI
```

Jede beobachtete S1-B-Nachwirkung ist bis zu einer kontrollierten
Gegenpruefung vollstaendig als lineare reziproke Zweizustandsdynamik zu
bezeichnen.

## Entscheidung

```text
L-Zustand:                         implementiert
Schema-3-Snapshot:                 implementiert
exakte S/H/L-Integration:          implementiert
Nullarm:                           bestanden
Bilanz und Zeitteilung:            bestanden
Observer, Tausch, Neutralisierung: bestanden
Kernregressionen:                  bestanden
S1-B technischer Status:           gebunden
S2-Forschungsfreigabe:             nein
Forschungslauf:                    nein
```

## Bester naechster Schritt

S2-A ist mit einer kleinen kontrollierten audiovisuellen Rezeptor-Testwelt,
`1, 2, 4, 8` getrennten Kontakten gegen kontaktzeitgleiche Dauerkontakte und
B0- bis B5-Pflichtarmen vorregistriert. S2-B bindet inzwischen den
technischen Runnervertrag und der S2-C-Kern ist implementiert. S2-C2 bis
S2-C8 binden Einzelbatch, r1.a/c1.a, S/H-Angleichung, Probe P, N8, Observer,
Einpaardistanzen und Identitaetskontrolle; S2-C9 bis S2-C16 schliessen die
A/B-Referenz bis zur kanonischen End-to-End-Komposition. Der
S2-Zwischenentscheid verweist als naechsten Schritt auf den statischen
S1-C-Kandidatenvertrag. Noch keinen Versuch ausfuehren und keine Praegung
behaupten.
