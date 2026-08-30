# S2-FZ: Unabhaengiger 18-Schritt-Bestaetigungslauf

## Ausfuehrungsgrenze

Der freigegebene Hauptlauf wurde genau einmal unter der neuen Lauf-ID
`s2fz-confirmation-20260830-01` ausgefuehrt. Geschichte, Fixtures, Schwellen,
Speicherkerne und Auswertungsregeln blieben unveraendert. Der Umfang lautet:

- 24 Rezeptoranalysen;
- 54 Bildungen;
- 18 Komponentenidentitaetspruefungen;
- eine Folgenprobe;
- sechs Inhaltsproben;
- 103 Operationen und 206 verkettete Ereignisse.

Der Launcher meldet Exit-Code `0`, genau einen `run_main_once`-Aufruf und
Retryzahl `0`. Das Hauptgate wurde danach wieder auf `False` geschlossen.
S2-FX und seine Belege blieben unveraendert `NOT_EVALUABLE`.

## Unabhaengige Verifikation

Der unabhaengige read-only Verifikator wurde genau einmal auf das fertige
Fuenf-Dateien-Laufverzeichnis angewendet. Ergebnis:

```text
RECORDING_COMPLETE
103 Operationen
206 Ereignisse
Issues: 0
Finding-Digest:
7b9140a5a5e938f94d21145983b3fe0da907a528682238b7401a56ea0f5dfa21
```

Erst nach diesem Befund wurde die reine Funktionsauswertung aus den
gespeicherten Belegen materialisiert. Dabei wurden keine Rezeptor-, Speicher-
oder Koordinatorfunktionen erneut aufgerufen.

## Materialisierungsgrenze

Die erste reine Materialisierung uebergab versehentlich das vollstaendige
aufgezeichnete B4-Ereignisobjekt an das kanonische Auswerterfeld, statt dessen
bereits enthaltenes Feld `event` zu verwenden. Dadurch meldete der Auswerter
18 rein formale B4-Ereignisabweichungen. Dieser Befund ist mit
`INVALID_PURE_MATERIALIZATION_NOT_A_FUNCTIONAL_FINDING` markiert und bleibt
transparent erhalten.

Der statische Abgleich bestaetigte vor der kanonischen Materialisierung:

- jedes aufgezeichnete Objekt enthaelt genau den erwarteten kanonischen
  Ereignisnamen;
- alle 18 erwarteten B4-Ereignisse stimmen ueberein;
- die erste Auswertung enthielt ausschliesslich diese 18 Projektionsfehler;
- Hauptlauf, Verifikator und aufgezeichnete Belege wurden nicht wiederholt
  oder veraendert.

Die kanonische reine Materialisierung projiziert deshalb ausschliesslich
`b4_event.event`. Schwellen, Sollwerte und Entscheidungsregeln bleiben
unveraendert.

## Funktionsergebnis

Die kanonische Auswertung lautet:

```text
S2FU_FUNCTION_CONFIRMED
Method issues: 0
Functional findings: 0
P2 unstable trace present: true
Evaluation-Digest:
244f9b7e848c90eb029e62746c9be5f9f3a88145618648409bb90327f6e72dc6
```

Getrennte Befunde:

- B4 erkennt nach Schritt 4 die gespeicherte Folge P1, P2, P3, P4 in ihrer
  tatsaechlichen Bildungsreihenfolge.
- P1 fehlt am Ende aus B4 und TSPM-Fast.
- P1 besitzt auditiv und visuell Slow-Support `3`, ist stabil und wird
  read-only erkannt.
- P2 fehlt am Ende aus B4 und TSPM-Fast.
- P2 besitzt auditiv und visuell Slow-Support `1`, ist instabil und wird
  nicht erkannt.
- Composite und Standalone-Komponenten stimmen nach allen 18 Schritten
  ueberein.
- Alle Probezugriffe bleiben read-only.
- Es gibt keine automatische Auswahl zwischen `B4_RECENT`, `TSPM_FAST` und
  `TSPM_SLOW`.

## Einordnung

S2-FZ bestaetigt fuer genau diese gebundene synthetische Geschichte einen
begrenzten technischen Funktionsnachweis des atomaren B4-/TSPM-1-Verbunds:
Kurzfolge, wiederholungsabhaengige Slow-Erhaltung und kontrolliertes
Vergessen werden gleichzeitig abgebildet.

Der Befund ist ein belastbarer MCM-kompatibler Memory-Grundbaustein auf
Engineeringebene. Er belegt keine allgemeine oder langfristige Memory, keine
Semantik, keine automatische Kontextauswahl und keine MCM-spezifische
Speicherphysik. Feldintegration ist nicht erfolgt.

Status:

`S2FZ_LIMITED_ATOMIC_B4_TSPM1_MEMORY_FUNCTION_CONFIRMED`
