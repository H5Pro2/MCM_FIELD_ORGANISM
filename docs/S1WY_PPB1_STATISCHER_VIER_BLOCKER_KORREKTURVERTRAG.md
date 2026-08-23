# S1-WY: Statischer Vier-Blocker-Korrekturvertrag

## Auftrag und Grenze

S1-WY korrigiert ausschliesslich die vier in S1-WX gebundenen Luecken des
S1-WW-Funktionsvertrags. Alle anderen S1-WW-Rollen bleiben unveraendert
verbindlich. Implementierung, Fixturematerialisierung, Bildung, Probe,
Baseline, Matrix und Feld bleiben unausgefuehrt.

## 1. Erreichbare Schwellen und Probeabstaende

Der Zielprototyp ist fuer beide Modalitaeten ein reduzierter Nullvektor in
der jeweils gebundenen Traegerdimension. Jede Komponente einer Probe besitzt
denselben vorab festgelegten Wert. Damit entspricht die normalisierte
mittlere L1-Distanz exakt diesem Komponentenwert.

Auditive Bindung:

| Probe | Distanz | Erwartung |
|---|---:|---|
| exakt positiv | 0,00 | erkannt |
| nah positiv | 0,10 | erkannt |
| Schwellenrand | 0,20 | erkannt |
| nah negativ | 0,30 | nicht erkannt |
| deutlich negativ | 0,60 | nicht erkannt |

Die auditive Matchschwelle ist `0,20`.

Visuelle Bindung:

| Probe | Distanz | Erwartung |
|---|---:|---|
| exakt positiv | 0,00 | erkannt |
| nah positiv | 0,05 | erkannt |
| Schwellenrand | 0,10 | erkannt |
| nah negativ | 0,20 | nicht erkannt |
| deutlich negativ | 0,50 | nicht erkannt |

Die visuelle Matchschwelle ist `0,10`. Alle Werte liegen im vorhandenen
normalisierten Wertebereich und sind in jeder positiven Traegerdimension
direkt konstruierbar. Eine nachtraegliche Auswahl bleibt verboten.

## 2. Baselineerklaerung ohne Metadatenzirkularitaet

Eine Baseline erklaert eine Zelle funktional nur ueber:

- gleiche `RECOGNIZED`-Entscheidung;
- beide Distanzen null oder Distanzabweichung hoechstens `1e-12`.

Eine einzelne Baseline muss alle zehn Audio-/Video-Probezellen erklaeren.
Verschiedene Baselines duerfen nicht zellenweise kombiniert werden.

Zustandsdigests, Identitaet, Herkunft, Speicherrollen, gespeicherte
Skalarwerte und Rohhistorienzugriff werden separat berichtet. Ihre
Verschiedenheit ist kein funktionaler Unterschied und kann eine einfache
Baseline nicht kuenstlich ausschliessen.

## 3. No-Memory-Nullrolle

No-Memory bindet `observed_state_present = false`, nullable Zustands-,
Identitaets- und Herkunftsdigests, null Speicherrollen, null gespeicherte
Werte, null naechste Distanz und `recognized = false`. Diese Nullrollen
werden im Befunddigest gebunden. Ein erfundener Leerzustandsdigest ist nicht
zulaessig.

## 4. All-of-Aggregation

Ein technischer Funktionspass erfordert beide stabilisierten Bildungen und
alle zehn richtigen Kandidatenzellen: fuenf auditive und fuenf visuelle.
Eine vorhandene Zelle mit falscher Entscheidung ergibt Funktions-Fail. Eine
fehlende, doppelte, wiederholte oder digestungueltige Zelle macht die Methode
ungueltig. Eine Modalitaet darf die andere nicht ersetzen.

## Status

Die 60-Zellen-Struktur bleibt unveraendert:

```text
2 Modalitaeten x 6 Systeme x 5 Probearten = 60 Zellen
10 Kandidatenzellen + 50 Baselinezellen
execution_count = 0
```

Vertragsdigest:

```text
3a37d4dfaf83661cf93ff6328be73fc65b159455112426c3878c934c3a1dc6c9
```

`10 von 10` statische Vertragstests bestehen. Die technische Memory-Funktion
ist nun endlich spezifiziert, aber weder ausgefuehrt noch nachgewiesen. Auch
eine spaetere fehlende Baselineerklaerung waere fuer sich kein Nachweis einer
MCM-spezifischen Memory.

## Naechster Schritt

S1-WZ ist als rein statischer Abschlussaudit der kombinierten
S1-WW-/S1-WY-Vertragslage vorgesehen. Er muss bestaetigen, dass alle vier
S1-WX-Blocker geschlossen sind, ohne neue Luecken oder zirkulaere
Entscheidungen einzufuehren. Noch keine Fixture-, Matrix- oder
Feldausfuehrung.

## Grundlagen

- [S1-WX Vollstaendigkeits- und Fairnessaudit](S1WX_PPB1_STATISCHER_VOLLSTAENDIGKEITS_FAIRNESS_UND_NICHTZIRKULARITAETSAUDIT.md)
- [Maschinenlesbarer S1-WY-Vertrag](S1WY_PPB1_KORREKTURVERTRAG_SCHWELLE_BASELINE_NULLROLLE_AGGREGATION_V1.json)
