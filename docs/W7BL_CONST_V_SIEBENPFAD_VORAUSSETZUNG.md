# W7-BL: CONST-V-Siebenpfad-Voraussetzung

## Zweck

W7-BL korrigiert die Anschlussgrenze vor der registrierten 70-fachen
R2/R4-Konvergenzpruefung. W7-BK hat technisch nur AB/R4 und BA/R4 erzeugt.
Das reicht nicht fuer die im W7-BJ-Vertrag gebundenen 35 Rollen.

## Zulassungsschranke

Vor jeder Distanz-, Epsilon- oder Effektbodenberechnung muessen alle sieben
Pfade `ab`, `ag`, `ba`, `bg`, `ua`, `ub` und `ug` auf allen drei Aufloesungen
R1, R2 und R4 materialisiert und strukturell gebunden sein. Das sind 35
Pfad-Checkpoint-Rollen und 70 S/H-Komponenten.

Die Schranke erzeugt selbst keine Laufzeitdaten. Sie erlaubt weder eine
Konvergenzentscheidung noch eine Memory-, Feldfunktions- oder
Organisationsaussage.

## Aktueller Befund

Der W7-BL-Gate ist statisch implementiert und bindet den bestehenden
Siebenpfadplan sowie den W7-BJ-Vertrag. Die fehlenden sechs Pfade und ihre
R1/R2/R4-Strukturen sind noch nicht ausgefuehrt. Deshalb bleiben die
70 Vergleiche gesperrt.

## Naechster Anschluss

Als naechstes ist ein privater CONST-V-Siebenpfad-Executor erforderlich. Erst
nach dessen vollstaendiger R1/R2/R4-Materialisierung darf die numerische
Konvergenzpruefung implementiert oder ausgefuehrt werden.
