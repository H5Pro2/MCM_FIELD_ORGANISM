# S1-XA: Statischer Fixture- und Matrixmaterialisierungsvertrag

## Auftrag und Grenze

S1-XA bindet die endlichen Rollen fuer den ersten vollstaendigen privaten
Bildungs-/Probe-Funktionspfad. Es werden weder Fixturegenerator noch Runner
implementiert und weder Profilbinder, Referenzkern, Lebenszyklus, Probe,
Baseline oder Matrix ausgefuehrt.

## Vorhandenes Rezeptorprofil

Der Vertrag verwendet ausschliesslich das bestehende Profil `controlled`:

```text
auditory.log12.50-1500.w400.h40.v1       12 Traeger
visual.grid6x4.channels3.source24x16.v1  72 Traeger
```

Die geordneten Traegerkennungen muessen spaeter aus dem vorhandenen privaten
Profilbinder abgeleitet werden. Eine zweite hart codierte Traegerliste ist
verboten. Inventar- und Konfigurationsdigests muessen vor jeder Ausfuehrung
materialisiert sein.

## Endliche Konfigurationen

| Rolle | Audio | Video |
|---|---:|---:|
| Kapazitaet | 8 | 4 |
| Matchschwelle | 0,20 | 0,10 |
| Aktualisierungsrate | 0,10 | 0,10 |
| Stabilisierung | 3 | 3 |
| Ablaufgrenze | 512 | 128 |

Alle Werte liegen in den vorhandenen Profilkorridoren.

## Bildung und eingefrorener Zustand

Jede Modalitaet erhaelt drei Nullvektor-Kontakte in den Fenstern `0-1`,
`1-2` und `2-3`. Erwartet werden genau drei akzeptierte Schritte, ein
belegter stabilisierter Platz `.slot.000`, Stuetzung drei und ein
Nullprototyp. Alle anderen Plaetze bleiben frei.

Bank- und Identitaetsdigest werden nach der Bildung eingefroren. Jede der
fuenf Kandidatenproben beginnt unabhaengig von exakt diesem Zustand.

## Probe-Fixtures

Alle Proben verwenden das Fenster `4-5`. Ihre Komponentenwerte sind in jeder
Traegerdimension konstant und deshalb gleich der normalisierten L1-Distanz.

| Probe | Audio | Video | Erwartung |
|---|---:|---:|---|
| exakt positiv | 0,00 | 0,00 | erkannt |
| nah positiv | 0,10 | 0,05 | erkannt |
| Schwellenrand | 0,20 | 0,10 | erkannt |
| nah negativ | 0,30 | 0,20 | nicht erkannt |
| deutlich negativ | 0,60 | 0,50 | nicht erkannt |

## Systeme und Informationsbudgets

Sechs Systeme werden registriert: PPB-1, No-Memory, Replay, statischer
Prototyp, gleitender Zustand und Distanz zum letzten Bildungsvektor.

PPB-1 und die drei einfachen Einvektorbaselines speichern je eine
Modalitaetsdimension. Replay speichert drei Dimensionen und meldet seinen
Historienzugriff. No-Memory speichert null. Diese Rollen werden berichtet,
aber nicht fuer funktionale Gleichheit verlangt.

Der minimale Nullvektorpfad ist bewusst durch Replay und die drei einfachen
Einvektorbaselines erklaerbar. Ein spaeter vertragsgemaesses Ergebnis waere
daher vorab
`TECHNICAL_MEMORY_FUNCTION_PASS_BASELINE_EXPLAINED`, kein besonderer
MCM-Memory-Befund.

## 60-Zellen-Registry

Die geordnete Registry entsteht eindeutig aus:

```text
2 Modalitaeten x 6 Systeme x 5 Probearten = 60 Zellen
```

Zell-ID:

```text
s1xa.{modality_id}.{system_id}.{probe_class}
```

Registry-Digest:

```text
77d9437ce497bf298029c0b017cbb91df7f92a06d678c500d09319158b52668d
```

Vor jeder spaeteren Ausfuehrung muessen Profile, Traeger, Konfigurationen,
Bildungsgeschichten, eingefrorene Kandidaten- und Baselinezustaende, zehn
Probeframes und alle 60 Zellplaene digestgebunden materialisiert sein. Kein
Wert darf aus einem beobachteten Resultat stammen.

## Reproduzierbare Bindung

Vertragsdigest:

```text
2c3e36d4e3acaa05a5158a5e209b445f925e8d9b7926794a7b82e0c91dbc093c
```

`11 von 11` statische Vertragstests bestehen. Sie lesen Quellen und JSON,
importieren aber kein Projektmodul und erzeugen keinen Fixturezustand.

## Naechster Schritt

S1-XB ist als rein statischer Materialisierungs-, Registry- und
Nichtausfuehrungsaudit vorgesehen. Er muss Quellen, Profilableitung,
Konfigurationen, Fixtureerreichbarkeit, 60 eindeutige Zellidentitaeten,
Informationsbudgets, erwartete Baselineerklaerung und alle Nullzaehler
bestaetigen. Noch keine Implementierung oder Ausfuehrung.

## Grundlagen

- [S1-WZ korrigierter Vertragsabschlussaudit](S1WZ_PPB1_STATISCHER_KORRIGIERTER_VERTRAGSABSCHLUSSAUDIT.md)
- [Maschinenlesbarer S1-XA-Vertrag](S1XA_PPB1_STATISCHER_FIXTURE_UND_60_ZELLEN_MATRIXMATERIALISIERUNGSVERTRAG_V1.json)
