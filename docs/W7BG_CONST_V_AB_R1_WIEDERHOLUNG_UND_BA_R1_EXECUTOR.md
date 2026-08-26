# W7-BG: CONST-V-AB/R1-Wiederholung und BA/R1-Executor

## Zweck

W7-BG setzt die in W7-BF registrierte Zweirollenfolge um. Der Executor
wiederholt zuerst den kanonischen AB/R1-Lauf. BA/R1 wird nur dann
materialisiert, wenn der AB-Gesamtdigest exakt dem W7-BE-Referenzdigest
entspricht.

## Technischer Ablauf

1. AB/R1 wird mit demselben W7-BE-Einstieg erneut erzeugt.
2. Der Ergebnisdigest sowie die gebundene Rollenstruktur werden geprueft.
3. Bei Abweichung endet der Executor vor BA/R1.
4. Bei exakter Wiederholung wird BA/R1 ueber denselben privaten Einpfadkern
   mit dem autorisierten B-Praefix und vier autorisierten A-Fortsetzungen
   erzeugt.

Beide Rollen verwenden R1, fuenf Hauptproduktionen, fuenf isolierte
Checkpointproben und 91 rohe S/H/Skalar-Samples je Probe.

## Evidenzgrenze

Das einzige Ergebnis ist `TECHNICAL_TWO_ROLE_COMPLETE`. W7-BG berechnet
keine AB/BA-Distanz, kein Epsilon, keinen Effektboden und kein Profil. Der
technische Skalar bleibt eine Baselinezustandsvariable und ist kein Memory.
Der Executor ist privat und schreibt keine Reports.

## Technischer Laufbefund

- AB-Wiederholungsdigest: `88fd9722420a94f09c15fbce9e4e0b2a283a1a56422ed653e92ef2a7aeaf8708`
- terminaler W7-BG-Digest: `3d2abeda7658443639b327f33d79c304ffc1a6bdc8fa56016d7e42040c841927`
- AB und BA jeweils bis Tick 8.000.000;
- zusammen 2502 Integrationssubschritte;
- maximaler Massenerhaltungsfehler: `6.283862319378386e-14`;
- 7 fokussierte Tests bestanden.

## Naechster Anschluss

W7-BH registriert die R2-Wiederholung derselben beiden Richtungen. Erst mit
R1 und R2 darf eine erste rohe D12-Distanz vorbereitet werden; eine
Konvergenz- oder Wirkungsentscheidung bleibt bis R4 gesperrt.

W7-BH hat diesen R2-Vertrag mit Digest `b191a837...3583` statisch registriert.
W7-BI folgt als wertfreier R2-Executor.
