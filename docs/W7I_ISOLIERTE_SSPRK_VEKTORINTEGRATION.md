# W7-I: Isolierte SSPRK-Vektorintegration

Stand: 2026-08-09

Entscheidung: `ISOLATED_CAPACITY_SSPRK_IMPLEMENTED`

Arbeitsart: additive opt-in Integrationsscheibe

SharedMCMField-Runtime: unveraendert

Forschungslauf: nein

## Implementierter Umfang

Neu implementiert wurde:

```text
mcm_field_organism/capacity_limited_mcm_f3_integrator.py
```

Das Modul integriert ausschliesslich die W7-G-Kopplungsableitung:

- M wird durch den kapazitaetsbegrenzten Kantenfluss fortgeschrieben;
- S erhaelt nur die an denselben M-Fluss gebundene Rueckarbeit;
- H bleibt exakt unveraendert;
- F0, Rezeptorkontakt, schnelle Felddiffusion, Dissipation und Weltzeitpfad
  sind nicht Bestandteil dieser Scheibe.

Das Ergebnis besteht aus technischen S/H/M-Vektoren und passiven skalaren
Diagnosen. Es wird kein `SharedMCMField` erzeugt oder fortgeschrieben.

## Integrationsform

Fuer jeden SSPRK-Stufenzustand erzeugt das Modul temporaer:

- einen `MCMNeuronLayer` mit den aktuellen technischen S/H-Vektoren;
- einen `MCMSubstrateState` mit dem aktuellen M-Vektor.

Danach wird ausschliesslich
`compute_capacity_limited_mcm_f3_coupling(...)` aus W7-G aufgerufen. Es gibt
keine zweite Implementierung der Kantenphysik.

Die drei Shu-Osher-Stufen verwenden die in W7-H gebundene Schrittweite:

```text
rho_S = 4*eta*lambda_sm*d_max
rho_M = 2*lambda_sm*d_max
h_safe = 0.5 / max(rho_S, rho_M)
```

Diese reduzierte Grenze gilt nur fuer die isolierte Kopplung. Eine spaetere
vollstaendige Runtime muss zusaetzlich die vorhandenen F0-, H-, Dock- und
Dissipationsraten einbeziehen.

## P0 und Nullzeit

Bei `lambda_sm = 0` werden keine SSPRK-Stufen ausgefuehrt. Alle Vektoren
bleiben exakt unveraendert und die Methode lautet `p0.exact`.

Auch ein Intervall der Dauer null erzeugt keine Stufe. Bei aktivem Arm bleibt
die technische Methodenkennung erhalten, damit Nullzeit nicht mit einer
P0-Ablation verwechselt wird.

## Diagnosen

Die Scheibe liefert:

- Methode, Subschritt- und Stufenzahl;
- Refinement, sichere und groesste verwendete Schrittweite;
- maximalen Gesamtmassenfehler;
- kleinstes und groesstes M;
- kleinste freie Kapazitaet;
- groesste Kapazitaetsueberschreitung;
- maximale absolute S- und H-Auslenkung;
- SHA-256-Digest aus Gleichungskennung und `site_capacity`.

Jeder vollstaendige SSPRK-Stufenzustand wird vor weiterer Verwendung
validiert. Nichtendlichkeit, S/H-Grenzverletzung, negatives M,
Kapazitaetsueberschreitung oder Massenfehler brechen ohne Korrektur ab.

## Technische Tests

Neu angelegt:

```text
tests/test_capacity_limited_mcm_f3_integrator.py
```

Die sieben Tests pruefen:

1. exakten P0-Pfad und unveraenderte Eingaben;
2. S/H/M-, Massen- und Kapazitaetsinvarianten im aktiven SSPRK-Pfad;
3. exakte deterministische Wiederholung;
4. geordnete n/2n/4n-Zeitverfeinerung;
5. Nullzeit ohne Stufenausfuehrung;
6. harte Dauer- und Kapazitaetsfehler;
7. fehlenden Export ueber `current_api`.

Der fokussierte Verbund aus W7-I, W7-G und bestehender K2/F3-Kopplung ergibt:

```text
Ran 28 tests in 0.084s
OK
```

Mit Syntaxpruefung und den drei bestehenden `current_api`-
Verbrauchersuiten ergibt sich:

```text
Ran 46 tests in 0.384s
OK
```

## Unveraenderte Grenzen

W7-I hat nicht veraendert:

- bestehende K2/F3-Kopplung und -Runtime;
- `SharedMCMField` oder sein Snapshot-Schema;
- `mcm_field_organism.__init__`;
- `mcm_field_organism.current_api`;
- Browser-, Audio-, Video-, Runner- und Reportpfade.

Der Kapazitaetsvertrag wird nicht persistiert. Sein Digest ist nur passive
Diagnose des expliziten Funktionsarguments.

## Aussagegrenze

W7-I belegt die diskrete technische Invarianz des isolierten gekoppelten
S/M-Teils im geprueften Korridor. Nicht belegt sind:

- Zusammenspiel mit F0, Nachhallentwicklung oder Rezeptorereignissen;
- Snapshot/Restore einer vollstaendigen Feldruntime;
- kontrolliertes Audio-, Video- oder Browserverhalten;
- konkurrierende Verdraengung, funktionale Loesung oder
  Kapazitaetswiederverwendung;
- Verdichtung, Feldzeit, Memory, Organisation, Semantik,
  Selbstregulation oder KI.

## Entscheidung

```text
isolierte SSPRK-Scheibe:             implementiert
W7-G als einzige Kopplungsquelle:    ja
M- und Kapazitaetsgrenzen:           bestanden
deterministische Wiederholung:       bestanden
n/2n/4n-Verfeinerung:                bestanden
SharedMCMField-Runtime:              unveraendert
current_api:                         unveraendert
Forschungslauf:                      nein
```

## Verwendete Projektquellen

- [W7-G reine Kopplungsimplementierung](W7G_IMPLEMENTIERUNG_REINE_KAPAZITAETSBEGRENZTE_KOPPLUNG.md)
- [W7-H diskreter Integrationsvertrag](W7H_DISKRETER_INTEGRATIONSVERTRAG_KAPAZITAETSBEGRENZTER_TRANSPORT.md)
- [K2/F3 Integratorfamilien-Audit](K2_F3_INTEGRATORFAMILIEN_AUDIT.md)
- [K2/F3 SSPRK-Runtimevertrag](K2_F3_SCHEIBE_C_SSPRK_RUNTIME_VERTRAG.md)

## Bester naechster Schritt

W7-J bindet statisch den opt-in Adaptervertrag zur vollstaendigen
`SharedMCMField`-Runtime. Er muss die vorhandenen F0-/H-/Ereignisraten mit
der W7-H-Kapazitaetsgrenze vereinigen, die Obergrenze nach jeder SSPRK-Stufe
und vor Commit pruefen, den Kapazitaetsvertrag bei Restore explizit binden
und P0 exakt lassen. W7-J implementiert noch keinen Adapter und startet keine
Testwelt.
