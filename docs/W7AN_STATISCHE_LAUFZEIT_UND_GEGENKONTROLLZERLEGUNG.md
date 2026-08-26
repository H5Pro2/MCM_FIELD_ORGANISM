# W7-AN: Statische Laufzeit- und Gegenkontrollzerlegung

## Entscheidung

`W7AN_EXECUTION_DECOMPOSITION_BOUND_CONTAINER_STILL_OPEN`

Der bisherige serielle Vollauf vermischt Primaermaterialisierung und
Gegenkontrollen. Diese Datei bindet deren tatsaechliches Inventar statisch.
Es wurde keine CAP-Kette, Testwelt oder Auswertung ausgefuehrt.

## Primaerdurchgang

Je R1-, R2- und R4-Rolle fallen an:

- 67 kanonische CAP-Integrationen mit Produktionszeugen;
- 35 kanonische Messintegrationen mit Messzeugen;
- 67 Wiederholungen fuer die CAP-Pfadreihenfolge;
- 4 Wiederholungen fuer die Haupt-/Probe-Reihenfolge;
- 35 Wiederholungen fuer die Messreihenfolge;
- 1 Wiederholung fuer die Observerpassivitaet.

Das sind 209 Integrationen je Rolle und 627 im Primaerdurchgang. Nur die
306 kanonischen Produktions- und Messintegrationen liefern die im
W7-AM-Vertrag geforderten, dauerhaft gebundenen Zeugen. Die weiteren 321
Integrationen sind Gegenkontrollen.

## Vollstaendige Determinismuspruefung

Der bisherige Container wiederholt kein vollstaendiges
Aufloesungsresultat und verarbeitet die drei Aufloesungsrollen nicht in
umgekehrter Reihenfolge. W7-AM fordert beides. Der kleinste gemeinsame
Gegenlauf wiederholt daher alle 627 Primaerintegrationen in der Rollenfolge
R4, R2, R1 und vergleicht jeden Aufloesungsdigest mit seinem Primaerresultat.

Damit umfasst eine vollstaendige W7-AN-Abnahme 1.254 Integrationen:

```text
627 Primaerdurchgang
+ 627 deterministische Wiederholung in umgekehrter Rollenfolge
= 1.254 Integrationen
```

Davon sind 306 zeugentragende Primaerintegrationen und 948 reine
Validierungsintegrationen.

## Gebundene Batches

`w7an_execution_decomposition.py` zerlegt beide Durchgaenge in insgesamt 36
statische Batches. Kein Batch umfasst mehr als 67 Integrationen. Die Rollen,
Faktoren, Phasen und Anzahlen sind digestgebunden. Der Plan selbst fuehrt
nichts aus und setzt ausdruecklich:

- `runtime_executed = false`;
- `container_completed = false`.

W7-AE und W7-AG besitzen private Grenzen fuer alle sechs Phasen je
Aufloesung. Der private Stufenexecutor verbindet sie und hat seine reale
R1-Kompatibilitaetsausfuehrung bestanden.

## Grenzen

- Kein Kontrollresultat wird aus einem Primaerresultat nur abgeleitet.
- Keine Pflichtgegenkontrolle wird entfernt oder als bestanden markiert.
- Es gibt keinen Gesamtcontainerdigest und keinen Nachweis von 306 Zeugen.
- Keine Konvergenz, Schwelle oder Feldauswertung wird berechnet.
- Kein Browser, Runner, Report oder Forschungslauf wurde gestartet.
- Daraus folgt kein Funktions-, Memory-, Feldzeit-, Organisations- oder
  KI-Befund.

## Bester naechster Schritt

Vor R2 und R4 einen privaten Gesamtkoordinator statisch binden. Er muss die
Primaer- und Gegenlaufreihenfolge, P0-Einmaligkeit und den Stopp nach jeder
einzelnen Phase erzwingen.
