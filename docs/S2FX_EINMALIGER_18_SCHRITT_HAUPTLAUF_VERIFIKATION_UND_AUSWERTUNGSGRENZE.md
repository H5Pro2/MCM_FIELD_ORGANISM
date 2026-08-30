# S2-FX: Einmaliger 18-Schritt-Hauptlauf

## Ausfuehrung

Der Hauptlauf wurde genau einmal unter der Lauf-ID
`s2fx-main-20260830-01` ausgefuehrt. Der Umfang blieb unveraendert:

- 24 Rezeptoranalysen;
- 54 Bildungen;
- 18 Komponentenidentitaetspruefungen;
- eine Folgenprobe;
- sechs Inhaltsproben;
- 103 Operationen und 206 START-/RESULT-Ereignisse.

Der Ausfuehrungsschalter wurde nur fuer diesen Aufruf auf `True` gesetzt und
anschliessend wieder auf `False` geschlossen. Der aktuelle Runner besitzt
wieder seinen qualifizierten SHA-256
`495675b846698f57517a0f0cf94df55849062e027d0e56c7929223f7fef133ec`.
Es gab keine Wiederholung, Teilfortsetzung, Parameter- oder Schwellenaenderung.

## Unabhaengige Verifikation

Der unabhaengige read-only Verifikator wurde genau einmal auf das fertige
Fuenf-Dateien-Laufverzeichnis angewendet. Ergebnis:

```text
RECORDING_COMPLETE
103 Operationen
206 Ereignisse
Issues: 0
Finding-Digest:
c178f351f706c9e94270494ca7ab8b7647579468aeb96b81bcc33eb345e2b5be
```

Damit ist die technische Aufzeichnung vollstaendig. Dieser Status bewertet
noch keine Speicherfunktion.

## Auswertungsgrenze

Die getrennte reine Funktionsauswertung wurde nach erfolgreicher Verifikation
begonnen, stoppte jedoch fail-closed vor dem Aufruf von `evaluate_s2fu`.
Grund ist ein Widerspruch innerhalb der gespeicherten Belege:

- der Formationsbeleg meldet fuer visuellen P1-Support ab Schritt 8 den Wert
  `0`;
- der aufgezeichnete visuelle PPB-1-Zustand und der finale read-only Befund
  enthalten fuer P1 einen stabilen Slot mit Support `3`;
- auditiv wird P1 bereits im Formationsbeleg korrekt mit Support `3` erfasst.

Die Ursache liegt im reinen Beleghelfer `_slow_supports`: Er identifiziert
einen Prototyp nur durch exakte Float-Tupelgleichheit. Nach Mittelung weicht
der visuelle Prototyp im letzten Bitbereich vom literal gebundenen
Rezeptorwert ab, obwohl seine Distanz praktisch null ist. Dadurch wird der
vorhandene visuelle Slot im zusammenfassenden Formationsbeleg nicht gefunden.

Der Widerspruch wurde nicht repariert, uminterpretiert oder durch Auswahl nur
einer Modalitaet verdeckt. Der Auswerter besitzt fuer den Formationsverlauf
nur ein gemeinsames Supportfeld und kann die widerspruechlichen auditiven und
visuellen Angaben daher nicht verlustfrei uebernehmen.

Status:

`S2FX_FUNCTION_EVALUATION_NOT_EVALUABLE_EVIDENCE_CONTRADICTION`

## Deskriptiv aufgezeichnete Einzelbefunde

Ohne positive Gesamtwertung zeigen die unveraenderten Rohbelege:

- die B4-Folgenprobe nach Schritt 4 ist erkannt und read-only;
- P1 und P2 fehlen final aus B4 und TSPM-Fast;
- der naechste P1-Slow-Slot besitzt auditiv und visuell Support `3`, ist
  stabil und wird erkannt;
- der naechste P2-Slow-Slot besitzt auditiv und visuell Support `1`, ist
  instabil und wird nicht erkannt;
- alle sechs Inhaltsproben besitzen identische Vor-/Nachzustandsdigests;
- es gibt keine automatische Auswahl zwischen `B4_RECENT`, `TSPM_FAST` und
  `TSPM_SLOW`.

Diese Punkte sind deskriptive Einzelbefunde, kein bestaetigter
S2-FU-Gesamtbefund. Der Lauf bleibt dauerhaft abgeschlossen und wird nicht
wiederholt oder nachtraeglich repariert.

## Naechster Schritt

Vor einem neuen unabhaengigen Funktionslauf ist ausschliesslich die
Instrumentierung zu korrigieren: Slow-Support muss aus dem validierten
Slotbefund beziehungsweise einer gebundenen Distanzregel stammen und auditiv
wie visuell getrennt belegbar bleiben. Diese Korrektur benoetigt eine neue
Freigabe und darf den abgeschlossenen S2-FX-Lauf nicht veraendern.
