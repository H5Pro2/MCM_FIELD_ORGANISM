# W7-BJ: Vertrag fuer CONST-V-AB/BA-R4 und Konvergenz

## Zweck

W7-BJ registriert die letzte technische Aufloesung vor der R1/R2/R4-
Konvergenzpruefung. Zuerst werden AB/R4 und BA/R4 mit der R2-Struktur
wiederholt. Erst nach bestandener R4-Wiederholung darf die vorregistrierte
Konvergenzpruefung vorbereitet werden.

## Gebundene Grundlage

- W7-BH-Digest: `b191a837...3583`
- W7-BI-Digest: `b4daf8e5...cbf77`
- W7-BD-Adapterdigest: `496a7955...58db`
- W7-Y-Plan: `c771a3c...5b32`
- Aufloesung: R4

AB und BA bleiben mit fuenf Hauptproduktionen, fuenf isolierten Checkpoint-
Proben und 91 erwarteten Rohsamples je Probe strukturell identisch. Jede
Checkpointkopie setzt nur S und H auf null; der technische Skalar bleibt
erhalten und die Probe kehrt nicht in die Hauptkette zurueck.

## Konvergenzgrenze nach R4

Nach erfolgreicher R4-Wiederholung sind 35 Rollen und zwei Komponenten (`S`,
`H`) gebunden, also 70 R2/R4-Vergleiche. Die Regel lautet:

`D24 < D12` oder beide Werte sind exakt null.

Erst bei vollstaendiger Aufloesung ist Epsilon das Maximum aller 70 R2/R4-
Linf-Abstaende. Der Effektboden ist danach `10 * Epsilon`. W7-BJ berechnet
keine dieser Werte.

## Evidenzgrenze

Der Vertrag erlaubt keine Memory-, Feldfunktions- oder Organisationsaussage.
Die technische Skalarvariable bleibt eine Baselinevariable. R4 ist nur die
Voraussetzung fuer die spaetere numerische Pruefung.

## Naechster Anschluss

W7-BK implementiert den privaten AB/BA-R4-Executor. W7-BL muss vor einer
numerischen Auswertung zuerst die sechs fehlenden Pfade des Siebenpfadplans
in R1/R2/R4 materialisieren; die 70er-Pruefung bleibt bis dahin gesperrt.
